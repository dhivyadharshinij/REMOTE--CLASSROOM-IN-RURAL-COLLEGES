# Smart Classroom for Rural Colleges

A simple full-stack project: **Python (Flask) backend** + **HTML/CSS/JS frontend**,
designed to run on low-spec, low-bandwidth setups typical in rural colleges.

## Folder structure
```
smart-classroom/
├── backend/
│   ├── app.py              # Flask API + SQLite database
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Dashboard UI
│   ├── style.css           # Styling
│   └── script.js           # Talks to the backend API
└── README.md
```

## How to run in VS Code

### 1. Open the project
Open the `smart-classroom` folder in VS Code (`File > Open Folder`).

### 2. Run the backend
Open a terminal in VS Code (`` Ctrl+` ``):
```bash
cd backend
python -m venv venv          # optional but recommended
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python app.py
```
This starts the API at **http://127.0.0.1:5000**. It also auto-creates a
`smart_classroom.db` SQLite file the first time it runs — no separate database
setup needed.

### 3. Run the frontend
Open `frontend/index.html` in a browser. The easiest way in VS Code:
- Install the **Live Server** extension
- Right-click `index.html` → **Open with Live Server**

(Opening the file directly by double-clicking also works, since it just calls
the API over `http://127.0.0.1:5000`.)

### 4. Use the app
- Add courses, students
- Mark and view attendance per course
- Upload/view study material links (PDFs, videos, notes) per course — useful
  for low-bandwidth areas since students can download once and view offline
- Post announcements

## Notes
- The backend uses SQLite, so there's zero database configuration — perfect
  for colleges without dedicated server infrastructure.
- CORS is enabled so the frontend can be opened as a static file while the
  backend runs separately.
- This is a starting scaffold — you can extend it with login/auth, video
  conferencing links, or a proper file-upload endpoint as needed.
