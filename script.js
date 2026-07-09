// ---------------------------------------------------------------------------
// Smart Classroom for Rural Colleges - Frontend logic
// Talks to the Flask backend running at API_BASE
// ---------------------------------------------------------------------------

const API_BASE = "http://127.0.0.1:5000/api";

// ---- Tab switching ----------------------------------------------------
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

// ---- Health check -------------------------------------------------------
async function checkHealth() {
  const statusEl = document.getElementById("status");
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error();
    statusEl.textContent = "✅ Connected to backend";
    statusEl.className = "status ok";
  } catch (e) {
    statusEl.textContent = "⚠️ Backend not reachable. Run 'python app.py' in the backend folder.";
    statusEl.className = "status error";
  }
}

// ---- Courses -------------------------------------------------------------
async function loadCourses() {
  const res = await fetch(`${API_BASE}/courses`);
  const courses = await res.json();

  const list = document.getElementById("courseList");
  list.innerHTML = courses.length
    ? courses.map(c => `
        <div class="item">
          <h3>${c.title}</h3>
          <p><span class="badge">Teacher</span>${c.teacher || "—"}</p>
          <p>${c.description || ""}</p>
        </div>`).join("")
    : "<p>No courses added yet.</p>";

  // populate all course dropdowns
  const selects = ["attCourse", "attViewCourse", "resCourse", "resViewCourse"];
  selects.forEach(id => {
    const sel = document.getElementById(id);
    sel.innerHTML = courses.map(c => `<option value="${c.id}">${c.title}</option>`).join("");
  });
}

document.getElementById("courseForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = document.getElementById("courseTitle").value;
  const teacher = document.getElementById("courseTeacher").value;
  const description = document.getElementById("courseDesc").value;

  await fetch(`${API_BASE}/courses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, teacher, description }),
  });
  e.target.reset();
  loadCourses();
});

// ---- Students --------------------------------------------------------
async function loadStudents() {
  const res = await fetch(`${API_BASE}/students`);
  const students = await res.json();

  const list = document.getElementById("studentList");
  list.innerHTML = students.length
    ? students.map(s => `
        <div class="item">
          <h3>${s.name}</h3>
          <p><span class="badge">Roll No</span>${s.roll_no}</p>
          <p>${s.village || ""} ${s.phone ? " · " + s.phone : ""}</p>
        </div>`).join("")
    : "<p>No students added yet.</p>";

  const sel = document.getElementById("attStudent");
  sel.innerHTML = students.map(s => `<option value="${s.id}">${s.name} (${s.roll_no})</option>`).join("");
}

document.getElementById("studentForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("studentName").value;
  const roll_no = document.getElementById("studentRoll").value;
  const village = document.getElementById("studentVillage").value;
  const phone = document.getElementById("studentPhone").value;

  const res = await fetch(`${API_BASE}/students`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, roll_no, village, phone }),
  });

  if (!res.ok) {
    const err = await res.json();
    alert(err.error || "Could not add student");
    return;
  }
  e.target.reset();
  loadStudents();
});

// ---- Attendance --------------------------------------------------------
document.getElementById("attendanceForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const student_id = document.getElementById("attStudent").value;
  const course_id = document.getElementById("attCourse").value;
  const status = document.getElementById("attStatus").value;
  const date = document.getElementById("attDate").value;

  await fetch(`${API_BASE}/attendance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id, course_id, status, date }),
  });
  alert("Attendance recorded");
});

document.getElementById("loadAttendanceBtn").addEventListener("click", async () => {
  const courseId = document.getElementById("attViewCourse").value;
  if (!courseId) return;
  const res = await fetch(`${API_BASE}/attendance/${courseId}`);
  const records = await res.json();

  const list = document.getElementById("attendanceList");
  list.innerHTML = records.length
    ? records.map(r => `
        <div class="item">
          <h3>${r.name} (${r.roll_no})</h3>
          <p><span class="badge">${r.status}</span>${r.date}</p>
        </div>`).join("")
    : "<p>No attendance records for this course yet.</p>";
});

// ---- Resources ----------------------------------------------------------
document.getElementById("resourceForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const course_id = document.getElementById("resCourse").value;
  const title = document.getElementById("resTitle").value;
  const type = document.getElementById("resType").value;
  const url = document.getElementById("resUrl").value;

  await fetch(`${API_BASE}/resources`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ course_id, title, type, url }),
  });
  e.target.reset();
});

document.getElementById("loadResourcesBtn").addEventListener("click", async () => {
  const courseId = document.getElementById("resViewCourse").value;
  if (!courseId) return;
  const res = await fetch(`${API_BASE}/resources/${courseId}`);
  const resources = await res.json();

  const list = document.getElementById("resourceList");
  list.innerHTML = resources.length
    ? resources.map(r => `
        <div class="item">
          <h3>${r.title}</h3>
          <p><span class="badge">${r.type}</span><a href="${r.url}" target="_blank">${r.url}</a></p>
          <p>Uploaded: ${r.uploaded_on}</p>
        </div>`).join("")
    : "<p>No resources uploaded for this course yet.</p>";
});

// ---- Announcements -------------------------------------------------------
async function loadAnnouncements() {
  const res = await fetch(`${API_BASE}/announcements`);
  const items = await res.json();

  const list = document.getElementById("announcementList");
  list.innerHTML = items.length
    ? items.map(a => `
        <div class="item">
          <h3>${a.title}</h3>
          <p>${a.message}</p>
          <p><span class="badge">${a.posted_on}</span></p>
        </div>`).join("")
    : "<p>No announcements yet.</p>";
}

document.getElementById("announcementForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = document.getElementById("annTitle").value;
  const message = document.getElementById("annMessage").value;

  await fetch(`${API_BASE}/announcements`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, message }),
  });
  e.target.reset();
  loadAnnouncements();
});

// ---- Init -----------------------------------------------------------------
checkHealth();
loadCourses();
loadStudents();
loadAnnouncements();
