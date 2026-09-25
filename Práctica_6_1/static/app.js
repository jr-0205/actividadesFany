const $ = (selector) => document.querySelector(selector);

let currentAccount = localStorage.getItem("bancoflow_active_account") || "1002003001";
let availableAccounts = [];

const money = (value) =>
  new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" }).format(Number(value || 0));

const shortDate = (value) => {
  if (!value) return "—";
  const parts = value.slice(0, 10).split("-").map(Number);
  return new Intl.DateTimeFormat("es-MX", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  }).format(new Date(parts[0], parts[1] - 1, parts[2]));
};

const typeLabel = {
  DEPOSITO: "Depósito",
  RETIRO: "Retiro",
  TRANSFERENCIA_SALIDA: "Transferencia enviada",
  TRANSFERENCIA_ENTRADA: "Transferencia recibida",
  PAGO_TARJETA: "Pago de tarjeta"
};

function toast(message, error) {
  const el = $("#toast");
  el.textContent = message;
  el.classList.toggle("error", Boolean(error));
  el.classList.remove("hidden");
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => el.classList.add("hidden"), 3600);
}

async function request(url, options) {
  const response = await fetch(url, Object.assign({
    headers: { "Content-Type": "application/json" }
  }, options || {}));
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || data.message || "No se pudo completar la operación.");
  }
  return data;
}

function initials(name) {
  return String(name || "")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((word) => word.charAt(0).toUpperCase())
    .join("");
}

function renderTrace(trace) {
  const list = $("#traceList");
  const rows = trace || [];
  if (!rows.length) {
    list.innerHTML = '<div class="empty-state">Realiza una operación para ver la trazabilidad.</div>';
    return;
  }

  list.innerHTML = rows.map((step) =>
    '<div class="trace-step"><strong>' +
    step.agent +
    '</strong><span>' +
    step.message +
    '</span></div>'
  ).join("");
}

function renderTransactions(rows) {
  const body = $("#transactionsBody");
  if (!rows || !rows.length) {
    body.innerHTML = '<tr><td colspan="5" class="empty-state">No hay movimientos registrados.</td></tr>';
    return;
  }

  body.innerHTML = rows.map((row) => {
    const incoming =
      row.type === "DEPOSITO" ||
      row.type === "TRANSFERENCIA_ENTRADA";
    const sign = incoming ? "+" : "-";
    const amountClass = incoming ? "amount-positive" : "amount-negative";

    return '<tr>' +
      '<td>' + (typeLabel[row.type] || row.type) + '</td>' +
      '<td>' + row.description + '</td>' +
      '<td class="' + amountClass + '">' + sign + money(row.amount) + '</td>' +
      '<td>' + (row.related_account || "—") + '</td>' +
      '<td>' + shortDate(row.created_at) + '</td>' +
      '</tr>';
  }).join("");
}

function renderLoans(rows) {
  const list = $("#loansList");
  if (!rows || !rows.length) {
    list.innerHTML = '<div class="empty-state">Aún no hay préstamos registrados.</div>';
    return;
  }

  list.innerHTML = rows.map((row) =>
    '<div class="mini-item"><div><strong>' +
    row.loan_type.toUpperCase() +
    ' · ' +
    money(row.amount) +
    '</strong><p>' +
    row.months +
    ' meses · Tasa ' +
    Number(row.annual_rate).toFixed(1) +
    '% anual</p></div><span>' +
    money(row.monthly_payment) +
    '/mes</span></div>'
  ).join("");
}

function renderInsurance(rows) {
  const list = $("#insuranceList");
  if (!rows || !rows.length) {
    list.innerHTML = '<div class="empty-state">Aún no hay seguros contratados.</div>';
    return;
  }

  list.innerHTML = rows.map((row) =>
    '<div class="mini-item"><div><strong>' +
    row.insurance_type.replaceAll("_", " ").toUpperCase() +
    '</strong><p>' +
    row.coverage +
    '</p></div><span>' +
    money(row.monthly_premium) +
    '/mes</span></div>'
  ).join("");
}

function renderTransferTargets(rows) {
  const select = $("#targetAccount");

  if (!rows || !rows.length) {
    select.innerHTML = '<option value="">Sin cuentas destino</option>';
    return;
  }

  select.innerHTML = rows.map((row) =>
    '<option value="' +
    row.account_number +
    '">' +
    row.account_number +
    ' · ' +
    row.full_name +
    ' · saldo ' +
    money(row.balance) +
    '</option>'
  ).join("");
}

function updateSwitchButton() {
  const button = $("#switchAccountButton");
  if (!button || availableAccounts.length < 2) {
    if (button) button.disabled = true;
    return;
  }

  const index = availableAccounts.findIndex(
    (item) => item.account_number === currentAccount
  );
  const next = availableAccounts[(index + 1) % availableAccounts.length];
  button.disabled = false;
  button.querySelector("span").textContent =
    "Cambiar a " + next.account_number;
  button.title =
    "Ver cuenta de " + next.full_name + " con saldo " + money(next.balance);
}

function clearCreditPanel() {
  $("#creditAvailable").textContent = "$0.00";
  $("#creditCard").textContent = "Sin tarjeta";
  $("#creditLast4").textContent = "SIN TDC";
  $("#creditLimit").textContent = "$0.00";
  $("#creditBalance").textContent = "$0.00";
  $("#minimumPayment").textContent = "$0.00";
  $("#totalPayment").textContent = "$0.00";
  $("#cutoffDate").textContent = "—";
  $("#paymentDate").textContent = "—";
  $("#dueDate").textContent = "—";
  $("#dueHint").textContent = "Sin tarjeta de crédito";
  $("#creditProgress").style.width = "0%";
  $("#creditAlert").classList.add("hidden");
}

async function loadDashboard() {
  const data = await request(
    "/api/dashboard?account=" + encodeURIComponent(currentAccount)
  );

  const account = data.account;
  const credit = data.credit;

  currentAccount = account.account_number;
  localStorage.setItem("bancoflow_active_account", currentAccount);
  availableAccounts = data.accounts || [];

  $("#balanceValue").textContent = money(account.balance);
  $("#accountNumber").textContent = "Cuenta " + account.account_number;
  $("#activeAccountChip").textContent = "Cuenta " + account.account_number;
  $("#debitCard").textContent = "•••• " + (account.debit_last4 || "—");
  $("#clientName").textContent = account.full_name;
  $("#clientEmail").textContent = account.email;
  $("#clientPhone").textContent = account.phone;
  $("#clientInitials").textContent = initials(account.full_name);

  if (credit) {
    $("#creditAvailable").textContent = money(credit.available);
    $("#creditCard").textContent = "Crédito •••• " + credit.last4;
    $("#creditLast4").textContent = "•••• " + credit.last4;
    $("#creditLimit").textContent = money(credit.credit_limit);
    $("#creditBalance").textContent = money(credit.balance);
    $("#minimumPayment").textContent = money(credit.minimum_payment);
    $("#totalPayment").textContent = money(credit.total_payment);
    $("#cutoffDate").textContent = shortDate(credit.cutoff_date);
    $("#paymentDate").textContent = shortDate(credit.due_date);
    $("#dueDate").textContent = shortDate(credit.due_date);
    $("#dueHint").textContent = credit.alert
      ? "Alerta: faltan " + credit.days_until_due + " día(s)"
      : credit.days_until_due + " día(s) para el pago";
    $("#creditAlert").classList.toggle("hidden", !credit.alert);

    const used = Number(credit.credit_limit) > 0
      ? Math.min(
          100,
          (Number(credit.balance) / Number(credit.credit_limit)) * 100
        )
      : 0;
    $("#creditProgress").style.width = used + "%";
  } else {
    clearCreditPanel();
  }

  renderTransferTargets(data.transfer_targets);
  renderTransactions(data.transactions);
  renderLoans(data.loans);
  renderInsurance(data.insurance);
  updateSwitchButton();
}

$("#switchAccountButton").addEventListener("click", async () => {
  if (availableAccounts.length < 2) return;

  const index = availableAccounts.findIndex(
    (item) => item.account_number === currentAccount
  );
  const next = availableAccounts[(index + 1) % availableAccounts.length];
  currentAccount = next.account_number;

  try {
    await loadDashboard();
    renderTrace([]);
    toast(
      "Cuenta activa: " +
      next.account_number +
      " · " +
      next.full_name +
      "."
    );
  } catch (error) {
    toast(error.message, true);
  }
});

$("#debitAction").addEventListener("change", (event) => {
  $("#targetField").classList.toggle(
    "hidden",
    event.target.value !== "transfer"
  );
});

$("#debitForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(
    new FormData(event.currentTarget).entries()
  );
  payload.account_number = currentAccount;
  const action = payload.action;

  try {
    const data = await request("/api/debit", {
      method: "POST",
      body: JSON.stringify(payload)
    });

    renderTrace(data.trace);
    event.currentTarget.reset();
    $("#targetField").classList.add("hidden");
    await loadDashboard();

    if (action === "transfer" && data.target_balance !== null) {
      toast(
        "Transferencia confirmada. Saldo origen: " +
        money(data.balance) +
        " · saldo destino: " +
        money(data.target_balance) +
        ". Usa Cambiar cuenta para comprobarlo."
      );
    } else {
      toast("Operación completada. Saldo actual: " + money(data.balance) + ".");
    }
  } catch (error) {
    toast(error.message, true);
  }
});

$("#creditForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(
    new FormData(event.currentTarget).entries()
  );
  payload.account_number = currentAccount;

  try {
    const data = await request("/api/credit", {
      method: "POST",
      body: JSON.stringify(payload)
    });

    renderTrace(data.trace);
    event.currentTarget.reset();
    await loadDashboard();
    toast(
      "Crédito actualizado. Deuda: " +
      money(data.credit_balance) +
      " · débito: " +
      money(data.debit_balance) +
      "."
    );
  } catch (error) {
    toast(error.message, true);
  }
});

$("#loanForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(
    new FormData(event.currentTarget).entries()
  );
  payload.account_number = currentAccount;

  try {
    const data = await request("/api/loans", {
      method: "POST",
      body: JSON.stringify(payload)
    });

    renderTrace(data.trace);
    const result = $("#loanResult");
    result.innerHTML =
      'Tasa anual: <strong>' +
      Number(data.annual_rate).toFixed(1) +
      '%</strong><br>Pago mensual estimado: <strong>' +
      money(data.monthly_payment) +
      '</strong>';
    result.classList.remove("hidden");
    toast("Préstamo registrado en la cuenta " + currentAccount + ".");
    await loadDashboard();
  } catch (error) {
    toast(error.message, true);
  }
});

$("#insuranceForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(
    new FormData(event.currentTarget).entries()
  );
  payload.account_number = currentAccount;

  try {
    const data = await request("/api/insurance", {
      method: "POST",
      body: JSON.stringify(payload)
    });

    renderTrace(data.trace);
    const result = $("#insuranceResult");
    result.innerHTML =
      data.coverage +
      '<br>Prima mensual: <strong>' +
      money(data.premium) +
      '</strong>';
    result.classList.remove("hidden");
    toast("Seguro contratado en la cuenta " + currentAccount + ".");
    await loadDashboard();
  } catch (error) {
    toast(error.message, true);
  }
});

$("#refreshButton").addEventListener("click", async () => {
  try {
    await loadDashboard();
    toast("Saldos y movimientos actualizados.");
  } catch (error) {
    toast(error.message, true);
  }
});

$("#resetButton").addEventListener("click", async () => {
  try {
    const data = await request("/api/reset", {
      method: "POST",
      body: "{}"
    });

    currentAccount = data.default_account || "1002003001";
    localStorage.setItem("bancoflow_active_account", currentAccount);
    renderTrace([]);
    $("#loanResult").classList.add("hidden");
    $("#insuranceResult").classList.add("hidden");
    await loadDashboard();
    toast("Datos restaurados. Cuenta principal: " + currentAccount + ".");
  } catch (error) {
    toast(error.message, true);
  }
});

loadDashboard().catch(async (error) => {
  currentAccount = "1002003001";
  localStorage.setItem("bancoflow_active_account", currentAccount);
  try {
    await loadDashboard();
  } catch (secondError) {
    toast(secondError.message || error.message, true);
  }
});
