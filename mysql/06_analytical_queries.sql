-- ============================================================================
-- Project: Hospital & Clinic Appointment & Billing Management System
-- Script: 06_analytical_queries.sql - Advanced SQL Business & Analytical Queries
-- Topics: Window Functions, CTEs, Aggregations, Cohorts, and KPI Reporting
-- ============================================================================

USE hospital_clinic_db;

-- ----------------------------------------------------------------------------
-- QUERY 1: Doctor Performance & Revenue Leaderboard
-- Uses: DENSE_RANK() Window Function, Aggregation
-- Business Question: Rank doctors by total revenue generated and consultations completed.
-- ----------------------------------------------------------------------------
SELECT 
    d.doctor_id,
    CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
    s.specialization_name,
    COUNT(DISTINCT a.appointment_id) AS total_consultations,
    COALESCE(SUM(i.total_amount), 0.00) AS total_revenue_generated,
    COALESCE(SUM(i.paid_amount), 0.00) AS total_revenue_collected,
    DENSE_RANK() OVER (ORDER BY COALESCE(SUM(i.total_amount), 0) DESC) AS revenue_rank
FROM doctors d
JOIN specializations s ON d.specialization_id = s.specialization_id
LEFT JOIN appointments a ON d.doctor_id = a.doctor_id AND a.status = 'Completed'
LEFT JOIN invoices i ON a.appointment_id = i.appointment_id
GROUP BY d.doctor_id, d.first_name, d.last_name, s.specialization_name
ORDER BY revenue_rank;


-- ----------------------------------------------------------------------------
-- QUERY 2: Running Total of Daily Clinic Revenue
-- Uses: Window Function (SUM() OVER (ORDER BY ...))
-- Business Question: Track cumulative revenue growth day-by-day.
-- ----------------------------------------------------------------------------
SELECT 
    DATE(p.payment_date) AS payment_day,
    COUNT(p.payment_id) AS transactions_count,
    SUM(p.amount_paid) AS daily_collection,
    SUM(SUM(p.amount_paid)) OVER (ORDER BY DATE(p.payment_date)) AS cumulative_revenue_to_date
FROM payments p
WHERE p.payment_status = 'Success'
GROUP BY DATE(p.payment_date)
ORDER BY payment_day;


-- ----------------------------------------------------------------------------
-- QUERY 3: Patient Retention & Repeat Visit Analysis
-- Uses: Common Table Expressions (CTEs), CASE Statements
-- Business Question: Classify patients into One-Time vs Repeat Visitors and analyze retention.
-- ----------------------------------------------------------------------------
WITH patient_visit_counts AS (
    SELECT 
        p.patient_id,
        CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
        p.gender,
        p.phone,
        COUNT(a.appointment_id) AS total_visits,
        MIN(a.appointment_date) AS first_visit_date,
        MAX(a.appointment_date) AS latest_visit_date
    FROM patients p
    LEFT JOIN appointments a ON p.patient_id = a.patient_id
    GROUP BY p.patient_id, p.first_name, p.last_name, p.gender, p.phone
)
SELECT 
    patient_id,
    patient_name,
    gender,
    total_visits,
    first_visit_date,
    latest_visit_date,
    CASE 
        WHEN total_visits = 0 THEN 'Never Booked'
        WHEN total_visits = 1 THEN 'First-Time / One-Time'
        ELSE 'Repeat / Loyal Patient'
    END AS patient_category
FROM patient_visit_counts
ORDER BY total_visits DESC, patient_name;


-- ----------------------------------------------------------------------------
-- QUERY 4: Appointment Status Distribution by Specialization
-- Uses: Conditional Aggregation (SUM CASE), Percentages
-- Business Question: What is the completion, cancellation, and no-show rate per medical department?
-- ----------------------------------------------------------------------------
SELECT 
    s.specialization_name,
    COUNT(a.appointment_id) AS total_booked,
    SUM(CASE WHEN a.status = 'Completed' THEN 1 ELSE 0 END) AS completed_count,
    SUM(CASE WHEN a.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
    SUM(CASE WHEN a.status = 'No-Show' THEN 1 ELSE 0 END) AS noshow_count,
    ROUND(SUM(CASE WHEN a.status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(a.appointment_id), 0), 1) AS completion_rate_pct,
    ROUND(SUM(CASE WHEN a.status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(a.appointment_id), 0), 1) AS cancellation_rate_pct
FROM specializations s
LEFT JOIN doctors d ON s.specialization_id = d.specialization_id
LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
GROUP BY s.specialization_id, s.specialization_name
HAVING COUNT(a.appointment_id) > 0
ORDER BY total_booked DESC;


-- ----------------------------------------------------------------------------
-- QUERY 5: Outstanding Balance Aging Analysis
-- Uses: DATEDIFF, CASE categorizations
-- Business Question: Identify unpaid bills and bucket them by delinquency aging.
-- ----------------------------------------------------------------------------
SELECT 
    i.invoice_number,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.phone AS patient_contact,
    i.invoice_date,
    i.due_date,
    i.total_amount,
    i.paid_amount,
    (i.total_amount - i.paid_amount) AS outstanding_amount,
    DATEDIFF(CURDATE(), i.due_date) AS days_overdue,
    CASE 
        WHEN DATEDIFF(CURDATE(), i.due_date) <= 0 THEN 'Current (Not Overdue)'
        WHEN DATEDIFF(CURDATE(), i.due_date) BETWEEN 1 AND 7 THEN '1 - 7 Days Overdue'
        WHEN DATEDIFF(CURDATE(), i.due_date) BETWEEN 8 AND 15 THEN '8 - 15 Days Overdue'
        ELSE '15+ Days Delinquent'
    END AS aging_bucket
FROM invoices i
JOIN patients p ON i.patient_id = p.patient_id
WHERE i.payment_status IN ('Unpaid', 'Partially Paid')
ORDER BY days_overdue DESC;


-- ----------------------------------------------------------------------------
-- QUERY 6: Peak Appointment Hours Distribution
-- Uses: HOUR(), Aggregation
-- Business Question: Which hours of the day experience highest clinic traffic?
-- ----------------------------------------------------------------------------
SELECT 
    HOUR(appointment_time) AS hour_of_day,
    CONCAT(TIME_FORMAT(appointment_time, '%h:00 %p'), ' - ', TIME_FORMAT(ADDTIME(appointment_time, '01:00:00'), '%h:00 %p')) AS time_slot,
    COUNT(*) AS total_appointments,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM appointments), 2) AS pct_of_total_traffic
FROM appointments
GROUP BY HOUR(appointment_time)
ORDER BY total_appointments DESC;


-- ----------------------------------------------------------------------------
-- QUERY 7: Preferred Payment Methods Breakdown
-- Uses: Aggregation, SUM, Percentage calculation
-- Business Question: Which payment channels (UPI, Cards, Cash, Insurance) are most utilized?
-- ----------------------------------------------------------------------------
SELECT 
    p.payment_method,
    COUNT(p.payment_id) AS total_transactions,
    SUM(p.amount_paid) AS total_volume_inr,
    ROUND(SUM(p.amount_paid) * 100.0 / (SELECT SUM(amount_paid) FROM payments WHERE payment_status = 'Success'), 2) AS percentage_of_revenue
FROM payments p
WHERE p.payment_status = 'Success'
GROUP BY p.payment_method
ORDER BY total_volume_inr DESC;


-- ----------------------------------------------------------------------------
-- QUERY 8: Patient Demographics & Average Spend by Age Group
-- Uses: CTE, TIMESTAMPDIFF, Aggregation
-- Business Question: How does healthcare expenditure differ across age demographics?
-- ----------------------------------------------------------------------------
WITH patient_age_groups AS (
    SELECT 
        p.patient_id,
        TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) AS age,
        CASE 
            WHEN TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) < 18 THEN 'Pediatric (<18)'
            WHEN TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) BETWEEN 18 AND 35 THEN 'Young Adult (18-35)'
            WHEN TIMESTAMPDIFF(YEAR, p.dob, CURDATE()) BETWEEN 36 AND 55 THEN 'Middle-Aged (36-55)'
            ELSE 'Senior Citizen (55+)'
        END AS age_group,
        COALESCE(SUM(i.total_amount), 0.00) AS total_billed
    FROM patients p
    LEFT JOIN appointments a ON p.patient_id = a.patient_id
    LEFT JOIN invoices i ON a.appointment_id = i.appointment_id
    GROUP BY p.patient_id, p.dob
)
SELECT 
    age_group,
    COUNT(patient_id) AS patient_count,
    SUM(total_billed) AS group_total_revenue,
    ROUND(AVG(total_billed), 2) AS average_spend_per_patient
FROM patient_age_groups
GROUP BY age_group
ORDER BY group_total_revenue DESC;
