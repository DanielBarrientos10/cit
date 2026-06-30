// ═══════════════════════════════════════════
//  dashboard.js — Lógica completa del Dashboard
// ═══════════════════════════════════════════

const API = '/api/';
let TOKEN = localStorage.getItem('token') || null;
let USER = null;
let currentSection = null;
let unreadNotifCount = 0;

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
    if (res.status === 401) { showToast('Sesión expirada', 'warning'); logout(); return null; }
    const data = await res.json();
    return { ok: res.ok, status: res.status, data };
  } catch (e) {
    showToast('Error de conexión con el servidor', 'error');
    return null;
  }
}

// ─── SESSION ───
async function checkSession() {
  if (!TOKEN) return false;
  try {
    const payload = JSON.parse(atob(TOKEN.split('.')[1]));
    if (payload.exp * 1000 < Date.now()) { showToast('Sesión expirada', 'warning'); logout(); return false; }
    await loadUser();
    return !!USER;
  } catch { logout(); return false; }
}

async function loadUser() {
  if (!TOKEN) return;
  try {
    const payload = JSON.parse(atob(TOKEN.split('.')[1]));
    const p = await apiFetch(`users/${payload.user_id}/`);
    if (p && p.ok) {
      USER = p.data;
      const name = USER.nombre_completo || 'Usuario';
      const role = USER.id_rol_nombre || '—';
      const initial = name[0].toUpperCase();
      document.getElementById('navName').textContent = name.split(' ')[0];
      document.getElementById('navRole').textContent = role;
      document.getElementById('navAvatar').textContent = initial;
      document.getElementById('sidebarAvatarLg').textContent = initial;
      document.getElementById('sidebarUserName').textContent = name;
      document.getElementById('sidebarUserRole').textContent = role;
    }
  } catch(e) { logout(); }
}

function logout() {
  TOKEN = null; USER = null; currentSection = null;
  localStorage.removeItem('token');
  window.location.href = '/static/login.html';
}

// ─── SIDEBAR CONFIG ───
const sidebarConfig = {
  paciente: [
    { id: 'home',          label: 'Inicio',          icon: 'bi-house-door',       fn: 'renderHome' },
    { id: 'mis-citas',     label: 'Mis Citas',        icon: 'bi-calendar-check',   fn: 'renderMisCitas' },
    { id: 'agendar',       label: 'Agendar Cita',     icon: 'bi-plus-circle',      fn: 'renderAgendar' },
    { id: 'historial',     label: 'Mi Historial',     icon: 'bi-clipboard2-pulse', fn: 'renderHistorial' },
    { id: 'notificaciones',label: 'Notificaciones',   icon: 'bi-bell',             fn: 'renderNotificaciones', badge: true },
    { id: 'perfil',        label: 'Mi Perfil',        icon: 'bi-person',           fn: 'renderPerfil' },
  ],
  medico: [
    { id: 'home',           label: 'Inicio',           icon: 'bi-house-door',       fn: 'renderHome' },
    { id: 'citas-recibidas',label: 'Citas Recibidas',  icon: 'bi-calendar2-week',   fn: 'renderCitasRecibidas' },
    { id: 'mis-horarios',   label: 'Mis Horarios',     icon: 'bi-clock-history',    fn: 'renderMisHorarios' },
    { id: 'mis-especialidades',label:'Mis Especialidades',icon:'bi-heart-pulse',     fn: 'renderMisEspecialidades' },
    { id: 'notificaciones', label: 'Notificaciones',   icon: 'bi-bell',             fn: 'renderNotificaciones', badge: true },
    { id: 'perfil',         label: 'Mi Perfil',        icon: 'bi-person',           fn: 'renderPerfil' },
  ],
  admin: [
    { id: 'home',           label: 'Inicio',           icon: 'bi-house-door',       fn: 'renderHome' },
    { id: 'usuarios',       label: 'Usuarios',         icon: 'bi-people',           fn: 'renderAdminUsuarios' },
    { id: 'medicos',        label: 'Médicos',          icon: 'bi-hospital',         fn: 'renderAdminMedicos' },
    { id: 'especialidades', label: 'Especialidades',   icon: 'bi-heart-pulse',      fn: 'renderAdminEspecialidades' },
    { id: 'reportes',       label: 'Reportes',         icon: 'bi-bar-chart-line',   fn: 'renderAdminReportes' },
    { id: 'notificaciones', label: 'Notificaciones',   icon: 'bi-bell',             fn: 'renderNotificaciones', badge: true },
    { id: 'perfil',         label: 'Mi Perfil',        icon: 'bi-person',           fn: 'renderPerfil' },
  ]
};

function buildSidebar() {
  const role = USER?.id_rol_nombre;
  const links = sidebarConfig[role] || [];
  const container = document.getElementById('sidebarLinks');
  container.innerHTML = links.map(l =>
    `<a class="sidebar-link" href="#" data-section="${l.id}" onclick="navigateTo('${l.id}','${l.fn}');return false;">
      <i class="bi ${l.icon}"></i>${l.label}
      ${l.badge ? `<span class="notif-badge" id="notifBadge" style="position:relative;top:unset;right:unset;display:none;margin-left:auto;border:none">${unreadNotifCount}</span>` : ''}
    </a>`
  ).join('');
}

function navigateTo(id, fn) {
  document.querySelectorAll('#sidebarLinks .sidebar-link').forEach(l => l.classList.remove('active'));
  document.querySelector(`#sidebarLinks [data-section="${id}"]`)?.classList.add('active');
  closeSidebar();
  currentSection = id;
  if (window[fn]) window[fn]();
}

function openSidebar() {
  document.getElementById('sidebar').classList.add('show');
  document.getElementById('sidebarOverlay').classList.add('show');
}

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('show');
  document.getElementById('sidebarOverlay').classList.remove('show');
}

// ─── DASHBOARD INIT ───
function showDashboard() {
  document.getElementById('navUser').style.cssText = 'display:flex !important';
  document.getElementById('sidebar').style.display = '';
  document.getElementById('mainContent').classList.remove('no-sidebar');
  buildSidebar();
  refreshNotifBadge();
  const first = sidebarConfig[USER?.id_rol_nombre]?.[0];
  if (first) navigateTo(first.id, first.fn);
}

// ─── NOTIFICATION BADGE ───
async function refreshNotifBadge() {
  const res = await apiFetch('notificaciones/?leida=false');
  if (res?.ok) {
    unreadNotifCount = res.data.length;
    const badge = document.getElementById('notifBadge');
    if (badge) {
      badge.textContent = unreadNotifCount;
      badge.style.display = unreadNotifCount > 0 ? '' : 'none';
    }
  }
}

// ─── THEME ───
function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  const icon = document.querySelector('#themeToggleBtn i');
  if (icon) icon.className = next === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
}

// ─── HELPERS ───
function formatDate(d) {
  if (!d) return '—';
  return new Date(d + (d.includes('T') ? '' : 'T00:00:00')).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatTime(t) {
  if (!t) return '—';
  return t.substring(0, 5);
}

function estadoBadge(estado) {
  return `<span class="badge-status badge-${estado}">${estado}</span>`;
}

function showConfirm(title, body, onConfirm) {
  document.getElementById('confirmModalLabel').textContent = title;
  document.getElementById('confirmModalBody').innerHTML = body;
  const btn = document.getElementById('confirmModalBtn');
  const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('confirmModal'));
  btn.onclick = () => { modal.hide(); onConfirm(); };
  modal.show();
}

// ═══════════════════════════════════════════
//  VIEWS
// ═══════════════════════════════════════════

function setPage(html) {
  document.getElementById('dashboardPages').innerHTML = `<div class="section-page active">${html}</div>`;
}

// ─── HOME ───
async function renderHome() {
  setPage(`<div class="loading-container"><div class="spinner-border"></div><span>Cargando datos...</span></div>`);
  const role = USER?.id_rol_nombre;
  const res = await apiFetch('citas/');
  const citas = res?.ok ? res.data : [];
  const pendientes = citas.filter(c => c.estado_nombre === 'pendiente');
  const realizadas = citas.filter(c => c.estado_nombre === 'realizada');
  const canceladas = citas.filter(c => c.estado_nombre === 'cancelada');

  let extraStats = '';
  if (role === 'admin') {
    const [resU, resM] = await Promise.all([apiFetch('users/'), apiFetch('medicos/')]);
    extraStats = `
      <div class="stat-card cyan">
        <div class="stat-icon cyan"><i class="bi bi-people-fill"></i></div>
        <div class="stat-info"><div class="stat-number">${resU?.ok ? resU.data.length : '—'}</div><div class="stat-label">Usuarios</div></div>
      </div>
      <div class="stat-card blue">
        <div class="stat-icon blue"><i class="bi bi-hospital"></i></div>
        <div class="stat-info"><div class="stat-number">${resM?.ok ? resM.data.length : '—'}</div><div class="stat-label">Médicos</div></div>
      </div>`;
  }

  const upcoming = role === 'paciente'
    ? citas.filter(c => c.estado_nombre === 'pendiente').slice(0, 5)
    : role === 'medico'
    ? citas.filter(c => c.estado_nombre === 'pendiente').slice(0, 5)
    : [];

  setPage(`
    <div class="page-header">
      <h1 class="page-title"><i class="bi bi-speedometer2"></i>Panel de Control</h1>
      <span style="font-size:.82rem;color:var(--text-muted)">Bienvenido, <strong>${USER?.nombre_completo?.split(' ')[0]}</strong></span>
    </div>
    <div class="stats-grid">
      <div class="stat-card blue">
        <div class="stat-icon blue"><i class="bi bi-calendar-check-fill"></i></div>
        <div class="stat-info"><div class="stat-number">${citas.length}</div><div class="stat-label">Total Citas</div></div>
      </div>
      <div class="stat-card orange">
        <div class="stat-icon orange"><i class="bi bi-hourglass-split"></i></div>
        <div class="stat-info"><div class="stat-number">${pendientes.length}</div><div class="stat-label">Pendientes</div></div>
      </div>
      <div class="stat-card green">
        <div class="stat-icon green"><i class="bi bi-check-circle-fill"></i></div>
        <div class="stat-info"><div class="stat-number">${realizadas.length}</div><div class="stat-label">Realizadas</div></div>
      </div>
      <div class="stat-card red">
        <div class="stat-icon red"><i class="bi bi-x-circle-fill"></i></div>
        <div class="stat-info"><div class="stat-number">${canceladas.length}</div><div class="stat-label">Canceladas</div></div>
      </div>
      ${extraStats}
    </div>
    <div class="card-panel">
      <div class="card-panel-header">
        <h2 class="card-panel-title"><i class="bi bi-calendar2-week"></i>${role === 'admin' ? 'Resumen del Sistema' : 'Próximas Citas'}</h2>
        ${role === 'paciente' ? `<button class="btn btn-primary btn-sm" onclick="navigateTo('agendar','renderAgendar')"><i class="bi bi-plus-lg"></i> Agendar</button>` : ''}
      </div>
      <div class="card-panel-body">
        ${upcoming.length === 0
          ? `<div class="empty-state"><i class="bi bi-calendar-x"></i><p>No hay citas programadas</p></div>`
          : `<div class="table-container"><table class="table">
              <thead><tr><th>Fecha</th><th>Hora</th><th>Médico</th><th>Estado</th></tr></thead>
              <tbody>${upcoming.map(c => `<tr>
                <td>${formatDate(c.id_horario?.fecha)}</td>
                <td>${formatTime(c.id_horario?.hora_inicio)}</td>
                <td>${c.medico_nombre || '—'}</td>
                <td>${estadoBadge(c.estado_nombre)}</td>
              </tr>`).join('')}</tbody>
            </table></div>`
        }
      </div>
    </div>
  `);
}

// ─── MIS CITAS (Paciente) ───
async function renderMisCitas() {
  setPage(`<div class="loading-container"><div class="spinner-border"></div><span>Cargando citas...</span></div>`);
  const res = await apiFetch('citas/');
  const citas = res?.ok ? res.data : [];

  setPage(`
    <div class="page-header">
      <h1 class="page-title"><i class="bi bi-calendar-check"></i>Mis Citas</h1>
      <button class="btn btn-primary btn-sm" onclick="navigateTo('agendar','renderAgendar')"><i class="bi bi-plus-lg"></i> Agendar nueva</button>
    </div>
    ${citas.length === 0
      ? `<div class="card-panel"><div class="card-panel-body"><div class="empty-state"><i class="bi bi-calendar-x"></i><p>No tienes citas agendadas</p></div></div></div>`
      : `<div class="card-panel"><div class="card-panel-body"><div class="table-container"><table class="table">
          <thead><tr><th>ID</th><th>Fecha</th><th>Hora</th><th>Médico</th><th>Motivo</th><th>Estado</th><th>Acciones</th></tr></thead>
          <tbody>${citas.map(c => `<tr>
            <td>#${c.id_cita}</td>
            <td>${formatDate(c.id_horario?.fecha)}</td>
            <td>${formatTime(c.id_horario?.hora_inicio)} - ${formatTime(c.id_horario?.hora_fin)}</td>
            <td>${c.medico_nombre || '—'}</td>
            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${c.motivo || '—'}</td>
            <td>${estadoBadge(c.estado_nombre)}</td>
            <td>${c.estado_nombre === 'pendiente' ? `<button class="btn btn-danger btn-sm" onclick="cancelarCita(${c.id_cita})"><i class="bi bi-x-lg"></i></button>` : ''}</td>
          </tr>`).join('')}</tbody>
        </table></div></div></div>`
    }
  `);
}

async function cancelarCita(id) {
  showConfirm('Cancelar Cita', '<p>¿Estás seguro de que deseas cancelar esta cita?</p><p style="font-size:.8rem;color:var(--text-muted)">Debe ser con al menos 24 horas de anticipación.</p>', async () => {
    const res = await apiFetch(`citas/${id}/cancelar/`, { method: 'PUT' });
    if (res?.ok) {
      showToast('Cita cancelada exitosamente', 'success');
      renderMisCitas();
    } else {
      showToast(res?.data?.detail || 'No se pudo cancelar la cita', 'error');
    }
  });
}

// ─── AGENDAR CITA (Wizard 4 pasos) ───
let agendarState = { step: 1, especialidad: null, medico: null, horario: null, motivo: '' };

async function renderAgendar() {
  agendarState = { step: 1, especialidad: null, medico: null, horario: null, motivo: '' };
  renderAgendarStep();
}

function renderAgendarWizard() {
  const steps = [
    { n: 1, label: 'Especialidad' },
    { n: 2, label: 'Médico' },
    { n: 3, label: 'Horario' },
    { n: 4, label: 'Confirmar' }
  ];
  return `<div class="wizard-steps">${steps.map((s, i) => `
    <div class="wizard-step ${agendarState.step === s.n ? 'active' : agendarState.step > s.n ? 'completed' : ''}">
      <div class="wizard-step-number">${agendarState.step > s.n ? '<i class="bi bi-check-lg"></i>' : s.n}</div>
      <span class="wizard-step-label">${s.label}</span>
    </div>
    ${i < steps.length - 1 ? `<div class="wizard-connector ${agendarState.step > s.n ? 'completed' : ''}"></div>` : ''}
  `).join('')}</div>`;
}

async function renderAgendarStep() {
  const wizard = renderAgendarWizard();

  if (agendarState.step === 1) {
    setPage(`<div class="page-header"><h1 class="page-title"><i class="bi bi-plus-circle"></i>Agendar Cita</h1></div>${wizard}
      <div class="card-panel"><div class="card-panel-header"><h2 class="card-panel-title"><i class="bi bi-heart-pulse"></i>Selecciona Especialidad</h2></div>
      <div class="card-panel-body" id="agendarContent"><div class="loading-container"><div class="spinner-border"></div></div></div></div>`);
    const res = await apiFetch('especialidades/');
    const esp = res?.ok ? res.data : [];
    document.getElementById('agendarContent').innerHTML = `<div class="row g-3">${esp.map(e =>
      `<div class="col-6 col-md-4 col-lg-3">
        <div class="esp-showcase-card" style="cursor:pointer" onclick="selectEspecialidad(${e.id_especialidad},'${e.nombre}')">
          <div class="esp-showcase-icon"><i class="bi bi-heart-pulse"></i></div>
          <div class="esp-showcase-name">${e.nombre}</div>
        </div>
      </div>`
    ).join('')}</div>`;
  }
}

function selectEspecialidad(id, nombre) {
  agendarState.especialidad = { id, nombre };
  agendarState.step = 2;
  renderAgendarMedicos();
}

async function renderAgendarMedicos() {
  const wizard = renderAgendarWizard();
  setPage(`<div class="page-header"><h1 class="page-title"><i class="bi bi-plus-circle"></i>Agendar Cita</h1></div>${wizard}
    <div class="card-panel"><div class="card-panel-header"><h2 class="card-panel-title"><i class="bi bi-hospital"></i>Selecciona Médico — ${agendarState.especialidad.nombre}</h2></div>
    <div class="card-panel-body" id="agendarContent"><div class="loading-container"><div class="spinner-border"></div></div></div></div>`);
  const res = await apiFetch(`buscar/disponibilidad/?especialidad=${agendarState.especialidad.id}`);
  const slots = res?.ok ? res.data : [];
  const medicosMap = {};
  slots.forEach(s => {
    const key = s.id_medico;
    if (!medicosMap[key]) medicosMap[key] = { id: s.id_medico, nombre: s.medico_nombre, count: 0 };
    medicosMap[key].count++;
  });
  const medicos = Object.values(medicosMap);
  document.getElementById('agendarContent').innerHTML = medicos.length === 0
    ? `<div class="empty-state"><i class="bi bi-person-x"></i><p>No hay médicos disponibles para esta especialidad</p></div>`
    : `<div class="row g-3">${medicos.map(m =>
      `<div class="col-md-4 col-lg-3">
        <div class="card-panel" style="cursor:pointer;transition:all .2s" onclick="selectMedico(${m.id},'${m.nombre.replace(/'/g,"\\'")}')"
             onmouseover="this.style.transform='translateY(-3px)';this.style.boxShadow='var(--shadow-md)'"
             onmouseout="this.style.transform='';this.style.boxShadow=''">
          <div class="card-panel-body text-center" style="padding:1.5rem">
            <div style="width:50px;height:50px;border-radius:14px;background:var(--primary-light);color:var(--primary);display:flex;align-items:center;justify-content:center;font-size:1.3rem;margin:0 auto .75rem">
              <i class="bi bi-person-badge"></i>
            </div>
            <div style="font-weight:700;font-size:.9rem">${m.nombre}</div>
            <div style="font-size:.78rem;color:var(--text-muted)">${m.count} horarios disponibles</div>
          </div>
        </div>
      </div>`
    ).join('')}</div>`;
}

function selectMedico(id, nombre) {
  agendarState.medico = { id, nombre };
  agendarState.step = 3;
  renderAgendarHorarios();
}

async function renderAgendarHorarios() {
  const wizard = renderAgendarWizard();
  setPage(`<div class="page-header"><h1 class="page-title"><i class="bi bi-plus-circle"></i>Agendar Cita</h1></div>${wizard}
    <div class="card-panel"><div class="card-panel-header"><h2 class="card-panel-title"><i class="bi bi-clock"></i>Selecciona Horario — Dr. ${agendarState.medico.nombre}</h2></div>
    <div class="card-panel-body" id="agendarContent"><div class="loading-container"><div class="spinner-border"></div></div></div></div>`);
  const res = await apiFetch(`buscar/disponibilidad/?medico=${agendarState.medico.id}`);
  const slots = res?.ok ? res.data : [];
  const byDate = {};
  slots.forEach(s => {
    if (!byDate[s.fecha]) byDate[s.fecha] = [];
    byDate[s.fecha].push(s);
  });
  const dates = Object.keys(byDate).sort();
  document.getElementById('agendarContent').innerHTML = dates.length === 0
    ? `<div class="empty-state"><i class="bi bi-clock-history"></i><p>No hay horarios disponibles</p></div>`
    : dates.map(fecha => `
      <div style="margin-bottom:1.5rem">
        <h6 style="font-weight:700;color:var(--text-muted);margin-bottom:.5rem"><i class="bi bi-calendar3 me-1"></i>${formatDate(fecha)}</h6>
        <div class="slots-grid">${byDate[fecha].map(s =>
          `<button class="slot-btn" onclick="selectHorario(${s.id_horario},'${fecha}','${s.hora_inicio}','${s.hora_fin}')">${formatTime(s.hora_inicio)} - ${formatTime(s.hora_fin)}</button>`
        ).join('')}</div>
      </div>
    `).join('');
}

function selectHorario(id, fecha, hora_inicio, hora_fin) {
  agendarState.horario = { id, fecha, hora_inicio, hora_fin };
  agendarState.step = 4;
  renderAgendarConfirm();
}

function renderAgendarConfirm() {
  const wizard = renderAgendarWizard();
  setPage(`<div class="page-header"><h1 class="page-title"><i class="bi bi-plus-circle"></i>Agendar Cita</h1></div>${wizard}
    <div class="card-panel"><div class="card-panel-header"><h2 class="card-panel-title"><i class="bi bi-check-circle"></i>Confirmar Cita</h2></div>
    <div class="card-panel-body">
      <div style="max-width:500px;margin:0 auto">
        <div style="background:var(--primary-light);border-radius:var(--radius-md);padding:1.5rem;margin-bottom:1.5rem">
          <div style="display:grid;gap:.75rem">
            <div><strong>Especialidad:</strong> ${agendarState.especialidad.nombre}</div>
            <div><strong>Médico:</strong> Dr. ${agendarState.medico.nombre}</div>
            <div><strong>Fecha:</strong> ${formatDate(agendarState.horario.fecha)}</div>
            <div><strong>Hora:</strong> ${formatTime(agendarState.horario.hora_inicio)} - ${formatTime(agendarState.horario.hora_fin)}</div>
          </div>
        </div>
        <div class="mb-3">
          <label class="form-label">Motivo de consulta</label>
          <textarea class="form-control" id="agendarMotivo" rows="3" placeholder="Describe brevemente el motivo de tu consulta..." required></textarea>
        </div>
        <div class="d-flex gap-2 justify-content-end">
          <button class="btn btn-outline-secondary" onclick="agendarState.step=3;renderAgendarHorarios()"><i class="bi bi-arrow-left"></i> Volver</button>
          <button class="btn btn-primary" onclick="confirmarCita()"><i class="bi bi-check-lg"></i> Confirmar Cita</button>
        </div>
      </div>
    </div></div>`);
}

async function confirmarCita() {
  const motivo = document.getElementById('agendarMotivo')?.value.trim();
  if (!motivo) { showToast('Ingresa el motivo de la consulta', 'warning'); return; }
  const res = await apiFetch('citas/', {
    method: 'POST',
    body: JSON.stringify({ id_horario: agendarState.horario.id, motivo })
  });
  if (res?.ok) {
    showToast('¡Cita agendada exitosamente!', 'success');
    navigateTo('mis-citas', 'renderMisCitas');
  } else {
    showToast(res?.data?.detail || 'No se pudo agendar la cita', 'error');
  }
}

// ─── HISTORIAL CLÍNICO (Paciente) ───
async function renderHistorial() {
  setPage(`<div class="loading-container"><div class="spinner-border"></div><span>Cargando historial...</span></div>`);
  const res = await apiFetch('historial/');
  const registros = res?.ok ? res.data : [];

  setPage(`
    <div class="page-header"><h1 class="page-title"><i class="bi bi-clipboard2-pulse"></i>Mi Historial Clínico</h1></div>
    ${registros.length === 0
      ? `<div class="card-panel"><div class="card-panel-body"><div class="empty-state"><i class="bi bi-clipboard-x"></i><p>No hay registros en tu historial</p></div></div></div>`
      : registros.map(r => `
        <div class="card-panel" style="margin-bottom:1rem">
          <div class="card-panel-header">
            <h2 class="card-panel-title"><i class="bi bi-calendar3"></i>${formatDate(r.fecha)}</h2>
            <span style="font-size:.82rem;color:var(--text-muted)">Dr. ${r.id_medico?.usuario_info?.nombre || '—'}</span>
          </div>
          <div class="card-panel-body">
            <div style="margin-bottom:.75rem"><strong>Diagnóstico:</strong> ${r.diagnostico}</div>
            ${r.tratamiento ? `<div style="margin-bottom:.75rem"><strong>Tratamiento:</strong> ${r.tratamiento}</div>` : ''}
            ${r.notas ? `<div><strong>Notas:</strong> ${r.notas}</div>` : ''}
          </div>
        </div>
      `).join('')
    }
  `);
}

// ─── NOTIFICACIONES ───
async function renderNotificaciones() {
  setPage(`<div class="loading-container"><div class="spinner-border"></div><span>Cargando notificaciones...</span></div>`);
  const res = await apiFetch('notificaciones/');
  const notifs = res?.ok ? res.data : [];

  setPage(`
    <div class="page-header"><h1 class="page-title"><i class="bi bi-bell"></i>Notificaciones</h1></div>
    ${notifs.length === 0
      ? `<div class="card-panel"><div class="card-panel-body"><div class="empty-state"><i class="bi bi-bell-slash"></i><p>No tienes notificaciones</p></div></div></div>`
      : notifs.map(n => `
        <div class="card-panel" style="margin-bottom:.75rem;${n.leida ? 'opacity:.6' : ''}">
          <div class="card-panel-body" style="display:flex;align-items:center;gap:1rem;padding:1rem 1.25rem">
            <div style="width:40px;height:40px;border-radius:12px;background:${n.leida ? 'var(--bg)' : 'var(--primary-light)'};color:${n.leida ? 'var(--muted)' : 'var(--primary)'};display:flex;align-items:center;justify-content:center;flex-shrink:0">
              <i class="bi ${n.leida ? 'bi-bell' : 'bi-bell-fill'}"></i>
            </div>
            <div style="flex:1">
              <div style="font-size:.88rem;font-weight:${n.leida ? '400' : '600'}">${n.mensaje}</div>
              <div style="font-size:.75rem;color:var(--text-muted);margin-top:.2rem">${new Date(n.created_at).toLocaleString('es-CO')}</div>
            </div>
            ${!n.leida ? `<button class="btn btn-outline-primary btn-sm" onclick="marcarLeida(${n.id_notificacion})"><i class="bi bi-check-lg"></i></button>` : ''}
          </div>
        </div>
      `).join('')
    }
  `);
}

async function marcarLeida(id) {
  await apiFetch(`notificaciones/${id}/leer/`, { method: 'PUT' });
  refreshNotifBadge();
  renderNotificaciones();
}

// ─── PERFIL ───
async function renderPerfil() {
  setPage(`<div class="loading-container"><div class="spinner-border"></div><span>Cargando perfil...</span></div>`);
  const res = await apiFetch(`users/${USER.id_usuario}/`);
  const u = res?.ok ? res.data : USER;

  setPage(`
    <div class="page-header"><h1 class="page-title"><i class="bi bi-person"></i>Mi Perfil</h1></div>
    <div class="card-panel">
      <div class="card-panel-body">
        <div class="profile-header">
          <div class="profile-avatar">${(u.nombre_completo || 'U')[0]}</div>
          <div class="profile-info">
            <h3>${u.nombre_completo}</h3>
            <p><i class="bi bi-envelope me-1"></i>${u.correo} · <i class="bi bi-person-badge me-1"></i>${u.id_rol_nombre}</p>
          </div>
        </div>
        <form onsubmit="return guardarPerfil(event)">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Nombre completo</label>
              <input type="text" class="form-control" id="perfilNombre" value="${u.nombre_completo || ''}">
            </div>
            <div class="col-md-6">
              <label class="form-label">Correo electrónico</label>
              <input type="email" class="form-control" value="${u.correo || ''}" disabled>
            </div>
            <div class="col-md-6">
              <label class="form-label">Documento</label>
              <input type="text" class="form-control" value="${u.documento || ''}" disabled>
            </div>
            <div class="col-md-6">
              <label class="form-label">Teléfono</label>
              <input type="text" class="form-control" id="perfilTelefono" value="${u.telefono || ''}">
            </div>
          </div>
          <div class="mt-4">
            <button type="submit" class="btn btn-primary"><i class="bi bi-check-lg me-1"></i>Guardar cambios</button>
          </div>
        </form>
      </div>
    </div>
  `);
}

async function guardarPerfil(e) {
  e.preventDefault();
  const res = await apiFetch(`users/${USER.id_usuario}/`, {
    method: 'PUT',
    body: JSON.stringify({
      nombre_completo: document.getElementById('perfilNombre').value,
      telefono: document.getElementById('perfilTelefono').value
    })
  });
  if (res?.ok) {
    showToast('Perfil actualizado', 'success');
    await loadUser();
    renderPerfil();
  } else {
    showToast('No se pudo actualizar el perfil', 'error');
  }
}

// ═══════════════════════════════════════════
//  MÉDICO VIEWS
// ═══════════════════════════════════════════

async function renderCitasRecibidas() {
  setPage(`<div class="loading-container"><div class="spinner-border"></div><span>Cargando citas...</span></div>`);
  const res = await apiFetch('citas/');
  const citas = res?.ok ? res.data : [];

  setPage(`
    <div class="page-header"><h1 class="page-title"><i class="bi bi-calendar2-week"></i>Citas Recibidas</h1></div>
    ${citas.length === 0
      ? `<div class="card-panel"><div class="card-panel-body"><div class="empty-state"><i class="bi bi-calendar-x"></i><p>No tienes citas asignadas</p></div></div></div>`
      : `<div class="card-panel"><div class="card-panel-body"><div class="table-container"><table class="table">
          <thead><tr><th>ID</th><th>Fecha</th><th>Hora</th><th>Paciente</th><th>Motivo</th><th>Estado</th><th>Acciones</th></tr></thead>
          <tbody>${citas.map(c => `<tr>
            <td>#${c.id_cita}</td>
            <td>${formatDate(c.id_horario?.fecha)}</td>
            <td>${formatTime(c.id_horario?.hora_inicio)} - ${formatTime(c.id_horario?.hora_fin)}</td>
            <td>${c.paciente_nombre || '—'}</td>
            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${c.motivo || '—'}</td>
            <td>${estadoBadge(c.estado_nombre)}</td>
            <td>${c.estado_nombre === 'pendiente' ? `
              <button class="btn btn-success btn-sm" onclick="marcarCita(${c.id_cita},'realizada')" title="Marcar realizada"><i class="bi bi-check-lg"></i></button>
              <button class="btn btn-outline-secondary btn-sm" onclick="marcarCita(${c.id_cita},'no-asistio')" title="No asistió"><i class="bi bi-person-x"></i></button>
            ` : ''}</td>
          </tr>`).join('')}</tbody>
        </table></div></div></div>`
    }
  `);
}

async function marcarCita(id, action) {
  const label = action === 'realizada' ? 'realizada' : 'no asistió';
  showConfirm(`Marcar como ${label}`, `<p>¿Confirmar que el paciente ${label}?</p>`, async () => {
    const res = await apiFetch(`citas/${id}/${action}/`, { method: 'PUT' });
    if (res?.ok) {
      showToast(`Cita marcada como ${label}`, 'success');
      renderCitasRecibidas();
    } else {
      showToast(res?.data?.detail || 'Error al actualizar', 'error');
    }
  });
}

// ─── MIS HORARIOS (Médico) ───
async function renderMisHorarios() {
  setPage(`<div class="loading-container"><div class="spinner-border"></div><span>Cargando horarios...</span></div>`);
  const payload = JSON.parse(atob(TOKEN.split('.')[1]));
  const res = await apiFetch(`horarios/?id_medico=${payload.user_id}`);
  const horarios = res?.ok ? res.data : [];

  setPage(`
    <div class="page-header">
      <h1 class="page-title"><i class="bi bi-clock-history"></i>Mis Horarios</h1>
      <button class="btn btn-primary btn-sm" onclick="showCrearSlotsModal()"><i class="bi bi-plus-lg"></i> Crear Slots</button>
    </div>
    ${horarios.length === 0
      ? `<div class="card-panel"><div class="card-panel-body"><div class="empty-state"><i class="bi bi-clock"></i><p>No tienes horarios creados</p></div></div></div>`
      : `<div class="card-panel"><div class="card-panel-body"><div class="table-container"><table class="table">
          <thead><tr><th>Fecha</th><th>Hora Inicio</th><th>Hora Fin</th><th>Disponible</th></tr></thead>
          <tbody>${horarios.map(h => `<tr>
            <td>${formatDate(h.fecha)}</td>
            <td>${formatTime(h.hora_inicio)}</td>
            <td>${formatTime(h.hora_fin)}</td>
            <td>${h.disponible ? '<span class="badge-status badge-activo">Disponible</span>' : '<span class="badge-status badge-cancelada">Ocupado</span>'}</td>
          </tr>`).join('')}</tbody>
        </table></div></div></div>`
    }
  `);
}

function showCrearSlotsModal() {
  showConfirm('Crear Horarios', `
    <div>
      <div class="mb-3"><label class="form-label">Fecha</label><input type="date" class="form-control" id="slotFecha"></div>
      <div class="row g-2 mb-3">
        <div class="col"><label class="form-label">Hora inicio</label><input type="time" class="form-control" id="slotInicio" value="08:00"></div>
        <div class="col"><label class="form-label">Hora fin</label><input type="time" class="form-control" id="slotFin" value="12:00"></div>
      </div>
      <div class="mb-3"><label class="form-label">Duración (minutos)</label><input type="number" class="form-control" id="slotDuracion" value="30" min="15" max="120"></div>
    </div>
  `, crearSlots);
}

async function crearSlots() {
  const payload = JSON.parse(atob(TOKEN.split('.')[1]));
  const res = await apiFetch('horarios/crear-slots/', {
    method: 'POST',
    body: JSON.stringify({
      id_medico: payload.user_id,
      fecha: document.getElementById('slotFecha').value,
      hora_inicio: document.getElementById('slotInicio').value,
      hora_fin: document.getElementById('slotFin').value,
      duracion_minutos: parseInt(document.getElementById('slotDuracion').value)
    })
  });
  if (res?.ok) {
    showToast(`${res.data.slots_creados} slots creados`, 'success');
    renderMisHorarios();
  } else {
    showToast(res?.data?.detail || 'Error al crear slots', 'error');
  }
}

// ─── MIS ESPECIALIDADES (Médico) ───
async function renderMisEspecialidades() {
  setPage(`<div class="loading-container"><div class="spinner-border"></div><span>Cargando especialidades...</span></div>`);
  const payload = JSON.parse(atob(TOKEN.split('.')[1]));
  const res = await apiFetch(`medicos/${payload.user_id}/especialidades/`);
  const especialidades = res?.ok ? res.data : [];

  setPage(`
    <div class="page-header"><h1 class="page-title"><i class="bi bi-heart-pulse"></i>Mis Especialidades</h1></div>
    ${especialidades.length === 0
      ? `<div class="card-panel"><div class="card-panel-body"><div class="empty-state"><i class="bi bi-heart"></i><p>No tienes especialidades asignadas</p></div></div></div>`
      : `<div class="row g-3">${especialidades.map(e =>
        `<div class="col-6 col-md-4 col-lg-3">
          <div class="card-panel">
            <div class="card-panel-body text-center" style="padding:1.5rem">
              <div style="width:50px;height:50px;border-radius:14px;background:var(--primary-light);color:var(--primary);display:flex;align-items:center;justify-content:center;font-size:1.3rem;margin:0 auto .75rem">
                <i class="bi bi-heart-pulse"></i>
              </div>
              <div style="font-weight:700">${e.nombre}</div>
            </div>
          </div>
        </div>`
      ).join('')}</div>`
    }
  `);
}

// ═══════════════════════════════════════════
//  ADMIN VIEWS
// ═══════════════════════════════════════════

async function renderAdminUsuarios() {
  setPage(`<div class="loading-container"><div class="spinner-border"></div><span>Cargando usuarios...</span></div>`);
  const res = await apiFetch('users/');
  const usuarios = res?.ok ? res.data : [];

  setPage(`
    <div class="page-header"><h1 class="page-title"><i class="bi bi-people"></i>Gestión de Usuarios</h1></div>
    <div class="card-panel"><div class="card-panel-body"><div class="table-container"><table class="table">
      <thead><tr><th>ID</th><th>Nombre</th><th>Correo</th><th>Documento</th><th>Rol</th><th>Estado</th><th>Acciones</th></tr></thead>
      <tbody>${usuarios.map(u => `<tr>
        <td>#${u.id_usuario}</td>
        <td>${u.nombre_completo}</td>
        <td>${u.correo}</td>
        <td>${u.documento}</td>
        <td>${u.id_rol_nombre}</td>
        <td>${u.activo ? '<span class="badge-status badge-activo">Activo</span>' : '<span class="badge-status badge-inactivo">Inactivo</span>'}</td>
        <td><button class="btn btn-outline-secondary btn-sm" onclick="toggleUsuario(${u.id_usuario})" title="${u.activo ? 'Desactivar' : 'Activar'}">
          <i class="bi bi-${u.activo ? 'person-dash' : 'person-check'}"></i>
        </button></td>
      </tr>`).join('')}</tbody>
    </table></div></div></div>
  `);
}

async function toggleUsuario(id) {
  showConfirm('Cambiar estado', '<p>¿Cambiar el estado de este usuario?</p>', async () => {
    const res = await apiFetch(`admin/usuarios/${id}/bloquear/`, { method: 'PUT' });
    if (res?.ok) {
      showToast('Estado actualizado', 'success');
      renderAdminUsuarios();
    } else {
      showToast('Error al cambiar estado', 'error');
    }
  });
}

async function renderAdminMedicos() {
  setPage(`<div class="loading-container"><div class="spinner-border"></div><span>Cargando médicos...</span></div>`);
  const res = await apiFetch('medicos/');
  const medicos = res?.ok ? res.data : [];

  setPage(`
    <div class="page-header">
      <h1 class="page-title"><i class="bi bi-hospital"></i>Gestión de Médicos</h1>
      <button class="btn btn-primary btn-sm" onclick="new bootstrap.Modal(document.getElementById('modalNuevoMedico')).show()"><i class="bi bi-person-plus"></i> Registrar Médico</button>
    </div>
    <div class="card-panel"><div class="card-panel-body"><div class="table-container"><table class="table">
      <thead><tr><th>ID</th><th>Nombre</th><th>Correo</th><th>Registro</th><th>Consultorio</th><th>Estado</th></tr></thead>
      <tbody>${medicos.map(m => `<tr>
        <td>#${m.id_medico}</td>
        <td>${m.usuario_info?.nombre || '—'}</td>
        <td>${m.usuario_info?.correo || '—'}</td>
        <td>${m.registro_profesional}</td>
        <td>${m.consultorio}</td>
        <td>${m.estado === 'activo' ? '<span class="badge-status badge-activo">Activo</span>' : '<span class="badge-status badge-inactivo">Inactivo</span>'}</td>
      </tr>`).join('')}</tbody>
    </table></div></div></div>
  `);
}

async function registrarNuevoMedico(e) {
  e.preventDefault();
  const alertEl = document.getElementById('modalMedicoAlert');
  hideAlert(alertEl);
  const res = await apiFetch('medicos/', {
    method: 'POST',
    body: JSON.stringify({
      usuario: {
        nombre_completo: document.getElementById('nmNombre').value,
        correo: document.getElementById('nmCorreo').value,
        documento: document.getElementById('nmDocumento').value,
        telefono: document.getElementById('nmTelefono').value,
        password: document.getElementById('nmPassword').value
      },
      registro_profesional: document.getElementById('nmRegistro').value,
      consultorio: document.getElementById('nmConsultorio').value
    })
  });
  if (res?.ok) {
    showToast('Médico registrado exitosamente', 'success');
    bootstrap.Modal.getInstance(document.getElementById('modalNuevoMedico')).hide();
    document.getElementById('formNuevoMedico').reset();
    renderAdminMedicos();
  } else {
    showAlert(alertEl, res?.data?.detail || 'Error al registrar médico', 'error');
  }
  return false;
}

async function renderAdminEspecialidades() {
  setPage(`<div class="loading-container"><div class="spinner-border"></div><span>Cargando especialidades...</span></div>`);
  const res = await apiFetch('especialidades/');
  const especialidades = res?.ok ? res.data : [];

  setPage(`
    <div class="page-header">
      <h1 class="page-title"><i class="bi bi-heart-pulse"></i>Especialidades</h1>
      <button class="btn btn-primary btn-sm" onclick="showCrearEspecialidadModal()"><i class="bi bi-plus-lg"></i> Nueva</button>
    </div>
    <div class="row g-3">${especialidades.map(e =>
      `<div class="col-6 col-md-4 col-lg-3">
        <div class="card-panel">
          <div class="card-panel-body text-center" style="padding:1.5rem">
            <div style="width:50px;height:50px;border-radius:14px;background:var(--primary-light);color:var(--primary);display:flex;align-items:center;justify-content:center;font-size:1.3rem;margin:0 auto .75rem">
              <i class="bi bi-heart-pulse"></i>
            </div>
            <div style="font-weight:700">${e.nombre}</div>
          </div>
        </div>
      </div>`
    ).join('')}</div>
  `);
}

function showCrearEspecialidadModal() {
  showConfirm('Nueva Especialidad', `
    <div><label class="form-label">Nombre</label><input type="text" class="form-control" id="nuevaEspecialidad" placeholder="Ej: Cardiología"></div>
  `, async () => {
    const nombre = document.getElementById('nuevaEspecialidad').value.trim();
    if (!nombre) { showToast('Ingresa un nombre', 'warning'); return; }
    const res = await apiFetch('especialidades/', { method: 'POST', body: JSON.stringify({ nombre }) });
    if (res?.ok) {
      showToast('Especialidad creada', 'success');
      renderAdminEspecialidades();
    } else {
      showToast(res?.data?.detail || 'Error al crear', 'error');
    }
  });
}

async function renderAdminReportes() {
  setPage(`<div class="loading-container"><div class="spinner-border"></div><span>Cargando reportes...</span></div>`);
  const [res1, res2, res3] = await Promise.all([
    apiFetch('admin/reportes/?tipo=citas-por-especialidad'),
    apiFetch('admin/reportes/?tipo=cancelaciones'),
    apiFetch('admin/reportes/?tipo=no-asistencia-por-medico')
  ]);

  const porEsp = res1?.ok ? res1.data : [];
  const cancelaciones = res2?.ok ? res2.data : {};
  const noAsist = res3?.ok ? res3.data : [];

  setPage(`
    <div class="page-header"><h1 class="page-title"><i class="bi bi-bar-chart-line"></i>Reportes</h1></div>
    <div class="row g-3 mb-3">
      <div class="col-md-4">
        <div class="stat-card blue"><div class="stat-icon blue"><i class="bi bi-calendar-check"></i></div>
          <div class="stat-info"><div class="stat-number">${cancelaciones.total_citas || 0}</div><div class="stat-label">Total Citas</div></div></div>
      </div>
      <div class="col-md-4">
        <div class="stat-card red"><div class="stat-icon red"><i class="bi bi-x-circle"></i></div>
          <div class="stat-info"><div class="stat-number">${cancelaciones.total_canceladas || 0}</div><div class="stat-label">Canceladas</div></div></div>
      </div>
      <div class="col-md-4">
        <div class="stat-card orange"><div class="stat-icon orange"><i class="bi bi-percent"></i></div>
          <div class="stat-info"><div class="stat-number">${cancelaciones.porcentaje || 0}%</div><div class="stat-label">% Cancelación</div></div></div>
      </div>
    </div>
    <div class="row g-3">
      <div class="col-md-6">
        <div class="card-panel">
          <div class="card-panel-header"><h2 class="card-panel-title"><i class="bi bi-pie-chart"></i>Citas por Especialidad</h2></div>
          <div class="card-panel-body"><div class="chart-container"><canvas id="chartEspecialidad"></canvas></div></div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card-panel">
          <div class="card-panel-header"><h2 class="card-panel-title"><i class="bi bi-person-x"></i>No Asistencia por Médico</h2></div>
          <div class="card-panel-body"><div class="chart-container"><canvas id="chartNoAsistencia"></canvas></div></div>
        </div>
      </div>
    </div>
  `);

  // Charts
  setTimeout(() => {
    if (document.getElementById('chartEspecialidad') && porEsp.length) {
      new Chart(document.getElementById('chartEspecialidad'), {
        type: 'doughnut',
        data: {
          labels: porEsp.map(p => p.medico || 'Sin asignar'),
          datasets: [{ data: porEsp.map(p => p.total), backgroundColor: ['#003A70','#1a6cf6','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#ec4899'] }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { font: { size: 11 } } } } }
      });
    }
    if (document.getElementById('chartNoAsistencia') && noAsist.length) {
      new Chart(document.getElementById('chartNoAsistencia'), {
        type: 'bar',
        data: {
          labels: noAsist.map(n => n.medico || 'Sin asignar'),
          datasets: [{ label: 'No asistencias', data: noAsist.map(n => n.total), backgroundColor: '#ef4444' }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
      });
    }
  }, 100);
}

// ═══════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════

document.getElementById('sidebarToggle')?.addEventListener('click', () => {
  const sidebar = document.getElementById('sidebar');
  if (sidebar.classList.contains('show')) closeSidebar();
  else openSidebar();
});

(async function init() {
  initTheme();
  if (!TOKEN) { window.location.href = '/static/login.html'; return; }
  const valid = await checkSession();
  if (valid) showDashboard();
  else window.location.href = '/static/login.html';
})();
