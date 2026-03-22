-- ============================================================
-- College Placement System - Database Setup
-- Run this in MySQL Workbench or via: mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS placement_management;
USE placement_management;

-- --------------------------------------------------------
-- Students table
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS Students (
    student_id   INT AUTO_INCREMENT PRIMARY KEY,
    full_name    VARCHAR(100) NOT NULL,
    email        VARCHAR(100) NOT NULL UNIQUE,
    department   VARCHAR(100) NOT NULL DEFAULT 'Please Update Profile',
    cgpa         DECIMAL(3,1) NOT NULL DEFAULT 0.0,
    resume_link  VARCHAR(500) DEFAULT NULL
);

-- --------------------------------------------------------
-- Users table (login accounts - linked to Students for students)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS Users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    email       VARCHAR(100) NOT NULL UNIQUE,
    password    VARCHAR(256) NOT NULL,  -- SHA-256 hash
    role        ENUM('Student', 'Admin') NOT NULL DEFAULT 'Student',
    student_id  INT DEFAULT NULL,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE SET NULL
);

-- --------------------------------------------------------
-- Companies table
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS Companies (
    company_id   INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    job_role     VARCHAR(100) NOT NULL,
    package_lpa  DECIMAL(5,2) NOT NULL,
    visit_date   DATE NOT NULL
);

-- --------------------------------------------------------
-- Applications table
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS Applications (
    application_id   INT AUTO_INCREMENT PRIMARY KEY,
    student_id       INT NOT NULL,
    company_id       INT NOT NULL,
    status           ENUM('Applied', 'Interviewing', 'Selected', 'Rejected') NOT NULL DEFAULT 'Applied',
    application_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES Companies(company_id) ON DELETE CASCADE,
    -- Prevent duplicate applications
    UNIQUE KEY uq_student_company (student_id, company_id)
);

-- --------------------------------------------------------
-- Seed Data: Default Admin Account
-- Password: Admin@123  (SHA-256 hash)
-- --------------------------------------------------------
INSERT IGNORE INTO Users (email, password, role, student_id)
VALUES ('admin@xie.edu.in', 'a0baa1cd4c25bc61d3a0e99e7e87b50f5e4c2a5e4c2ab6d789f7ac5c5a345b1c', 'Admin', NULL);
