"""The links of the docstrings of the stubs, for mkdocstrings.

A docstring of the stubs links a page as reStructuredText does, with a reference and its target in the same docstring:

    Implements a `MoneroDaemon` using `monerod-rpc`_.

    .. _monerod-rpc: https://docs.getmonero.org/rpc-library/monerod-rpc/

Editors show a docstring as it is written, and mkdocstrings reads it as Markdown, where both are text. This extension makes each
reference a Markdown link to its target, which opens in a new tab, and drops the targets. It does it when griffe makes the object, before
any other extension reads its docstring: the overloads of griffe_overloads.py have their links when their docstrings are joined.
"""

from __future__ import annotations

import ast
import re
from typing import Any

from griffe import Extension, Inspector, Object, ObjectNode, Visitor, logger
from typing_extensions import override

# a target, on a line of its own: ".. _monerod-rpc: https://docs.getmonero.org/rpc-library/monerod-rpc/"
_TARGET = re.compile(r"^[ \t]*\.\. _(?P<name>[^:\n]+):[ \t]+(?P<url>\S+)[ \t]*(?:\n|$)", re.MULTILINE)
# a reference to a target: "`monerod-rpc`_", not the anonymous "`text`__"
_REFERENCE = re.compile(r"`(?P<name>[^`\n]+)`_(?!_)")


class RstLinks(Extension):
    """Makes the links of reStructuredText in the docstrings links of Markdown."""

    @override
    def on_instance(self, *, node: ast.AST | ObjectNode, obj: Object, agent: Visitor | Inspector, **kwargs: Any) -> None:
        if obj.docstring is None or ".. _" not in obj.docstring.value:
            return
        text: str = obj.docstring.value
        targets: dict[str, str] = {self._key(match["name"]): match["url"] for match in _TARGET.finditer(text)}
        referenced: set[str] = set()

        def link(match: re.Match[str]) -> str:
            key: str = self._key(match["name"])
            if key not in targets:
                logger.warning("%s: the reference `%s`_ has no target in its docstring", obj.path, match["name"])
                return match[0]
            referenced.add(key)
            return f'[{match["name"]}]({targets[key]}){{ target="_blank" rel="noopener" }}'

        obj.docstring.value = _REFERENCE.sub(link, _TARGET.sub("", text)).rstrip()
        for key in targets.keys() - referenced:
            logger.warning("%s: the target `%s` is not referenced in its docstring", obj.path, key)

    @staticmethod
    def _key(name: str) -> str:
        """The name of a target as reStructuredText matches it: without case, and with its spaces as one."""
        return " ".join(name.split()).lower()
