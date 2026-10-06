-- PurrfectMatch Database Schema (SQLite Version)
-- 100% Offline, Zero-installation required

-- 1. Users table (Staff and Admin)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'Staff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Cats table
CREATE TABLE IF NOT EXISTS cats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    breed TEXT DEFAULT 'Domestic Shorthair',
    age_months INTEGER DEFAULT 12,
    gender TEXT DEFAULT 'Unknown',
    color TEXT DEFAULT 'Mixed',
    intake_date TEXT NOT NULL,
    health_status TEXT DEFAULT 'Healthy',
    is_spayed_neutered INTEGER DEFAULT 0,
    adoption_status TEXT DEFAULT 'Available',
    cage_number TEXT DEFAULT 'Cage A-1',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Adopters table
CREATE TABLE IF NOT EXISTS adopters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    contact_number TEXT NOT NULL,
    email TEXT,
    address TEXT NOT NULL,
    housing_type TEXT DEFAULT 'House with Yard',
    has_other_pets INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Adoption Applications table
CREATE TABLE IF NOT EXISTS adoption_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cat_id INTEGER NOT NULL,
    adopter_id INTEGER NOT NULL,
    application_date TEXT NOT NULL,
    review_status TEXT DEFAULT 'Pending Review',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cat_id) REFERENCES cats (id) ON DELETE CASCADE,
    FOREIGN KEY (adopter_id) REFERENCES adopters (id) ON DELETE CASCADE
);

-- 5. Cat Images table (Supports up to 10 images per cat)
CREATE TABLE IF NOT EXISTS cat_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cat_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    is_primary INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cat_id) REFERENCES cats (id) ON DELETE CASCADE
);

-- ============================================================
-- Seed Data
-- ============================================================

-- Default users (admin / admin123, staff / staff123)
INSERT OR IGNORE INTO users (id, username, password_hash, full_name, role) VALUES
(1, 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Shelter Administrator', 'Admin'),
(2, 'staff', '1ebe2a24911bfbe558c49e19543e593d69eeef1f45ae945ecda96d66e744dff7', 'Jane Doe (Shelter Caregiver)', 'Staff');

-- Sample Cats
INSERT OR IGNORE INTO cats (id, name, breed, age_months, gender, color, intake_date, health_status, is_spayed_neutered, adoption_status, cage_number, notes) VALUES
(1, 'Luna', 'British Shorthair', 18, 'Female', 'Silver Grey', '2026-01-15', 'Healthy & Vaccinated', 1, 'Available', 'Suite A-1', 'Calm and affectionate, loves head scratches.'),
(2, 'Oliver', 'Orange Tabby', 8, 'Male', 'Ginger Orange', '2026-02-01', 'Healthy', 1, 'Available', 'Suite A-2', 'Playful kitten, enjoys feather toys.'),
(3, 'Milo', 'Calico', 24, 'Female', 'Tri-Color', '2026-02-10', 'Under Observation (Minor Skin Allergy)', 1, 'Medical Hold', 'Clinic Room 2', 'Receiving daily topical cream.'),
(4, 'Bella', 'Siamese Mix', 14, 'Female', 'Seal Point', '2026-02-14', 'Healthy & Dewormed', 1, 'Pending', 'Suite B-1', 'Very vocal, bonds closely with people.'),
(5, 'Leo', 'Maine Coon Mix', 36, 'Male', 'Brown Tabby', '2025-11-20', 'Healthy', 1, 'Adopted', 'N/A', 'Adopted by loving family.');

-- Sample Adopters
INSERT OR IGNORE INTO adopters (id, full_name, contact_number, email, address, housing_type, has_other_pets, status) VALUES
(1, 'Sophia Martinez', '0917-555-1234', 'sophia.m@example.com', '123 Maple Street, Green Valley', 'House with Yard', 0, 'Approved'),
(2, 'Liam Chen', '0922-888-5678', 'liam.chen@example.com', 'Unit 405 Sunrise Condominiums', 'Condo', 1, 'Active'),
(3, 'Emma Watson', '0918-999-4321', 'emma.w@example.com', '78 Pine Ridge Ave, Crestview', 'Townhouse', 0, 'Active');

-- Sample Applications
INSERT OR IGNORE INTO adoption_applications (id, cat_id, adopter_id, application_date, review_status, notes) VALUES
(1, 4, 1, '2026-02-16', 'Interview Scheduled', 'Adopter visited on weekend. Interview scheduled for Saturday morning.'),
(2, 5, 2, '2026-01-20', 'Completed', 'Adoption finalized. Cat happily rehomed with Liam.');
