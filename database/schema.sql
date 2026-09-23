-- PurrfectMatch Database Schema
-- Designed for XAMPP MySQL (EDOOP Case Study)

CREATE DATABASE IF NOT EXISTS `purrfect_match_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `purrfect_match_db`;

-- 1. Users table (Staff and Admin)
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(64) NOT NULL,
    `full_name` VARCHAR(100) NOT NULL,
    `role` ENUM('Admin', 'Staff') DEFAULT 'Staff',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Cats table
CREATE TABLE IF NOT EXISTS `cats` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL,
    `breed` VARCHAR(50) DEFAULT 'Domestic Shorthair',
    `age_months` INT DEFAULT 12,
    `gender` ENUM('Male', 'Female', 'Unknown') DEFAULT 'Unknown',
    `color` VARCHAR(50) DEFAULT 'Mixed',
    `intake_date` DATE NOT NULL,
    `health_status` VARCHAR(100) DEFAULT 'Healthy',
    `is_spayed_neutered` TINYINT(1) DEFAULT 0,
    `adoption_status` ENUM('Available', 'Pending', 'Adopted', 'Medical Hold') DEFAULT 'Available',
    `cage_number` VARCHAR(20) DEFAULT 'Cage A-1',
    `notes` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Adopters table
CREATE TABLE IF NOT EXISTS `adopters` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `full_name` VARCHAR(100) NOT NULL,
    `contact_number` VARCHAR(30) NOT NULL,
    `email` VARCHAR(100),
    `address` TEXT NOT NULL,
    `housing_type` ENUM('Apartment', 'House with Yard', 'Condo', 'Townhouse') DEFAULT 'House with Yard',
    `has_other_pets` TINYINT(1) DEFAULT 0,
    `status` ENUM('Active', 'Approved', 'Inactive') DEFAULT 'Active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Adoption Applications table
CREATE TABLE IF NOT EXISTS `adoption_applications` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `cat_id` INT NOT NULL,
    `adopter_id` INT NOT NULL,
    `application_date` DATE NOT NULL,
    `review_status` ENUM('Pending Review', 'Interview Scheduled', 'Approved', 'Rejected', 'Completed') DEFAULT 'Pending Review',
    `notes` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_app_cat` FOREIGN KEY (`cat_id`) REFERENCES `cats` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_app_adopter` FOREIGN KEY (`adopter_id`) REFERENCES `adopters` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- Seed Data
-- ============================================================

-- Default users:
-- admin / admin123 (SHA-256: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9)
-- staff / staff123 (SHA-256: 1ebe2a24911bfbe558c49e19543e593d69eeef1f45ae945ecda96d66e744dff7)
INSERT IGNORE INTO `users` (`id`, `username`, `password_hash`, `full_name`, `role`) VALUES
(1, 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Shelter Administrator', 'Admin'),
(2, 'staff', '1ebe2a24911bfbe558c49e19543e593d69eeef1f45ae945ecda96d66e744dff7', 'Jane Doe (Shelter Caregiver)', 'Staff');

-- Sample Cats
INSERT IGNORE INTO `cats` (`id`, `name`, `breed`, `age_months`, `gender`, `color`, `intake_date`, `health_status`, `is_spayed_neutered`, `adoption_status`, `cage_number`, `notes`) VALUES
(1, 'Luna', 'British Shorthair', 18, 'Female', 'Silver Grey', '2026-01-15', 'Healthy & Vaccinated', 1, 'Available', 'Suite A-1', 'Calm and affectionate, loves head scratches.'),
(2, 'Oliver', 'Orange Tabby', 8, 'Male', 'Ginger Orange', '2026-02-01', 'Healthy', 1, 'Available', 'Suite A-2', 'Playful kitten, enjoys feather toys.'),
(3, 'Milo', 'Calico', 24, 'Female', 'Tri-Color', '2026-02-10', 'Under Observation (Minor Skin Allergy)', 1, 'Medical Hold', 'Clinic Room 2', 'Receiving daily topical cream.'),
(4, 'Bella', 'Siamese Mix', 14, 'Female', 'Seal Point', '2026-02-14', 'Healthy & Dewormed', 1, 'Pending', 'Suite B-1', 'Very vocal, bonds closely with people.'),
(5, 'Leo', 'Maine Coon Mix', 36, 'Male', 'Brown Tabby', '2025-11-20', 'Healthy', 1, 'Adopted', 'N/A', 'Adopted by loving family.');

-- Sample Adopters
INSERT IGNORE INTO `adopters` (`id`, `full_name`, `contact_number`, `email`, `address`, `housing_type`, `has_other_pets`, `status`) VALUES
(1, 'Sophia Martinez', '0917-555-1234', 'sophia.m@example.com', '123 Maple Street, Green Valley', 'House with Yard', 0, 'Approved'),
(2, 'Liam Chen', '0922-888-5678', 'liam.chen@example.com', 'Unit 405 Sunrise Condominiums', 'Condo', 1, 'Active'),
(3, 'Emma Watson', '0918-999-4321', 'emma.w@example.com', '78 Pine Ridge Ave, Crestview', 'Townhouse', 0, 'Active');

-- Sample Applications
INSERT IGNORE INTO `adoption_applications` (`id`, `cat_id`, `adopter_id`, `application_date`, `review_status`, `notes`) VALUES
(1, 4, 1, '2026-02-16', 'Interview Scheduled', 'Adopter visited on weekend. Interview scheduled for Saturday morning.'),
(2, 5, 2, '2026-01-20', 'Completed', 'Adoption finalized. Cat happily rehomed with Liam.');
