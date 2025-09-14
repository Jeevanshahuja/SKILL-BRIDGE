import os
import json
import requests
import docx2txt
import fitz
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for, session
from gemini_call import getjson
from project import generate_project_roadmap

# ------------------ Flask App ------------------ #
app = Flask(__name__)

# Secret key for sessions
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set in environment.")
app.secret_key = SECRET_KEY

# Secure cookie settings
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# YouTube API Key
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY not set in environment.")

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# ------------------ Resume Parsing ------------------ #
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def extract_text_from_docx(docx_file):
    return docx2txt.process(docx_file)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------ Course Fetching ------------------ #
def get_courses(query):
    url = f"https://www.coursera.org/search?query={query.replace(' ', '+')}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        cards = soup.select('ul.cds-10 li.cds-grid-item')[:5]

        courses = []
        for card in cards:
            title_tag = card.select_one('a.cds-CommonCard-titleLink h3')
            link = card.select_one('a.cds-CommonCard-titleLink')
            institution = card.select_one('div.cds-ProductCard-partners')
            meta = card.select_one('div.cds-CommonCard-metadata p')
            rating = card.select_one('div.cds-RatingStat-meter')
            reviews = card.select_one('div.cds-RatingStat-sizeLabel + div.css-vac8rf')

            courses.append({
                'name': title_tag.get_text(strip=True) if title_tag else 'N/A',
                'link': f"https://www.coursera.org{link['href']}" if link else 'N/A',
                'institution': institution['title'] if institution and institution.has_attr('title') else 'N/A',
                'rating': rating['aria-valuenow'] if rating and rating.has_attr('aria-valuenow') else 'N/A',
                'reviews': reviews.get_text(strip=True) if reviews else 'N/A',
                'difficulty': meta.get_text(strip=True).split(' · ')[0] if meta else 'N/A',
                'type': meta.get_text(strip=True).split(' · ')[1] if meta and ' · ' in meta.get_text() else 'N/A',
                'duration': meta.get_text(strip=True).split(' · ')[2] if meta and len(meta.get_text().split(' · ')) > 2 else 'N/A'
            })

        return courses
    except Exception as e:
        print(f"Error while scraping: {e}")
        return []

# ------------------ YouTube Fetching ------------------ #
def getyt(skill):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": skill,
        "type": "playlist",
        "maxResults": 5,
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = []
    for item in data.get("items", []):
        playlist_id = item["id"]["playlistId"]
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        access_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
        results.append({
            "title": title,
            "channel": channel,
            "playlist_url": access_url,
            "thumbnail": thumbnail
        })
    return results

# ------------------ Routes ------------------ #
@app.route("/", methods=["GET", "POST"])
def upload_resume():
    if request.method == "POST":
        if 'resume' not in request.files:
            return "No file part"
        file = request.files['resume']
        if file.filename == '':
            return "No selected file"
        if allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()

            if ext == "pdf":
                text = extract_text_from_pdf(file)
            elif ext == "docx":
                text = extract_text_from_docx(file)
            else:
                return "Unsupported file type."

            raw_data = getjson(text)
            try:
                data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            except json.JSONDecodeError:
                data = {}

            session['user_data'] = data
            return redirect(url_for("results"))
        else:
            return "Invalid file type. Please upload PDF or DOCX."
    return render_template("index.html")

@app.route("/results")
def results():
    if "user_data" not in session:
        return redirect(url_for("upload_resume"))
    return render_template("results.html", data=session["user_data"])

@app.route("/learn")
def learn():
    if 'user_data' not in session:
        return redirect(url_for('upload_resume'))
    return render_template("learn.html", data=session['user_data'])

@app.route("/courses")
def show_courses():
    if 'user_data' not in session:
        return redirect(url_for('upload_resume'))

    user_data = session['user_data']
    missing_skills = user_data.get("missing", [])

    all_courses = []
    for skill in missing_skills:
        skill_courses = get_courses(skill)
        all_courses.extend(skill_courses)

    return render_template("course.html", data=all_courses)

@app.route("/getskill/<skill>")
def getytcourses(skill):
    if 'user_data' not in session:
        return redirect(url_for('upload_resume'))
    yt_courses = getyt(skill)
    coursera_courses = get_courses(skill)
    return render_template("ytcourse.html", data=yt_courses, coursera=coursera_courses)

@app.route("/project/<project_name>")
def project_roadmap(project_name):
    roadmap = generate_project_roadmap(project_name)
    return render_template("project.html", project_name=project_name, roadmap=roadmap)

# ------------------ Run App ------------------ #
if __name__ == "__main__": 
    app.run(debug=True)