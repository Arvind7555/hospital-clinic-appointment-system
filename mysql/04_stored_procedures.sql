-- ============================================================================
-- Project: Hospital & Clinic Appointment & Billing Management System
-- Script: 04_stored_procedures.sql - Core Business Logic Procedures
-- ============================================================================

USE hospital_clinic_db;

DELIMITER //

-- ----------------------------------------------------------------------------
-- Procedure 1: sp_book_appointment
-- Books an appointment safely with conflict checking
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_book_appointment //
CREATE PROCEDURE sp_book_appointment (
    IN p_patient_id INT,
    IN p_doctor_id INT,
    IN p_appointment_date DATE,
    IN p_appointment_time TIME,
    IN p_reason VARCHAR(255),
    OUT p_appointment_number VARCHAR(30),
    OUT p_status_message VARCHAR(255)
)
BEGIN
    DECLARE v_doctor_active_count INT DEFAULT 0;
    DECLARE v_existing_booking_count INT DEFAULT 0;
    DECLARE v_new_number VARCHAR(30);

    -- 1. Check if Doctor exists and is Active
    SELECT COUNT(*) INTO v_doctor_active_count
    FROM doctors 
    WHERE doctor_id = p_doctor_id AND status = 'Active';

    IF v_doctor_active_count = 0 THEN
        SET p_appointment_number = NULL;
        SET p_status_message = 'ERROR: Doctor does not exist or is currently inactive.';
    ELSE
        -- 2. Check if Doctor already has a booking at that slot
        SELECT COUNT(*) INTO v_existing_booking_count
        FROM appointments
        WHERE doctor_id = p_doctor_id
          AND appointment_date = p_appointment_date
          AND appointment_time = p_appointment_time
          AND status IN ('Scheduled', 'Confirmed');

        IF v_existing_booking_count > 0 THEN
            SET p_appointment_number = NULL;
            SET p_status_message = 'ERROR: Doctor already has an active booking at this time slot.';
        ELSE
            -- 3. Generate unique appointment number (APT-YYYYMMDD-UUID/RANDOM)
            SET v_new_number = CONCAT('APT-', DATE_FORMAT(p_appointment_date, '%Y%m%d'), '-', LPAD(FLOOR(RAND() * 9000) + 1000, 4, '0'));

            -- 4. Insert Appointment
            INSERT INTO appointments (
                appointment_number, patient_id, doctor_id, 
                appointment_date, appointment_time, status, reason_for_visit
            ) VALUES (
                v_new_number, p_patient_id, p_doctor_id, 
                p_appointment_date, p_appointment_time, 'Scheduled', p_reason
            );

            SET p_appointment_number = v_new_number;
            SET p_status_message = 'SUCCESS: Appointment successfully booked.';
        END IF;
    END IF;
END //

-- ----------------------------------------------------------------------------
-- Procedure 2: sp_generate_invoice
-- Automatically generates an itemized invoice for an appointment
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_generate_invoice //
CREATE PROCEDURE sp_generate_invoice (
    IN p_appointment_id INT,
    IN p_procedure_charges DECIMAL(10, 2),
    IN p_medication_charges DECIMAL(10, 2),
    IN p_discount_amount DECIMAL(10, 2),
    IN p_tax_rate_percent DECIMAL(5, 2),
    IN p_due_days INT,
    OUT p_invoice_number VARCHAR(30),
    OUT p_total_amount DECIMAL(10, 2),
    OUT p_status_message VARCHAR(255)
)
BEGIN
    DECLARE v_patient_id INT;
    DECLARE v_doctor_id INT;
    DECLARE v_consultation_fee DECIMAL(10, 2);
    DECLARE v_subtotal DECIMAL(10, 2);
    DECLARE v_tax_amount DECIMAL(10, 2);
    DECLARE v_final_total DECIMAL(10, 2);
    DECLARE v_invoice_exists INT DEFAULT 0;
    DECLARE v_new_inv_num VARCHAR(30);

    -- Check if invoice already exists
    SELECT COUNT(*) INTO v_invoice_exists FROM invoices WHERE appointment_id = p_appointment_id;

    IF v_invoice_exists > 0 THEN
        SET p_invoice_number = NULL;
        SET p_total_amount = 0.00;
        SET p_status_message = 'ERROR: Invoice already exists for this appointment.';
    ELSE
        -- Retrieve patient and doctor consultation fee
        SELECT a.patient_id, a.doctor_id, d.consultation_fee 
        INTO v_patient_id, v_doctor_id, v_consultation_fee
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.appointment_id = p_appointment_id;

        IF v_patient_id IS NULL THEN
            SET p_invoice_number = NULL;
            SET p_total_amount = 0.00;
            SET p_status_message = 'ERROR: Appointment ID not found.';
        ELSE
            -- Calculations
            SET v_subtotal = (v_consultation_fee + COALESCE(p_procedure_charges, 0) + COALESCE(p_medication_charges, 0)) - COALESCE(p_discount_amount, 0);
            IF v_subtotal < 0 THEN 
                SET v_subtotal = 0; 
            END IF;

            SET v_tax_amount = ROUND(v_subtotal * (COALESCE(p_tax_rate_percent, 0) / 100.0), 2);
            SET v_final_total = v_subtotal + v_tax_amount;

            SET v_new_inv_num = CONCAT('INV-', DATE_FORMAT(CURDATE(), '%Y%m%d'), '-', LPAD(FLOOR(RAND() * 9000) + 1000, 4, '0'));

            -- Insert Invoice
            INSERT INTO invoices (
                invoice_number, appointment_id, patient_id, invoice_date,
                consultation_fee, procedure_charges, medication_charges,
                discount_amount, tax_amount, total_amount, paid_amount,
                payment_status, due_date
            ) VALUES (
                v_new_inv_num, p_appointment_id, v_patient_id, CURDATE(),
                v_consultation_fee, COALESCE(p_procedure_charges, 0), COALESCE(p_medication_charges, 0),
                COALESCE(p_discount_amount, 0), v_tax_amount, v_final_total, 0.00,
                'Unpaid', DATE_ADD(CURDATE(), INTERVAL COALESCE(p_due_days, 14) DAY)
            );

            -- Update appointment status to completed if not already
            UPDATE appointments SET status = 'Completed' WHERE appointment_id = p_appointment_id;

            SET p_invoice_number = v_new_inv_num;
            SET p_total_amount = v_final_total;
            SET p_status_message = 'SUCCESS: Invoice generated successfully.';
        END IF;
    END IF;
END //

-- ----------------------------------------------------------------------------
-- Procedure 3: sp_record_payment
-- Records payment against invoice and updates invoice balance & status
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_record_payment //
CREATE PROCEDURE sp_record_payment (
    IN p_invoice_id INT,
    IN p_amount_paid DECIMAL(10, 2),
    IN p_payment_method VARCHAR(30),
    IN p_txn_ref VARCHAR(100),
    IN p_notes VARCHAR(255),
    OUT p_payment_reference VARCHAR(30),
    OUT p_updated_status VARCHAR(20),
    OUT p_status_message VARCHAR(255)
)
BEGIN
    DECLARE v_total_amount DECIMAL(10, 2);
    DECLARE v_current_paid DECIMAL(10, 2);
    DECLARE v_remaining_balance DECIMAL(10, 2);
    DECLARE v_new_paid DECIMAL(10, 2);
    DECLARE v_new_status VARCHAR(20);
    DECLARE v_pay_ref VARCHAR(30);

    -- Retrieve current invoice details
    SELECT total_amount, paid_amount 
    INTO v_total_amount, v_current_paid
    FROM invoices 
    WHERE invoice_id = p_invoice_id;

    IF v_total_amount IS NULL THEN
        SET p_payment_reference = NULL;
        SET p_updated_status = NULL;
        SET p_status_message = 'ERROR: Invoice not found.';
    ELSE
        SET v_remaining_balance = v_total_amount - v_current_paid;

        IF p_amount_paid <= 0 THEN
            SET p_payment_reference = NULL;
            SET p_updated_status = NULL;
            SET p_status_message = 'ERROR: Payment amount must be greater than zero.';
        ELSEIF p_amount_paid > v_remaining_balance THEN
            SET p_payment_reference = NULL;
            SET p_updated_status = NULL;
            SET p_status_message = CONCAT('ERROR: Payment amount exceeds outstanding balance of ', v_remaining_balance);
        ELSE
            -- Generate Payment Reference
            SET v_pay_ref = CONCAT('PAY-', DATE_FORMAT(CURDATE(), '%Y%m%d'), '-', LPAD(FLOOR(RAND() * 9000) + 1000, 4, '0'));

            -- Record Payment
            INSERT INTO payments (
                payment_reference, invoice_id, payment_date, 
                amount_paid, payment_method, payment_status, transaction_reference, notes
            ) VALUES (
                v_pay_ref, p_invoice_id, NOW(), 
                p_amount_paid, p_payment_method, 'Success', p_txn_ref, p_notes
            );

            -- Determine new payment status
            SET v_new_paid = v_current_paid + p_amount_paid;
            IF v_new_paid >= v_total_amount THEN
                SET v_new_status = 'Paid';
            ELSE
                SET v_new_status = 'Partially Paid';
            END IF;

            -- Update Invoice
            UPDATE invoices 
            SET paid_amount = v_new_paid,
                payment_status = v_new_status
            WHERE invoice_id = p_invoice_id;

            SET p_payment_reference = v_pay_ref;
            SET p_updated_status = v_new_status;
            SET p_status_message = 'SUCCESS: Payment recorded and invoice updated successfully.';
        END IF;
    END IF;
END //

DELIMITER ;
