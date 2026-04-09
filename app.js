const STORAGE_KEY = "timimoun_journalist_members";

const memberForm = document.getElementById("memberForm");
const membersTableBody = document.getElementById("membersTableBody");
const rowTemplate = document.getElementById("rowTemplate");
const searchInput = document.getElementById("searchInput");
const exportCsvBtn = document.getElementById("exportCsv");
const saveBtn = document.getElementById("saveBtn");
const liveQr = document.getElementById("liveQr");
const barcodeInput = document.getElementById("barcodeText");

let members = loadMembers();
let editingMemberId = null;

renderTable();
updateLiveQr(barcodeInput.value);

memberForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const member = getFormData();
  if (!member.memberId) return;

  if (editingMemberId) {
    members = members.map((item) => (item.memberId === editingMemberId ? member : item));
    editingMemberId = null;
    saveBtn.textContent = "حفظ العضو";
  } else {
    const exists = members.some((item) => item.memberId === member.memberId);
    if (exists) {
      alert("رقم التعريف موجود مسبقاً. يمكنك تعديله من الجدول.");
      return;
    }
    members.unshift(member);
  }

  persistMembers();
  renderTable(searchInput.value.trim());
  memberForm.reset();
  updateLiveQr("");
});

memberForm.addEventListener("reset", () => {
  editingMemberId = null;
  saveBtn.textContent = "حفظ العضو";
  updateLiveQr("");
});

barcodeInput.addEventListener("input", () => {
  updateLiveQr(barcodeInput.value.trim());
});

searchInput.addEventListener("input", () => {
  renderTable(searchInput.value.trim());
});

exportCsvBtn.addEventListener("click", () => {
  if (!members.length) {
    alert("لا توجد بيانات للتصدير.");
    return;
  }

  const headers = [
    "رقم التعريف",
    "الاسم واللقب",
    "الجنس",
    "تاريخ ومكان الميلاد",
    "الإقامة",
    "اسم الولي",
    "رقم الولي",
    "رقم الهاتف",
    "الصفة",
    "تاريخ الانضمام",
    "نص الباركود",
  ];

  const rows = members.map((m) => [
    m.memberId,
    m.fullName,
    m.gender,
    m.birthInfo,
    m.residence,
    m.guardianName,
    m.guardianPhone,
    m.phone,
    m.role,
    m.joinDate,
    m.barcodeText,
  ]);

  const csvContent = [headers, ...rows]
    .map((row) => row.map((cell) => `"${String(cell || "").replaceAll('"', '""')}"`).join(","))
    .join("\n");

  const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "timimoun-club-members.csv";
  link.click();
  URL.revokeObjectURL(url);
});

function getFormData() {
  return {
    memberId: document.getElementById("memberId").value.trim(),
    fullName: document.getElementById("fullName").value.trim(),
    gender: document.getElementById("gender").value,
    birthInfo: document.getElementById("birthInfo").value.trim(),
    residence: document.getElementById("residence").value.trim(),
    guardianName: document.getElementById("guardianName").value.trim(),
    guardianPhone: document.getElementById("guardianPhone").value.trim(),
    phone: document.getElementById("phone").value.trim(),
    role: document.getElementById("role").value,
    joinDate: document.getElementById("joinDate").value,
    barcodeText: document.getElementById("barcodeText").value.trim(),
  };
}

function renderTable(searchQuery = "") {
  membersTableBody.innerHTML = "";

  const normalized = searchQuery.toLowerCase();
  const filteredMembers = members.filter((member) => {
    if (!normalized) return true;

    return [member.memberId, member.fullName, member.gender, member.phone, member.guardianName, member.guardianPhone]
      .join(" ")
      .toLowerCase()
      .includes(normalized);
  });

  if (!filteredMembers.length) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="13" class="empty">لا توجد نتائج مطابقة.</td>`;
    membersTableBody.appendChild(row);
    return;
  }

  filteredMembers.forEach((member) => {
    const row = rowTemplate.content.firstElementChild.cloneNode(true);

    row.querySelectorAll("[data-key]").forEach((cell) => {
      const key = cell.dataset.key;
      if (key === "qr") return;
      cell.textContent = member[key] || "-";
    });

    renderQr(row.querySelector('[data-key="qr"]'), member.barcodeText, 54, 54);

    row.querySelector(".edit").addEventListener("click", () => {
      fillFormForEdit(member);
    });

    row.querySelector(".delete").addEventListener("click", () => {
      const accepted = confirm(`هل تريد حذف العضو: ${member.fullName}؟`);
      if (!accepted) return;

      members = members.filter((item) => item.memberId !== member.memberId);
      persistMembers();
      renderTable(searchInput.value.trim());
    });

    membersTableBody.appendChild(row);
  });
}

function fillFormForEdit(member) {
  document.getElementById("memberId").value = member.memberId;
  document.getElementById("fullName").value = member.fullName;
  document.getElementById("gender").value = member.gender || "";
  document.getElementById("birthInfo").value = member.birthInfo;
  document.getElementById("residence").value = member.residence;
  document.getElementById("guardianName").value = member.guardianName;
  document.getElementById("guardianPhone").value = member.guardianPhone || "";
  document.getElementById("phone").value = member.phone;
  document.getElementById("role").value = member.role;
  document.getElementById("joinDate").value = member.joinDate;
  document.getElementById("barcodeText").value = member.barcodeText;

  editingMemberId = member.memberId;
  saveBtn.textContent = "تحديث العضو";
  updateLiveQr(member.barcodeText);
}

function updateLiveQr(value) {
  renderQr(liveQr, value, 70, 70);
}

function renderQr(target, text, width, height) {
  target.innerHTML = "";

  if (!text) {
    target.innerHTML = "<small>بدون QR</small>";
    return;
  }

  new QRCode(target, {
    text,
    width,
    height,
    colorDark: "#0f1f38",
    colorLight: "#ffffff",
    correctLevel: QRCode.CorrectLevel.H,
  });
}

function loadMembers() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

function persistMembers() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(members));
}
