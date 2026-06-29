import os
import base64
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from ai_engine.rag_setup import get_retriever
import re
GROQ_MODEL = "qwen/qwen3.6-27b"
def apply_input_guardrails(variables: str) -> str | None:
    if len(variables) > 500:
        return "Error: Input too long. Please keep variable descriptions under 500 characters."
    sus_patterns= [r"ignore\s+previous", r"system\s+prompt", r"bypass", r"jailbreak"]
    for pattern in sus_patterns:
        if re.search(pattern, variables, re.IGNORECASE):
            return "Error: Security violation. Invalid prompt injection detected."
    return None

def solve_math(base64_image:str,variables:str) -> str:
    guardrail_error=apply_input_guardrails(variables)
    if guardrail_error:
        return guardrail_error
    api_key=os.environ.get('GROQ_API_KEY')
    if not api_key:
        return "Error:GROQ_API_KEY env is not set"
    chat=ChatGroq(model=GROQ_MODEL,api_key=api_key)
    try:
        retriever=get_retriever()
        docs=retriever.invoke(variables)
        context="\n".join([doc.page_content for doc in docs])
    except Exception as e:
        context="No relavant context found"
        print(f"rag warning {e}")
    system_inst=f"""
        You are an expert Math AI Assistant specializing in Calculus, Linear Algebra, and Statistics.
 SECURITY & CONTENT SAFETY RULES:
    1. ONLY answer math-related queries. If the image or text is NOT about math, reply EXACTLY with: "I can only assist with mathematics problems. Please upload a valid math equation."
    2. Refuse any requests to generate harmful, offensive, or non-educational content immediately.
    
    Look at the provided image containing a math equation.
    Use the following retrieved formulas/knowledge to help you solve it if relevant:
    
    <context>
    {context}
    </context>
    
    User provided variables/instructions: {variables}
    
    Provide a clear, step-by-step solution.
    """
    user_msg=HumanMessage(content=[{"type":"text","text":f"{system_inst}"},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{base64_image}"}}])
    try:
        response=chat.invoke([user_msg])
        return str(response.content)
    except Exception as e:
        return f"Error during LLM processing: {str(e)}"

if __name__ == "__main__":
    # Quick local test execution
    IMAGE_PATH = "test_math.png" 
    USER_VARIABLES = "Solve this equation step-by-step."
    
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Please place an image named '{IMAGE_PATH}' in the main folder to test.")
    else:
        print(f"Encoding image '{IMAGE_PATH}'...")
        with open(IMAGE_PATH, "rb") as image_file:
            encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
            
        print("Searching FAISS and calling Groq Vision Model...")
        result = solve_math(encoded_img, USER_VARIABLES)
        
        print("\n=========================================")
        print("AI ASSISTANT ANSWER:")
        print("=========================================")
        print(result)
