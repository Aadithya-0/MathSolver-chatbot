"""
Math Solver Engine using LangChain
Handles image processing and math problem solving
"""

import os
import json
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
import base64
from pathlib import Path


class MathSolverEngine:
    """Main engine for solving math problems from images using LangChain"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Math Solver Engine
        
        Args:
            api_key: OpenAI API key (uses env variable if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.llm = ChatOpenAI(
            model="gpt-4-vision-preview",
            api_key=self.api_key,
            temperature=0.7,
            max_tokens=2048
        )
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image file to base64 string
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string of the image
        """
        with open(image_path, "rb") as image_file:
            return base64.standard_b64encode(image_file.read()).decode("utf-8")
    
    def solve_math_problem(
        self,
        image_path: str,
        variables: str = "",
        solve_step_by_step: bool = True
    ) -> Dict[str, Any]:
        """
        Solve a math problem from an image
        
        Args:
            image_path: Path to the uploaded image containing the math problem
            variables: JSON string of variables to consider in solving
            solve_step_by_step: Whether to provide step-by-step solution
            
        Returns:
            Dictionary containing:
                - solution: The mathematical solution
                - steps: Step-by-step breakdown (if requested)
                - explanation: Explanation of the approach
                - variables_used: Variables that were applied
                - confidence: Confidence level of the solution
        """
        try:
            # Validate image exists
            if not Path(image_path).exists():
                return {
                    "error": f"Image not found at {image_path}",
                    "solution": None,
                    "confidence": 0
                }
            
            # Parse variables if provided
            variables_dict = {}
            if variables:
                try:
                    variables_dict = json.loads(variables)
                except json.JSONDecodeError:
                    return {
                        "error": f"Invalid variables JSON: {variables}",
                        "solution": None,
                        "confidence": 0
                    }
            
            # Encode image
            image_base64 = self.encode_image_to_base64(image_path)
            
            # Build prompt based on variables and options
            prompt = self._build_prompt(solve_step_by_step, variables_dict)
            
            # Call LangChain with vision capabilities
            # Note: This is a placeholder for the actual LangChain integration
            # Replace with actual implementation using Abishek's functions
            response = self._call_langchain_solver(
                image_base64, 
                prompt, 
                variables_dict
            )
            
            return response
            
        except Exception as e:
            return {
                "error": str(e),
                "solution": None,
                "confidence": 0
            }
    
    def _build_prompt(self, step_by_step: bool, variables: Dict) -> str:
        """Build the prompt for the LLM"""
        base_prompt = """You are an expert mathematics tutor. Analyze the mathematical problem in the image and provide:
1. Identification of the problem type
2. The solution
3. Mathematical reasoning"""
        
        if step_by_step:
            base_prompt += "\n4. Detailed step-by-step solution process"
        
        if variables:
            base_prompt += f"\n\nConsider these variables: {json.dumps(variables)}"
        
        base_prompt += "\n\nProvide your response in JSON format with keys: problem_type, solution, reasoning, and steps (if applicable)."
        
        return base_prompt
    
    def _call_langchain_solver(
        self, 
        image_base64: str, 
        prompt: str, 
        variables: Dict
    ) -> Dict[str, Any]:
        """
        Call LangChain for solving (placeholder for Abishek's implementation)
        
        Args:
            image_base64: Base64 encoded image
            prompt: The prompt to send to the LLM
            variables: Variables dictionary
            
        Returns:
            Structured response from the solver
        """
        # TODO: Integrate with Abishek's LangChain functions
        # This is a placeholder implementation
        return {
            "solution": "Awaiting LangChain integration",
            "steps": ["Step 1", "Step 2", "Step 3"],
            "explanation": "Integration with Abishek's LangChain solver pending",
            "variables_used": variables,
            "confidence": 0.5,
            "problem_type": "unknown"
        }


def get_solver() -> MathSolverEngine:
    """Factory function to get MathSolverEngine instance"""
    return MathSolverEngine()
