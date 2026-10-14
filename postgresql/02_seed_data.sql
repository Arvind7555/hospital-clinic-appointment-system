-- ============================================================================
-- Project: Hospital & Clinic Appointment & Billing Management System
-- Dialect: PostgreSQL 14+ / 18+
-- Script: postgresql/02_seed_data.sql - Realistic Demo Dataset
-- ============================================================================

-- 1. Insert Specializations
INSERT INTO specializations (specialization_id, specialization_name, description) VALUES
(1, 'General Medicine', 'Primary healthcare, chronic disease management, and regular checkups'),
(2, 'Cardiology', 'Heart health, cardiovascular disorders, and hypertension care'),
(3, 'Dermatology', 'Skin, hair, nail disorders, and cosmetic dermatology'),
(4, 'Orthopedics', 'Musculoskeletal issues, bone fractures, and joint replacement'),
(5, 'Pediatrics', 'Medical care for infants, children, and adolescents'),
(6, 'Neurology', 'Disorders of the nervous system, brain, and spinal cord'),
(7, 'Gynecology & Obstetrics', 'Women reproductive health, prenatal, and maternity care'),
(8, 'Ophthalmology', 'Eye care, vision testing, and surgical ophthalmic treatments');

SELECT setval('specializations_specialization_id_seq', (SELECT MAX(specialization_id) FROM specializations));

-- 2. Insert Doctors
INSERT INTO doctors (doctor_id, specialization_id, first_name, last_name, email, phone, qualification, experience_years, consultation_fee, status) VALUES
(1, 1, 'Rajesh', 'Sharma', 'dr.rajesh.sharma@hospital.com', '+91-9876543210', 'MBBS, MD (Internal Medicine)', 14, 600.00, 'Active'),
(2, 2, 'Priya', 'Nair', 'dr.priya.nair@hospital.com', '+91-9876543211', 'MBBS, DM (Cardiology)', 12, 1200.00, 'Active'),
(3, 3, 'Amit', 'Verma', 'dr.amit.verma@hospital.com', '+91-9876543212', 'MBBS, MD (Dermatology)', 8, 800.00, 'Active'),
(4, 4, 'Suresh', 'Menon', 'dr.suresh.menon@hospital.com', '+91-9876543213', 'MBBS, MS (Orthopedics)', 16, 1000.00, 'Active'),
(5, 5, 'Ananya', 'Deshmukh', 'dr.ananya.deshmukh@hospital.com', '+91-9876543214', 'MBBS, DCH, MD (Pediatrics)', 9, 700.00, 'Active'),
(6, 6, 'Vikram', 'Malhotra', 'dr.vikram.malhotra@hospital.com', '+91-9876543215', 'MBBS, DM (Neurology)', 15, 1500.00, 'Active'),
(7, 7, 'Sunita', 'Rao', 'dr.sunita.rao@hospital.com', '+91-9876543216', 'MBBS, MS (OBG)', 11, 900.00, 'Active'),
(8, 8, 'Kavita', 'Singhania', 'dr.kavita.s@hospital.com', '+91-9876543217', 'MBBS, MS (Ophthalmology)', 7, 750.00, 'Active'),
(9, 1, 'Arjun', 'Kapoor', 'dr.arjun.k@hospital.com', '+91-9876543218', 'MBBS, DNB (Family Medicine)', 6, 500.00, 'Active'),
(10, 2, 'Rohan', 'Gupta', 'dr.rohan.gupta@hospital.com', '+91-9876543219', 'MBBS, MD, FACC (Cardiology)', 18, 1400.00, 'Active');

SELECT setval('doctors_doctor_id_seq', (SELECT MAX(doctor_id) FROM doctors));

-- 3. Insert Doctor Schedules
INSERT INTO doctor_schedules (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes, max_patients) VALUES
(1, 'Monday', '09:00:00', '13:00:00', 30, 8),
(1, 'Wednesday', '09:00:00', '13:00:00', 30, 8),
(1, 'Friday', '09:00:00', '13:00:00', 30, 8),
(2, 'Monday', '10:00:00', '14:00:00', 30, 8),
(2, 'Tuesday', '10:00:00', '14:00:00', 30, 8),
(2, 'Thursday', '10:00:00', '14:00:00', 30, 8),
(3, 'Tuesday', '14:00:00', '18:00:00', 30, 8),
(3, 'Thursday', '14:00:00', '18:00:00', 30, 8),
(3, 'Saturday', '10:00:00', '14:00:00', 30, 8),
(4, 'Monday', '14:00:00', '18:00:00', 30, 8),
(4, 'Wednesday', '14:00:00', '18:00:00', 30, 8),
(4, 'Friday', '14:00:00', '18:00:00', 30, 8),
(5, 'Monday', '09:00:00', '12:00:00', 20, 9),
(5, 'Thursday', '09:00:00', '12:00:00', 20, 9),
(5, 'Saturday', '09:00:00', '13:00:00', 20, 12),
(6, 'Wednesday', '11:00:00', '15:00:00', 30, 8),
(6, 'Friday', '11:00:00', '15:00:00', 30, 8),
(7, 'Tuesday', '09:00:00', '13:00:00', 30, 8),
(7, 'Thursday', '09:00:00', '13:00:00', 30, 8),
(8, 'Monday', '15:00:00', '19:00:00', 30, 8),
(8, 'Saturday', '14:00:00', '18:00:00', 30, 8),
(9, 'Tuesday', '09:00:00', '13:00:00', 30, 8),
(9, 'Thursday', '09:00:00', '13:00:00', 30, 8),
(10, 'Saturday', '10:00:00', '14:00:00', 30, 8);

-- 4. Insert Patients
INSERT INTO patients (patient_id, first_name, last_name, dob, gender, blood_group, phone, email, address, emergency_contact_name, emergency_contact_phone) VALUES
(1, 'Aarav', 'Mehta', '1988-04-12', 'Male', 'O+', '+91-9123456701', 'aarav.mehta@example.com', 'Flat 402, Green Meadows, Mumbai', 'Neha Mehta', '+91-9123456791'),
(2, 'Sneha', 'Patil', '1995-08-25', 'Female', 'B+', '+91-9123456702', 'sneha.patil@example.com', '12 Lake View Apts, Pune', 'Ramesh Patil', '+91-9123456792'),
(3, 'Karan', 'Johar', '1982-11-03', 'Male', 'A+', '+91-9123456703', 'karan.j@example.com', 'B-14 Sector 21, Noida', 'Simran Johar', '+91-9123456793'),
(4, 'Pooja', 'Iyer', '1999-01-19', 'Female', 'AB+', '+91-9123456704', 'pooja.iyer@example.com', '7th Cross Indira Nagar, Bengaluru', 'Venkat Iyer', '+91-9123456794'),
(5, 'Manish', 'Chopra', '1976-06-30', 'Male', 'O-', '+91-9123456705', 'manish.c@example.com', 'House 55, Model Town, Delhi', 'Geeta Chopra', '+91-9123456795'),
(6, 'Divya', 'Bansal', '2002-09-14', 'Female', 'A-', '+91-9123456706', 'divya.b@example.com', 'Flat 101, Galaxy Heights, Jaipur', 'Mohan Bansal', '+91-9123456796'),
(7, 'Rahul', 'Verma', '1990-12-05', 'Male', 'B-', '+91-9123456707', 'rahul.v@example.com', 'Road No 3, Banjara Hills, Hyderabad', 'Pooja Verma', '+91-9123456797'),
(8, 'Tanvi', 'Shah', '1993-03-22', 'Female', 'O+', '+91-9123456708', 'tanvi.shah@example.com', '45 Ellis Bridge, Ahmedabad', 'Jignesh Shah', '+91-9123456798'),
(9, 'Kabir', 'Khan', '2018-05-10', 'Male', 'AB-', '+91-9123456709', 'farhan.khan@example.com', '9 Park Circus, Kolkata', 'Farhan Khan', '+91-9123456799'),
(10, 'Ritu', 'Mishra', '1985-07-17', 'Female', 'B+', '+91-9123456710', 'ritu.m@example.com', 'Civil Lines, Lucknow', 'Sanjay Mishra', '+91-9123456780'),
(11, 'Deepak', 'Saini', '1991-10-28', 'Male', 'A+', '+91-9123456711', 'deepak.saini@example.com', 'Sec 15, Chandigarh', 'Komal Saini', '+91-9123456781'),
(12, 'Meera', 'Nambiar', '1996-02-14', 'Female', 'O+', '+91-9123456712', 'meera.n@example.com', 'Panampilly Nagar, Kochi', 'Unni Nambiar', '+91-9123456782'),
(13, 'Gaurav', 'Tiwari', '1987-12-20', 'Male', 'B+', '+91-9123456713', 'gaurav.t@example.com', 'Vikas Nagar, Kanpur', 'Archana Tiwari', '+91-9123456783'),
(14, 'Ishaan', 'Bhatia', '2019-11-08', 'Male', 'O+', '+91-9123456714', 'varun.bhatia@example.com', 'Sushant Lok, Gurugram', 'Varun Bhatia', '+91-9123456784'),
(15, 'Ananya', 'Saxena', '1994-04-05', 'Female', 'AB+', '+91-9123456715', 'ananya.s@example.com', 'Arera Colony, Bhopal', 'Vivek Saxena', '+91-9123456785');

SELECT setval('patients_patient_id_seq', (SELECT MAX(patient_id) FROM patients));

-- 5. Insert Appointments
INSERT INTO appointments (appointment_id, appointment_number, patient_id, doctor_id, appointment_date, appointment_time, status, reason_for_visit, notes) VALUES
(1,  'APT-2026-0001', 1,  1,  '2026-10-02', '09:30:00', 'Completed', 'Persistent viral fever and dry cough', 'Patient recovered well'),
(2,  'APT-2026-0002', 2,  3,  '2026-10-03', '14:30:00', 'Completed', 'Severe acne flare-up and rash', 'Topical gel recommended'),
(3,  'APT-2026-0003', 3,  2,  '2026-10-05', '10:00:00', 'Completed', 'Chest discomfort and shortness of breath', 'ECG done, normal sinus rhythm'),
(4,  'APT-2026-0004', 4,  7,  '2026-10-06', '09:30:00', 'Completed', 'Routine prenatal checkup (2nd trimester)', 'Fetal heart sound clear'),
(5,  'APT-2026-0005', 5,  4,  '2026-10-07', '14:30:00', 'Completed', 'Acute right knee pain after jogging', 'Advised MRI, suspected meniscus tear'),
(6,  'APT-2026-0006', 6,  8,  '2026-10-08', '15:30:00', 'Completed', 'Blurry vision and headache during screen use', 'Prescription glasses updated'),
(7,  'APT-2026-0007', 7,  6,  '2026-10-09', '11:30:00', 'Completed', 'Frequent migraine attacks with aura', 'Preventive medications started'),
(8,  'APT-2026-0008', 9,  5,  '2026-10-10', '09:30:00', 'Completed', 'Annual pediatric vaccination & growth assessment', 'Growth percentiles normal'),
(9,  'APT-2026-0009', 8,  1,  '2026-10-12', '10:30:00', 'Completed', 'Diabetes management and routine blood sugar evaluation', 'Insulin dosage adjusted'),
(10, 'APT-2026-0010', 10, 2,  '2026-10-13', '11:00:00', 'Completed', 'High blood pressure follow-up', 'BP 130/85, stable'),
(11, 'APT-2026-0011', 11, 4,  '2026-10-14', '15:00:00', 'Completed', 'Lower back stiffness and sciatica symptom', 'Physical therapy referral'),
(12, 'APT-2026-0012', 12, 3,  '2026-10-15', '15:30:00', 'Cancelled', 'Eczema consultation', 'Cancelled by patient due to travel'),
(13, 'APT-2026-0013', 13, 9,  '2026-10-15', '10:00:00', 'No-Show',   'General health checkup', 'Patient did not arrive'),
(14, 'APT-2026-0014', 14, 5,  '2026-10-17', '10:00:00', 'Confirmed', 'Childhood asthma review', 'Brought recent spirometry report'),
(15, 'APT-2026-0015', 15, 7,  '2026-10-18', '10:30:00', 'Confirmed', 'PCOS evaluation & irregular cycles', 'Ultrasound report pending'),
(16, 'APT-2026-0016', 1,  2,  '2026-10-19', '10:30:00', 'Scheduled', 'Cardiovascular risk evaluation', 'Family history of CAD'),
(17, 'APT-2026-0017', 2,  8,  '2026-10-19', '16:00:00', 'Scheduled', 'Dry eyes and irritation', 'First time visit'),
(18, 'APT-2026-0018', 3,  6,  '2026-10-21', '12:00:00', 'Scheduled', 'Nerve tingling in fingers', 'Carpal tunnel screening'),
(19, 'APT-2026-0019', 5,  10, '2026-10-24', '11:00:00', 'Scheduled', 'Senior cardiac consultation', 'Second opinion'),
(20, 'APT-2026-0020', 7,  1,  '2026-10-26', '11:00:00', 'Scheduled', 'Gastric reflux and acidity', 'Dietary counseling requested');

SELECT setval('appointments_appointment_id_seq', (SELECT MAX(appointment_id) FROM appointments));

-- 6. Insert Medical Records
INSERT INTO medical_records (record_id, appointment_id, symptoms, diagnosis, prescribed_tests, medication_prescriptions, doctor_notes, follow_up_date) VALUES
(1,  1,  'Fever 101F, body aches, dry cough', 'Acute Viral Pharyngitis', 'CBC, ESR', 'Paracetamol 650mg TDS, Levocetirizine 5mg OD', 'Rest and fluid hydration for 4 days', '2026-10-09'),
(2,  2,  'Papules and pustules on cheeks, oily skin', 'Acne Vulgaris Grade II', 'Hormonal profile if persistent', 'Adapalene 0.1% Gel, Clindamycin lotion', 'Avoid harsh soaps, apply sunscreen', '2026-11-03'),
(3,  3,  'Substernal heaviness on exertion, breathlessness', 'Atypical Angina / Exertional Dyspnea', 'TMT (Stress Test), 2D Echocardiogram, Lipid Profile', 'Aspirin 75mg OD, Atorvastatin 20mg HS', 'Avoid strenuous physical activities till TMT is complete', '2026-10-20'),
(4,  4,  'Mild backache, normal gestational movement', 'Intrauterine Pregnancy at 22 weeks', 'Anomaly Ultrasound Scan, Urine Routine', 'Calcium Carbonate 500mg, Iron & Folic Acid OD', 'Vitals and baby growth optimal', '2026-11-04'),
(5,  5,  'Joint line tenderness, swelling, flexion limitation', 'Right Medial Meniscus Sprain', 'MRI Right Knee Joint', 'Aceclofenac + Paracetamol, Chymoral Forte', 'Knee brace immobilization for 10 days', '2026-10-25'),
(6,  6,  'Asthenopia, headaches when working on laptop', 'Compound Myopic Astigmatism (Both Eyes)', 'Refraction & Fundoscopy', 'Lubricating Eye Drops, Anti-glare glasses', 'Strict 20-20-20 digital screen rule', '2027-04-08'),
(7,  7,  'Unilateral pulsating headache, photophobia, nausea', 'Chronic Migraine without aura', 'Brain MRI (screened normal)', 'Rizatriptan 10mg PRN, Propranolol 40mg OD prophylaxis', 'Identify food triggers (caffeine, aged cheese)', '2026-11-10'),
(8,  8,  'Vaccination milestone, normal diet', 'Healthy Child Development Milestone', 'None', 'Hexavalent vaccine administered, Vitamin D drops', 'Normal motor and cognitive milestones', '2027-04-10'),
(9,  9,  'Fasting glucose 158 mg/dL, fatigue', 'Type 2 Diabetes Mellitus with sub-optimal control', 'HbA1c, Kidney Function Test, Microalbuminuria', 'Metformin 1000mg BD, Glimepiride 1mg OD', 'Strict low-glycemic diabetic diet', '2026-11-12'),
(10, 10, 'Blood pressure check, mild occipital morning headache', 'Primary Essential Hypertension Stage 1', 'Serum Electrolytes, Renal Doppler', 'Telmisartan 40mg OD, Amlodipine 5mg OD', 'Salt restriction (< 5g/day), daily 30m brisk walk', '2026-11-13'),
(11, 11, 'Radiating pain along L5-S1 dermatome to left calf', 'Lumbar Radiculopathy / Sciatica', 'MRI Lumbo-sacral Spine', 'Pregabalin 75mg HS, Methylcobalamin 1500mcg OD', 'Core strengthening exercises with physiotherapist', '2026-10-28');

SELECT setval('medical_records_record_id_seq', (SELECT MAX(record_id) FROM medical_records));

-- 7. Insert Invoices
INSERT INTO invoices (invoice_id, invoice_number, appointment_id, patient_id, invoice_date, consultation_fee, procedure_charges, medication_charges, discount_amount, tax_amount, total_amount, paid_amount, payment_status, due_date) VALUES
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
(13, 'INV-2026-0015', 15, 15, '2026-10-14', 900.00,  0.00,   0.00,   0.00,  45.00,   945.00,  0.00,    'Unpaid',         '2026-10-18');

SELECT setval('invoices_invoice_id_seq', (SELECT MAX(invoice_id) FROM invoices));

-- 8. Insert Payments
INSERT INTO payments (payment_id, payment_reference, invoice_id, payment_date, amount_paid, payment_method, payment_status, transaction_reference, notes) VALUES
(1,  'PAY-2026-0001', 1,  '2026-10-02 10:15:00+00', 840.00,  'UPI',         'Success', 'UPI/20261002/982181283', 'Paid via Google Pay'),
(2,  'PAY-2026-0002', 2,  '2026-10-03 15:20:00+00', 1627.50, 'Credit Card', 'Success', 'TXN_CC_98291039401',     'HDFC Credit Card ending 4412'),
(3,  'PAY-2026-0003', 3,  '2026-10-05 11:00:00+00', 2047.50, 'Insurance',   'Success', 'TPA/ICICI/91823901',     'Cashless claim approval by ICICI Lombard'),
(4,  'PAY-2026-0004', 4,  '2026-10-06 10:45:00+00', 1680.00, 'UPI',         'Success', 'UPI/20261006/812930192', 'Paid via PhonePe'),
(5,  'PAY-2026-0005', 5,  '2026-10-07 16:00:00+00', 1500.00, 'Debit Card',  'Success', 'TXN_DC_81029381923',     'Initial partial deposit, balance due'),
(6,  'PAY-2026-0006', 6,  '2026-10-08 16:30:00+00', 1050.00, 'Cash',        'Success', 'CASH_REC_08102026',      'Desk cash counter payment'),
(7,  'PAY-2026-0007', 7,  '2026-10-09 12:45:00+00', 2100.00, 'Net Banking', 'Success', 'NETB_AXIS_091823901',    'Axis Net Banking portal'),
(8,  'PAY-2026-0008', 8,  '2026-10-10 10:30:00+00', 2520.00, 'UPI',         'Success', 'UPI/20261010/771928391', 'Paid via Paytm'),
(9,  'PAY-2026-0009', 9,  '2026-10-12 11:45:00+00', 1365.00, 'Credit Card', 'Success', 'TXN_CC_90182938190',     'SBI Card ending 9012'),
(10, 'PAY-2026-0010', 10, '2026-10-13 12:15:00+00', 700.00,  'Cash',        'Success', 'CASH_REC_13102026',      'Partial cash advance payment'),
(11, 'PAY-2026-0011', 12, '2026-10-14 14:00:00+00', 735.00,  'UPI',         'Success', 'UPI/20261014/192830192', 'Advance booking fee settled');

SELECT setval('payments_payment_id_seq', (SELECT MAX(payment_id) FROM payments));
