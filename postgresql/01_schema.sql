-- ============================================================================
-- Project: Hospital & Clinic Appointment & Billing Management System
-- Dialect: PostgreSQL 14+ / 18+
-- Script: postgresql/01_schema.sql - Database Schema Definition
-- ============================================================================

-- If creating a fresh database (run in psql as postgres user):
-- CREATE DATABASE hospital_clinic_db;
-- \c hospital_clinic_db;

-- Drop tables in reverse foreign key order if re-running
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS medical_records CASCADE;
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS doctor_schedules CASCADE;
DROP TABLE IF EXISTS doctors CASCADE;
DROP TABLE IF EXISTS specializations CASCADE;

-- ----------------------------------------------------------------------------
-- Table 1: Specializations
-- ----------------------------------------------------------------------------
CREATE TABLE specializations (
    specialization_id SERIAL PRIMARY KEY,
    specialization_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- Table 2: Doctors
-- ----------------------------------------------------------------------------
CREATE TABLE doctors (
    doctor_id SERIAL PRIMARY KEY,
    specialization_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE,
    qualification VARCHAR(100) NOT NULL,
    experience_years INT NOT NULL CHECK (experience_years >= 0),
    consultation_fee NUMERIC(10, 2) NOT NULL CHECK (consultation_fee >= 0),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'On Leave', 'Inactive')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_doctor_specialization FOREIGN KEY (specialization_id) 
        REFERENCES specializations(specialization_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ----------------------------------------------------------------------------
-- Table 3: Doctor Schedules (Weekly Availability)
-- ----------------------------------------------------------------------------
CREATE TABLE doctor_schedules (
    schedule_id SERIAL PRIMARY KEY,
    doctor_id INT NOT NULL,
    day_of_week VARCHAR(10) NOT NULL CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_duration_minutes INT DEFAULT 30 CHECK (slot_duration_minutes > 0),
    max_patients INT DEFAULT 20 CHECK (max_patients > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_schedule_doctor FOREIGN KEY (doctor_id) 
        REFERENCES doctors(doctor_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_doctor_day UNIQUE (doctor_id, day_of_week)
);

-- ----------------------------------------------------------------------------
-- Table 4: Patients
-- ----------------------------------------------------------------------------
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    blood_group VARCHAR(5) CHECK (blood_group IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(100) UNIQUE,
    address VARCHAR(255),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- Table 5: Appointments
-- ----------------------------------------------------------------------------
CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    appointment_number VARCHAR(30) NOT NULL UNIQUE,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'Scheduled' CHECK (status IN ('Scheduled', 'Confirmed', 'Completed', 'Cancelled', 'No-Show')),
    reason_for_visit VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_appointment_patient FOREIGN KEY (patient_id) 
        REFERENCES patients(patient_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_appointment_doctor FOREIGN KEY (doctor_id) 
        REFERENCES doctors(doctor_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_doctor_slot UNIQUE (doctor_id, appointment_date, appointment_time)
);

-- ----------------------------------------------------------------------------
-- Table 6: Medical Records / Prescriptions
-- ----------------------------------------------------------------------------
CREATE TABLE medical_records (
    record_id SERIAL PRIMARY KEY,
    appointment_id INT NOT NULL UNIQUE,
    symptoms TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    prescribed_tests TEXT,
    medication_prescriptions TEXT,
    doctor_notes TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_record_appointment FOREIGN KEY (appointment_id) 
        REFERENCES appointments(appointment_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- ----------------------------------------------------------------------------
-- Table 7: Invoices (Billing Tracking)
-- ----------------------------------------------------------------------------
CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(30) NOT NULL UNIQUE,
    appointment_id INT NOT NULL UNIQUE,
    patient_id INT NOT NULL,
    invoice_date DATE NOT NULL,
    consultation_fee NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (consultation_fee >= 0),
    procedure_charges NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (procedure_charges >= 0),
    medication_charges NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (medication_charges >= 0),
    discount_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (discount_amount >= 0),
    tax_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (tax_amount >= 0),
    total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount >= 0),
    paid_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (paid_amount >= 0),
    payment_status VARCHAR(20) DEFAULT 'Unpaid' CHECK (payment_status IN ('Unpaid', 'Partially Paid', 'Paid', 'Refunded')),
    due_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_invoice_appointment FOREIGN KEY (appointment_id) 
        REFERENCES appointments(appointment_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_invoice_patient FOREIGN KEY (patient_id) 
        REFERENCES patients(patient_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ----------------------------------------------------------------------------
-- Table 8: Payments (Payment Transactions Tracking)
-- ----------------------------------------------------------------------------
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    payment_reference VARCHAR(30) NOT NULL UNIQUE,
    invoice_id INT NOT NULL,
    payment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    amount_paid NUMERIC(10, 2) NOT NULL CHECK (amount_paid > 0),
    payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('Cash', 'Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Insurance')),
    payment_status VARCHAR(20) DEFAULT 'Success' CHECK (payment_status IN ('Success', 'Failed', 'Refunded')),
    transaction_reference VARCHAR(100),
    notes VARCHAR(255),
    CONSTRAINT fk_payment_invoice FOREIGN KEY (invoice_id) 
        REFERENCES invoices(invoice_id) ON DELETE CASCADE ON UPDATE CASCADE
);

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
