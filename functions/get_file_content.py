import os
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the content of a specific file within the working directory. Returns the file content as a string, truncated at 10,000 characters if necessary.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "working_directory": types.Schema(
                type=types.Type.STRING,
                description="The base working directory containing the file to read.",
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to read, relative to the working directory.",
            ),
        },
        required=["working_directory", "file_path"],
    ),
)
available_functions = types.Tool(
    function_declarations=[
        schema_get_file_content,
    ]
)


def get_file_content(working_directory, file_path: str):
    abs_working_dir = os.path.abspath(working_directory)
    target_dir = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_dir.startswith(abs_working_dir):
        return f'Error: Cannot read "{target_dir}" as it is outside the permitted working directory'
    if not os.path.isfile(target_dir):
        return f'Error: File not found or is not a regular file: "{target_dir}"'
    MAX_CHARS = 10000
    try:
        with open(target_dir, "r") as f:
            file_content_string = f.read(MAX_CHARS + 1)
        if len(file_content_string) >= MAX_CHARS:
            file_content_string = file_content_string[:MAX_CHARS]
            file_content_string += (
                f'[...File "{file_path}" truncated at 10000 characters]'
            )
        return file_content_string

    except Exception as err:
        return f"Error reading file  {err}"
