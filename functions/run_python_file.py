import os
import subprocess
from google.genai import types


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file in the specified working directory with optional command-line arguments. The file path must be relative to and within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The base working directory from which to execute the Python file.",
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to execute, relative to the working directory. Must end with .py extension.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional command-line arguments to pass to the Python script.",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["working_directory", "file_path"],
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_run_python_file,
    ]
)


def run_python_file(working_directory, file_path, args=[]):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

    if not (
        abs_file_path.startswith(abs_working_dir + os.sep)
        or abs_file_path == abs_working_dir
    ):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.exists(abs_file_path):
        return f'Error: File "{file_path}" not found.'

    if not abs_file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'

    try:
        completed_process = subprocess.run(
            ["python", abs_file_path] + args,
            cwd=working_directory,
            timeout=30,
            capture_output=True,
            text=True,
        )

        stdout_output = (
            completed_process.stdout.strip() if completed_process.stdout else ""
        )
        stderr_output = (
            completed_process.stderr.strip() if completed_process.stderr else ""
        )

        result_parts = []

        if stdout_output:
            result_parts.append(f"STDOUT: {stdout_output}")

        if stderr_output:
            result_parts.append(f"STDErR: {stderr_output}")

        if completed_process.returncode != 0:
            result_parts.append(
                f"Process exited with code: {completed_process.returncode}"
            )

        if not result_parts:
            return "No output produced."

        return "\n".join(result_parts)

    except subprocess.TimeoutExpired as e:
        return f"Error: executing Python file: {e}"
    except Exception as e:
        return f"Error: executing Python file: {e}"
