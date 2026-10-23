# CampusLens AI

An AI-assisted campus accessibility and issue-prioritization web application built with Flask, Python, SQLite, HTML, CSS, and JavaScript.

## Current repository status
The original project package is available as `CampusLens_AI_Working_Website.zip`. Extract the ZIP archive locally to inspect the complete source project.

## Deploy on Render
This project expects a Python Flask application. In Render's Web Service settings, choose **Python** (not Node), with:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app`

The files `app.py`, `requirements.txt`, `templates/`, and `static/` must exist in the selected root directory. The ZIP file alone is not enough for Render to install dependencies or start the Flask app.

## Important
Use a persistent disk or an external database for production use if report data must survive redeployments. Configure a strong `SECRET_KEY` and the `ADMIN_PASSWORD_HASH` environment variable before enabling administrator access.

## Repository
https://github.com/Ayushman07-dev/CampusLens-AI
