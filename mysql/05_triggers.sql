-- ============================================================================
-- Project: Hospital & Clinic Appointment & Billing Management System
-- Script: 05_triggers.sql - Business Rules & Integrity Triggers
-- ============================================================================

USE hospital_clinic_db;

DELIMITER //

-- ----------------------------------------------------------------------------
-- Trigger 1: trg_validate_doctor_availability_before_insert
-- Ensures appointment cannot be booked with an Inactive or On-Leave doctor
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_validate_doctor_availability_before_insert //
CREATE TRIGGER trg_validate_doctor_availability_before_insert
BEFORE INSERT ON appointments
FOR EACH ROW
BEGIN
    DECLARE v_doctor_status VARCHAR(20);

    SELECT status INTO v_doctor_status
    FROM doctors
    WHERE doctor_id = NEW.doctor_id;

    IF v_doctor_status != 'Active' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Validation Failed: Cannot book appointment with an Inactive or On-Leave doctor.';
    END IF;
END //

-- ----------------------------------------------------------------------------
-- Trigger 2: trg_mark_appointment_completed_on_medical_record
-- When clinical notes/medical record is entered, auto-complete appointment
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_mark_appointment_completed_on_medical_record //
CREATE TRIGGER trg_mark_appointment_completed_on_medical_record
AFTER INSERT ON medical_records
FOR EACH ROW
BEGIN
    UPDATE appointments
    SET status = 'Completed'
    WHERE appointment_id = NEW.appointment_id;
END //

-- ----------------------------------------------------------------------------
-- Trigger 3: trg_reconcile_invoice_on_payment_insert
-- Reconciles total paid amount and sets status ('Paid', 'Partially Paid')
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_reconcile_invoice_on_payment_insert //
CREATE TRIGGER trg_reconcile_invoice_on_payment_insert
AFTER INSERT ON payments
FOR EACH ROW
BEGIN
    DECLARE v_total_paid DECIMAL(10, 2);
    DECLARE v_invoice_total DECIMAL(10, 2);

    IF NEW.payment_status = 'Success' THEN
        -- Calculate sum of all successful payments for this invoice
        SELECT COALESCE(SUM(amount_paid), 0.00) INTO v_total_paid
        FROM payments
        WHERE invoice_id = NEW.invoice_id AND payment_status = 'Success';

        SELECT total_amount INTO v_invoice_total
        FROM invoices
        WHERE invoice_id = NEW.invoice_id;

        -- Update Invoice status and paid_amount
        UPDATE invoices
        SET paid_amount = v_total_paid,
            payment_status = CASE 
                WHEN v_total_paid >= v_invoice_total THEN 'Paid'
                WHEN v_total_paid > 0 THEN 'Partially Paid'
                ELSE 'Unpaid'
            END
        WHERE invoice_id = NEW.invoice_id;
    END IF;
END //

DELIMITER ;
