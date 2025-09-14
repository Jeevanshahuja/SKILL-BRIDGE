import google.generativeai as genai
import os
import json

# Configure Gemini API (make sure to set your API key in environment variable GEMINI_API_KEY)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_project_roadmap(project_name: str):
    """Generate a structured JSON roadmap for a project using Gemini API"""
    prompt = f"""
    Create a step-by-step roadmap for building the project: "{project_name}".
    
    Return the output strictly in JSON format with this structure and never use a "/" as will be using to redirect keep in mind  :
    {{
      "project": "{project_name}",
      "phases": [
        {{
          "phase": "Phase name",
          "description": "Short description of the phase",
          "skills": ["Skill1", "Skill2"],
          "tools": ["Tool1", "Tool2"],
          "tasks": ["Task1", "Task2"]
        }}
      ]
    }}
    """

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(prompt)

    if not response or not response.text:
        return {"project": project_name, "phases": []}

    try:
        # Try to find JSON inside response
        text = response.text.strip()
        # Sometimes Gemini may wrap in ```json ... ```
        if text.startswith("```"):
            text = text.split("```json")[-1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        print("Error parsing roadmap:", e)
        return {"project": project_name, "phases": []}
