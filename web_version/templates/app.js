// PurrfectMatch - PyWebView Frontend Controller

let currentCustomer = null;
let currentStaff = null;
let catsData = [];
let activeCatId = null;
let activeFilter = 'All';

// Wait for pywebview API to initialize
window.addEventListener('pywebviewready', () => {
  console.log("PyWebView Ready!");
  loadCats();
  updateAuthUI();
});

// Fallback for regular browser testing
setTimeout(() => {
  if (catsData.length === 0) {
    loadCats();
    updateAuthUI();
  }
}, 500);

// ==========================================
// DATA LOADING
// ==========================================
async function loadCats() {
  if (window.pywebview && window.pywebview.api) {
    catsData = await window.pywebview.api.get_cats();
  } else {
    // Mock fallback if running in plain browser without pywebview
    catsData = [
      { id: 1, name: "Luna", breed: "British Shorthair", age_months: 18, formatted_age: "1 yr 6 mos", gender: "Female", color: "Silver Grey", adoption_status: "Available", notes: "Calm and affectionate, loves head scratches." },
      { id: 2, name: "Oliver", breed: "Orange Tabby", age_months: 8, formatted_age: "8 mos", gender: "Male", color: "Ginger Orange", adoption_status: "Available", notes: "Playful kitten, loves feather wand toys." },
      { id: 3, name: "Milo", breed: "Calico", age_months: 24, formatted_age: "2 yrs", gender: "Female", color: "Tri-Color", adoption_status: "Medical Hold", notes: "Under observation for minor skin allergy." },
      { id: 4, name: "Bella", breed: "Siamese Mix", age_months: 14, formatted_age: "1 yr 2 mos", gender: "Female", color: "Seal Point", adoption_status: "Pending", notes: "Very vocal, bonds closely with people." },
      { id: 5, name: "Leo", breed: "Maine Coon Mix", age_months: 36, formatted_age: "3 yrs", gender: "Male", color: "Brown Tabby", adoption_status: "Adopted", notes: "Adopted by loving family." }
    ];
  }
  renderCatsGrid();
}

function renderCatsGrid() {
  const grid = document.getElementById('cats-grid');
  const search = (document.getElementById('search-input').value || '').toLowerCase().trim();

  const filtered = catsData.filter(cat => {
    // Filter by status: public only sees Available or Pending
    const matchesSearch = cat.name.toLowerCase().includes(search) || 
                          cat.breed.toLowerCase().includes(search) || 
                          (cat.color && cat.color.toLowerCase().includes(search));

    if (!matchesSearch) return false;

    if (activeFilter === 'Kitten') return cat.age_months < 12;
    if (activeFilter === 'Female') return cat.gender === 'Female';
    if (activeFilter === 'Male') return cat.gender === 'Male';
    return true;
  });

  if (filtered.length === 0) {
    grid.innerHTML = `<div class="col-span-full text-center py-16 text-slate-400">No matching cats found.</div>`;
    return;
  }

  // Cat avatar emojis based on breed/color
  const avatars = ['🐱', '🐈', '😸', '😽', '😻'];

  grid.innerHTML = filtered.map((cat, i) => {
    const avatar = avatars[cat.id % avatars.length];
    const isAvailable = cat.adoption_status === 'Available';
    const isPending = cat.adoption_status === 'Pending';

    let statusBadge = '';
    if (isAvailable) {
      statusBadge = `<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Available</span>`;
    } else if (isPending) {
      statusBadge = `<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">Pending</span>`;
    } else {
      statusBadge = `<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200">${cat.adoption_status}</span>`;
    }

    return `
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition duration-200 overflow-hidden flex flex-col">
        <!-- Card Header / Avatar -->
        <div class="h-44 bg-gradient-to-tr from-slate-100 to-indigo-50/50 flex items-center justify-center relative">
          <span class="text-7xl select-none transform hover:scale-110 transition duration-300">${avatar}</span>
          <div class="absolute top-3 right-3">
            ${statusBadge}
          </div>
          <div class="absolute bottom-3 left-3 bg-white/80 backdrop-blur-sm px-2.5 py-0.5 rounded-md text-xs font-bold text-slate-700">
            ${cat.gender === 'Female' ? '♀ Female' : '♂ Male'} • ${cat.formatted_age || (cat.age_months + ' mos')}
          </div>
        </div>

        <!-- Card Body -->
        <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
          <div>
            <div class="flex justify-between items-baseline">
              <h3 class="text-lg font-extrabold text-slate-900">${cat.name}</h3>
              <span class="text-xs font-medium text-slate-400">#${cat.id}</span>
            </div>
            <p class="text-xs font-semibold text-indigo-600">${cat.breed}</p>
            <p class="text-xs text-slate-500 mt-2 line-clamp-2">${cat.notes || 'Gentle and friendly shelter cat.'}</p>
          </div>

          <!-- Adopt Button -->
          <div>
            ${isAvailable ? `
              <button onclick="handleAdoptClick(${cat.id})" class="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm rounded-xl transition flex items-center justify-center gap-2 shadow-sm">
                <span>🐾</span> Adopt Me!
              </button>
            ` : `
              <button disabled class="w-full py-2.5 bg-slate-100 text-slate-400 font-bold text-sm rounded-xl cursor-not-allowed">
                ${cat.adoption_status}
              </button>
            `}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// ==========================================
// FILTERS & SEARCH
// ==========================================
function setFilter(filter) {
  activeFilter = filter;
  document.querySelectorAll('.filter-btn').forEach(btn => {
    if (btn.dataset.filter === filter) {
      btn.className = "filter-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white";
    } else {
      btn.className = "filter-btn px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-600 hover:bg-slate-200";
    }
  });
  renderCatsGrid();
}

function handleSearch() {
  renderCatsGrid();
}

// ==========================================
// ADOPT BUTTON FLOW: GUEST VS LOGGED IN
// ==========================================
function handleAdoptClick(catId) {
  activeCatId = catId;
  const cat = catsData.find(c => c.id === catId);

  // If user is not logged in: show the login/signup modal in the center!
  if (!currentCustomer) {
    openAuthModal();
  } else {
    // Already logged in: directly open adoption form
    openApplyModal(cat);
  }
}

// ==========================================
// MODAL CONTROLS
// ==========================================
function openAuthModal() {
  document.getElementById('auth-modal').classList.remove('hidden');
}

function closeAuthModal() {
  document.getElementById('auth-modal').classList.add('hidden');
}

function setAuthMode(mode) {
  const signinForm = document.getElementById('form-signin');
  const signupForm = document.getElementById('form-signup');
  const signinBtn = document.getElementById('tab-btn-signin');
  const signupBtn = document.getElementById('tab-btn-signup');

  if (mode === 'signin') {
    signinForm.classList.remove('hidden');
    signupForm.classList.add('hidden');
    signinBtn.className = "text-sm font-bold text-indigo-600 pb-1 border-b-2 border-indigo-600";
    signupBtn.className = "text-sm font-bold text-slate-400 pb-1 hover:text-slate-600";
  } else {
    signinForm.classList.add('hidden');
    signupForm.classList.remove('hidden');
    signupBtn.className = "text-sm font-bold text-indigo-600 pb-1 border-b-2 border-indigo-600";
    signinBtn.className = "text-sm font-bold text-slate-400 pb-1 hover:text-slate-600";
  }
}

async function handleCustomerLogin(e) {
  e.preventDefault();
  const loginId = document.getElementById('cust-login-id').value.trim();

  let adopter = null;
  if (window.pywebview && window.pywebview.api) {
    adopter = await window.pywebview.api.find_adopter_by_contact(loginId);
  } else {
    adopter = { id: 1, full_name: "Sophia Martinez", contact_number: loginId, email: "sophia@example.com", address: "123 Maple St", housing_type: "House with Yard" };
  }

  if (adopter) {
    currentCustomer = adopter;
    closeAuthModal();
    updateAuthUI();

    // If an adoption was in progress, continue to apply modal!
    if (activeCatId) {
      const cat = catsData.find(c => c.id === activeCatId);
      openApplyModal(cat);
    }
  } else {
    alert("Adopter record not found. Please click 'Create Account' to register!");
  }
}

async function handleCustomerSignup(e) {
  e.preventDefault();
  const newAdopter = {
    full_name: document.getElementById('reg-name').value.trim(),
    contact_number: document.getElementById('reg-contact').value.trim(),
    email: document.getElementById('reg-email').value.trim(),
    address: document.getElementById('reg-address').value.trim(),
    housing_type: document.getElementById('reg-housing').value
  };

  let res = null;
  if (window.pywebview && window.pywebview.api) {
    res = await window.pywebview.api.register_adopter(newAdopter);
    if (res.success) {
      newAdopter.id = res.id;
      currentCustomer = newAdopter;
    } else {
      alert("Registration error: " + res.message);
      return;
    }
  } else {
    newAdopter.id = Date.now();
    currentCustomer = newAdopter;
  }

  closeAuthModal();
  updateAuthUI();

  if (activeCatId) {
    const cat = catsData.find(c => c.id === activeCatId);
    openApplyModal(cat);
  }
}

function updateAuthUI() {
  const container = document.getElementById('auth-actions');
  if (currentCustomer) {
    container.innerHTML = `
      <div class="flex items-center gap-2">
        <span class="text-xs font-bold text-slate-700">👤 ${currentCustomer.full_name}</span>
        <button onclick="logoutCustomer()" class="text-xs text-rose-500 hover:text-rose-700 font-semibold">Sign Out</button>
      </div>
    `;
  } else {
    container.innerHTML = `
      <button onclick="openAuthModal()" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold transition">
        Sign In / Register
      </button>
    `;
  }
}

function logoutCustomer() {
  currentCustomer = null;
  activeCatId = null;
  updateAuthUI();
}

// ==========================================
// APPLY MODAL
// ==========================================
function openApplyModal(cat) {
  if (!cat) return;
  document.getElementById('modal-cat-name').innerText = cat.name;
  document.getElementById('apply-cat-id').value = cat.id;

  document.getElementById('modal-cat-summary').innerHTML = `
    <span class="text-4xl">🐱</span>
    <div>
      <h4 class="font-extrabold text-slate-900">${cat.name} (${cat.breed})</h4>
      <p class="text-xs text-slate-600">${cat.gender} • ${cat.formatted_age || (cat.age_months + ' mos')} • ${cat.color}</p>
    </div>
  `;

  document.getElementById('modal-adopter-info').innerHTML = `
    <p><strong>Name:</strong> ${currentCustomer.full_name}</p>
    <p><strong>Contact:</strong> ${currentCustomer.contact_number} | ${currentCustomer.email || 'No email'}</p>
    <p><strong>Address:</strong> ${currentCustomer.address} (${currentCustomer.housing_type})</p>
  `;

  document.getElementById('apply-modal').classList.remove('hidden');
}

function closeApplyModal() {
  document.getElementById('apply-modal').classList.add('hidden');
  activeCatId = null;
}

async function handleApplicationSubmit(e) {
  e.preventDefault();
  const catId = parseInt(document.getElementById('apply-cat-id').value);
  const notes = document.getElementById('apply-notes').value.trim();

  const applicationData = {
    cat_id: catId,
    adopter_id: currentCustomer.id,
    notes: notes
  };

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.submit_application(applicationData);
    if (res.success) {
      alert("🎉 Application submitted successfully! Shelter staff will review your request.");
      closeApplyModal();
      loadCats(); // Refresh to show updated pending status
      showTab('applications');
    } else {
      alert("Error submitting application: " + res.message);
    }
  } else {
    alert("🎉 Application submitted (mock mode)! Shelter staff will review your request.");
    closeApplyModal();
  }
}

// ==========================================
// TABS & NAVIGATION
// ==========================================
function showTab(tabName) {
  document.getElementById('tab-catalog').classList.add('hidden');
  document.getElementById('tab-applications').classList.add('hidden');
  document.getElementById('tab-staff').classList.add('hidden');

  document.getElementById('nav-catalog').className = "px-3 py-2 rounded-lg text-sm font-semibold text-slate-600 hover:text-indigo-600 hover:bg-slate-100 transition";
  document.getElementById('nav-applications').className = "px-3 py-2 rounded-lg text-sm font-semibold text-slate-600 hover:text-indigo-600 hover:bg-slate-100 transition";
  document.getElementById('nav-staff').className = "px-3 py-2 rounded-lg text-sm font-semibold text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition flex items-center gap-1.5";

  if (tabName === 'catalog') {
    document.getElementById('tab-catalog').classList.remove('hidden');
    document.getElementById('nav-catalog').className = "px-3 py-2 rounded-lg text-sm font-semibold text-indigo-600 bg-indigo-50 transition";
  } else if (tabName === 'applications') {
    document.getElementById('tab-applications').classList.remove('hidden');
    document.getElementById('nav-applications').className = "px-3 py-2 rounded-lg text-sm font-semibold text-indigo-600 bg-indigo-50 transition";
    loadUserApplications();
  } else if (tabName === 'staff') {
    document.getElementById('tab-staff').classList.remove('hidden');
    document.getElementById('nav-staff').className = "px-3 py-2 rounded-lg text-sm font-semibold text-indigo-600 bg-indigo-50 transition flex items-center gap-1.5";
  }
}

async function loadUserApplications() {
  const container = document.getElementById('user-applications-list');
  if (!currentCustomer) {
    container.innerHTML = `
      <div class="text-center py-12">
        <p class="text-slate-500 text-sm">Please sign in to view your submitted applications.</p>
        <button onclick="openAuthModal()" class="mt-3 px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold">Sign In Now</button>
      </div>
    `;
    return;
  }

  let apps = [];
  if (window.pywebview && window.pywebview.api) {
    apps = await window.pywebview.api.get_my_applications(currentCustomer.id);
  } else {
    apps = [
      { id: 101, cat_name: "Luna", application_date: "2026-02-18", review_status: "Pending Review", notes: "Excited to adopt!" }
    ];
  }

  if (apps.length === 0) {
    container.innerHTML = `<div class="text-center py-12 text-slate-400">You have not submitted any applications yet.</div>`;
    return;
  }

  container.innerHTML = apps.map(app => `
    <div class="border border-slate-200 rounded-xl p-4 flex justify-between items-center bg-slate-50/50">
      <div>
        <h4 class="font-bold text-slate-900">Application #${app.id} - 🐱 ${app.cat_name}</h4>
        <p class="text-xs text-slate-500 mt-1">Submitted on: ${app.application_date} | Notes: ${app.notes || 'None'}</p>
      </div>
      <div>
        <span class="px-3 py-1 rounded-full text-xs font-bold ${
          app.review_status === 'Completed' ? 'bg-purple-100 text-purple-700' :
          app.review_status === 'Approved' ? 'bg-emerald-100 text-emerald-700' :
          app.review_status === 'Rejected' ? 'bg-rose-100 text-rose-700' :
          'bg-amber-100 text-amber-700'
        }">${app.review_status}</span>
      </div>
    </div>
  `).join('');
}

// ==========================================
// STAFF LOGIN & DASHBOARD
// ==========================================
async function handleStaffLogin(e) {
  e.preventDefault();
  const u = document.getElementById('staff-user').value.trim();
  const p = document.getElementById('staff-pass').value.trim();

  let res = null;
  if (window.pywebview && window.pywebview.api) {
    res = await window.pywebview.api.staff_login(u, p);
  } else {
    res = { success: (u === 'admin' && p === 'admin123'), user: { full_name: "Shelter Admin" } };
  }

  if (res.success) {
    currentStaff = res.user;
    document.getElementById('staff-auth-gate').classList.add('hidden');
    document.getElementById('staff-dashboard').classList.remove('hidden');
    loadStaffApplications();
  } else {
    alert("Invalid staff credentials.");
  }
}

function logoutStaff() {
  currentStaff = null;
  document.getElementById('staff-dashboard').classList.add('hidden');
  document.getElementById('staff-auth-gate').classList.remove('hidden');
}

async function loadStaffApplications() {
  const table = document.getElementById('staff-applications-table');
  let apps = [];
  if (window.pywebview && window.pywebview.api) {
    apps = await window.pywebview.api.get_all_applications();
  }

  table.innerHTML = apps.map(app => `
    <tr class="hover:bg-slate-50">
      <td class="px-6 py-4 font-bold">#${app.id}</td>
      <td class="px-6 py-4 font-semibold text-indigo-600">🐱 ${app.cat_name}</td>
      <td class="px-6 py-4">${app.adopter_name}</td>
      <td class="px-6 py-4 text-xs text-slate-500">${app.application_date}</td>
      <td class="px-6 py-4">
        <span class="px-2.5 py-0.5 rounded-full text-xs font-bold ${
          app.review_status === 'Completed' ? 'bg-purple-100 text-purple-700' :
          app.review_status === 'Approved' ? 'bg-emerald-100 text-emerald-700' :
          app.review_status === 'Rejected' ? 'bg-rose-100 text-rose-700' :
          'bg-amber-100 text-amber-700'
        }">${app.review_status}</span>
      </td>
      <td class="px-6 py-4 flex gap-2">
        ${app.review_status !== 'Completed' ? `
          <button onclick="updateStaffApp(${app.id}, 'Approved')" class="px-2.5 py-1 bg-emerald-50 text-emerald-700 text-xs font-bold rounded hover:bg-emerald-100">Approve</button>
          <button onclick="updateStaffApp(${app.id}, 'Completed')" class="px-2.5 py-1 bg-purple-50 text-purple-700 text-xs font-bold rounded hover:bg-purple-100">Finalize Adoption</button>
        ` : `<span class="text-xs text-slate-400 font-semibold">Adopted 🎉</span>`}
      </td>
    </tr>
  `).join('');
}

async function updateStaffApp(appId, newStatus) {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.update_application_status(appId, newStatus);
    loadStaffApplications();
    loadCats();
  }
}
