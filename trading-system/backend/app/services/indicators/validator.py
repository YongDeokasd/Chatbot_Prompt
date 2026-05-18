"""AST-based static analysis of user indicator code (§9.2)."""
import ast

ALLOWED_IMPORTS = {"numpy", "pandas", "pandas_ta", "math"}
BANNED_CALLS = {
    "__import__", "exec", "eval", "open", "subprocess", "compile",
    "globals", "locals", "getattr", "setattr",
}
MAX_CODE_BYTES = 10 * 1024


def _call_name(node: ast.Call) -> str | None:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def validate_code(code: str) -> None:
    if len(code.encode("utf-8")) > MAX_CODE_BYTES:
        raise ValueError("Code exceeds 10KB limit")

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise ValueError(f"Syntax error: {e}")

    has_compute = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in ALLOWED_IMPORTS:
                    raise ValueError(f"Import not allowed: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root not in ALLOWED_IMPORTS:
                raise ValueError(f"Import not allowed: {node.module}")
        elif isinstance(node, ast.Call):
            name = _call_name(node)
            if name in BANNED_CALLS:
                raise ValueError(f"Banned call: {name}")
        elif isinstance(node, ast.FunctionDef) and node.name == "compute":
            args = [a.arg for a in node.args.args]
            if args != ["candles", "params"]:
                raise ValueError(
                    "compute() must have exactly (candles, params) args"
                )
            has_compute = True

    if not has_compute:
        raise ValueError("Missing def compute(candles, params)")
