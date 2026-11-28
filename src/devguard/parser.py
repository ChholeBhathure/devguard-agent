import ast
from pathlib import Path
from typing import Any


class CodeStructureVisitor(ast.NodeVisitor):
    """Extract structural metadata from a Python AST."""

    def __init__(self):
        self.functions: list[dict[str, Any]] = []
        self.classes: list[dict[str, Any]] = []
        self.imports: list[dict[str, Any]] = []

        self.class_stack: list[str] = []
        self.function_stack: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        self.imports.append({
            "name": ast.unparse(node),
            "lineno": node.lineno
        })

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.imports.append({
            "name": ast.unparse(node),
            "lineno": node.lineno
        })

    def _record_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:

        if self.function_stack:
            scope = "nested"
        elif self.class_stack:
            scope = "method"
        else:
            scope = "function"

        qualified_name = ".".join(
            self.class_stack + self.function_stack + [node.name]
        )

        func_info = {
            "name": node.name,
            "lineno": node.lineno,
            "args": [arg.arg for arg in node.args.args],
            "docstring": ast.get_docstring(node),
            "scope": scope,
            "qualified_name": qualified_name,
        }

        self.functions.append(func_info)
        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_function(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_info = {
            "name": node.name,
            "lineno": node.lineno,
            "docstring": ast.get_docstring(node),
            "methods": [
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            ],
        }

        self.classes.append(class_info)
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()


def parse_python_source(
    source_code: str,
    file_name: str = "<unknown>",
) -> dict[str, Any]:
    """Extract AST metadata directly from Python source code."""

    tree = ast.parse(source_code, filename=file_name)

    visitor = CodeStructureVisitor()
    visitor.visit(tree)

    return {
        "file_name": Path(file_name).name,
        "imports": visitor.imports,
        "classes": visitor.classes,
        "functions": visitor.functions,
    }


def parse_python_file(file_path: str | Path) -> dict[str, Any]:
    """Read a Python file and extract its structural metadata."""

    path = Path(file_path)

    if not path.exists() or not path.is_file() or path.suffix.lower() != ".py":
        raise ValueError(f"Invalid Python file path: {file_path}")

    source_code = path.read_text(encoding="utf-8")

    return parse_python_source(source_code, file_name=path.name)