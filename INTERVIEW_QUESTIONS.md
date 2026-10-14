# 🎯 Hospital Management SQL Project - Interview Questions & Answers

This document covers frequently asked technical questions by interviewers for Data Analyst, SQL Developer, and Database Engineer roles regarding this project.

---

### Q1: How did you prevent double-booking for the same doctor at the same time?
**Answer:**
We enforced this at two levels:
1. **Database Constraint (Integrity Level):** 
   A composite `UNIQUE KEY` was placed on `(doctor_id, appointment_date, appointment_time)` in the `appointments` table. Any duplicate booking attempt immediately raises a unique constraint violation error.
2. **Business Logic (Stored Procedure & Trigger Level):**
   In `sp_book_appointment` and `trg_validate_doctor_availability`, we explicitly check if the doctor is currently 'Active' (not 'On Leave' or 'Inactive') and whether an overlapping appointment already exists before attempting insertion.

---

### Q2: What normal form is your database designed in, and why?
**Answer:**
The schema is normalized to **Third Normal Form (3NF)**:
* **1NF:** All attributes contain atomic values, and each record has a Primary Key.
* **2NF:** No partial functional dependencies exist on composite keys (all non-key attributes depend fully on the primary key).
* **3NF:** No transitive dependencies exist. For example, `specialization_name` is stored in `specializations` rather than duplicating it across multiple `doctors` rows, and payment transactions are separated from invoice headers.

---

### Q3: Explain how the invoice payment reconciliation works automatically.
**Answer:**
Instead of relying on manual application-level updates, we built `trg_reconcile_invoice_payment` on the `payments` table. Whenever an `AFTER INSERT` happens on `payments`:
1. It calculates `SUM(amount)` for the relevant `invoice_id`.
2. Compares the total paid against `invoices.net_amount`.
3. Automatically updates `invoices.paid_amount` and marks status as `'Paid'` (if balance = 0) or `'Partially Paid'` (if balance > 0).

---

### Q4: Which window functions did you use and what business problems did they solve?
**Answer:**
* **`DENSE_RANK() OVER (ORDER BY gross_revenue DESC)`:**
  Used in the Doctor Leaderboard to rank doctors by earned revenue without skipping rank numbers in case of ties.
* **`SUM(daily_collection) OVER (ORDER BY payment_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`:**
  Used to calculate the cumulative running total of clinic revenue day-over-day to track monthly targets and collection velocity.

---

### Q5: How did you segment patients into First-Time vs Repeat (Loyal) cohorts?
**Answer:**
Using a Common Table Expression (CTE):
```sql
WITH PatientVisitStats AS (
    SELECT 
        patient_id,
        COUNT(appointment_id) AS total_visits,
        MIN(appointment_date) AS first_visit,
        MAX(appointment_date) AS latest_visit
    FROM appointments
    WHERE status = 'Completed'
    GROUP BY patient_id
)
SELECT 
    patient_id,
    total_visits,
    CASE 
        WHEN total_visits > 1 THEN 'Repeat / Loyal Patient'
        ELSE 'First-Time / One-Time'
    END AS cohort_category
FROM PatientVisitStats;
```
This enables clinic administrators to measure patient retention rates and target follow-up communications.

---

### Q6: If this database scales to 10 million appointments, how would you optimize performance?
**Answer:**
1. **Composite Indexing:** Create targeted B-Tree indexes on `(doctor_id, appointment_date)` and `(patient_id, appointment_date)`.
2. **Partitioning:** Implement table range partitioning on `appointments` and `invoices` by year or month (e.g., `PARTITION BY RANGE (YEAR(appointment_date))`).
3. **Materialized Views / Aggregated Rollups:** Pre-calculate daily revenue summaries and monthly doctor rankings rather than scanning historical raw tables repeatedly.
4. **Archiving:** Move closed appointments and settled invoices older than 3-5 years into an archive/cold storage database.
