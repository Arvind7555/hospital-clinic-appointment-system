"""
================================================================================
Hospital & Clinic Appointment & Billing Management System - Demo Runner
Runs using Python's built-in SQLite engine with zero extra dependencies!
================================================================================
"""

import sqlite3
import os
import sys

DB_FILE = "hospital_demo.db"

def get_connection():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def print_section(title):
    print("\n" + "=" * 80)
    print(f" {title.upper()} ".center(80, "="))
    print("=" * 80)

def print_table(cursor, headers, title=None):
    rows = cursor.fetchall()
    if title:
        print(f"\n>>> [ {title} ]")
    if not rows:
        print("  (No records found)")
        return

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val) if val is not None else "NULL"))

    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    header_line = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    
    print(sep)
    print(header_line)
    print(sep)
    for row in rows:
        print("| " + " | ".join(str(val if val is not None else "NULL").ljust(widths[i]) for i, val in enumerate(row)) + " |")
    print(sep)
    print(f"Total Rows: {len(rows)}\n")

def init_schema(conn):
    print("\n[+] Initializing Database Schema...")
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE specializations (
        specialization_id INTEGER PRIMARY KEY AUTOINCREMENT,
        specialization_name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE doctors (
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        specialization_id INTEGER NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL UNIQUE,
        qualification TEXT NOT NULL,
        experience_years INTEGER NOT NULL CHECK (experience_years >= 0),
        consultation_fee REAL NOT NULL CHECK (consultation_fee >= 0),
        status TEXT DEFAULT 'Active' CHECK (status IN ('Active', 'On Leave', 'Inactive')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (specialization_id) REFERENCES specializations(specialization_id)
    );

    CREATE TABLE doctor_schedules (
        schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER NOT NULL,
        day_of_week TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        slot_duration_minutes INTEGER DEFAULT 30,
        max_patients INTEGER DEFAULT 20,
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
        UNIQUE (doctor_id, day_of_week)
    );

    CREATE TABLE patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        dob DATE NOT NULL,
        gender TEXT NOT NULL,
        blood_group TEXT,
        phone TEXT NOT NULL UNIQUE,
        email TEXT UNIQUE,
        address TEXT,
        emergency_contact_name TEXT,
        emergency_contact_phone TEXT,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE appointments (
        appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_number TEXT NOT NULL UNIQUE,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date DATE NOT NULL,
        appointment_time TEXT NOT NULL,
        status TEXT DEFAULT 'Scheduled',
        reason_for_visit TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
        UNIQUE (doctor_id, appointment_date, appointment_time)
    );

    CREATE TABLE medical_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER NOT NULL UNIQUE,
        symptoms TEXT NOT NULL,
        diagnosis TEXT NOT NULL,
        prescribed_tests TEXT,
        medication_prescriptions TEXT,
        doctor_notes TEXT,
        follow_up_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
    );

    CREATE TABLE invoices (
        invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT NOT NULL UNIQUE,
        appointment_id INTEGER NOT NULL UNIQUE,
        patient_id INTEGER NOT NULL,
        invoice_date DATE NOT NULL,
        consultation_fee REAL NOT NULL DEFAULT 0.0,
        procedure_charges REAL NOT NULL DEFAULT 0.0,
        medication_charges REAL NOT NULL DEFAULT 0.0,
        discount_amount REAL NOT NULL DEFAULT 0.0,
        tax_amount REAL NOT NULL DEFAULT 0.0,
        total_amount REAL NOT NULL,
        paid_amount REAL NOT NULL DEFAULT 0.0,
        payment_status TEXT DEFAULT 'Unpaid',
        due_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    );

    CREATE TABLE payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_reference TEXT NOT NULL UNIQUE,
        invoice_id INTEGER NOT NULL,
        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        amount_paid REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payment_status TEXT DEFAULT 'Success',
        transaction_reference TEXT,
        notes TEXT,
        FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
    );
    """)
    conn.commit()
    print("    [OK] 8 Core Tables created successfully.")

def seed_data(conn):
    print("\n[+] Seeding Demo Data...")
    cur = conn.cursor()
    
    # 1. Specializations
    specializations = [
        (1, 'General Medicine', 'Primary healthcare, chronic disease management, and regular checkups'),
        (2, 'Cardiology', 'Heart health, cardiovascular disorders, and hypertension care'),
        (3, 'Dermatology', 'Skin, hair, nail disorders, and cosmetic dermatology'),
        (4, 'Orthopedics', 'Musculoskeletal issues, bone fractures, and joint replacement'),
        (5, 'Pediatrics', 'Medical care for infants, children, and adolescents'),
        (6, 'Neurology', 'Disorders of the nervous system, brain, and spinal cord'),
        (7, 'Gynecology & Obstetrics', 'Women reproductive health, prenatal, and maternity care'),
        (8, 'Ophthalmology', 'Eye care, vision testing, and surgical ophthalmic treatments')
    ]
    cur.executemany("INSERT INTO specializations VALUES (?,?,?,CURRENT_TIMESTAMP)", specializations)

    # 2. Doctors
    doctors = [
        (1, 1, 'Rajesh', 'Sharma', 'dr.rajesh.sharma@hospital.com', '+91-9876543210', 'MBBS, MD', 14, 600.00, 'Active'),
        (2, 2, 'Priya', 'Nair', 'dr.priya.nair@hospital.com', '+91-9876543211', 'MBBS, DM', 12, 1200.00, 'Active'),
        (3, 3, 'Amit', 'Verma', 'dr.amit.verma@hospital.com', '+91-9876543212', 'MBBS, MD', 8, 800.00, 'Active'),
        (4, 4, 'Suresh', 'Menon', 'dr.suresh.menon@hospital.com', '+91-9876543213', 'MBBS, MS', 16, 1000.00, 'Active'),
        (5, 5, 'Ananya', 'Deshmukh', 'dr.ananya.deshmukh@hospital.com', '+91-9876543214', 'MBBS, DCH', 9, 700.00, 'Active'),
        (6, 6, 'Vikram', 'Malhotra', 'dr.vikram.malhotra@hospital.com', '+91-9876543215', 'MBBS, DM', 15, 1500.00, 'Active'),
        (7, 7, 'Sunita', 'Rao', 'dr.sunita.rao@hospital.com', '+91-9876543216', 'MBBS, MS', 11, 900.00, 'Active'),
        (8, 8, 'Kavita', 'Singhania', 'dr.kavita.s@hospital.com', '+91-9876543217', 'MBBS, MS', 7, 750.00, 'Active'),
        (9, 1, 'Arjun', 'Kapoor', 'dr.arjun.k@hospital.com', '+91-9876543218', 'MBBS, DNB', 6, 500.00, 'Active'),
        (10, 2, 'Rohan', 'Gupta', 'dr.rohan.gupta@hospital.com', '+91-9876543219', 'MBBS, MD', 18, 1400.00, 'Active')
    ]
    cur.executemany("INSERT INTO doctors VALUES (?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)", doctors)

    # 3. Patients
    patients = [
        (1, 'Aarav', 'Mehta', '1988-04-12', 'Male', 'O+', '+91-9123456701', 'aarav.mehta@example.com', 'Mumbai', 'Neha Mehta', '+91-9123456791'),
        (2, 'Sneha', 'Patil', '1995-08-25', 'Female', 'B+', '+91-9123456702', 'sneha.patil@example.com', 'Pune', 'Ramesh Patil', '+91-9123456792'),
        (3, 'Karan', 'Johar', '1982-11-03', 'Male', 'A+', '+91-9123456703', 'karan.j@example.com', 'Noida', 'Simran Johar', '+91-9123456793'),
        (4, 'Pooja', 'Iyer', '1999-01-19', 'Female', 'AB+', '+91-9123456704', 'pooja.iyer@example.com', 'Bengaluru', 'Venkat Iyer', '+91-9123456794'),
        (5, 'Manish', 'Chopra', '1976-06-30', 'Male', 'O-', '+91-9123456705', 'manish.c@example.com', 'Delhi', 'Geeta Chopra', '+91-9123456795'),
        (6, 'Divya', 'Bansal', '2002-09-14', 'Female', 'A-', '+91-9123456706', 'divya.b@example.com', 'Jaipur', 'Mohan Bansal', '+91-9123456796'),
        (7, 'Rahul', 'Verma', '1990-12-05', 'Male', 'B-', '+91-9123456707', 'rahul.v@example.com', 'Hyderabad', 'Pooja Verma', '+91-9123456797'),
        (8, 'Tanvi', 'Shah', '1993-03-22', 'Female', 'O+', '+91-9123456708', 'tanvi.shah@example.com', 'Ahmedabad', 'Jignesh Shah', '+91-9123456798'),
        (9, 'Kabir', 'Khan', '2018-05-10', 'Male', 'AB-', '+91-9123456709', 'farhan.khan@example.com', 'Kolkata', 'Farhan Khan', '+91-9123456799'),
        (10, 'Ritu', 'Mishra', '1985-07-17', 'Female', 'B+', '+91-9123456710', 'ritu.m@example.com', 'Lucknow', 'Sanjay Mishra', '+91-9123456780'),
        (11, 'Deepak', 'Saini', '1991-10-28', 'Male', 'A+', '+91-9123456711', 'deepak.saini@example.com', 'Chandigarh', 'Komal Saini', '+91-9123456781'),
        (12, 'Meera', 'Nambiar', '1996-02-14', 'Female', 'O+', '+91-9123456712', 'meera.n@example.com', 'Kochi', 'Unni Nambiar', '+91-9123456782'),
        (13, 'Gaurav', 'Tiwari', '1987-12-20', 'Male', 'B+', '+91-9123456713', 'gaurav.t@example.com', 'Kanpur', 'Archana Tiwari', '+91-9123456783'),
        (14, 'Ishaan', 'Bhatia', '2019-11-08', 'Male', 'O+', '+91-9123456714', 'varun.bhatia@example.com', 'Gurugram', 'Varun Bhatia', '+91-9123456784'),
        (15, 'Ananya', 'Saxena', '1994-04-05', 'Female', 'AB+', '+91-9123456715', 'ananya.s@example.com', 'Bhopal', 'Vivek Saxena', '+91-9123456785')
    ]
    cur.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)", patients)

    # 4. Appointments
    appointments = [
        (1,  'APT-2026-0001', 1,  1,  '2026-10-02', '09:30:00', 'Completed', 'Persistent viral fever and dry cough', 'Recovered'),
        (2,  'APT-2026-0002', 2,  3,  '2026-10-03', '14:30:00', 'Completed', 'Severe acne flare-up and rash', 'Medication prescribed'),
        (3,  'APT-2026-0003', 3,  2,  '2026-10-05', '10:00:00', 'Completed', 'Chest discomfort and shortness of breath', 'ECG Normal'),
        (4,  'APT-2026-0004', 4,  7,  '2026-10-06', '09:30:00', 'Completed', 'Routine prenatal checkup (2nd trimester)', 'Normal scan'),
        (5,  'APT-2026-0005', 5,  4,  '2026-10-07', '14:30:00', 'Completed', 'Acute right knee pain after jogging', 'Meniscus sprain'),
        (6,  'APT-2026-0006', 6,  8,  '2026-10-08', '15:30:00', 'Completed', 'Blurry vision and headache', 'Prescription glasses'),
        (7,  'APT-2026-0007', 7,  6,  '2026-10-09', '11:30:00', 'Completed', 'Frequent migraine attacks with aura', 'Prophylaxis started'),
        (8,  'APT-2026-0008', 9,  5,  '2026-10-10', '09:30:00', 'Completed', 'Annual pediatric vaccination', 'Vaccinated'),
        (9,  'APT-2026-0009', 8,  1,  '2026-10-12', '10:30:00', 'Completed', 'Diabetes management', 'Insulin adjusted'),
        (10, 'APT-2026-0010', 10, 2,  '2026-10-13', '11:00:00', 'Completed', 'High blood pressure follow-up', 'Stable BP'),
        (11, 'APT-2026-0011', 11, 4,  '2026-10-14', '15:00:00', 'Completed', 'Lower back stiffness and sciatica', 'Physiotherapy advised'),
        (12, 'APT-2026-0012', 12, 3,  '2026-10-15', '15:30:00', 'Cancelled', 'Eczema consultation', 'Patient cancelled'),
        (13, 'APT-2026-0013', 13, 9,  '2026-10-15', '10:00:00', 'No-Show',   'General health checkup', 'Did not arrive'),
        (14, 'APT-2026-0014', 14, 5,  '2026-10-17', '10:00:00', 'Confirmed', 'Childhood asthma review', 'Reports normal'),
        (15, 'APT-2026-0015', 15, 7,  '2026-10-18', '10:30:00', 'Confirmed', 'PCOS evaluation & irregular cycles', 'Ultrasound scheduled'),
        (16, 'APT-2026-0016', 1,  2,  '2026-10-19', '10:30:00', 'Scheduled', 'Cardiovascular risk evaluation', 'Family history CAD'),
        (17, 'APT-2026-0017', 2,  8,  '2026-10-19', '16:00:00', 'Scheduled', 'Dry eyes and irritation', 'First visit'),
        (18, 'APT-2026-0018', 3,  6,  '2026-10-21', '12:00:00', 'Scheduled', 'Nerve tingling in fingers', 'Carpal tunnel screening'),
        (19, 'APT-2026-0019', 5,  10, '2026-10-24', '11:00:00', 'Scheduled', 'Senior cardiac consultation', 'Second opinion'),
        (20, 'APT-2026-0020', 7,  1,  '2026-10-26', '11:00:00', 'Scheduled', 'Gastric reflux and acidity', 'Diet counseling')
    ]
    cur.executemany("INSERT INTO appointments VALUES (?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)", appointments)

    # 5. Invoices
    invoices = [
        (1,  'INV-2026-0001', 1,  1,  '2026-10-02', 600.00,  0.00,   250.00, 50.00, 40.00,   840.00,  840.00,  'Paid',           '2026-10-02'),
        (2,  'INV-2026-0002', 2,  2,  '2026-10-03', 800.00,  300.00, 450.00, 0.00,  77.50,   1627.50, 1627.50, 'Paid',           '2026-10-03'),
        (3,  'INV-2026-0003', 3,  3,  '2026-10-05', 1200.00, 600.00, 150.00, 0.00,  97.50,   2047.50, 2047.50, 'Paid',           '2026-10-05'),
        (4,  'INV-2026-0004', 4,  4,  '2026-10-06', 900.00,  500.00, 300.00, 100.00, 80.00,  1680.00, 1680.00, 'Paid',           '2026-10-06'),
        (5,  'INV-2026-0005', 5,  5,  '2026-10-07', 1000.00, 1200.00, 400.00, 0.00, 130.00,  2730.00, 1500.00, 'Partially Paid', '2026-10-21'),
        (6,  'INV-2026-0006', 6,  6,  '2026-10-08', 750.00,  250.00, 0.00,   0.00,  50.00,   1050.00, 1050.00, 'Paid',           '2026-10-08'),
        (7,  'INV-2026-0007', 7,  7,  '2026-10-09', 1500.00, 0.00,   600.00, 100.00, 100.00, 2100.00, 2100.00, 'Paid',           '2026-10-09'),
        (8,  'INV-2026-0008', 8,  9,  '2026-10-10', 700.00,  1500.00, 200.00, 0.00, 120.00,  2520.00, 2520.00, 'Paid',           '2026-10-10'),
        (9,  'INV-2026-0009', 9,  8,  '2026-10-12', 600.00,  400.00, 350.00, 50.00, 65.00,   1365.00, 1365.00, 'Paid',           '2026-10-12'),
        (10, 'INV-2026-0010', 10, 10, '2026-10-13', 1200.00, 0.00,   200.00, 0.00,  70.00,   1470.00, 700.00,  'Partially Paid', '2026-10-27'),
        (11, 'INV-2026-0011', 11, 11, '2026-10-14', 1000.00, 500.00, 350.00, 0.00,  92.50,   1942.50, 0.00,    'Unpaid',         '2026-10-28'),
        (12, 'INV-2026-0014', 14, 14, '2026-10-14', 700.00,  0.00,   0.00,   0.00,  35.00,   735.00,  735.00,  'Paid',           '2026-10-17'),
        (13, 'INV-2026-0015', 15, 15, '2026-10-14', 900.00,  0.00,   0.00,   0.00,  45.00,   945.00,  0.00,    'Unpaid',         '2026-10-18')
    ]
    cur.executemany("INSERT INTO invoices VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)", invoices)

    # 6. Payments
    payments = [
        (1,  'PAY-2026-0001', 1,  '2026-10-02 10:15:00', 840.00,  'UPI',         'Success', 'UPI/20261002/982181283', 'Paid via Google Pay'),
        (2,  'PAY-2026-0002', 2,  '2026-10-03 15:20:00', 1627.50, 'Credit Card', 'Success', 'TXN_CC_98291039401',     'HDFC Credit Card ending 4412'),
        (3,  'PAY-2026-0003', 3,  '2026-10-05 11:00:00', 2047.50, 'Insurance',   'Success', 'TPA/ICICI/91823901',     'Cashless claim approval by ICICI'),
        (4,  'PAY-2026-0004', 4,  '2026-10-06 10:45:00', 1680.00, 'UPI',         'Success', 'UPI/20261006/812930192', 'Paid via PhonePe'),
        (5,  'PAY-2026-0005', 5,  '2026-10-07 16:00:00', 1500.00, 'Debit Card',  'Success', 'TXN_DC_81029381923',     'Initial partial deposit'),
        (6,  'PAY-2026-0006', 6,  '2026-10-08 16:30:00', 1050.00, 'Cash',        'Success', 'CASH_REC_08102026',      'Desk cash counter payment'),
        (7,  'PAY-2026-0007', 7,  '2026-10-09 12:45:00', 2100.00, 'Net Banking', 'Success', 'NETB_AXIS_091823901',    'Axis Net Banking portal'),
        (8,  'PAY-2026-0008', 8,  '2026-10-10 10:30:00', 2520.00, 'UPI',         'Success', 'UPI/20261010/771928391', 'Paid via Paytm'),
        (9,  'PAY-2026-0009', 9,  '2026-10-12 11:45:00', 1365.00, 'Credit Card', 'Success', 'TXN_CC_90182938190',     'SBI Card ending 9012'),
        (10, 'PAY-2026-0010', 10, '2026-10-13 12:15:00', 700.00,  'Cash',        'Success', 'CASH_REC_13102026',      'Partial cash advance payment'),
        (11, 'PAY-2026-0011', 12, '2026-10-14 14:00:00', 735.00,  'UPI',         'Success', 'UPI/20261014/192830192', 'Advance booking settled')
    ]
    cur.executemany("INSERT INTO payments VALUES (?,?,?,?,?,?,?,?,?)", payments)

    conn.commit()
    print("    [OK] Seeded 8 Specializations, 10 Doctors, 15 Patients, 20 Appointments, 13 Invoices, 11 Payments.")

def run_business_queries(conn):
    cur = conn.cursor()

    # Query 1: Doctor Performance & Revenue Leaderboard
    print_section("QUERY 1: Doctor Revenue Leaderboard & Consultations (DENSE_RANK)")
    q1 = """
    SELECT 
        d.doctor_id,
        'Dr. ' || d.first_name || ' ' || d.last_name AS doctor_name,
        s.specialization_name,
        COUNT(DISTINCT a.appointment_id) AS total_consultations,
        COALESCE(SUM(i.total_amount), 0.0) AS total_revenue_generated,
        COALESCE(SUM(i.paid_amount), 0.0) AS total_revenue_collected,
        DENSE_RANK() OVER (ORDER BY COALESCE(SUM(i.total_amount), 0) DESC) AS revenue_rank
    FROM doctors d
    JOIN specializations s ON d.specialization_id = s.specialization_id
    LEFT JOIN appointments a ON d.doctor_id = a.doctor_id AND a.status = 'Completed'
    LEFT JOIN invoices i ON a.appointment_id = i.appointment_id
    GROUP BY d.doctor_id, d.first_name, d.last_name, s.specialization_name
    ORDER BY revenue_rank;
    """
    cur.execute(q1)
    print_table(cur, ["Doc ID", "Doctor Name", "Specialization", "Consultations", "Gross Rev (Rs)", "Collected (Rs)", "Rank"], "Doctor Leaderboard")

    # Query 2: Cumulative Daily Revenue (Running Total)
    print_section("QUERY 2: Daily Cumulative Revenue Collection (Running Total)")
    q2 = """
    SELECT 
        DATE(p.payment_date) AS payment_day,
        COUNT(p.payment_id) AS txns_count,
        SUM(p.amount_paid) AS daily_collection,
        SUM(SUM(p.amount_paid)) OVER (ORDER BY DATE(p.payment_date)) AS cumulative_revenue_to_date
    FROM payments p
    WHERE p.payment_status = 'Success'
    GROUP BY DATE(p.payment_date)
    ORDER BY payment_day;
    """
    cur.execute(q2)
    print_table(cur, ["Payment Date", "Transactions", "Daily Total (Rs)", "Running Cumulative (Rs)"], "Daily Revenue Velocity")

    # Query 3: Patient Retention & Loyalty Analysis
    print_section("QUERY 3: Patient Retention & Repeat Visit Segmentation (CTE)")
    q3 = """
    WITH patient_visit_counts AS (
        SELECT 
            p.patient_id,
            p.first_name || ' ' || p.last_name AS patient_name,
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
    ORDER BY total_visits DESC, patient_name
    LIMIT 10;
    """
    cur.execute(q3)
    print_table(cur, ["Patient ID", "Patient Name", "Gender", "Total Visits", "First Visit", "Latest Visit", "Cohort Category"], "Top Patient Retention Cohorts")

    # Query 4: Outstanding Balance Aging
    print_section("QUERY 4: Unpaid Invoice Delinquency Aging Buckets")
    q4 = """
    SELECT 
        i.invoice_number,
        p.first_name || ' ' || p.last_name AS patient_name,
        p.phone AS contact,
        i.due_date,
        i.total_amount,
        i.paid_amount,
        (i.total_amount - i.paid_amount) AS balance_due,
        i.payment_status
    FROM invoices i
    JOIN patients p ON i.patient_id = p.patient_id
    WHERE i.payment_status IN ('Unpaid', 'Partially Paid')
    ORDER BY balance_due DESC;
    """
    cur.execute(q4)
    print_table(cur, ["Invoice #", "Patient Name", "Phone", "Due Date", "Billed (Rs)", "Paid (Rs)", "Balance Due (Rs)", "Status"], "Outstanding Balance Recovery List")

    # Query 5: Preferred Payment Methods Breakdown
    print_section("QUERY 5: Payment Channel & Method Breakdown")
    q5 = """
    SELECT 
        payment_method,
        COUNT(payment_id) AS total_transactions,
        SUM(amount_paid) AS total_amount_inr,
        ROUND(SUM(amount_paid) * 100.0 / (SELECT SUM(amount_paid) FROM payments WHERE payment_status = 'Success'), 2) AS percentage_of_revenue
    FROM payments
    WHERE payment_status = 'Success'
    GROUP BY payment_method
    ORDER BY total_amount_inr DESC;
    """
    cur.execute(q5)
    print_table(cur, ["Payment Channel", "Transactions", "Amount (Rs)", "% Share of Revenue"], "Payment Channels Share")

def main():
    print("=" * 80)
    print("  HOSPITAL & CLINIC APPOINTMENT & BILLING MANAGEMENT SYSTEM")
    print("  Interactive SQL & Analytics Execution Engine")
    print("=" * 80)
    conn = get_connection()
    try:
        init_schema(conn)
        seed_data(conn)
        run_business_queries(conn)
        print("\n[SUCCESS] All SQL structures, sample data, and analytical queries executed perfectly!")
        print(f"Database exported and persisted to: {os.path.abspath(DB_FILE)}\n")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
