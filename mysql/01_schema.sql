-- ============================================================================
-- Project: Hospital & Clinic Appointment & Billing Management System
-- Database: MySQL / MariaDB (ANSI SQL Compliant)
-- Script: 01_schema.sql - Database Schema Definition
-- ============================================================================

DROP DATABASE IF EXISTS hospital_clinic_db;
CREATE DATABASE hospital_clinic_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hospital_clinic_db;

-- ----------------------------------------------------------------------------
-- Table 1: Specializations
-- Medical departments/specialties (e.g., Cardiology, Dermatology, etc.)
-- ----------------------------------------------------------------------------
CREATE TABLE specializations (
    specialization_id INT AUTO_INCREMENT PRIMARY KEY,
    specialization_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 2: Doctors
-- Registered doctors associated with their respective specializations
-- ----------------------------------------------------------------------------
CREATE TABLE doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    specialization_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE,
    qualification VARCHAR(100) NOT NULL,
    experience_years INT NOT NULL CHECK (experience_years >= 0),
    consultation_fee DECIMAL(10, 2) NOT NULL CHECK (consultation_fee >= 0),
    status ENUM('Active', 'On Leave', 'Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_doctor_specialization FOREIGN KEY (specialization_id) 
        REFERENCES specializations(specialization_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 3: Doctor Schedules (Weekly Availability)
-- Days and working hours when doctors take consultations
-- ----------------------------------------------------------------------------
CREATE TABLE doctor_schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_duration_minutes INT DEFAULT 30 CHECK (slot_duration_minutes > 0),
    max_patients INT DEFAULT 20 CHECK (max_patients > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_schedule_doctor FOREIGN KEY (doctor_id) 
        REFERENCES doctors(doctor_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_doctor_day UNIQUE (doctor_id, day_of_week)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 4: Patients
-- Patient demographic and contact information
-- ----------------------------------------------------------------------------
CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') DEFAULT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100) UNIQUE,
    address VARCHAR(255),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 5: Appointments
-- Scheduled, confirmed, completed, or cancelled patient bookings
-- ----------------------------------------------------------------------------
CREATE TABLE appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_number VARCHAR(30) NOT NULL UNIQUE,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('Scheduled', 'Confirmed', 'Completed', 'Cancelled', 'No-Show') DEFAULT 'Scheduled',
    reason_for_visit VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_appointment_patient FOREIGN KEY (patient_id) 
        REFERENCES patients(patient_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_appointment_doctor FOREIGN KEY (doctor_id) 
        REFERENCES doctors(doctor_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    -- Prevent double booking of doctor at the exact same date & time slot:
    CONSTRAINT uq_doctor_slot UNIQUE (doctor_id, appointment_date, appointment_time)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 6: Medical Records / Prescriptions
-- Clinical notes and diagnoses generated upon consultation completion
-- ----------------------------------------------------------------------------
CREATE TABLE medical_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL UNIQUE,
    symptoms TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    prescribed_tests TEXT,
    medication_prescriptions TEXT,
    doctor_notes TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_record_appointment FOREIGN KEY (appointment_id) 
        REFERENCES appointments(appointment_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 7: Invoices (Billing Tracking)
-- Itemized invoices linked to appointments
-- ----------------------------------------------------------------------------
CREATE TABLE invoices (
    invoice_id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(30) NOT NULL UNIQUE,
    appointment_id INT NOT NULL UNIQUE,
    patient_id INT NOT NULL,
    invoice_date DATE NOT NULL,
    consultation_fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (consultation_fee >= 0),
    procedure_charges DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (procedure_charges >= 0),
    medication_charges DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (medication_charges >= 0),
    discount_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (discount_amount >= 0),
    tax_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (tax_amount >= 0),
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    paid_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (paid_amount >= 0),
    payment_status ENUM('Unpaid', 'Partially Paid', 'Paid', 'Refunded') DEFAULT 'Unpaid',
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_invoice_appointment FOREIGN KEY (appointment_id) 
        REFERENCES appointments(appointment_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_invoice_patient FOREIGN KEY (patient_id) 
        REFERENCES patients(patient_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 8: Payments (Payment Transactions Tracking)
-- Payment records against invoices (supports multiple partial payments)
-- ----------------------------------------------------------------------------
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    payment_reference VARCHAR(30) NOT NULL UNIQUE,
    invoice_id INT NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount_paid DECIMAL(10, 2) NOT NULL CHECK (amount_paid > 0),
    payment_method ENUM('Cash', 'Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Insurance') NOT NULL,
    payment_status ENUM('Success', 'Failed', 'Refunded') DEFAULT 'Success',
    transaction_reference VARCHAR(100),
    notes VARCHAR(255),
    CONSTRAINT fk_payment_invoice FOREIGN KEY (invoice_id) 
        REFERENCES invoices(invoice_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Indexes for High Performance Queries
-- ----------------------------------------------------------------------------
CREATE INDEX idx_doctors_specialization ON doctors(specialization_id);
CREATE INDEX idx_appointments_date_status ON appointments(appointment_date, status);
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX idx_invoices_patient ON invoices(patient_id);
CREATE INDEX idx_invoices_status ON invoices(payment_status);
CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_payments_invoice ON payments(invoice_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
