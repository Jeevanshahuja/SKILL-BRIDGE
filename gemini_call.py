import google.generativeai as genai
import re 
import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ No Gemini API Key found. Please set GEMINI_API_KEY in your environment.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")

def getjson(text):
    json_response = model.generate_content("""
                                           Extract the following details from the resume:
1. The job role the resume is written for, only one role which matches the best
2. All skills the candidate has give broad categories like python java machine learning broad terms dont include ides, try to complete in max 10 skills
3. All missing skills required for the role but not present in resume
4. never use a "/" as will be using to redirect keep in mind 
Return output strictly in this JSON format:
{
  "role": "<job role>",
  "skills": ["skill1", "skill2", "..."],
  "missing": ["missing_skill1", "missing_skill2", "..."],
  "tips" : [... tips to increase ats score line , tip1 , tip2 ],
  "projects" : [5 projects based on currect skills which he should do just project name with tech stack in bracket , project1 , project2]
}
just return the json nothing else resume is ---"""+ text)
    raw_text = json_response.text
    match = re.search(r"```json(.*?)```", raw_text, re.DOTALL)
    raw_json = match.group(1).strip() if match else raw_text.strip()
    return raw_json