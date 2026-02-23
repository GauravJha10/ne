import os
import sys
import traceback
import re
from io import StringIO
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Code Interpreter API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GEMINI API Key from user
os.environ["GEMINI_API_KEY"] = "AIzaSyBnGIYx_ye3EKTZ630Vl279f2L0gydYczE"

class CodeRequest(BaseModel):
    code: str

class ErrorAnalysis(BaseModel):
    error_lines: List[int]

class InterpreterResponse(BaseModel):
    error: List[int]
    result: str

def execute_python_code(code: str) -> dict:
    """
    Execute Python code and return exact output.
    """
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        # Use a single dictionary for both globals and locals.
        # This allows functions defined in the code to access global variables correctly.
        exec_globals = {"__builtins__": __builtins__}
        exec(code, exec_globals)
        output = sys.stdout.getvalue()
        return {"success": True, "output": output}

    except BaseException:
        # Get full traceback
        output = traceback.format_exc()
        print(f"--- Execution Failed ---\nCODE:\n{code}\nTRACEBACK:\n{output}\n------------------------")
        return {"success": False, "output": output}

    finally:
        sys.stdout = old_stdout

def analyze_error_with_ai(code: str, error_traceback: str) -> List[int]:
    """
    Use LLM with structured output to identify error line numbers.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    prompt = f"""
Analyze this Python code and its error traceback.
Identify the line number(s) where the error occurred.

CODE:
{code}

TRACEBACK:
{error_traceback}

Return the line number(s) where the error is located.
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ErrorAnalysis
            )
        )
        if response.parsed:
            return response.parsed.error_lines
    except Exception as e:
        print(f"AI Analysis Call Failed (Quota or Connection): {e}")

    # Heuristic fallback: Parse line number from traceback
    try:
        # Typical traceback line: '  File "<string>", line 3, in <module>'
        # We look for all occurrences and take the ones relevant to "<string>"
        lines = re.findall(r'File "<string>", line (\d+)', error_traceback)
        if lines:
            # We return only the last one as the primary error location
            return [int(lines[-1])]
    except Exception as he:
        print(f"Heuristic Fallback Error: {he}")
    
    return []

@app.get("/")
async def root():
    return {"status": "ok", "message": "Code Interpreter API is running (V2 fixed)"}

@app.post("/code-interpreter", response_model=InterpreterResponse)
async def code_interpreter(request: CodeRequest):
    # 1. Execute the code
    execution_result = execute_python_code(request.code)
    
    # 2. Determine error lines
    error_lines = []
    if not execution_result["success"]:
        # 3. AI Agent analyzes error (with fallback)
        error_lines = analyze_error_with_ai(request.code, execution_result["output"])
    
    # 4. Return results
    return {
        "error": error_lines,
        "result": execution_result["output"]
    }

if __name__ == "__main__":
    import uvicorn
    # Use port 8006 as before
    uvicorn.run(app, host="0.0.0.0", port=8006)
