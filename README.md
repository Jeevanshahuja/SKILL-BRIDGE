# Resume Analyzer & Learning Recommendation App

A Flask-based web application that helps users analyze their resumes, identify missing skills, and get curated learning resources. The app combines AI-powered resume parsing with educational recommendations to help users enhance their career readiness.

---

## Features

- **Resume Parsing:** Upload PDF or DOCX resumes to extract structured information.
- **AI Skill Analysis:** Uses Gemini AI to identify skills present and missing in your resume.
- **Learning Recommendations:**
  - Curated Coursera courses for missing skills.
  - YouTube playlists to help learn new skills effectively.
- **Project Roadmaps:** Generate a detailed roadmap for any project idea.
- **Secure Session Management:** Uses environment variables to manage sensitive keys securely.

---

## Technology Stack

- Python 3.9+
- Flask Web Framework
- docx2txt (DOCX parsing)
- PyMuPDF (`fitz`) for PDF parsing
- BeautifulSoup4 and Requests for web scraping
- Gemini AI for structured resume analysis
- HTML/CSS for front-end templates

---

## How It Works

1. **Upload Resume:** Users provide a resume in PDF or DOCX format.  
2. **AI Parsing:** Gemini AI analyzes the resume to extract personal details, skills, education, experience, and identifies missing skills.  
3. **Learning Recommendations:** The app fetches top Coursera courses and YouTube playlists for missing skills.  
4. **Project Roadmaps:** Users can enter a project name to receive a structured roadmap for execution.  

---

## Environment & Security

- All sensitive keys (like Flask `SECRET_KEY` and YouTube API keys) are stored securely using environment variables.  
- The app does **not** expose any API keys or secrets in the codebase, making it safe for public repositories.  

---

