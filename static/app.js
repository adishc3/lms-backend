const content = document.getElementById('content');
const alertArea = document.getElementById('alert-area');
const userActions = document.getElementById('user-actions');
const navHome = document.getElementById('nav-home-link');
const navCourses = document.getElementById('nav-courses-link');
const navMyCourses = document.getElementById('nav-my-courses-link');
const navQuizzes = document.getElementById('nav-quizzes-link');
const navAI = document.getElementById('nav-ai-link');
const navAdmin = document.getElementById('nav-admin-link');

let token = localStorage.getItem('lms_token');
let currentUser = null;
let currentCourse = null;
let currentLesson = null;
let currentQuiz = null;
let currentTheme = localStorage.getItem('lms_theme') || 'light';

function initTheme() {
  document.documentElement.setAttribute('data-bs-theme', currentTheme);
}

window.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  navHome.addEventListener('click', (event) => { event.preventDefault(); showHome(); });
  navCourses.addEventListener('click', (event) => { event.preventDefault(); showCourses(); });
  navMyCourses?.addEventListener('click', (event) => { event.preventDefault(); showMyCourses(); });
  navQuizzes.addEventListener('click', (event) => { event.preventDefault(); showQuizzes(); });
  navAI.addEventListener('click', (event) => { event.preventDefault(); showAI(); });
  navAdmin.addEventListener('click', (event) => { event.preventDefault(); showAdmin(); });

  await loadUser();
  showHome();
});

function showAlert(message, type = 'info') {
  alertArea.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;
}

function clearAlert() {
  alertArea.innerHTML = '';
}

function authHeader() {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function fetchJson(path, options = {}, auth = true) {
  const headers = {
    Accept: 'application/json',
    ...options.headers,
  };
  if (auth && token) {
    headers.Authorization = `Bearer ${token}`;
  }
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    let errorText = response.statusText;
    try {
      const data = await response.json();
      errorText = data.detail || data.message || JSON.stringify(data);
    } catch (err) {
      // ignore parse errors
    }
    if (response.status === 401) {
      logout(false);
    }
    throw new Error(errorText);
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

async function loadUser() {
  if (!token) {
    currentUser = null;
    updateNav();
    return;
  }
  try {
    currentUser = await fetchJson('/auth/me');
  } catch (error) {
    currentUser = null;
    localStorage.removeItem('lms_token');
    token = null;
  }
  updateNav();
}

function updateNav() {
  if (currentUser) {
    userActions.innerHTML = `
      <button class="btn btn-outline-light btn-sm me-2" id="theme-toggle" title="Toggle dark mode">
        <i class="bi bi-${currentTheme === 'light' ? 'moon-stars' : 'sun'}-fill"></i>
      </button>
      <span class="me-3 text-white">${currentUser.email} (${currentUser.role})</span>
      <button class="btn btn-outline-light btn-sm" id="logout-btn">Logout</button>
    `;
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
    document.getElementById('logout-btn').addEventListener('click', () => logout(true));
    navAdmin.classList.remove('hidden');
    navMyCourses?.classList.remove('hidden');
    if (currentUser.role !== 'admin') {
      navAdmin.classList.add('hidden');
    }
    if (currentUser.role === 'instructor' || currentUser.role === 'admin') {
      navMyCourses?.classList.add('hidden');
    }
  } else {
    userActions.innerHTML = `
      <button class="btn btn-outline-light btn-sm me-2" id="theme-toggle" title="Toggle dark mode">
        <i class="bi bi-moon-stars-fill"></i>
      </button>
      <button class="btn btn-outline-light btn-sm me-2" id="login-btn">Login</button>
      <button class="btn btn-light btn-sm" id="register-btn">Register</button>
    `;
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
    document.getElementById('login-btn').addEventListener('click', () => showHome('login'));
    document.getElementById('register-btn').addEventListener('click', () => showHome('register'));
    navAdmin.classList.add('hidden');
    navMyCourses?.classList.add('hidden');
  }
}

function toggleTheme() {
  currentTheme = currentTheme === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-bs-theme', currentTheme);
  localStorage.setItem('lms_theme', currentTheme);
  if (currentUser) {
    document.querySelector('#theme-toggle i').className = `bi bi-${currentTheme === 'light' ? 'moon-stars' : 'sun'}-fill`;
  } else {
    document.querySelector('#theme-toggle i').className = `bi bi-${currentTheme === 'light' ? 'moon-stars' : 'sun'}-fill`;
  }
}

function logout(showMessage = true) {
  token = null;
  currentUser = null;
  localStorage.removeItem('lms_token');
  updateNav();
  if (showMessage) {
    showAlert('Signed out successfully.', 'success');
  }
  showHome();
}

function setActiveNav(selected) {
  [navHome, navCourses, navMyCourses, navQuizzes, navAI, navAdmin].forEach((link) => {
    if (link) link.classList.toggle('active', link.id === selected);
  });
}

function showHome(mode = 'default') {
  setActiveNav('nav-home-link');
  clearAlert();
  if (!currentUser) {
    showLogin();
    return;
  }

  content.innerHTML = `
    <div class="card card-section welcome-card">
      <div class="card-body">
        <h3 class="mb-2"><i class="bi bi-emoji-smile me-2"></i>Welcome back, ${currentUser.full_name || currentUser.email}!</h3>
        <p class="mb-0">Use the navigation to browse courses, take quizzes, and access AI tools.</p>
      </div>
    </div>
    <div class="row g-3">
      <div class="col-md-4">
        <div class="card card-section h-100">
          <div class="card-header"><i class="bi bi-book me-2"></i>Quick actions</div>
          <div class="card-body d-grid gap-2">
            <button class="btn btn-primary" onclick="showCourses()"><i class="bi bi-book me-2"></i>Browse Courses</button>
            <button class="btn btn-outline-primary" onclick="showQuizzes()"><i class="bi bi-patch-question me-2"></i>My Quizzes</button>
            <button class="btn btn-outline-info" onclick="showAI()"><i class="bi bi-robot me-2"></i>AI Tools</button>
          </div>
        </div>
      </div>
      <div class="col-md-8">
        <div class="card card-section h-100">
          <div class="card-header"><i class="bi bi-person-gear me-2"></i>Your profile</div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-sm-6">
                <p class="mb-1"><strong>Email:</strong></p>
                <p class="text-muted mb-0">${currentUser.email}</p>
              </div>
              <div class="col-sm-6">
                <p class="mb-1"><strong>Role:</strong></p>
                <p class="text-muted mb-0">${currentUser.role}</p>
              </div>
              <div class="col-sm-6">
                <p class="mb-1"><strong>Status:</strong></p>
                <p class="text-muted mb-0">${currentUser.is_active ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Inactive</span>'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function showLogin() {
  setActiveNav('nav-home-link');
  clearAlert();
  content.innerHTML = `
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="text-center mb-5">
          <h1 class="display-5 fw-bold"><i class="bi bi-mortarboard-fill text-primary"></i> Beginner LMS</h1>
          <p class="text-muted">Your learning journey starts here</p>
        </div>
        <div class="card card-section">
          <div class="card-header"><i class="bi bi-box-arrow-in-right me-2"></i>Login</div>
          <div class="card-body">
            <form id="login-form">
              <div class="mb-3">
                <label class="form-label"><i class="bi bi-envelope me-1"></i>Email</label>
                <input type="email" class="form-control" name="email" placeholder="you@example.com" required>
              </div>
              <div class="mb-3">
                <label class="form-label"><i class="bi bi-key me-1"></i>Password</label>
                <input type="password" class="form-control" name="password" required>
              </div>
              <button type="submit" class="btn btn-primary w-100"><i class="bi bi-box-arrow-in-right me-2"></i>Sign In</button>
            </form>
            <hr>
            <div class="text-center">
              <p class="mb-0">Don't have an account? <a href="#" onclick="showRegister(); return false;" class="fw-bold text-decoration-none">Create one</a></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
  document.getElementById('login-form').addEventListener('submit', handleLogin);
}

function showRegister() {
  setActiveNav('nav-home-link');
  clearAlert();
  content.innerHTML = `
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="text-center mb-5">
          <h1 class="display-5 fw-bold"><i class="bi bi-mortarboard-fill text-primary"></i> Beginner LMS</h1>
          <p class="text-muted">Join our learning community</p>
        </div>
        <div class="card card-section">
          <div class="card-header"><i class="bi bi-person-plus me-2"></i>Create Account</div>
          <div class="card-body">
            <form id="register-form">
              <div class="mb-3">
                <label class="form-label"><i class="bi bi-person me-1"></i>Full Name</label>
                <input type="text" class="form-control" name="full_name" placeholder="John Doe">
              </div>
              <div class="mb-3">
                <label class="form-label"><i class="bi bi-envelope me-1"></i>Email</label>
                <input type="email" class="form-control" name="email" placeholder="you@example.com" required>
              </div>
              <div class="mb-3">
                <label class="form-label"><i class="bi bi-key me-1"></i>Password</label>
                <input type="password" class="form-control" name="password" required>
              </div>
              <div class="mb-3">
                <label class="form-label"><i class="bi bi-person-gear me-1"></i>I am registering as</label>
                <select class="form-select" name="role">
                  <option value="student"><i class="bi bi-mortarboard"></i> Student (learn courses)</option>
                  <option value="instructor"><i class="bi bi-easel"></i> Instructor (create courses)</option>
                </select>
              </div>
              <button type="submit" class="btn btn-success w-100"><i class="bi bi-person-plus me-2"></i>Register</button>
            </form>
            <hr>
            <div class="text-center">
              <p class="mb-0">Already have an account? <a href="#" onclick="showLogin(); return false;" class="fw-bold text-decoration-none">Sign in</a></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
  document.getElementById('register-form').addEventListener('submit', handleRegister);
}

async function handleLogin(event) {
  event.preventDefault();
  clearAlert();
  const form = event.target;
  const email = form.email.value.trim();
  const password = form.password.value;
  const body = new URLSearchParams({ username: email, password });
  try {
    const response = await fetch('/auth/login', {
      method: 'POST',
      body,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    if (!response.ok) {
      const error = await response.json().catch(() => null);
      throw new Error(error?.detail || response.statusText);
    }
    const data = await response.json();
    token = data.access_token;
    localStorage.setItem('lms_token', token);
    await loadUser();
    showAlert('Login successful.', 'success');
    showHome();
  } catch (error) {
    showAlert(`Login failed: ${error.message}`, 'danger');
  }
}

async function handleRegister(event) {
  event.preventDefault();
  clearAlert();
  const form = event.target;
  const payload = {
    full_name: form.full_name.value.trim() || undefined,
    email: form.email.value.trim(),
    password: form.password.value,
    role: form.role.value,
  };
  try {
    await fetchJson('/auth/register', { method: 'POST', body: JSON.stringify(payload) }, false);
    showAlert('Registration complete. Logging in...', 'success');
    const loginEvent = { target: { email: { value: payload.email }, password: { value: payload.password } } };
    await handleLogin({ preventDefault: () => {}, target: { email: { value: payload.email }, password: { value: payload.password } } });
  } catch (error) {
    showAlert(`Registration failed: ${error.message}`, 'danger');
  }
}

async function showCourses() {
  setActiveNav('nav-courses-link');
  clearAlert();
  currentCourse = null;
  currentLesson = null;
  let courses = [];
  try {
    courses = await fetchJson('/courses/');
  } catch (error) {
    showAlert(`Unable to load courses: ${error.message}`, 'danger');
    return;
  }
  content.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1"><i class="bi bi-book me-2"></i>Courses</h2>
        <p class="text-muted mb-0">Browse and enroll in available courses</p>
      </div>
      ${currentUser && ['instructor', 'admin'].includes(currentUser.role) ? '<button class="btn btn-primary" id="new-course-btn"><i class="bi bi-plus-circle me-2"></i>Create course</button>' : ''}
    </div>
    <div id="course-list" class="row row-cols-1 row-cols-md-2 g-4"></div>
    <div id="course-form-container"></div>
  `;

  const list = document.getElementById('course-list');
  if (!courses.length) {
    list.innerHTML = `<div class="col"><div class="alert alert-warning">No courses available yet.</div></div>`;
  }

  courses.forEach((course) => {
    const card = document.createElement('div');
    card.className = 'col';
    card.innerHTML = `
      <div class="card h-100">
        <div class="card-body">
          <h5 class="card-title">${course.title}</h5>
          <p class="card-text">${course.description || 'No description provided.'}</p>
          <p class="text-muted small"><i class="bi bi-person-badge me-1"></i>Instructor ID: ${course.owner_id}</p>
        </div>
        <div class="card-footer d-flex justify-content-between align-items-center">
          <button class="btn btn-sm btn-outline-primary" onclick="showCourse(${course.id})"><i class="bi bi-eye me-1"></i>View</button>
          ${currentUser && currentUser.role !== 'instructor' ? `<button class="btn btn-sm btn-success" onclick="enrollCourse(${course.id})"><i class="bi bi-bookmark-plus me-1"></i>Enroll</button>` : ''}
        </div>
      </div>
    `;
    list.appendChild(card);
  });

  if (currentUser && ['instructor', 'admin'].includes(currentUser.role)) {
    document.getElementById('new-course-btn').addEventListener('click', renderCreateCourseForm);
  }
}

async function renderCreateCourseForm() {
  const container = document.getElementById('course-form-container');
  container.innerHTML = `
    <div class="card card-section">
      <div class="card-header"><i class="bi bi-plus-circle me-2"></i>Create New Course</div>
      <div class="card-body">
        <form id="create-course-form">
          <div class="mb-3">
            <label class="form-label"><i class="bi bi-bookmark me-1"></i>Title</label>
            <input class="form-control" name="title" placeholder="e.g., Introduction to Python" required>
          </div>
          <div class="mb-3">
            <label class="form-label"><i class="bi bi-card-text me-1"></i>Description</label>
            <textarea class="form-control" name="description" placeholder="What students will learn..."></textarea>
          </div>
          <button type="submit" class="btn btn-success"><i class="bi bi-check-circle me-2"></i>Create Course</button>
        </form>
      </div>
    </div>
  `;
  document.getElementById('create-course-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    clearAlert();
    const form = event.target;
    const payload = { title: form.title.value.trim(), description: form.description.value.trim() || undefined };
    try {
      const created = await fetchJson('/courses/', { method: 'POST', body: JSON.stringify(payload) });
      showAlert(`Course created: ${created.title}`, 'success');
      showCourse(created.id);
    } catch (error) {
      showAlert(`Course creation failed: ${error.message}`, 'danger');
    }
  });
}

async function enrollCourse(courseId) {
  clearAlert();
  if (!currentUser) {
    showAlert('Please log in to enroll in a course.', 'warning');
    return;
  }
  try {
    await fetchJson(`/courses/${courseId}/enroll`, { method: 'POST' });
    showAlert('Successfully enrolled in the course.', 'success');
    showCourse(courseId);
  } catch (error) {
    showAlert(`Enrollment failed: ${error.message}`, 'danger');
  }
}

async function showCourse(courseId) {
  setActiveNav('nav-courses-link');
  clearAlert();
  currentCourse = await fetchJson(`/courses/${courseId}`);
  currentLesson = null;

  let lessons = [];
  let lessonError = null;
  try {
    lessons = await fetchJson(`/courses/${courseId}/lessons`);
  } catch (error) {
    lessonError = error.message;
  }

  content.innerHTML = `
    <div class="d-flex justify-content-between align-items-start mb-4">
      <div>
        <h2 class="mb-2">${currentCourse.title}</h2>
        <p class="lead mb-2">${currentCourse.description || 'No description.'}</p>
        <p class="text-muted small"><i class="bi bi-person-badge me-1"></i>Instructor ID: ${currentCourse.owner_id}</p>
      </div>
      <div class="btn-group">
        <button class="btn btn-outline-light" onclick="showCourses()"><i class="bi bi-arrow-left me-1"></i>Back</button>
        <button class="btn btn-light" onclick="showCourseQuizzes(${currentCourse.id})"><i class="bi bi-patch-question me-1"></i>Quizzes</button>
      </div>
    </div>
    <div class="row g-4">
      <div class="col-lg-7">
        <div class="card card-section h-100">
          <div class="card-header"><i class="bi bi-journal-text me-2"></i>Lessons</div>
          <div class="card-body" id="lesson-list"></div>
        </div>
      </div>
      <div class="col-lg-5">
        <div class="card card-section h-100">
          <div class="card-header"><i class="bi bi-gear me-2"></i>Course Actions</div>
          <div class="card-body d-grid gap-2" id="course-actions"></div>
        </div>
      </div>
    </div>
  `;

  const lessonList = document.getElementById('lesson-list');
  if (lessonError) {
    lessonList.innerHTML = `<div class="alert alert-warning"><i class="bi bi-exclamation-triangle me-2"></i>${lessonError}</div>`;
  } else if (!lessons.length) {
    lessonList.innerHTML = `<div class="alert alert-info"><i class="bi bi-info-circle me-2"></i>No lessons published yet.</div>`;
  } else {
    lessonList.innerHTML = lessons
      .map(
        (lesson) => `
          <div class="card card-section lesson-card mb-3">
            <div class="card-body">
              <h5 class="mb-2">${lesson.title}</h5>
              <p class="text-muted small mb-3">${lesson.content.substring(0, 120)}${lesson.content.length > 120 ? '...' : ''}</p>
              <button class="btn btn-sm btn-outline-primary" onclick="showLesson(${currentCourse.id}, ${lesson.id})"><i class="bi bi-eye me-1"></i>View lesson</button>
            </div>
          </div>
        `,
      )
      .join('');
  }

  const courseActions = document.getElementById('course-actions');
  courseActions.innerHTML = `
    <div class="mb-3">
      <p class="mb-1"><strong>Current status:</strong></p>
      <span class="badge ${lessonError ? 'bg-warning' : 'bg-success'}">${lessonError ? 'Enrollment or access required' : 'Access granted'}</span>
    </div>
  `;

  if (currentUser && ['instructor', 'admin'].includes(currentUser.role)) {
    courseActions.innerHTML += `
      <button class="btn btn-success w-100 mb-3" id="new-lesson-btn"><i class="bi bi-plus-circle me-2"></i>Publish lesson</button>
      <div id="lesson-form-container"></div>
    `;
    document.getElementById('new-lesson-btn').addEventListener('click', renderCreateLessonForm);
  }
}

async function renderCreateLessonForm() {
  const container = document.getElementById('lesson-form-container');
  container.innerHTML = `
    <div class="card card-section mt-3">
      <div class="card-header"><i class="bi bi-journal-plus me-2"></i>Add a lesson</div>
      <div class="card-body">
        <form id="create-lesson-form">
          <div class="mb-3">
            <label class="form-label"><i class="bi bi-bookmark me-1"></i>Title</label>
            <input class="form-control" name="title" placeholder="Lesson title" required>
          </div>
          <div class="mb-3">
            <label class="form-label"><i class="bi bi-card-text me-1"></i>Content</label>
            <textarea class="form-control" name="content" placeholder="Lesson content..." required></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label"><i class="bi bi-upload me-1"></i>Attachment (optional)</label>
            <input type="file" class="form-control" name="file" accept=".pdf,.png,.jpg,.jpeg,.gif,.mp4,.mp3,.txt,.csv,.zip">
            <div class="form-text">Supported formats: PDF, images, videos, audio, text, CSV, ZIP (max 20MB)</div>
          </div>
          <button type="submit" class="btn btn-success w-100"><i class="bi bi-upload me-2"></i>Publish Lesson</button>
        </form>
      </div>
    </div>
  `;
  document.getElementById('create-lesson-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    clearAlert();
    const form = event.target;
    
    try {
      const lesson = await fetchJson(`/courses/${currentCourse.id}/lessons`, { 
        method: 'POST', 
        body: JSON.stringify({ title: form.title.value.trim(), content: form.content.value.trim() }) 
      });
      
      if (form.file.files[0]) {
        const fd = new FormData();
        fd.append('file', form.file.files[0]);
        
        const uploadResponse = await fetch(`/courses/${currentCourse.id}/lessons/${lesson.id}/upload`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: fd
        });
        
        if (!uploadResponse.ok) {
          const err = await uploadResponse.json().catch(() => null);
          showAlert(`Lesson created but upload failed: ${err?.detail || 'Unknown error'}`, 'warning');
        } else {
          showAlert(`Lesson created with attachment: ${lesson.title}`, 'success');
        }
      } else {
        showAlert(`Lesson created: ${lesson.title}`, 'success');
      }
      showCourse(currentCourse.id);
    } catch (error) {
      showAlert(`Lesson creation failed: ${error.message}`, 'danger');
    }
  });
}

async function showLesson(courseId, lessonId) {
  setActiveNav('nav-courses-link');
  clearAlert();
  currentCourse = await fetchJson(`/courses/${courseId}`);
  currentLesson = await fetchJson(`/courses/${courseId}/lessons/${lessonId}`);

  content.innerHTML = `
    <div class="d-flex justify-content-between align-items-start mb-4">
      <div>
        <h2 class="mb-2">${currentLesson.title}</h2>
        <p class="text-muted mb-0"><i class="bi bi-book me-1"></i>Course: ${currentCourse.title}</p>
      </div>
      <button class="btn btn-outline-light" onclick="showCourse(${courseId})"><i class="bi bi-arrow-left me-1"></i>Back to course</button>
    </div>
    <div class="card card-section lesson-card mb-4">
      <div class="card-body">
        <p class="mb-3">${currentLesson.content}</p>
        ${currentLesson.asset_url ? `<p><a href="${currentLesson.asset_url}" target="_blank" class="btn btn-outline-primary btn-sm"><i class="bi bi-download me-1"></i>Download attachment</a></p>` : ''}
      </div>
    </div>
    <div class="row">
      <div class="col-md-6">
        <div class="card card-section h-100">
          <div class="card-header"><i class="bi bi-chat-dots me-2"></i>AI Study Assistant</div>
          <div class="card-body">
            <form id="ai-study-form">
              <div class="mb-3">
                <label class="form-label"><i class="bi bi-question-circle me-1"></i>Ask a question</label>
                <textarea class="form-control" name="question" placeholder="Ask anything about this lesson..." required></textarea>
              </div>
              <button class="btn btn-primary w-100"><i class="bi bi-send me-2"></i>Ask AI</button>
            </form>
            <div class="mt-3" id="ai-study-response"></div>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card card-section h-100">
          <div class="card-header"><i class="bi bi-robot me-2"></i>AI Quiz Generator</div>
          <div class="card-body">
            <form id="ai-quiz-form">
              <div class="mb-3">
                <label class="form-label"><i class="bi bi-hash me-1"></i>Number of questions</label>
                <input type="number" class="form-control" name="question_count" value="3" min="1" max="10" required>
              </div>
              <button class="btn btn-info w-100"><i class="bi bi-gear me-2"></i>Generate Quiz</button>
            </form>
            <div class="mt-3" id="ai-quiz-response"></div>
          </div>
        </div>
      </div>
    </div>
  `;

  document.getElementById('ai-study-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    clearAlert();
    const form = event.target;
    const payload = { lesson_id: currentLesson.id, question: form.question.value.trim() };
    try {
      const result = await fetchJson('/ai/study-assistant', { method: 'POST', body: JSON.stringify(payload) });
      document.getElementById('ai-study-response').innerHTML = `<div class="alert alert-success">${result.answer}</div>`;
    } catch (error) {
      showAlert(`AI study request failed: ${error.message}`, 'danger');
    }
  });

  document.getElementById('ai-quiz-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    clearAlert();
    const form = event.target;
    const payload = { lesson_id: currentLesson.id, question_count: Number(form.question_count.value) };
    try {
      const result = await fetchJson('/ai/quiz-generator', { method: 'POST', body: JSON.stringify(payload) });
      document.getElementById('ai-quiz-response').innerHTML = `<div class="alert alert-success"><pre>${result.quiz}</pre></div>`;
    } catch (error) {
      showAlert(`AI quiz generation failed: ${error.message}`, 'danger');
    }
  });
}

async function showQuizzes() {
  setActiveNav('nav-quizzes-link');
  clearAlert();
  if (!currentCourse) {
    content.innerHTML = `
      <div class="alert alert-info">Open a course to view available quizzes. First select a course from the Courses tab.</div>
    `;
    return;
  }
  showCourseQuizzes(currentCourse.id);
}

async function showMyCourses() {
  setActiveNav('nav-my-courses-link');
  clearAlert();
  if (!currentUser) {
    content.innerHTML = `<div class="alert alert-warning"><i class="bi bi-exclamation-triangle me-2"></i>Please log in to view your courses.</div>`;
    return;
  }
  if (currentUser.role === 'instructor' || currentUser.role === 'admin') {
    content.innerHTML = `<div class="alert alert-info"><i class="bi bi-info-circle me-2"></i>Instructors can view their courses from the Courses tab.</div>`;
    return;
  }
  let courses = [];
  try {
    courses = await fetchJson('/courses/my/courses');
  } catch (error) {
    showAlert(`Unable to load enrolled courses: ${error.message}`, 'danger');
    return;
  }
  content.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1"><i class="bi bi-bookmark-star me-2"></i>My Enrolled Courses</h2>
        <p class="text-muted mb-0">Courses you're actively learning</p>
      </div>
      <button class="btn btn-outline-secondary"><i class="bi bi-arrow-left me-2"></i>Browse all courses</button>
    </div>
    <div id="my-course-list" class="row row-cols-1 row-cols-md-2 g-4"></div>
  `;
  const list = document.getElementById('my-course-list');
  if (!courses.length) {
    list.innerHTML = `<div class="col"><div class="alert alert-info"><i class="bi bi-info-circle me-2"></i>You are not enrolled in any courses yet. Browse courses to enroll.</div></div>`;
    return;
  }
  courses.forEach((course) => {
    const card = document.createElement('div');
    card.className = 'col';
    card.innerHTML = `
      <div class="card h-100 lesson-card">
        <div class="card-body">
          <h5 class="card-title">${course.title}</h5>
          <p class="card-text">${course.description || 'No description provided.'}</p>
        </div>
        <div class="card-footer d-flex justify-content-between align-items-center">
          <button class="btn btn-sm btn-outline-primary" onclick="showCourse(${course.id})"><i class="bi bi-eye me-1"></i>View</button>
          <button class="btn btn-sm btn-primary" onclick="showCourseQuizzes(${course.id})"><i class="bi bi-patch-question me-1"></i>Quizzes</button>
        </div>
      </div>
    `;
    list.appendChild(card);
  });
}

async function showCourseQuizzes(courseId) {
  clearAlert();
  currentCourse = await fetchJson(`/courses/${courseId}`);
  let quizzes = [];
  try {
    quizzes = await fetchJson(`/quizzes/course/${courseId}`);
  } catch (error) {
    showAlert(`Unable to load quizzes: ${error.message}`, 'danger');
    return;
  }
  content.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1"><i class="bi bi-patch-question me-2"></i>Quizzes for ${currentCourse.title}</h2>
        <p class="text-muted mb-0">Select a quiz to attempt or view details</p>
      </div>
      <button class="btn btn-outline-secondary" onclick="showMyCourses()"><i class="bi bi-arrow-left me-2"></i>Back</button>
    </div>
    <div id="quiz-list" class="row row-cols-1 row-cols-md-2 g-4"></div>
  `;

  const list = document.getElementById('quiz-list');
  if (!quizzes.length) {
    list.innerHTML = `<div class="col"><div class="alert alert-warning">No quizzes available for this course.</div></div>`;
    return;
  }
  quizzes.forEach((quiz) => {
    const card = document.createElement('div');
    card.className = 'col';
    card.innerHTML = `
      <div class="card h-100 quiz-card">
        <div class="card-body">
          <h5 class="card-title">${quiz.title}</h5>
          <p class="card-text">${quiz.description || 'No description.'}</p>
          <p class="text-muted small"><i class="bi bi-hash me-1"></i><strong>Questions:</strong> ${quiz.questions.length}</p>
        </div>
        <div class="card-footer text-end">
          <button class="btn btn-sm btn-primary" onclick="showQuiz(${quiz.id})"><i class="bi bi-play-circle me-1"></i>Attempt quiz</button>
        </div>
      </div>
    `;
    list.appendChild(card);
  });
}

async function showQuiz(quizId) {
  setActiveNav('nav-quizzes-link');
  clearAlert();
  currentQuiz = await fetchJson(`/quizzes/${quizId}`);
  content.innerHTML = `
    <div class="d-flex justify-content-between align-items-start mb-3">
      <div>
        <h2>${currentQuiz.title}</h2>
        <p>${currentQuiz.description || ''}</p>
        <p class="text-muted">Course ID: ${currentQuiz.course_id}</p>
      </div>
      <button class="btn btn-outline-secondary" onclick="showCourse(${currentQuiz.course_id})">Back to course</button>
    </div>
    <form id="quiz-attempt-form"></form>
  `;

  const form = document.getElementById('quiz-attempt-form');
  form.innerHTML = currentQuiz.questions
    .map((question, index) => `
      <div class="card card-section lesson-card">
        <div class="card-body">
          <h5 class="mb-3">Q${index + 1}: ${question.text}</h5>
          ${question.options
            .map(
              (option) => `
                <div class="form-check mb-2">
                  <input class="form-check-input" type="radio" name="question-${question.id}" id="option-${option.id}" value="${option.id}" required>
                  <label class="form-check-label" for="option-${option.id}">${option.text}</label>
                </div>
              `,
            )
            .join('')}
        </div>
      </div>
    `)
    .join('');

  form.innerHTML += `
    <div class="d-flex justify-content-between align-items-center mt-4">
      <button class="btn btn-outline-secondary" type="button" onclick="showMyCourses() || showCourse(${currentQuiz.course_id})"><i class="bi bi-arrow-left me-2"></i>Cancel</button>
      <button class="btn btn-success" type="submit"><i class="bi bi-check-circle me-2"></i>Submit Quiz</button>
    </div>
  `;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearAlert();
    const answers = currentQuiz.questions.map((question) => {
      const selected = form.querySelector(`input[name="question-${question.id}"]:checked`);
      return { question_id: question.id, selected_option_id: Number(selected?.value || 0) };
    });
    try {
      const attempt = await fetchJson(`/quizzes/${currentQuiz.id}/attempts`, { method: 'POST', body: JSON.stringify({ answers }) });
      content.innerHTML = `
        <div class="card card-section welcome-card">
          <div class="card-body text-center">
            <h3 class="mb-3"><i class="bi bi-check-circle me-2"></i>Quiz Submitted!</h3>
            <p class="display-4 fw-bold mb-2">${attempt.score} <small class="text-muted">/ ${attempt.total}</small></p>
            <p class="text-muted mb-4">Score: ${Math.round((attempt.score / attempt.total) * 100) || 0}%</p>
            <p class="text-muted"><i class="bi bi-calendar me-1"></i>Submitted at: ${new Date(attempt.submitted_at).toLocaleString()}</p>
          </div>
        </div>
        <div class="row g-3">${attempt.answers
          .map(
            (answer) => `
              <div class="col-md-6 col-lg-4">
                <div class="card card-section h-100">
                  <div class="card-body">
                    <h6 class="mb-2"><i class="bi bi-question-circle me-1"></i>Question ${answer.question_id}</h6>
                    <p class="mb-1 small"><strong>Selected:</strong> Option ${answer.selected_option_id}</p>
                    <p class="mb-0"><span class="badge ${answer.is_correct ? 'bg-success' : 'bg-danger'}">${answer.is_correct ? 'Correct' : 'Incorrect'}</span></p>
                  </div>
                </div>
              </div>
            `,
          )
          .join('')}</div>
      `;
    } catch (error) {
      showAlert(`Quiz submission failed: ${error.message}`, 'danger');
    }
  });
}

async function showAI() {
  setActiveNav('nav-ai-link');
  clearAlert();
  if (!currentUser) {
    content.innerHTML = `<div class="alert alert-warning"><i class="bi bi-exclamation-triangle me-2"></i>Please log in to use AI assistant features.</div>`;
    return;
  }
  if (!currentCourse) {
    content.innerHTML = `<div class="alert alert-info"><i class="bi bi-info-circle me-2"></i>Open a course from the Courses tab to use AI tools.</div>`;
    return;
  }
  if (!currentLesson) {
    content.innerHTML = `<div class="alert alert-info"><i class="bi bi-info-circle me-2"></i>Open a lesson within the selected course to enable AI tools.</div>`;
    return;
  }
  showLesson(currentCourse.id, currentLesson.id);
}

async function showAdmin() {
  setActiveNav('nav-admin-link');
  clearAlert();
  if (!currentUser || currentUser.role !== 'admin') {
    content.innerHTML = `<div class="alert alert-danger"><i class="bi bi-shield-exclamation me-2"></i>Admin access required.</div>`;
    return;
  }
  let users = [];
  try {
    users = await fetchJson('/admin/users');
  } catch (error) {
    showAlert(`Unable to load users: ${error.message}`, 'danger');
    return;
  }
  content.innerHTML = `
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-1"><i class="bi bi-shield-lock me-2"></i>Admin Dashboard</h2>
        <p class="text-muted mb-0">Manage users and system settings</p>
      </div>
      <button class="btn btn-outline-secondary"><i class="bi bi-house me-2"></i>Home</button>
    </div>
    <div class="card card-section">
      <div class="card-body">
        <table class="table table-hover mb-0">
          <thead>
            <tr>
              <th class="text-center">#</th>
              <th><i class="bi bi-envelope me-1"></i>Email</th>
              <th><i class="bi bi-person me-1"></i>Name</th>
              <th><i class="bi bi-person-badge me-1"></i>Role</th>
              <th><i class="bi bi-check-circle me-1"></i>Status</th>
            </tr>
          </thead>
          <tbody>${users
            .map(
              (user) => `
                <tr>
                  <td class="text-center">${user.id}</td>
                  <td>${user.email}</td>
                  <td>${user.full_name || '<span class="text-muted">-</span>'}</td>
                  <td><span class="badge bg-${user.role === 'admin' ? 'danger' : user.role === 'instructor' ? 'info' : 'primary'}">${user.role}</span></td>
                  <td>${user.is_active ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Inactive</span>'}</td>
                </tr>
              `,
            )
            .join('')}</tbody>
        </table>
      </div>
    </div>
  `;
}
