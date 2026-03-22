-- ============================================================
-- College Placement System — Schema Migration (v2)
-- Run this in MySQL Workbench AFTER schema.sql
-- ============================================================
USE placement_management;

-- --------------------------------------------------------
-- Upgrade Students table
-- --------------------------------------------------------
ALTER TABLE Students
  ADD COLUMN IF NOT EXISTS cgpa_year1     DECIMAL(4,2) NOT NULL DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS cgpa_year2     DECIMAL(4,2) NOT NULL DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS cgpa_year3     DECIMAL(4,2) NOT NULL DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS cgpa_year4     DECIMAL(4,2) NOT NULL DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS aggregate_cgpa DECIMAL(4,2) NOT NULL DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS marksheet_link VARCHAR(500) DEFAULT NULL;

-- Update old aggregate (previously called cgpa) to aggregate_cgpa for any existing rows
UPDATE Students SET aggregate_cgpa = cgpa WHERE aggregate_cgpa = 0.0 AND cgpa > 0.0;

-- --------------------------------------------------------
-- Upgrade Companies table
-- --------------------------------------------------------
ALTER TABLE Companies
  ADD COLUMN IF NOT EXISTS package_min DECIMAL(5,2) NOT NULL DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS package_max DECIMAL(5,2) NOT NULL DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS min_cgpa    DECIMAL(4,2) NOT NULL DEFAULT 0.0;

-- Copy existing package_lpa to package_min for any old rows
UPDATE Companies SET package_min = package_lpa, package_max = package_lpa WHERE package_min = 0.0 AND package_lpa > 0.0;

-- Add unique constraint so same company cannot post same role twice
ALTER TABLE Companies
  ADD UNIQUE KEY IF NOT EXISTS uq_company_role (company_name, job_role);
