"""A griffe extension for the stubs of src/monero, which mkdocs.yml loads.

griffe joins the @overload definitions of a function to the definition that follows them, the implementation. A stub has none, since
the implementation is in the C++ of the module: the overloads stay apart, the function is not a member of its class or module, and
mkdocstrings does not show it. For each of them this extension adds the function, with its overloads, which mkdocstrings shows as its
signatures, and with one docstring made from theirs: the description of each overload when they differ, and the parameters of all.
"""

from __future__ import annotations

import re
from typing import Any, cast

from griffe import Class, Docstring, Extension, Function, Module, Parameter, ParameterKind, Parameters, SphinxOptions, logger
from typing_extensions import override

# the start of a field of a sphinx docstring, as ":param int start_height:" or ":returns MoneroSyncResult:"
_FIELD = re.compile(r"^:(\w+)\b([^:]*):")


class StubOverloads(Extension):
    """Adds the functions of the stubs that only have overloads."""

    @override
    def on_package(self, *, pkg: Module, **kwargs: Any) -> None:
        self._add_functions(pkg)

    def _add_functions(self, obj: Module | Class) -> None:
        for name, overloads in list(obj.overloads.items()):
            if overloads and name not in obj.members:
                obj.set_member(name, self._function(obj, name, overloads))
                del obj.overloads[name]
        for member in obj.members.values():
            if not member.is_alias and isinstance(member, (Module, Class)):
                self._add_functions(member)

    def _function(self, parent: Module | Class, name: str, overloads: list[Function]) -> Function:
        first: Function = overloads[0]
        # what the module takes at runtime: pybind11 chooses the overload from the arguments
        parameters: Parameters = Parameters(
            Parameter("args", kind=ParameterKind.var_positional),
            Parameter("kwargs", kind=ParameterKind.var_keyword),
        )
        if "staticmethod" not in first.labels and isinstance(parent, Class):
            parameters = Parameters(Parameter("self", kind=ParameterKind.positional_or_keyword), *parameters)
        function: Function = Function(
            name,
            lineno=first.lineno,
            endlineno=overloads[-1].endlineno,
            parent=parent,
            parameters=parameters,
            returns=first.returns,
            decorators=[decorator for decorator in first.decorators if "overload" not in decorator.callable_path],
        )
        function.labels |= first.labels - {"overload"}
        function.overloads = overloads
        if first.docstring is not None:
            # the stubs are parsed as sphinx (docstring_style in mkdocs.yml). The parameters are in the signatures of the overloads, not in
            # the one of the function: _docstring checks them there
            options: SphinxOptions = cast(SphinxOptions, first.docstring.parser_options).copy()
            options["warn_unknown_params"] = False
            function.docstring = Docstring(
                self._docstring(overloads),
                lineno=first.docstring.lineno,
                endlineno=overloads[-1].docstring.endlineno if overloads[-1].docstring else first.docstring.endlineno,
                parent=function,
                parser=first.docstring.parser,
                parser_options=options,
            )
        return function

    def _docstring(self, overloads: list[Function]) -> str:
        descriptions: list[tuple[Function, str]] = []
        fields: dict[str, str] = {}
        for overload in overloads:
            description, overload_fields = self._split(overload.docstring.value if overload.docstring else "")
            descriptions.append((overload, description))
            names: set[str] = {parameter.name for parameter in overload.parameters}
            for key, field in overload_fields:
                if key.startswith("param ") and key[len("param "):] not in names:
                    # as the parser does for a function, which is told to not do it for these
                    logger.warning(f"{overload.filepath}:{overload.lineno}: Parameter '{key[len('param '):]}' does not appear in the signature of the overload")
                fields.setdefault(key, field)
        if len({description for _, description in descriptions}) == 1:
            text: str = descriptions[0][1]
        else:
            text = "\n".join(self._item(overload, description) for overload, description in descriptions)
        return "\n\n".join(part for part in (text, "\n".join(fields.values())) if part)

    @staticmethod
    def _split(docstring: str) -> tuple[str, list[tuple[str, str]]]:
        """The description of a docstring, and its fields by key: ("param start_height", ":param int start_height: ...")."""
        description: list[str] = []
        fields: list[tuple[str, list[str]]] = []
        for line in docstring.splitlines():
            match = _FIELD.match(line)
            if match:
                kind, rest = match.group(1), match.group(2).split()
                # a parameter is told from the others by its name, the last word before the colon; a :returns: is one
                key: str = f"{kind} {rest[-1]}" if kind == "param" and rest else kind
                fields.append((key, [line]))
            elif fields:
                fields[-1][1].append(line)
            else:
                description.append(line)
        return "\n".join(description).strip(), [(key, "\n".join(lines).rstrip()) for key, lines in fields]

    @staticmethod
    def _item(overload: Function, description: str) -> str:
        parameters: str = ", ".join(parameter.name for parameter in overload.parameters if parameter.name not in ("self", "cls"))
        lines: list[str] = description.splitlines() or [""]
        return "\n".join([f"- `{overload.name}({parameters})`: {lines[0]}"] + [f"    {line}" if line else "" for line in lines[1:]])
