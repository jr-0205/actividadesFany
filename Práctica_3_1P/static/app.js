const form = document.getElementById('registrationForm');
const ageInput = document.getElementById('age');
const genderSelect = document.getElementById('gender');
const sportSelect = document.getElementById('sportSelect');
const scheduleSelect = document.getElementById('scheduleSelect');
const guardianBlock = document.getElementById('guardianBlock');
const categoryBadge = document.getElementById('categoryBadge');
const sportInfo = document.getElementById('sportInfo');
const formMessage = document.getElementById('formMessage');
const submitButton = document.getElementById('submitButton');
const resultSection = document.getElementById('resultSection');
const recordsBody = document.getElementById('recordsBody');
const refreshButton = document.getElementById('refreshButton');

let sportsCatalog = [];

const money = value => new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(value);

const categoryClasses = ['category-woman', 'category-man', 'category-girl', 'category-boy', 'category-neutral'];

function categoryClass(category) {
  return {
    'Mujer': 'category-woman',
    'Hombre': 'category-man',
    'Niña': 'category-girl',
    'Niño': 'category-boy'
  }[category] || 'category-neutral';
}

function applyCategoryStyle(element, category) {
  if (!element) return;
  element.classList.remove(...categoryClasses);
  element.classList.add(categoryClass(category));
}

function setMessage(message = '', type = 'error') {
  formMessage.textContent = message;
  formMessage.className = message ? `form-message ${type}` : 'form-message hidden';
}

function resetAgents() {
  document.querySelectorAll('.agent-card').forEach(card => {
    card.classList.remove('is-running', 'is-ok', 'is-error');
    card.querySelector('.agent-state').textContent = 'En espera';
  });
}

function renderTrace(trace = []) {
  resetAgents();
  trace.forEach(step => {
    const card = document.querySelector(`.agent-card[data-agent="${CSS.escape(step.agent)}"]`);
    if (!card) return;
    card.classList.remove('is-running', 'is-ok', 'is-error');
    card.classList.add(step.status === 'ok' ? 'is-ok' : 'is-error');
    card.querySelector('.agent-state').textContent = step.status === 'ok' ? 'Correcto' : 'Error';
    card.title = step.message;
  });
}

async function loadCatalog() {
  const age = Number(ageInput.value);
  const gender = genderSelect.value;
  guardianBlock.classList.toggle('hidden', !(age >= 6 && age < 18));
  resultSection.classList.add('hidden');

  if (!age || age < 6 || !gender) {
    categoryBadge.textContent = 'Sin clasificar';
    applyCategoryStyle(categoryBadge, '');
    sportsCatalog = [];
    sportSelect.innerHTML = '<option value="">Primero indica edad y sexo</option>';
    scheduleSelect.innerHTML = '<option value="">Selecciona una disciplina</option>';
    scheduleSelect.disabled = true;
    sportInfo.classList.add('hidden');
    return;
  }

  try {
    const response = await fetch(`/api/catalogo?edad=${encodeURIComponent(age)}&genero=${encodeURIComponent(gender)}`);
    const data = await response.json();
    if (!data.ok) throw new Error(data.error);
    categoryBadge.textContent = data.category;
    applyCategoryStyle(categoryBadge, data.category);
    sportsCatalog = data.sports;
    sportSelect.innerHTML = '<option value="">Selecciona disciplina</option>' + data.sports.map(s => `<option value="${s.id}">${s.name} · ${money(s.monthly_fee)}/mes</option>`).join('');
    scheduleSelect.innerHTML = '<option value="">Selecciona una disciplina</option>';
    scheduleSelect.disabled = true;
    sportInfo.classList.add('hidden');
    setMessage();
  } catch (error) {
    categoryBadge.textContent = 'No disponible';
    applyCategoryStyle(categoryBadge, '');
    sportSelect.innerHTML = '<option value="">Sin opciones</option>';
    setMessage(error.message);
  }
}

async function loadSchedules() {
  const sportId = Number(sportSelect.value);
  const age = Number(ageInput.value);
  const sport = sportsCatalog.find(item => item.id === sportId);
  if (!sportId || !sport) {
    scheduleSelect.disabled = true;
    scheduleSelect.innerHTML = '<option value="">Selecciona una disciplina</option>';
    sportInfo.classList.add('hidden');
    return;
  }

  sportInfo.innerHTML = `<strong>${sport.icon} · ${sport.name}</strong> — ${sport.description}<br>Inscripción: ${money(sport.registration_fee)} · Mensualidad: ${money(sport.monthly_fee)}`;
  sportInfo.classList.remove('hidden');

  const response = await fetch(`/api/horarios?deporte_id=${sportId}&edad=${age}`);
  const data = await response.json();
  if (!data.ok) {
    setMessage(data.error);
    return;
  }
  scheduleSelect.disabled = false;
  scheduleSelect.innerHTML = '<option value="">Selecciona horario</option>' + data.schedules.map(s => `<option value="${s.id}">${s.label} · ${s.days} · ${s.start_time}-${s.end_time} · ${s.available_spots} lugares</option>`).join('');
  if (!data.schedules.length) scheduleSelect.innerHTML = '<option value="">No hay horarios con cupo</option>';
}

function showResult(registration) {
  document.getElementById('resultName').textContent = registration.full_name;
  const resultCategory = document.getElementById('resultCategory');
  resultCategory.textContent = registration.category;
  applyCategoryStyle(resultCategory, registration.category);
  const credential = resultSection.querySelector('.credential');
  credential.classList.remove(...categoryClasses);
  credential.classList.add(categoryClass(registration.category));
  document.getElementById('resultFolio').textContent = registration.folio;
  document.getElementById('resultSport').textContent = registration.sport;
  document.getElementById('resultSchedule').textContent = `${registration.schedule.label} · ${registration.schedule.days} · ${registration.schedule.time}`;
  document.getElementById('resultTotal').textContent = money(registration.costs.total_first_payment);
  document.getElementById('resultCosts').innerHTML = [
    `Inscripción ${money(registration.costs.registration_fee)}`,
    `Mensualidad ${money(registration.costs.monthly_fee)}`,
    `Descuento ${registration.costs.discount_rate}% (-${money(registration.costs.discount)})`
  ].map(text => `<span>${text}</span>`).join('');
  resultSection.classList.remove('hidden');
  resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

async function loadRecords() {
  const response = await fetch('/api/inscripciones');
  const data = await response.json();
  const rows = data.registrations || [];
  recordsBody.innerHTML = rows.length ? rows.map(row => `
    <tr>
      <td>${row.folio}</td><td>${row.full_name}</td><td><span class="table-category ${categoryClass(row.category)}">${row.category}</span></td>
      <td>${row.sport}</td><td>${row.schedule}</td><td>${money(row.total_first_payment)}</td>
    </tr>`).join('') : '<tr><td colspan="6" class="empty-cell">Aún no hay inscripciones registradas.</td></tr>';
}

ageInput.addEventListener('change', loadCatalog);
genderSelect.addEventListener('change', loadCatalog);
sportSelect.addEventListener('change', loadSchedules);
refreshButton.addEventListener('click', loadRecords);

form.addEventListener('submit', async event => {
  event.preventDefault();
  setMessage();
  resetAgents();
  submitButton.disabled = true;
  submitButton.firstElementChild.textContent = 'Coordinando agentes...';
  const coordinatorCard = document.querySelector('.agent-card[data-agent="Coordinador"]');
  coordinatorCard.classList.add('is-running');
  coordinatorCard.querySelector('.agent-state').textContent = 'Procesando';

  const payload = Object.fromEntries(new FormData(form).entries());
  payload.age = Number(payload.age);
  payload.sport_id = Number(payload.sport_id);
  payload.schedule_id = Number(payload.schedule_id);

  try {
    const response = await fetch('/api/inscripciones', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    renderTrace(data.trace);
    if (!data.ok) throw new Error(data.error || 'No fue posible completar la inscripción.');
    showResult(data.registration);
    await loadRecords();
    await loadSchedules();
  } catch (error) {
    setMessage(error.message);
  } finally {
    submitButton.disabled = false;
    submitButton.firstElementChild.textContent = 'Procesar con agentes';
  }
});

loadRecords();
