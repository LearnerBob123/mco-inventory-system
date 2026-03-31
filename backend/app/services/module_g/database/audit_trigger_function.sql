-- ============================================
-- Field-Level Audit Trigger Function
-- ============================================
-- This function tracks changes at the field level.
-- For each UPDATE, it creates one audit_log entry per changed field.
-- For INSERT/DELETE, it creates one entry per field.

CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    user_id INTEGER;
    record_id_value TEXT;
    old_record JSONB;
    new_record JSONB;
    field_key TEXT;
    old_val TEXT;
    new_val TEXT;
BEGIN
    -- Retrieve current user from session variable safely
    BEGIN
        user_id := NULLIF(TRIM(current_setting('app.current_user', true)), '')::INTEGER;
    EXCEPTION
        WHEN OTHERS THEN
            user_id := NULL;
    END;

    -- Determine the primary key value (record_id)
    -- This assumes the first column is the primary key
    -- Adjust if your primary key column name differs
    IF (TG_OP = 'DELETE') THEN
        record_id_value := (SELECT to_jsonb(OLD)->>(SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = TG_RELID AND i.indisprimary
            LIMIT 1));
        old_record := to_jsonb(OLD);
        new_record := NULL;
    ELSE
        record_id_value := (SELECT to_jsonb(NEW)->>(SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = TG_RELID AND i.indisprimary
            LIMIT 1));
        old_record := CASE WHEN TG_OP = 'UPDATE' THEN to_jsonb(OLD) ELSE NULL END;
        new_record := to_jsonb(NEW);
    END IF;

    -- Handle INSERT: Log all fields as new
    IF (TG_OP = 'INSERT') THEN
        FOR field_key IN SELECT jsonb_object_keys(new_record)
        LOOP
            new_val := new_record->>field_key;

            INSERT INTO audit_log (
                table_name,
                record_id,
                field_name,
                old_value,
                new_value,
                modified_by,
                modified_at
            ) VALUES (
                TG_TABLE_NAME,
                record_id_value,
                field_key,
                NULL,
                new_val,
                user_id,
                CURRENT_TIMESTAMP
            );
        END LOOP;
        RETURN NEW;

    -- Handle UPDATE: Log only changed fields
    ELSIF (TG_OP = 'UPDATE') THEN
        FOR field_key IN SELECT jsonb_object_keys(new_record)
        LOOP
            old_val := old_record->>field_key;
            new_val := new_record->>field_key;

            -- Only log if value actually changed
            IF (old_val IS DISTINCT FROM new_val) THEN
                INSERT INTO audit_log (
                    table_name,
                    record_id,
                    field_name,
                    old_value,
                    new_value,
                    modified_by,
                    modified_at
                ) VALUES (
                    TG_TABLE_NAME,
                    record_id_value,
                    field_key,
                    old_val,
                    new_val,
                    user_id,
                    CURRENT_TIMESTAMP
                );
            END IF;
        END LOOP;
        RETURN NEW;

    -- Handle DELETE: Log all fields as deleted
    ELSIF (TG_OP = 'DELETE') THEN
        FOR field_key IN SELECT jsonb_object_keys(old_record)
        LOOP
            old_val := old_record->>field_key;

            INSERT INTO audit_log (
                table_name,
                record_id,
                field_name,
                old_value,
                new_value,
                modified_by,
                modified_at
            ) VALUES (
                TG_TABLE_NAME,
                record_id_value,
                field_key,
                old_val,
                NULL,
                user_id,
                CURRENT_TIMESTAMP
            );
        END LOOP;
        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Function Comments
-- ============================================

COMMENT ON FUNCTION audit_trigger_function() IS
'Field-level audit trigger that logs each changed field separately.
For INSERT: logs all fields with NULL old_value.
For UPDATE: logs only changed fields with old and new values.
For DELETE: logs all fields with NULL new_value.';
