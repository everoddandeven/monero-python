#!/usr/bin/env python3
"""Lints the bindings of the installed module with pybind11-stubgen.

pybind11 writes the signature of every function it binds in the docstring of the function, and stubgen turns
those into stubs. What it can not make sense of is what is wrong with the bindings: a C++ type that leaked into
a docstring because it is not registered, a default value that is only a repr like <MoneroNetworkType.MAINNET: 0>
(py::arg_v gives it a text), a name that does not resolve.

This fails on an error or a warning of stubgen, and on a public function with parameters that have no name (arg0,
arg1, ...): a py::arg is missing in the binding, so the function can not be called with keywords and its docs say
nothing about the parameter. The special methods are left out, pybind11 names those of the containers it binds
itself, and so are the setters of the properties.

    pip install pybind11-stubgen
    bin/lint_bindings.py [module]      # monero, which has to be installed or on the path
"""
import ast
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def unnamed_parameters(tree):
    """The public functions of a stub that have parameters named by pybind11: ['Class.function(arg0)', ...]"""
    found = []

    def visit(node, owner):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                visit(child, child.name)
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if child.name.startswith('_'):
                    continue
                if any(isinstance(d, ast.Attribute) and d.attr == 'setter' for d in child.decorator_list):
                    continue
                args = child.args
                names = [a.arg for a in args.posonlyargs + args.args + args.kwonlyargs]
                unnamed = [n for n in names if re.fullmatch(r'arg\d+', n)]
                if unnamed:
                    found.append('%s.%s(%s)' % (owner, child.name, ', '.join(unnamed)))

    visit(tree, 'module')
    return sorted(set(found))


def main():
    module = sys.argv[1] if len(sys.argv) > 1 else 'monero'
    ok = True
    with tempfile.TemporaryDirectory() as out:
        run = subprocess.run([sys.executable, '-m', 'pybind11_stubgen', module, '-o', out, '--exit-code'],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if run.stdout.strip():
            print(run.stdout.strip())
        if run.returncode != 0:
            print('::error::pybind11-stubgen found errors in the bindings of %s' % module)
            ok = False
        elif '[WARNING]' in run.stdout:
            print('::error::pybind11-stubgen warns about the bindings of %s' % module)
            ok = False

        # no stubs are written when stubgen finds errors
        stubs = sorted(Path(out).rglob('*.pyi'))
        offenders = []
        for stub in stubs:
            offenders += unnamed_parameters(ast.parse(stub.read_text()))
        if offenders:
            print('Public functions with parameters that have no name, add a py::arg to their binding:')
            for o in offenders:
                print('  ' + o)
            print('::error::%d public functions of %s have unnamed parameters' % (len(offenders), module))
            ok = False
        elif stubs:
            print('%d stub files generated, no unnamed parameters' % len(stubs))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
