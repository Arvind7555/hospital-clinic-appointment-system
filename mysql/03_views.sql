-- ============================================================================
-- Project: Hospital & Clinic Appointment & Billing Management System
-- Script: 03_views.sql - Operational & Business Analytics Views
-- ============================================================================

USE hospital_clinic_db;

-- ----------------------------------------------------------------------------
-- View 1: vw_doctor_roster
-- Complete doctor directory with specialization, fee, and weekly schedules
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_doctor_roster AS
SELECT 
    d.doctor_id,
    CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
    s.specialization_name,
    d.qualification,
    d.experience_years,
    d.consultation_fee,
    d.status AS doctor_status,
    d.email,
    d.phone,
    GROUP_CONCAT(
        CONCAT(sch.day_of_week, ' (', TIME_FORMAT(sch.start_time, '%H:%i'), '-', TIME_FORMAT(sch.end_time, '%H:%i'), ')')
        ORDER BY FIELD(sch.day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
        SEPARATOR ', '
    ) AS weekly_schedule
FROM doctors d
JOIN specializations s ON d.specialization_id = s.specialization_id
LEFT JOIN doctor_schedules sch ON d.doctor_id = sch.doctor_id
GROUP BY d.doctor_id, d.first_name, d.last_name, s.specialization_name, d.qualification, d.experience_years, d.consultation_fee, d.status, d.email, d.phone;

-- ----------------------------------------------------------------------------
-- View 2: vw_appointment_details
-- Full appointment summary including patient info, doctor, department, and status
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_appointment_details AS
SELECT 
    a.appointment_id,
    a.appointment_number,
    a.appointment_date,
    TIME_FORMAT(a.appointment_time, '%h:%i %p') AS appointment_time,
    a.status AS appointment_status,
    a.reason_for_visit,
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) AS patient_age,
    p.gender AS patient_gender,
    p.blood_group,
    p.phone AS patient_phone,
    d.doctor_id,
    CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
    s.specialization_name,
    d.consultation_fee
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN doctors d ON a.doctor_id = d.doctor_id
JOIN specializations s ON d.specialization_id = s.specialization_id;

-- ----------------------------------------------------------------------------
-- View 3: vw_billing_invoices_detail
-- Complete billing details linking invoice, patient, appointment, and payment state
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_billing_invoices_detail AS
SELECT 
    i.invoice_id,
    i.invoice_number,
    i.invoice_date,
    a.appointment_number,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.phone AS patient_phone,
    CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
    s.specialization_name,
    i.consultation_fee,
    i.procedure_charges,
    i.medication_charges,
    i.discount_amount,
    i.tax_amount,
    i.total_amount,
    i.paid_amount,
    (i.total_amount - i.paid_amount) AS balance_due,
    i.payment_status,
    i.due_date,
    CASE 
        WHEN i.payment_status = 'Paid' THEN 'Settled'
        WHEN i.due_date < CURDATE() THEN 'Overdue'
        ELSE 'Due'
    END AS billing_alert
FROM invoices i
JOIN appointments a ON i.appointment_id = a.appointment_id
JOIN patients p ON i.patient_id = p.patient_id
JOIN doctors d ON a.doctor_id = d.doctor_id
JOIN specializations s ON d.specialization_id = s.specialization_id;

-- ----------------------------------------------------------------------------
-- View 4: vw_patient_billing_summary
-- Aggregated financial statement per patient
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_patient_billing_summary AS
SELECT 
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.phone,
    p.email,
    COUNT(DISTINCT a.appointment_id) AS total_appointments,
    COUNT(DISTINCT i.invoice_id) AS total_invoices,
    COALESCE(SUM(i.total_amount), 0.00) AS total_billed,
    COALESCE(SUM(i.paid_amount), 0.00) AS total_paid,
    COALESCE(SUM(i.total_amount - i.paid_amount), 0.00) AS total_outstanding
FROM patients p
LEFT JOIN appointments a ON p.patient_id = a.patient_id
LEFT JOIN invoices i ON a.appointment_id = i.appointment_id
GROUP BY p.patient_id, p.first_name, p.last_name, p.phone, p.email;

-- ----------------------------------------------------------------------------
-- View 5: vw_specialization_performance
-- Departmental KPI overview: appointments, patient load, revenue & recovery rate
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_specialization_performance AS
SELECT 
    s.specialization_id,
    s.specialization_name,
    COUNT(DISTINCT d.doctor_id) AS total_doctors,
    COUNT(DISTINCT a.appointment_id) AS total_appointments,
    SUM(CASE WHEN a.status = 'Completed' THEN 1 ELSE 0 END) AS completed_appointments,
    SUM(CASE WHEN a.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_appointments,
    COALESCE(SUM(i.total_amount), 0.00) AS gross_revenue,
    COALESCE(SUM(i.paid_amount), 0.00) AS collected_revenue,
    COALESCE(SUM(i.total_amount - i.paid_amount), 0.00) AS pending_revenue,
    ROUND(
        CASE 
            WHEN SUM(i.total_amount) > 0 THEN (SUM(i.paid_amount) / SUM(i.total_amount)) * 100 
            ELSE 0 
        END, 2
    ) AS payment_collection_rate_pct
FROM specializations s
LEFT JOIN doctors d ON s.specialization_id = d.specialization_id
LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
LEFT JOIN invoices i ON a.appointment_id = i.appointment_id
GROUP BY s.specialization_id, s.specialization_name;
