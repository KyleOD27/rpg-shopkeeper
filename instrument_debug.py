#!/usr/bin/env python3
import ast, astor, os
from argparse import ArgumentParser

class DebugInjector(ast.NodeTransformer):
    def __init__(self, entry_fmt="→ Entering {name}", exit_fmt="← Exiting {name}"):
        self.entry_fmt = entry_fmt
        self.exit_fmt = exit_fmt

    def _make_call(self, fmt, name):
        return ast.Expr(
            ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='self', ctx=ast.Load()),
                    attr='debug',
                    ctx=ast.Load()
                ),
                args=[ast.Constant(fmt.format(name=name))],
                keywords=[]
            )
        )

    def visit_FunctionDef(self, node):
        # only instrument instance methods (first arg is 'self')
        if not (node.args.args and node.args.args[0].arg == 'self'):
            return node

        entry = self._make_call(self.entry_fmt, node.name)
        exit_call = self._make_call(self.exit_fmt, node.name)

        # insert entry log
        node.body.insert(0, entry)

        new_body = []
        for stmt in node.body:
            if isinstance(stmt, ast.Return):
                new_body.append(exit_call)
                new_body.append(stmt)
            else:
                new_body.append(stmt)
        node.body = new_body

        # if no explicit return, add exit at end
        if not any(isinstance(st, ast.Return) for st in node.body):
            node.body.append(exit_call)

        return node

def instrument_file(path, injector):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    tree = ast.parse(src, filename=path)
    tree = injector.visit(tree)
    new_src = astor.to_source(tree)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_src)
    print(f"✔ Instrumented {path}")

def main():
    # default to this script's directory if no arg is given
    default_root = os.path.dirname(os.path.abspath(__file__))

    p = ArgumentParser(
        description="Auto-inject debug() calls into methods"
    )
    p.add_argument(
        "root",
        nargs='?',
        default=default_root,
        help=f"Project root dir (defaults to this script’s folder: {default_root})"
    )
    args = p.parse_args()
    root_dir = args.root

    injector = DebugInjector()
    for dirpath, _, files in os.walk(root_dir):
        # skip virtualenvs, caches, hidden dirs
        if any(part.startswith('.') or part in ('venv','__pycache__') for part in dirpath.split(os.sep)):
            continue
        for fn in files:
            if fn.endswith(".py") and fn != os.path.basename(__file__):
                instrument_file(os.path.join(dirpath, fn), injector)

if __name__ == "__main__":
    main()
