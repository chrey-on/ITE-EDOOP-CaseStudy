<div align="center">

# 🐾 PurrfectMatch
### *Smart, Heartwarming Cat Adoption & Shelter Management*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-1f6aa5?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Offline Ready](https://img.shields.io/badge/Offline-100%25_Ready-27ae60?style=for-the-badge)]()

**Connecting lovable shelter cats with caring families through a seamless, dual-interface desktop experience.**

[Features](#-features) • [Quick Start](#-quick-start) • [Default Logins](#-demo-credentials) • [Interfaces](#-two-tailored-experiences)

</div>

---

## ✨ Why PurrfectMatch?

Traditional shelter record-keeping is cluttered and slow. **PurrfectMatch** bridges the gap between public adopters and shelter staff with two purpose-built experiences powered by a shared, real-time offline database.

### 🌟 Key Highlights

* 🐱 **Browse Freely as a Guest:** Explore adorable shelter cats, filter by age or gender, and find the perfect match without needing an account upfront.
* 📋 **Frictionless Adoption:** Ready to adopt? A sleek centered sign-in pop-up appears only when you click **"Adopt Me!"** to submit your application in seconds.
* 🔐 **Dedicated Staff Dashboard:** Shelter caretakers manage cat intake, track adopter profiles, and review/finalize adoption requests with automatic status updates.
* ⚡ **Zero-Setup & 100% Offline:** Built-in SQLite database—no servers, no XAMPP, and no complex configurations required. Just launch and go!
* 🎨 **Dual Design Flavors:** Choose between the native **Python Desktop app** or the modern **Tailwind Web edition**.

---

## 🖥️ Two Tailored Experiences

| 🐱 **Customer Portal** | 🔐 **Staff Back-Office** |
| :--- | :--- |
| • Visual cat card gallery | • Real-time shelter statistics |
| • Filter by kitten, adult, or gender | • Complete Cat Intake (Add, Edit, Delete) |
| • Action-gated modal sign-in | • Adopter directory & search |
| • Personal application tracking | • One-click "Finalize Adoption" approval |

---

## 🚀 Quick Start

Get PurrfectMatch up and running in under a minute!

### 1. Install Dependencies
```bash
uv pip install -r requirements.txt
# or: pip install -r requirements.txt
```

### 2. Launch the Application

#### 🐍 Native Python Desktop (Recommended)
```bash
# Launch the Customer Adoption Portal:
uv run customer_app.py

# Launch the Staff Management Dashboard:
uv run admin_app.py
```

#### 🌐 Web / Tailwind Edition
```bash
# Launch either view via the interactive menu:
uv run web_version/main_web.py
```

---

## 🔑 Demo Credentials

Test the Staff Management Portal right away:

| Role | Username | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` |
| **Staff Member** | `staff` | `staff123` |

*(Convenient **Quick-Fill** buttons are provided right on the login screen for instant access!)*

---

<div align="center">

Made with ❤️ for shelter pets everywhere.

</div>
