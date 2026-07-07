"""
Week 1: Extraction script for repo-to-knowledge
Walks the target repo's `app/` folder and pulls out structural facts
(classes, functions, imports, route decorators) into a single JSON file.
No LLM calls here — just static analysis using Python's built-in `ast` module.
"""

import ast
import json
from pathlib import Path

# Adjust this if your folder names differ
REPO_ROOT = Path("../fastapi-mongodb-realworld-example-app/app")
OUTPUT_FILE = Path("output/extracted.json")


def get_decorator_name(decorator: ast.expr) -> str:
    """Turn a decorator AST node into a readable string, e.g. 'router.get'."""
    if isinstance(decorator, ast.Call):
        decorator = decorator.func
    if isinstance(decorator, ast.Attribute):
        value = decorator.value
        base = value.id if isinstance(value, ast.Name) else "?"
        return f"{base}.{decorator.attr}"
    if isinstance(decorator, ast.Name):
        return decorator.id
    return "unknown_decorator"


def get_decorator_args(decorator: ast.expr):
    """Pull string args out of a decorator call, e.g. the '/articles' in @router.get('/articles')."""
    args = []
    if isinstance(decorator, ast.Call):
        for arg in decorator.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                args.append(arg.value)
    return args


def extract_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict:
    return {
        "name": node.name,
        "is_async": isinstance(node, ast.AsyncFunctionDef),
        "args": [a.arg for a in node.args.args],
        "docstring": ast.get_docstring(node),
        "decorators": [get_decorator_name(d) for d in node.decorator_list],
        "route_paths": [
            p for d in node.decorator_list for p in get_decorator_args(d)
        ],
    }


def extract_class(node: ast.ClassDef) -> dict:
    return {
        "name": node.name,
        "bases": [ast.unparse(b) for b in node.bases],
        "docstring": ast.get_docstring(node),
        "methods": [
            extract_function(n)
            for n in node.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ],
    }


def extract_imports(tree: ast.Module) -> list[str]:
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def extract_file(filepath: Path) -> dict:
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))

    return {
        "path": str(filepath.relative_to(REPO_ROOT)),
        "module_docstring": ast.get_docstring(tree),
        "imports": extract_imports(tree),
        "classes": [
            extract_class(n) for n in tree.body if isinstance(n, ast.ClassDef)
        ],
        "functions": [
            extract_function(n)
            for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ],
    }


def main():
    if not REPO_ROOT.exists():
        raise FileNotFoundError(f"Can't find {REPO_ROOT.resolve()} — check the folder name/path.")

    results = []
    for py_file in REPO_ROOT.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        try:
            results.append(extract_file(py_file))
        except SyntaxError as e:
            print(f"Skipping {py_file} due to parse error: {e}")

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(results, indent=2))
    print(f"Extracted {len(results)} files -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()