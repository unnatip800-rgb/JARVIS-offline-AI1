import ast
import math
import operator
import platform
from datetime import datetime
from pathlib import Path


# ============================================================
# SAFE CALCULATOR
# ============================================================

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_calculate_node(node):

    if isinstance(node, ast.Expression):

        return _safe_calculate_node(
            node.body
        )

    if isinstance(node, ast.Constant):

        if isinstance(
            node.value,
            (int, float),
        ):

            return node.value

        raise ValueError(
            "Invalid value."
        )

    if isinstance(node, ast.UnaryOp):

        operator_function = _ALLOWED_OPERATORS.get(
            type(node.op)
        )

        if not operator_function:

            raise ValueError(
                "Unsupported operator."
            )

        return operator_function(
            _safe_calculate_node(node.operand)
        )

    if isinstance(node, ast.BinOp):

        operator_function = _ALLOWED_OPERATORS.get(
            type(node.op)
        )

        if not operator_function:

            raise ValueError(
                "Unsupported operator."
            )

        left = _safe_calculate_node(
            node.left
        )

        right = _safe_calculate_node(
            node.right
        )

        # Prevent absurd exponent calculations.
        if (
            isinstance(node.op, ast.Pow)
            and abs(right) > 100
        ):

            raise ValueError(
                "Exponent is too large."
            )

        return operator_function(
            left,
            right,
        )

    raise ValueError(
        "Only arithmetic expressions are supported."
    )


def calculate(expression):

    expression = expression.strip()

    if not expression:

        return "Please provide a calculation."

    try:

        tree = ast.parse(
            expression,
            mode="eval",
        )

        result = _safe_calculate_node(
            tree
        )

        return str(result)

    except Exception:

        return (
            "I couldn't safely calculate that. "
            "Use a normal arithmetic expression such as "
            "25 * (10 + 5)."
        )


# ============================================================
# DATE AND TIME
# ============================================================

def get_datetime():

    now = datetime.now()

    return {
        "date": now.strftime(
            "%A, %d %B %Y"
        ),
        "time": now.strftime(
            "%I:%M:%S %p"
        ),
        "iso": now.isoformat(),
    }


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def get_system_info():

    return {
        "Operating System": platform.system(),
        "OS Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
    }


# ============================================================
# LOCAL FILE INFORMATION
# ============================================================

def get_file_info(file_path):

    path = Path(file_path).expanduser()

    if not path.exists():

        return {
            "error": "File or folder does not exist."
        }

    try:

        if path.is_file():

            size = path.stat().st_size

            return {
                "type": "File",
                "name": path.name,
                "size_bytes": size,
                "extension": path.suffix,
                "location": str(
                    path.resolve()
                ),
            }

        if path.is_dir():

            items = list(
                path.iterdir()
            )

            files = [
                item
                for item in items
                if item.is_file()
            ]

            folders = [
                item
                for item in items
                if item.is_dir()
            ]

            return {
                "type": "Folder",
                "name": path.name,
                "location": str(
                    path.resolve()
                ),
                "files": len(files),
                "folders": len(folders),
                "total_items": len(items),
            }

    except Exception as error:

        return {
            "error": str(error)
        }


# ============================================================
# TOOL DISPATCHER
# ============================================================

def run_local_tool(
    tool_name,
    argument="",
):

    if tool_name == "Calculator":

        return calculate(
            argument
        )

    if tool_name == "Date & Time":

        data = get_datetime()

        return (
            f"Date: {data['date']}\n"
            f"Time: {data['time']}"
        )

    if tool_name == "System Information":

        data = get_system_info()

        return "\n".join(
            f"**{key}:** {value}"
            for key, value in data.items()
        )

    if tool_name == "File Information":

        data = get_file_info(
            argument
        )

        if "error" in data:

            return (
                f"Error: {data['error']}"
            )

        return "\n".join(
            f"**{key}:** {value}"
            for key, value in data.items()
        )

    return (
        "Unknown tool."
    )