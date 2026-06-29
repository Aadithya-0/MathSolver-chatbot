"""
AI Math Equation Evaluator — Gradio Frontend
=============================================
UI & Integration Specialist's component.

What this does:
1. Lets a user upload an image of a math problem (handwritten or typed).
2. Lets the user optionally type in variable values (e.g. "x = 5, y = 3").
3. Sends both to the FastAPI backend, which runs OCR + the LangChain/FAISS
   retrieval chain and returns a solved answer.
4. Displays the answer (and step-by-step work, if the backend provides it).

Backend contract (coordinate with the API/Backend Developer):
    POST {BACKEND_URL}/solve
    Content-Type: multipart/form-data
    fields:
        - image: file              (the uploaded image)
        - variables: str           (free-text variable values, may be empty)
    Response JSON:
        {
          "answer": str,           # required
          "steps": str,            # optional, markdown-formatted working
          "error": str             # optional, set if something went wrong
        }

Configuration:
    Set BACKEND_URL in a .env file or as an environment variable.
    Defaults to http://localhost:8000 for local testing against FastAPI.
"""

import os
import requests
import gradio as gr

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional; env vars can also be set directly

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
SOLVE_ENDPOINT = f"{BACKEND_URL}/solve"
TIMEOUT_SECONDS = 60


def solve_equation(image_path: str, variables_text: str) -> str:
    """Send the uploaded image + variables to the FastAPI backend and
    return a markdown string with the result (or a friendly error)."""

    if image_path is None:
        return "⚠️ Please upload an image of the math problem first."

    try:
        with open(image_path, "rb") as img_file:
            files = {
                "image": (os.path.basename(image_path), img_file, "image/png")
            }
            data = {"variables": variables_text or ""}
            response = requests.post(
                SOLVE_ENDPOINT,
                files=files,
                data=data,
                timeout=TIMEOUT_SECONDS,
            )
        response.raise_for_status()
        result = response.json()

        if result.get("error"):
            return f"❌ **Error from backend:** {result['error']}"

        answer = result.get("answer", "No answer was returned.")
        steps = result.get("steps")

        if steps:
            return f"### ✅ Answer\n{answer}\n\n### 🧮 Steps\n{steps}"
        return f"### ✅ Answer\n{answer}"

    except requests.exceptions.ConnectionError:
        return (
            f"❌ Couldn't connect to the backend at `{BACKEND_URL}`.\n\n"
            "Is the FastAPI server running? If you're testing locally, "
            "start it with `uvicorn main:app --reload` from the backend folder."
        )
    except requests.exceptions.Timeout:
        return "❌ The request timed out. The backend took too long to respond."
    except requests.exceptions.HTTPError as e:
        return f"❌ Backend returned an HTTP error: {e}"
    except ValueError:
        return "❌ Backend response wasn't valid JSON. Check the server logs."
    except Exception as e:  # noqa: BLE001 - surface unexpected errors to the user
        return f"❌ Unexpected error: {e}"


with gr.Blocks(title="AI Math Equation Evaluator") as demo:
    gr.Markdown(
        """
        # 🧮 AI Math Equation Evaluator

        Upload a photo of a math problem and (optionally) provide variable
        values. This bot currently supports:

        - **Calculus** — derivatives, integrals, limits
        - **Statistics** — probability, distributions, hypothesis testing
        - **Linear Algebra** — matrices, vectors, eigenvalues, systems of equations
        """
    )

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(
                type="filepath",
                label="📷 Upload Equation Image",
            )
            variables_input = gr.Textbox(
                label="🔢 Variables (optional)",
                placeholder="e.g. x = 5, y = 3, a = 2",
                lines=2,
            )
            submit_btn = gr.Button("Solve", variant="primary")
            clear_btn = gr.ClearButton([image_input, variables_input])

        with gr.Column():
            output_box = gr.Markdown(label="📝 Solution", value="Your solution will appear here.")

    submit_btn.click(
        fn=solve_equation,
        inputs=[image_input, variables_input],
        outputs=output_box,
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
