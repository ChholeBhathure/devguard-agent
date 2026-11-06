import ast
from pathlib import Path
from typing import Any

class CodeStructureVisitor(ast.NodeVisitor):
    #Extracts structural metadata from a Python AST.
    def __init__(self):
        self.functions: list[dict[str, Any]] = []
        self.classes: list[dict[str, Any]] = []
        self.imports: list[dict[str, Any]] = []

        self._class_stack: list[str] = []
        self._function_stack: list[str] = []

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
    def _record_function(self,node:ast.FunctionDef | ast.AsyncFunctionDef,) ->None:
        if self._function_stack:
            scope="nested"
        elif self._class_stack:
            scope="method"
        else:
            scope="function"
        qualified_parts = (
            self._class_stack + self._function_stack + [node.name]
        )
        #Record informationabout a regular or async function.
        func_info = {
            "name": node.name,
            "qualified_name": ".".join(qualified_parts),
            "scope": scope,
            "lineno": node.lineno,
            "args": [arg.arg for arg in node.args.args],
            "docstring": ast.get_docstring(node),
        }
        self.functions.append(func_info)
        self.generic_visit(node)
        self._function_stack.pop()
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_function(node)
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_function(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_info = {
            "name":node.name,
            "lineno": node.lineno,
            "docstring": ast.get_docstring(node),
            "methods": [
                item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            ],
        }
        self.classes.append(class_info)
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

def parse_python_file(file_path: str | Path) -> dict[str, Any]:
    #Reads a Python file and extracts its structural metadata via AST.
    path = Path(file_path)
    if not path.exists() or not path.is_file() or path.suffix.lower() != ".py":
        raise ValueError(f"Invalid Python file path: {file_path}")
    source_code = path.read_text(encoding="utf-8")
    tree = ast.parse(source_code, filename=str(path))

    visitor = CodeStructureVisitor()
    visitor.visit(tree)

    return {
        "file_name": path.name,
        "imports": visitor.imports,
        "classes": visitor.classes,
        "functions": visitor.functions,

    }
class UserService:
    def authenticate(self):
        def validate_password():
            pass
from pathlib import Path
from typing import Any

class CodeStructureVisitor(ast.NodeVisitor):
    #Extracts structural metadata from a Python AST.
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
            self.generic_visit(node)
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.imports.append({
            "name": ast.unparse(node),
            "lineno": node.lineno
        })
        self.generic_visit(node)
    def _record_function(
            self,
            node:ast.FunctionDef | ast.AsyncFunctionDef,
    ) ->None:

        if self.function_stack:
            scope="nested"
        elif self.class_stack:
            scope="method"
        else:
            scope="function"

        qualified_name = ".".join(self.class_stack + self.function_stack + [node.name])
        #Record informationabout a regular or async function.
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
            "name":node.name,
            "lineno": node.lineno,
            "docstring": ast.get_docstring(node),
            "methods": [
                item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            ],
        }
        self.classes.append(class_info)
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

def parse_python_file(file_path: str | Path) -> dict[str, Any]:
    #Reads a Python file and extracts its structural metadata via AST.
    path = Path(file_path)
    if not path.exists() or not path.is_file() or path.suffix.lower() != ".py":
        raise ValueError(f"Invalid Python file path: {file_path}")
    source_code = path.read_text(encoding="utf-8")
    tree = ast.parse(source_code, filename=str(path))

    visitor = CodeStructureVisitor()
    visitor.visit(tree)

    return {
        "file_name": path.name,
        "imports": visitor.imports,
        "classes": visitor.classes,
        "functions": visitor.functions,

    }







