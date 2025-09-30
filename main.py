from calculator.pkg.calculator import Calculator

from functions.get_files_info import get_files_info, schema_get_files_info

from functions.get_file_content import get_file_content, schema_get_file_content

from functions.run_python_file import run_python_file, schema_run_python_file

from functions.write_file_content import write_file, schema_write_file_content

from google import genai
import sys
import os
from dotenv import load_dotenv
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

FUNCTION_MAP = {
    "get_file_content": get_file_content,
    "get_files_info": get_files_info,
    "run_python_file": run_python_file,
    "write_file": write_file,
}

available_functions = types.Tool(
    function_declarations=[
        schema_get_file_content,
        schema_get_files_info,
        schema_run_python_file, # matches key above
        schema_write_file_content, # matches key above
    ]
)

def call_function(function_call_part, verbose=False) -> types.Content:
    func_name = function_call_part.name
    kwargs = dict(function_call_part.args or {})
    kwargs["working_directory"] = "./calculator"

    if verbose:
        print(f"Calling function: '{func_name}'({function_call_part.args})")
    else:
        print(f" - Calling function: {func_name}")

    fn = FUNCTION_MAP.get(func_name)
    if fn is None:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=func_name,
                    response={"error": f"Unknown function: {func_name}"},
                )
            ],
        )

    function_result = fn(**kwargs)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=func_name,
                response={"result": function_result},
            )
        ],
    )

client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

List files and directories
Read file contents
Execute Python files with optional arguments
Write or overwrite files
All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
Plan with tools first before answering directl
Assume if no directory is provided then it is in Current Directory itself.
"""

def main():
    print("Hello from cllmi!")
    if len(sys.argv) < 2:
        print("no input provided")
        sys.exit(1)

    user_prompt = sys.argv[1]
    verbose = len(sys.argv) >= 3 and sys.argv[2] == "--verbose"

    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

    try:
        for _ in range(20):
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=[available_functions],
                ),
            )

            
            for _ in response.candidates:
                messages.append(_.content)

            
            if response.function_calls:
                for fc in response.function_calls:
                    tool_content = call_function(fc, verbose=verbose)

                    
                    if not tool_content.parts:
                        raise RuntimeError("Function call returned no parts")
                    part = tool_content.parts[0]
                    fr = getattr(part, "function_response", None)
                    if not fr or not getattr(fr, "response", None):
                        raise RuntimeError(
                            "Missing function_response.response in tool content"
                        )

                    if verbose:
                        print(f"-> {fr.response}")

                    messages.append(tool_content)
                continue  #nxt

            
            if getattr(response, "text", None):
                print("Final response:")
                print(response.text)
                break

        if verbose and getattr(response, "usage_metadata", None):
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    except Exception as e:
        print(f"ERROR: {e}")
    sys.exit(0)    

if __name__ == "__main__":
    main()