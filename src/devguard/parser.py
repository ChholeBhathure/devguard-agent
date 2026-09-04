import ast
from pathlib import Path
from typing import Any, Dict, List

class CodeStructureVisitor(ast.NodeVisitor):
    #Traverses Python AST nodes to extraxt structural code metadata.
    def __init__(self):
        self.functions: List[Dict[str, Any]] = []
        self.classes: List[Dict[str, Any]] = []
        self.imports: List[str] = []
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")
        self.generic_visit(node)
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        func_info = {
            "name": node.name,
            "lineno": node.lineno,
            "args": [arg.arg for arg in node.args.args],
            "docstring": ast.get_docstring(node),
        }
        self.functions.append(func_info)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_info = {
            "name":node.name,
            "lineno": node.lineno,
            "docstring": ast.get_docstring(node),
            "methods": [
                item.name for item in node.body if isinstance(item, ast.FunctionDef)
            ],
        }
        self.classes.append(class_info)
        self.generic_visit(node)

def parse_python_file(file_path: str) -> Dict[str, Any]:
    #Reads a Python file and extracts its structural overview via AST.
    path = Path(file_path)
    if not path.exists() or not path.suffix == ".py":
        raise ValueError(f"Invalid Python file path: {file_path}")
    source_code = path.read_text(encoding="utf-8")
    tree = ast.parse(source_code, filename=path.name)

    visitor = CodeStructureVisitor()
    visitor.visit(tree)

    return {
        "file_name": path.name,
        "imports": visitor.imports,
        "classes": visitor.classes,
        "functions": visitor.functions,
    }