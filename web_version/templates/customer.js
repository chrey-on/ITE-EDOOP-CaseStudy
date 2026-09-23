// PurrfectMatch - Customer / Adopter Frontend Controller

let currentCustomer = null;
let catsData = [];
let activeCatId = null;
let activeFilter = 'All';

window.addEventListener('pywebviewready', () => {
  console.log("Customer Portal: PyWebView API Ready");
  loadCats();
  updateAuthUI();
});

// Fallback for browser preview
setTimeout(() => {
  if (catsData.length === 0) {
    loadCats();
    updateAuthUI();
  }
}, 400);

async function loadCats() {
  if (window.pywebview && window.pywebview.api) {
    catsData = await window.pywebview.api.get_cats();
  } else {
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
    // Only display cats that are Available or Pending (Medical hold or adopted are hidden from public catalog)
    if (cat.adoption_status === 'Medical Hold' || cat.adoption_status === 'Adopted') {
      return false;
    }

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
    grid.innerHTML = `<div class="col-span-full text-center py-16 text-slate-400">No available cats match your search.</div>`;
    return;
  }

  const avatars = ['🐱', '🐈', '😸', '😽', '😻'];

  grid.innerHTML = filtered.map(cat => {
    const avatar = avatars[cat.id % avatars.length];
    const isAvailable = cat.adoption_status === 'Available';

    const statusBadge = isAvailable
      ? `<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Available</span>`
      : `<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">Pending</span>`;

    return `
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition duration-200 overflow-hidden flex flex-col">
        <div class="h-44 bg-gradient-to-tr from-slate-100 to-indigo-50/50 flex items-center justify-center relative">
          <span class="text-7xl select-none transform hover:scale-110 transition duration-300">${avatar}</span>
          <div class="absolute top-3 right-3">${statusBadge}</div>
          <div class="absolute bottom-3 left-3 bg-white/80 backdrop-blur-sm px-2.5 py-0.5 rounded-md text-xs font-bold text-slate-700">
            ${cat.gender === 'Female' ? '♀ Female' : '♂ Male'} • ${cat.formatted_age || (cat.age_months + ' mos')}
          </div>
        </div>

        <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
          <div>
            <div class="flex justify-between items-baseline">
              <h3 class="text-lg font-extrabold text-slate-900">${cat.name}</h3>
              <span class="text-xs font-medium text-slate-400">#${cat.id}</span>
            </div>
            <p class="text-xs font-semibold text-indigo-600">${cat.breed}</p>
            <p class="text-xs text-slate-500 mt-2 line-clamp-2">${cat.notes || 'Gentle and friendly shelter cat looking for a home.'}</p>
          </div>

          <div>
            ${isAvailable ? `
              <button onclick="handleAdoptClick(${cat.id})" class="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm rounded-xl transition flex items-center justify-center gap-2 shadow-sm">
                <span>🐾</span> Adopt Me!
              </button>
            ` : `
              <button disabled class="w-full py-2.5 bg-slate-100 text-slate-400 font-bold text-sm rounded-xl cursor-not-allowed">
                Application Pending
              </button>
            `}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

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

function handleAdoptClick(catId) {
  activeCatId = catId;
  const cat = catsData.find(c => c.id === catId);

  // If user is a guest (not signed in), show centered login/signup modal!
  if (!currentCustomer) {
    openAuthModal();
  } else {
    // If already signed in, open the adoption confirmation form
    openApplyModal(cat);
  }
}

// ==========================================
// MODALS
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

    // Resume adoption flow
    if (activeCatId) {
      const cat = catsData.find(c => c.id === activeCatId);
      openApplyModal(cat);
    }
  } else {
    alert("No registered adopter found with that contact number or email. Please click 'Create Account' to sign up!");
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
      alert("🎉 Application submitted successfully! The shelter staff will review your application.");
      closeApplyModal();
      loadCats();
      showTab('applications');
    } else {
      alert("Error submitting application: " + res.message);
    }
  } else {
    alert("🎉 Application submitted! (mock mode)");
    closeApplyModal();
  }
}

function showTab(tabName) {
  document.getElementById('tab-catalog').classList.add('hidden');
  document.getElementById('tab-applications').classList.add('hidden');

  document.getElementById('nav-catalog').className = "px-3 py-2 rounded-lg text-sm font-semibold text-slate-600 hover:text-indigo-600 hover:bg-slate-100 transition";
  document.getElementById('nav-applications').className = "px-3 py-2 rounded-lg text-sm font-semibold text-slate-600 hover:text-indigo-600 hover:bg-slate-100 transition";

  if (tabName === 'catalog') {
    document.getElementById('tab-catalog').classList.remove('hidden');
    document.getElementById('nav-catalog').className = "px-3 py-2 rounded-lg text-sm font-semibold text-indigo-600 bg-indigo-50 transition";
  } else if (tabName === 'applications') {
    document.getElementById('tab-applications').classList.remove('hidden');
    document.getElementById('nav-applications').className = "px-3 py-2 rounded-lg text-sm font-semibold text-indigo-600 bg-indigo-50 transition";
    loadUserApplications();
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
      { id: 1, cat_name: "Bella", application_date: "2026-02-16", review_status: "Interview Scheduled", notes: "Interview scheduled." }
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
