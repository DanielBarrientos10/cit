// ═══════════════════════════════════════════
//  auth.js — Lógica de Login / Registro / Recuperación
// ═══════════════════════════════════════════

const API = '/api/';
let TOKEN = localStorage.getItem('token') || null;

// ─── TOAST ───
function showToast(msg, type = 'info') {
  const icons = { info: 'bi-info-circle', success: 'bi-check-circle-fill', error: 'bi-exclamation-circle-fill', warning: 'bi-exclamation-triangle-fill' };
  const container = document.getElementById('toastContainer');
  const id = 't' + Date.now();
  const typeClass = type === 'error' ? 'toast-error' : `toast-${type}`;
  container.innerHTML += `<div id="${id}" class="toast align-items-center border-0 fade ${typeClass}" role="alert">
    <div class="toast-body">
      <i class="bi ${icons[type]||icons.info} me-1" style="font-size:1rem"></i>
      <span class="flex-grow-1">${msg}</span>
      <button type="button" class="btn-close btn-close-sm ms-2" data-bs-dismiss="toast"></button>
    </div>
  </div>`;
  const el = document.getElementById(id);
  const bsToast = new bootstrap.Toast(el, { delay: 4000 });
  bsToast.show();
  el.addEventListener('hidden.bs.toast', () => el.remove());
}

function showAlert(el, msg, type) {
  el.className = `alert alert-${type === 'error' ? 'danger' : type}`;
  el.innerHTML = `<i class="bi ${type === 'error' ? 'bi-exclamation-circle' : type === 'success' ? 'bi-check-circle' : 'bi-info-circle'} me-1"></i>${msg}`;
  el.classList.remove('d-none');
}

function hideAlert(el) { el.classList.add('d-none'); }

// ─── API ───
async function apiFetch(url, options = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (TOKEN) headers['Authorization'] = `Bearer ${TOKEN}`;
  try {
    const res = await fetch(API + url, { ...options, headers });
    if (res.status === 401) { showToast('Sesión expirada', 'warning'); return null; }
    const data = await res.json();
    return { ok: res.ok, status: res.status, data };
  } catch (e) {
    showToast('Error de conexión con el servidor', 'error');
    return null;
  }
}

// ─── AUTH ───
let isRegister = false;

function toggleAuth() {
  isRegister = !isRegister;
  document.getElementById('authTitle').textContent = isRegister ? 'Crear Cuenta' : 'Iniciar Sesión';
  document.getElementById('authSubtitle').textContent = isRegister ? 'Regístrate para agendar tus citas médicas' : 'Accede a tu panel de citas médicas';
  const btn = document.getElementById('authBtn');
  btn.innerHTML = isRegister ? '<i class="bi bi-person-plus"></i> Crear Cuenta' : '<i class="bi bi-box-arrow-in-right"></i> Ingresar';
  ['nameGroup','docGroup','phoneGroup','confirmGroup'].forEach(g => {
    const el = document.getElementById(g);
    if (el) el.style.display = isRegister ? 'block' : 'none';
  });
  document.getElementById('authToggle').innerHTML = isRegister
    ? '¿Ya tienes cuenta? <a onclick="toggleAuth()">Inicia sesión</a>'
    : '¿No tienes cuenta? <a onclick="toggleAuth()">Regístrate gratis</a>';
  hideAlert(document.getElementById('authAlert'));
}

async function handleAuth(e) {
  e.preventDefault();
  const alertEl = document.getElementById('authAlert');
  hideAlert(alertEl);
  const email = document.getElementById('authEmail').value.trim();
  const password = document.getElementById('authPassword').value;

  if (isRegister) {
    const name = document.getElementById('regName').value.trim();
    const doc = document.getElementById('regDoc').value.trim();
    const phone = document.getElementById('regPhone').value.trim();
    const confirm = document.getElementById('regConfirm').value;
    if (password !== confirm) { showAlert(alertEl, 'Las contraseñas no coinciden', 'error'); return false; }
    const res = await apiFetch('auth/register/', {
      method: 'POST',
      body: JSON.stringify({ correo: email, password, nombre_completo: name, documento: doc, telefono: phone })
    });
    if (res && res.ok) { showAlert(alertEl, '¡Registro exitoso! Ahora puedes iniciar sesión.', 'success'); setTimeout(toggleAuth, 1500); }
    else showAlert(alertEl, res?.data?.detail || res?.data?.password?.[0] || 'Error al registrarse', 'error');
  } else {
    const res = await apiFetch('auth/login/', { method: 'POST', body: JSON.stringify({ correo: email, password }) });
    if (res && res.ok) {
      TOKEN = res.data.access;
      localStorage.setItem('token', TOKEN);
      showToast(`¡Bienvenido! Redirigiendo al panel...`, 'success');
      setTimeout(() => { window.location.href = '/static/dashboard.html'; }, 800);
    } else showAlert(alertEl, res?.data?.detail || 'Credenciales inválidas', 'error');
  }
  return false;
}

function showLogin() {
  document.getElementById('authPage').style.display = '';
  document.getElementById('forgotPage').style.display = 'none';
  if (isRegister) toggleAuth();
}

function showForgotPassword() {
  document.getElementById('authPage').style.display = 'none';
  document.getElementById('forgotPage').style.display = '';
  document.getElementById('forgotForm').style.display = 'block';
  document.getElementById('resetForm').style.display = 'none';
  hideAlert(document.getElementById('forgotAlert'));
}

async function handleForgotPassword(e) {
  e.preventDefault();
  const alertEl = document.getElementById('forgotAlert');
  hideAlert(alertEl);
  await apiFetch('auth/forgot-password/', {
    method: 'POST', body: JSON.stringify({ correo: document.getElementById('forgotEmail').value })
  });
  showAlert(alertEl, 'Si el correo existe, recibirás instrucciones. Revisa tu bandeja de entrada.', 'success');
  document.getElementById('forgotForm').style.display = 'none';
  document.getElementById('resetForm').style.display = 'block';
  return false;
}

async function handleResetPassword(e) {
  e.preventDefault();
  const alertEl = document.getElementById('forgotAlert');
  hideAlert(alertEl);
  const token = document.getElementById('resetToken').value;
  const pass = document.getElementById('resetPassword').value;
  const confirm = document.getElementById('resetConfirm').value;
  if (pass !== confirm) { showAlert(alertEl, 'Las contraseñas no coinciden', 'error'); return false; }
  const res = await apiFetch('auth/reset-password/', { method: 'POST', body: JSON.stringify({ token, password: pass }) });
  if (res && res.ok) {
    showAlert(alertEl, '¡Contraseña actualizada! Redirigiendo al login...', 'success');
    document.getElementById('forgotForm').style.display = 'block';
    document.getElementById('resetForm').style.display = 'none';
    setTimeout(() => { window.location.href = '/static/login.html'; }, 2000);
  } else showAlert(alertEl, res?.data?.detail || 'Error al restablecer', 'error');
  return false;
}

// ─── THEME ───
function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
}

// ─── INIT ───
(function init() {
  initTheme();

  // Si ya tiene token, redirigir al dashboard
  if (TOKEN) {
    try {
      const payload = JSON.parse(atob(TOKEN.split('.')[1]));
      if (payload.exp * 1000 > Date.now()) {
        window.location.href = '/static/dashboard.html';
        return;
      }
    } catch(e) { localStorage.removeItem('token'); }
  }

  // Si viene con ?mode=register, activar modo registro
  const params = new URLSearchParams(window.location.search);
  if (params.get('mode') === 'register' && !isRegister) {
    toggleAuth();
  }
})();
