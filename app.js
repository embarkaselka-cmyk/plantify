const STORAGE_KEY = "young-journalist-members";

const form = document.getElementById("memberForm");
const tableBody = document.getElementById("membersTable");
const stats = document.getElementById("stats");
const searchInput = document.getElementById("search");
const cancelEditBtn = document.getElementById("cancelEdit");

const statusClass = {
  نشط: "status-active",
  متوقف: "status-paused",
  "بانتظار التجديد": "status-renew",
};

function loadMembers() {
  return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
}

function saveMembers(members) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(members));
}

function createId() {
  return crypto.randomUUID ? crypto.randomUUID() : String(Date.now());
}

function clearForm() {
  form.reset();
  document.getElementById("memberId").value = "";
}

function fillForm(member) {
  document.getElementById("memberId").value = member.id;
  document.getElementById("name").value = member.name;
  document.getElementById("age").value = member.age;
  document.getElementById("phone").value = member.phone;
  document.getElementById("level").value = member.level;
  document.getElementById("track").value = member.track;
  document.getElementById("status").value = member.status;
}

function renderStats(members) {
  const total = members.length;
  const active = members.filter((m) => m.status === "نشط").length;
  const renew = members.filter((m) => m.status === "بانتظار التجديد").length;

  stats.innerHTML = `
    <span class="pill">إجمالي الأعضاء: ${total}</span>
    <span class="pill">نشط: ${active}</span>
    <span class="pill">بانتظار التجديد: ${renew}</span>
  `;
}

function renderTable() {
  const keyword = searchInput.value.trim().toLowerCase();
  const members = loadMembers();
  const filtered = members.filter(
    (m) => m.name.toLowerCase().includes(keyword) || m.phone.includes(keyword)
  );

  renderStats(members);

  tableBody.innerHTML = filtered
    .map(
      (m) => `
      <tr>
        <td>${m.name}</td>
        <td>${m.age}</td>
        <td>${m.phone}</td>
        <td>${m.level}</td>
        <td>${m.track}</td>
        <td><span class="status ${statusClass[m.status] || "status-paused"}">${m.status}</span></td>
        <td>
          <button class="btn btn-light" data-action="edit" data-id="${m.id}">تعديل</button>
          <button class="btn" style="background:#fde9ea" data-action="delete" data-id="${m.id}">حذف</button>
        </td>
      </tr>
    `
    )
    .join("");
}

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const member = {
    id: document.getElementById("memberId").value || createId(),
    name: document.getElementById("name").value.trim(),
    age: Number(document.getElementById("age").value),
    phone: document.getElementById("phone").value.trim(),
    level: document.getElementById("level").value,
    track: document.getElementById("track").value,
    status: document.getElementById("status").value,
  };

  const members = loadMembers();
  const existingIndex = members.findIndex((m) => m.id === member.id);

  if (existingIndex > -1) {
    members[existingIndex] = member;
  } else {
    members.push(member);
  }

  saveMembers(members);
  clearForm();
  renderTable();
});

tableBody.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (!button) return;

  const action = button.dataset.action;
  const id = button.dataset.id;
  const members = loadMembers();
  const member = members.find((m) => m.id === id);

  if (action === "edit" && member) {
    fillForm(member);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (action === "delete") {
    const nextMembers = members.filter((m) => m.id !== id);
    saveMembers(nextMembers);
    renderTable();
  }
});

cancelEditBtn.addEventListener("click", clearForm);
searchInput.addEventListener("input", renderTable);

renderTable();
