-- ============================================================================
-- Project: Hospital & Clinic Appointment & Billing Management System
-- Dialect: PostgreSQL 14+ / 18+
-- Script: postgresql/04_functions_triggers.sql - PL/pgSQL Functions, Triggers & Procedures
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Trigger Function: fn_validate_doctor_availability
-- Prevents booking with Inactive/On-Leave doctors
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_validate_doctor_availability()
RETURNS TRIGGER AS $$
DECLARE
    v_doctor_status VARCHAR(20);
BEGIN
    SELECT status INTO v_doctor_status
    FROM doctors
    WHERE doctor_id = NEW.doctor_id;

    IF v_doctor_status != 'Active' THEN
        RAISE EXCEPTION 'Validation Failed: Doctor is currently not active (% status).', v_doctor_status;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validate_doctor_availability ON appointments;
CREATE TRIGGER trg_validate_doctor_availability
BEFORE INSERT ON appointments
FOR EACH ROW
EXECUTE FUNCTION fn_validate_doctor_availability();

-- ----------------------------------------------------------------------------
-- 2. Trigger Function: fn_mark_appointment_completed
-- Auto-updates appointment status to Completed when medical record is added
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_mark_appointment_completed()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE appointments
    SET status = 'Completed', updated_at = CURRENT_TIMESTAMP
    WHERE appointment_id = NEW.appointment_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_mark_appointment_completed ON medical_records;
CREATE TRIGGER trg_mark_appointment_completed
AFTER INSERT ON medical_records
FOR EACH ROW
EXECUTE FUNCTION fn_mark_appointment_completed();

-- ----------------------------------------------------------------------------
-- 3. Trigger Function: fn_reconcile_invoice_payment
-- Reconciles invoice balance and payment status upon payment insertion
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_reconcile_invoice_payment()
RETURNS TRIGGER AS $$
DECLARE
    v_total_paid NUMERIC(10, 2);
    v_invoice_total NUMERIC(10, 2);
    v_new_status VARCHAR(20);
BEGIN
    IF NEW.payment_status = 'Success' THEN
        SELECT COALESCE(SUM(amount_paid), 0.00) INTO v_total_paid
        FROM payments
        WHERE invoice_id = NEW.invoice_id AND payment_status = 'Success';

        SELECT total_amount INTO v_invoice_total
        FROM invoices
        WHERE invoice_id = NEW.invoice_id;

        IF v_total_paid >= v_invoice_total THEN
            v_new_status := 'Paid';
        ELSIF v_total_paid > 0 THEN
            v_new_status := 'Partially Paid';
        ELSE
            v_new_status := 'Unpaid';
        END IF;

        UPDATE invoices
        SET paid_amount = v_total_paid,
            payment_status = v_new_status,
            updated_at = CURRENT_TIMESTAMP
        WHERE invoice_id = NEW.invoice_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_reconcile_invoice_payment ON payments;
CREATE TRIGGER trg_reconcile_invoice_payment
AFTER INSERT ON payments
FOR EACH ROW
EXECUTE FUNCTION fn_reconcile_invoice_payment();

-- ----------------------------------------------------------------------------
-- 4. Stored Procedure: sp_book_appointment
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_book_appointment (
    IN p_patient_id INT,
    IN p_doctor_id INT,
    IN p_appointment_date DATE,
    IN p_appointment_time TIME,
    IN p_reason VARCHAR(255),
    INOUT p_appointment_number VARCHAR(30) DEFAULT NULL,
    INOUT p_status_message VARCHAR(255) DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_doctor_active_count INT;
    v_existing_booking_count INT;
BEGIN
    SELECT COUNT(*) INTO v_doctor_active_count
    FROM doctors 
    WHERE doctor_id = p_doctor_id AND status = 'Active';

    IF v_doctor_active_count = 0 THEN
        p_appointment_number := NULL;
        p_status_message := 'ERROR: Doctor does not exist or is currently inactive.';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_existing_booking_count
    FROM appointments
    WHERE doctor_id = p_doctor_id
      AND appointment_date = p_appointment_date
      AND appointment_time = p_appointment_time
      AND status IN ('Scheduled', 'Confirmed');

    IF v_existing_booking_count > 0 THEN
        p_appointment_number := NULL;
        p_status_message := 'ERROR: Doctor already has an active booking at this time slot.';
        RETURN;
    END IF;

    p_appointment_number := 'APT-' || TO_CHAR(p_appointment_date, 'YYYYMMDD') || '-' || LPAD((FLOOR(RANDOM() * 9000) + 1000)::TEXT, 4, '0');

    INSERT INTO appointments (
        appointment_number, patient_id, doctor_id, 
        appointment_date, appointment_time, status, reason_for_visit
    ) VALUES (
        p_appointment_number, p_patient_id, p_doctor_id, 
        p_appointment_date, p_appointment_time, 'Scheduled', p_reason
    );

    p_status_message := 'SUCCESS: Appointment successfully booked.';
END;
$$;
