CLLMi
=====

Overview
--------
CLLMi is a command-line automation harness that wraps the Gemini API to inspect files, edit content, and execute Python modules inside a tightly sandboxed workspace (`calculator/`). It ships with a minimal sample project, a curated toolset, and guardrails that keep every action inside the permitted directory.

Salient Features
----------------
- Gemini-backed agent loop that plans tool calls before replying, keeping conversations and actions synchronized.
- Hard sandbox boundaries: all read/write/execute operations are scoped to `calculator/`, protecting the surrounding filesystem.
- Transparent Python tooling with explicit schemas, making it easy to audit behavior or add new capabilities.
- Headless workflow focus: runs entirely from the terminal with optional verbose traces of each tool invocation.

Setup
-----
1. Ensure Python 3.13+ is available. Install [uv](https://docs.astral.sh/uv/) (recommended) or create a virtual environment for `pyproject.toml`.
2. Install dependencies with `uv sync` *(or activate the virtual environment and pip install the compiled requirements).* 
3. Generate or reuse a Gemini API key via [Google AI Studio](https://aistudio.google.com/) (see the [API key docs](https://ai.google.dev/gemini-api/docs/api-key)), then create `.env` with `GEMINI_API_KEY="your_api_key_here"`.
4. Verify the tools with `uv run tests.py`.

Usage
-----
Start the agent by providing a natural-language prompt. Add `--verbose` to stream tool call payloads and responses.

```bash
uv run main.py "List files in pkg"
uv run main.py "Open lorem.txt" --verbose
```

The entry point automatically injects ./calculator as the working directory for every function call, so pass paths relative to that directory or cahnge in main.py.

Tool Reference
--------------
- `get_files_info`: Lists files in a directory with size metadata and directory flags.
- `get_file_content`: Reads up to 10,000 characters from a file and truncates longer responses with a notice.
- `run_python_file`: Executes a Python script with optional arguments, returning stdout, stderr, and exit code.
- `write_file`: Writes text into a file, creating parent directories if needed while rejecting traversal and directory targets.


Troubleshooting
---------------
- **Authentication errors**: Confirm the `.env` file exists and `GEMINI_API_KEY` is valid.
- **Permission errors**: Ensure requested paths live under `calculator/`.
- **Timeouts**: `run_python_file` enforces a 30-second limit; refactor or avoid long-running scripts.

Project Status
--------------
CLLMi is experimental and may change rapidly. Expect sharp edges, review generated output carefully, and adapt the codebase before deploying in production settings. Provided as-is for educational and prototyping use.


