-- ============================================
-- Audit Triggers for Critical Tables
-- ============================================
-- These triggers attach the audit_trigger_function to all
-- critical tables that need to be monitored.

-- ============================================
-- 1. gun table
-- ============================================
DROP TRIGGER IF EXISTS trg_audit_gun ON gun;
CREATE TRIGGER trg_audit_gun
AFTER INSERT OR UPDATE OR DELETE ON gun
FOR EACH ROW
EXECUTE FUNCTION audit_trigger_function();

-- ============================================
-- 2. major_assembly table
-- ============================================
DROP TRIGGER IF EXISTS trg_audit_major_assembly ON major_assembly;
CREATE TRIGGER trg_audit_major_assembly
AFTER INSERT OR UPDATE OR DELETE ON major_assembly
FOR EACH ROW
EXECUTE FUNCTION audit_trigger_function();

-- ============================================
-- 3. sub_assembly table
-- ============================================
DROP TRIGGER IF EXISTS trg_audit_sub_assembly ON sub_assembly;
CREATE TRIGGER trg_audit_sub_assembly
AFTER INSERT OR UPDATE OR DELETE ON sub_assembly
FOR EACH ROW
EXECUTE FUNCTION audit_trigger_function();

-- ============================================
-- 4. component table
-- ============================================
DROP TRIGGER IF EXISTS trg_audit_component ON component;
CREATE TRIGGER trg_audit_component
AFTER INSERT OR UPDATE OR DELETE ON component
FOR EACH ROW
EXECUTE FUNCTION audit_trigger_function();

-- ============================================
-- 5. authorization table
-- ============================================
DROP TRIGGER IF EXISTS trg_audit_authorization ON authorization;
CREATE TRIGGER trg_audit_authorization
AFTER INSERT OR UPDATE OR DELETE ON authorization
FOR EACH ROW
EXECUTE FUNCTION audit_trigger_function();

-- ============================================
-- 6. inventory_stock table
-- ============================================
DROP TRIGGER IF EXISTS trg_audit_inventory_stock ON inventory_stock;
CREATE TRIGGER trg_audit_inventory_stock
AFTER INSERT OR UPDATE OR DELETE ON inventory_stock
FOR EACH ROW
EXECUTE FUNCTION audit_trigger_function();

-- ============================================
-- 7. stock_transaction table
-- ============================================
DROP TRIGGER IF EXISTS trg_audit_stock_transaction ON stock_transaction;
CREATE TRIGGER trg_audit_stock_transaction
AFTER INSERT OR UPDATE OR DELETE ON stock_transaction
FOR EACH ROW
EXECUTE FUNCTION audit_trigger_function();

-- ============================================
-- 8. component_status table
-- ============================================
DROP TRIGGER IF EXISTS trg_audit_component_status ON component_status;
CREATE TRIGGER trg_audit_component_status
AFTER INSERT OR UPDATE OR DELETE ON component_status
FOR EACH ROW
EXECUTE FUNCTION audit_trigger_function();

-- ============================================
-- 9. users table
-- ============================================
DROP TRIGGER IF EXISTS trg_audit_users ON users;
CREATE TRIGGER trg_audit_users
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION audit_trigger_function();

-- ============================================
-- Verification Query
-- ============================================
-- Run this query to verify all triggers are installed:
--
-- SELECT trigger_name, event_object_table, action_timing, event_manipulation
-- FROM information_schema.triggers
-- WHERE trigger_name LIKE 'trg_audit_%'
-- ORDER BY event_object_table;
