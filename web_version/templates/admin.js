// PurrfectMatch - Staff / Admin Management Frontend Controller

let currentStaff = null;
let catsData = [];
let adoptersData = [];
let appsData = [];

window.addEventListener('pywebviewready', () => {
  console.log("Admin Portal: PyWebView API Ready");
});

function quickFill(user, pass) {
  document.getElementById('staff-username').value = user;
  document.getElementById('staff-password').value = pass;
}

async function handleStaffLogin(e) {
  e.preventDefault();
  const u = document.getElementById('staff-username').value.trim();
  const p = document.getElementById('staff-password').value.trim();

  let res = null;
  if (window.pywebview && window.pywebview.api) {
    res = await window.pywebview.api.staff_login(u, p);
  } else {
    // Browser mock
    res = { success: (u === 'admin' || u === 'staff'), user: { full_name: "Shelter Administrator", role: "Admin" } };
  }

  if (res && res.success) {
    currentStaff = res.user;
    document.getElementById('staff-display-name').innerText = currentStaff.full_name;
    document.getElementById('staff-display-role').innerText = `Role: ${currentStaff.role || 'Staff'}`;

    document.getElementById('staff-login-screen').classList.add('hidden');
    document.getElementById('staff-dashboard-screen').classList.remove('hidden');

    await refreshAllAdminData();
  } else {
    alert("Invalid username or password. Please try again.");
  }
}

function handleStaffLogout() {
  currentStaff = null;
  document.getElementById('staff-dashboard-screen').classList.add('hidden');
  document.getElementById('staff-login-screen').classList.remove('hidden');
}

async function refreshAllAdminData() {
  if (window.pywebview && window.pywebview.api) {
    catsData = await window.pywebview.api.get_cats();
    adoptersData = await window.pywebview.api.get_all_adopters();
    appsData = await window.pywebview.api.get_all_applications();
  } else {
    // Mock fallback
    catsData = [
      { id: 1, name: "Luna", breed: "British Shorthair", age_months: 18, formatted_age: "1 yr 6 mos", gender: "Female", color: "Silver Grey", adoption_status: "Available", cage_number: "Suite A-1" },
      { id: 2, name: "Oliver", breed: "Orange Tabby", age_months: 8, formatted_age: "8 mos", gender: "Male", color: "Ginger Orange", adoption_status: "Available", cage_number: "Suite A-2" },
      { id: 3, name: "Bella", breed: "Siamese Mix", age_months: 14, formatted_age: "1 yr 2 mos", gender: "Female", color: "Seal Point", adoption_status: "Pending", cage_number: "Suite B-1" }
    ];
    adoptersData = [
      { id: 1, full_name: "Sophia Martinez", contact_number: "0917-555-1234", email: "sophia@example.com", address: "123 Maple St", housing_type: "House with Yard", status: "Approved" },
      { id: 2, full_name: "Liam Chen", contact_number: "0922-888-5678", email: "liam@example.com", address: "Unit 405 Sunrise", housing_type: "Condo", status: "Active" }
    ];
    appsData = [
      { id: 1, cat_id: 3, cat_name: "Bella", adopter_id: 1, adopter_name: "Sophia Martinez", application_date: "2026-02-16", review_status: "Interview Scheduled", notes: "Interview scheduled." }
    ];
  }

  updateMetrics();
  renderCatsTable();
  renderAdoptersTable();
  renderAppsTable();
}

function updateMetrics() {
  document.getElementById('stat-total-cats').innerText = catsData.length;
  document.getElementById('stat-avail-cats').innerText = catsData.filter(c => c.adoption_status === 'Available').length;
  document.getElementById('stat-pending-apps').innerText = appsData.filter(a => a.review_status === 'Pending Review' || a.review_status === 'Interview Scheduled').length;
  document.getElementById('stat-completed-apps').innerText = appsData.filter(a => a.review_status === 'Completed').length;
}

function switchAdminTab(tabName) {
  const sections = ['overview', 'cats', 'adopters', 'applications'];
  sections.forEach(sec => {
    document.getElementById(`admin-sec-${sec}`).classList.add('hidden');
    const btn = document.getElementById(`sidebar-${sec}`);
    btn.className = "admin-nav-btn w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-50";
  });

  document.getElementById(`admin-sec-${tabName}`).classList.remove('hidden');
  const activeBtn = document.getElementById(`sidebar-${tabName}`);
  activeBtn.className = "admin-nav-btn w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-bold bg-indigo-50 text-indigo-600";
}

// ==========================================
// CATS CRUD
// ==========================================
function renderCatsTable() {
  const tbody = document.getElementById('admin-cats-table');
  if (catsData.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-slate-400">No cats registered.</td></tr>`;
    return;
  }

  tbody.innerHTML = catsData.map(c => `
    <tr class="hover:bg-slate-50">
      <td class="px-5 py-3 font-bold">#${c.id}</td>
      <td class="px-5 py-3 font-semibold text-slate-900">${c.name}</td>
      <td class="px-5 py-3 text-slate-600">${c.breed}</td>
      <td class="px-5 py-3">${c.formatted_age || (c.age_months + ' mos')}</td>
      <td class="px-5 py-3">${c.gender}</td>
      <td class="px-5 py-3">
        <span class="px-2.5 py-0.5 rounded-full text-xs font-bold ${
          c.adoption_status === 'Available' ? 'bg-emerald-100 text-emerald-700' :
          c.adoption_status === 'Pending' ? 'bg-amber-100 text-amber-700' :
          c.adoption_status === 'Adopted' ? 'bg-purple-100 text-purple-700' :
          'bg-rose-100 text-rose-700'
        }">${c.adoption_status}</span>
      </td>
      <td class="px-5 py-3 text-xs text-slate-500">${c.cage_number || '-'}</td>
      <td class="px-5 py-3 text-right space-x-2">
        <button onclick="editCat(${c.id})" class="text-indigo-600 hover:text-indigo-800 text-xs font-bold">Edit</button>
        <button onclick="deleteCat(${c.id})" class="text-rose-600 hover:text-rose-800 text-xs font-bold">Delete</button>
      </td>
    </tr>
  `).join('');
}

function openCatModal(cat = null) {
  document.getElementById('cat-modal-title').innerText = cat ? `Edit Cat #${cat.id}` : "Intake New Cat";
  document.getElementById('edit-cat-id').value = cat ? cat.id : "";
  document.getElementById('cat-form-name').value = cat ? cat.name : "";
  document.getElementById('cat-form-breed').value = cat ? cat.breed : "";
  document.getElementById('cat-form-age').value = cat ? cat.age_months : 12;
  document.getElementById('cat-form-gender').value = cat ? cat.gender : "Female";
  document.getElementById('cat-form-status').value = cat ? cat.adoption_status : "Available";
  document.getElementById('cat-form-color').value = cat ? cat.color : "";
  document.getElementById('cat-form-cage').value = cat ? cat.cage_number : "Suite A-1";
  document.getElementById('cat-form-notes').value = cat ? (cat.notes || "") : "";

  document.getElementById('cat-modal').classList.remove('hidden');
}

function closeCatModal() {
  document.getElementById('cat-modal').classList.add('hidden');
}

function editCat(id) {
  const cat = catsData.find(c => c.id === id);
  if (cat) openCatModal(cat);
}

async function handleSaveCat(e) {
  e.preventDefault();
  const id = document.getElementById('edit-cat-id').value;
  const catData = {
    id: id ? parseInt(id) : null,
    name: document.getElementById('cat-form-name').value.trim(),
    breed: document.getElementById('cat-form-breed').value.trim() || "Domestic Shorthair",
    age_months: parseInt(document.getElementById('cat-form-age').value) || 12,
    gender: document.getElementById('cat-form-gender').value,
    adoption_status: document.getElementById('cat-form-status').value,
    color: document.getElementById('cat-form-color').value.trim() || "Mixed",
    cage_number: document.getElementById('cat-form-cage').value.trim() || "Suite A-1",
    notes: document.getElementById('cat-form-notes').value.trim()
  };

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.save_cat(catData);
    if (res.success) {
      closeCatModal();
      await refreshAllAdminData();
    } else {
      alert("Error: " + res.message);
    }
  } else {
    closeCatModal();
  }
}

async function deleteCat(id) {
  if (!confirm(`Are you sure you want to delete Cat #${id}?`)) return;

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.delete_cat(id);
    if (res.success) {
      await refreshAllAdminData();
    } else {
      alert("Error: " + res.message);
    }
  }
}

// ==========================================
// ADOPTERS CRUD
// ==========================================
function renderAdoptersTable() {
  const tbody = document.getElementById('admin-adopters-table');
  if (adoptersData.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-slate-400">No adopters registered.</td></tr>`;
    return;
  }

  tbody.innerHTML = adoptersData.map(a => `
    <tr class="hover:bg-slate-50">
      <td class="px-5 py-3 font-bold">#${a.id}</td>
      <td class="px-5 py-3 font-semibold text-slate-900">${a.full_name}</td>
      <td class="px-5 py-3">${a.contact_number}</td>
      <td class="px-5 py-3 text-slate-500">${a.email || '-'}</td>
      <td class="px-5 py-3 text-xs">${a.housing_type}</td>
      <td class="px-5 py-3">
        <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-blue-700">${a.status || 'Active'}</span>
      </td>
      <td class="px-5 py-3 text-right space-x-2">
        <button onclick="editAdopter(${a.id})" class="text-indigo-600 hover:text-indigo-800 text-xs font-bold">Edit</button>
        <button onclick="deleteAdopter(${a.id})" class="text-rose-600 hover:text-rose-800 text-xs font-bold">Delete</button>
      </td>
    </tr>
  `).join('');
}

function openAdopterModal(adopter = null) {
  document.getElementById('adopter-modal-title').innerText = adopter ? `Edit Adopter #${adopter.id}` : "Register Adopter";
  document.getElementById('edit-adopter-id').value = adopter ? adopter.id : "";
  document.getElementById('adopter-form-name').value = adopter ? adopter.full_name : "";
  document.getElementById('adopter-form-contact').value = adopter ? adopter.contact_number : "";
  document.getElementById('adopter-form-email').value = adopter ? (adopter.email || "") : "";
  document.getElementById('adopter-form-address').value = adopter ? adopter.address : "";
  document.getElementById('adopter-form-housing').value = adopter ? adopter.housing_type : "House with Yard";

  document.getElementById('adopter-modal').classList.remove('hidden');
}

function closeAdopterModal() {
  document.getElementById('adopter-modal').classList.add('hidden');
}

function editAdopter(id) {
  const adopter = adoptersData.find(a => a.id === id);
  if (adopter) openAdopterModal(adopter);
}

async function handleSaveAdopter(e) {
  e.preventDefault();
  const id = document.getElementById('edit-adopter-id').value;
  const adopterData = {
    id: id ? parseInt(id) : null,
    full_name: document.getElementById('adopter-form-name').value.trim(),
    contact_number: document.getElementById('adopter-form-contact').value.trim(),
    email: document.getElementById('adopter-form-email').value.trim(),
    address: document.getElementById('adopter-form-address').value.trim(),
    housing_type: document.getElementById('adopter-form-housing').value
  };

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.save_adopter(adopterData);
    if (res.success) {
      closeAdopterModal();
      await refreshAllAdminData();
    } else {
      alert("Error: " + res.message);
    }
  } else {
    closeAdopterModal();
  }
}

async function deleteAdopter(id) {
  if (!confirm(`Are you sure you want to delete Adopter #${id}? Associated applications will be deleted.`)) return;

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.delete_adopter(id);
    if (res.success) {
      await refreshAllAdminData();
    } else {
      alert("Error: " + res.message);
    }
  }
}

// ==========================================
// APPLICATIONS REVIEW & ACTIONS
// ==========================================
function renderAppsTable() {
  const tbody = document.getElementById('admin-apps-table');
  if (appsData.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-slate-400">No applications received yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = appsData.map(a => `
    <tr class="hover:bg-slate-50">
      <td class="px-5 py-3 font-bold">#${a.id}</td>
      <td class="px-5 py-3 font-bold text-indigo-600">🐱 ${a.cat_name}</td>
      <td class="px-5 py-3">${a.adopter_name}</td>
      <td class="px-5 py-3 text-xs text-slate-500">${a.application_date}</td>
      <td class="px-5 py-3">
        <span class="px-2.5 py-0.5 rounded-full text-xs font-bold ${
          a.review_status === 'Completed' ? 'bg-purple-100 text-purple-700' :
          a.review_status === 'Approved' ? 'bg-emerald-100 text-emerald-700' :
          a.review_status === 'Rejected' ? 'bg-rose-100 text-rose-700' :
          'bg-amber-100 text-amber-700'
        }">${a.review_status}</span>
      </td>
      <td class="px-5 py-3 text-xs text-slate-500 max-w-xs truncate">${a.notes || 'None'}</td>
      <td class="px-5 py-3 text-right space-x-1.5">
        ${a.review_status !== 'Completed' ? `
          <button onclick="updateAppStatus(${a.id}, 'Approved')" class="px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-bold rounded">Approve</button>
          <button onclick="updateAppStatus(${a.id}, 'Completed')" class="px-2.5 py-1 bg-purple-50 hover:bg-purple-100 text-purple-700 text-xs font-bold rounded">Finalize Adoption</button>
          <button onclick="updateAppStatus(${a.id}, 'Rejected')" class="px-2 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 text-xs font-bold rounded">Reject</button>
        ` : `<span class="text-xs text-slate-400 font-bold">Adopted 🎉</span>`}
      </td>
    </tr>
  `).join('');
}

async function updateAppStatus(appId, newStatus) {
  if (newStatus === 'Completed') {
    if (!confirm("Finalizing will mark this adoption as Completed and automatically update the cat status to 'Adopted'. Proceed?")) return;
  }

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.update_application_status(appId, newStatus);
    if (res.success) {
      await refreshAllAdminData();
    } else {
      alert("Error: " + res.message);
    }
  }
}
