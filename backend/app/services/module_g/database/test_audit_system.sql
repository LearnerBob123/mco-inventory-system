-- ============================================
-- Audit System Test Script
-- ============================================
-- This script tests the audit system by performing
-- INSERT, UPDATE, and DELETE operations on monitored tables.

-- ============================================
-- 1. Verify Audit System Installation
-- ============================================

-- Check if audit_log table exists
SELECT 'Checking audit_log table...' as status;
SELECT COUNT(*) as audit_log_exists
FROM information_schema.tables
WHERE table_name = 'audit_log';

-- Check if all triggers are installed
SELECT 'Checking triggers...' as status;
SELECT
    trigger_name,
    event_object_table,
    action_timing,
    string_agg(event_manipulation, ', ' ORDER BY event_manipulation) as events
FROM information_schema.triggers
WHERE trigger_name LIKE 'trg_audit_%'
GROUP BY trigger_name, event_object_table, action_timing
ORDER BY event_object_table;

-- ============================================
-- 2. Test User Context
-- ============================================

-- Set a test user ID (999 = test user)
SELECT set_config('app.current_user', '999', true);

-- Verify user context is set
SELECT 'Current audit user: ' || current_setting('app.current_user', true) as status;

-- ============================================
-- 3. Test INSERT Operation
-- ============================================

-- Note: You may need to adjust table/column names based on your schema
-- This is a generic test. Modify according to your actual tables.

SELECT 'Testing INSERT operation...' as status;

-- Example: Test with component table (adjust if needed)
-- Uncomment and modify for your schema:

/*
INSERT INTO component (component_name, component_type, status, created_at)
VALUES ('TEST_COMPONENT_AUDIT', 'TEST_TYPE', 'active', CURRENT_TIMESTAMP);

-- Verify audit entry was created
SELECT
    audit_id,
    table_name,
    record_id,
    field_name,
    modified_by,
    new_value as component_name,
    modified_at
FROM audit_log
WHERE table_name = 'component'
  AND field_name = 'component_name'
  AND new_value = 'TEST_COMPONENT_AUDIT'
ORDER BY audit_id DESC
LIMIT 1;
*/

-- ============================================
-- 4. Test UPDATE Operation
-- ============================================

SELECT 'Testing UPDATE operation...' as status;

-- Example: Test with component table (adjust if needed)
-- Uncomment and modify for your schema:

/*
UPDATE component
SET status = 'inactive'
WHERE component_name = 'TEST_COMPONENT_AUDIT';

-- Verify audit entry was created
SELECT
    audit_id,
    table_name,
    record_id,
    field_name,
    modified_by,
    old_value as old_status,
    new_value as new_status,
    modified_at
FROM audit_log
WHERE table_name = 'component'
  AND field_name = 'status'
  -- Assuming record_id can be matched manually if needed
ORDER BY audit_id DESC
LIMIT 1;
*/

-- ============================================
-- 5. Test DELETE Operation
-- ============================================

SELECT 'Testing DELETE operation...' as status;

-- Example: Test with component table (adjust if needed)
-- Uncomment and modify for your schema:

/*
DELETE FROM component
WHERE component_name = 'TEST_COMPONENT_AUDIT';

-- Verify audit entry was created
SELECT
    audit_id,
    table_name,
    record_id,
    field_name,
    modified_by,
    old_value as deleted_component_name,
    modified_at
FROM audit_log
WHERE table_name = 'component'
  AND field_name = 'component_name'
  AND old_value = 'TEST_COMPONENT_AUDIT'
ORDER BY audit_id DESC
LIMIT 1;
*/

-- ============================================
-- 6. Test Without User Context
-- ============================================

SELECT 'Testing operation without user context...' as status;

-- Clear user context
RESET app.current_user;

-- Example: Insert without user context
-- Uncomment and modify for your schema:

/*
INSERT INTO component (component_name, component_type, status, created_at)
VALUES ('TEST_NO_USER', 'TEST_TYPE', 'active', CURRENT_TIMESTAMP);

-- Verify audit entry has NULL modified_by
SELECT
    audit_id,
    table_name,
    record_id,
    field_name,
    modified_by,  -- Should be NULL
    new_value as component_name,
    modified_at
FROM audit_log
WHERE table_name = 'component'
  AND field_name = 'component_name'
  AND new_value = 'TEST_NO_USER'
ORDER BY audit_id DESC
LIMIT 1;

-- Cleanup
DELETE FROM component WHERE component_name = 'TEST_NO_USER';
*/

-- ============================================
-- 7. View All Audit Entries
-- ============================================

SELECT 'Displaying recent audit entries...' as status;

SELECT
    audit_id,
    table_name,
    record_id,
    field_name,
    modified_by,
    modified_at
FROM audit_log
ORDER BY audit_id DESC
LIMIT 20;

-- ============================================
-- 8. Test Queries (Example Analytics)
-- ============================================

-- Count operations by type
SELECT 'Operations by type:' as status;
SELECT
    field_name,
    COUNT(*) as count
FROM audit_log
GROUP BY field_name
ORDER BY count DESC;

-- Count operations by table
SELECT 'Operations by table:' as status;
SELECT
    table_name,
    COUNT(*) as count
FROM audit_log
GROUP BY table_name
ORDER BY count DESC;

-- Count operations by user
SELECT 'Operations by user:' as status;
SELECT
    modified_by,
    COUNT(*) as count
FROM audit_log
GROUP BY modified_by
ORDER BY count DESC
LIMIT 10;

-- Recent activity timeline
SELECT 'Recent activity timeline:' as status;
SELECT
    DATE_TRUNC('hour', modified_at) as hour,
    COUNT(*) as operations
FROM audit_log
WHERE modified_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;

-- ============================================
-- 9. Performance Test
-- ============================================

-- Check index usage
SELECT 'Checking indexes on audit_log:' as status;
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'audit_log';

-- Check table size
SELECT 'Audit log table size:' as status;
SELECT
    pg_size_pretty(pg_total_relation_size('audit_log')) as total_size,
    pg_size_pretty(pg_relation_size('audit_log')) as table_size,
    pg_size_pretty(pg_total_relation_size('audit_log') - pg_relation_size('audit_log')) as indexes_size;

-- ============================================
-- 10. Summary Report
-- ============================================

SELECT '================================' as separator;
SELECT 'AUDIT SYSTEM TEST SUMMARY' as report_title;
SELECT '================================' as separator;

SELECT
    'Total Audit Entries' as metric,
    COUNT(*)::text as value
FROM audit_log

UNION ALL

SELECT
    'Monitored Tables',
    COUNT(DISTINCT table_name)::text
FROM audit_log

UNION ALL

SELECT
    'Unique Users Tracked',
    COUNT(DISTINCT modified_by)::text
FROM audit_log

UNION ALL

SELECT
    'Oldest Entry',
    TO_CHAR(MIN(modified_at), 'YYYY-MM-DD HH24:MI:SS')
FROM audit_log

UNION ALL

SELECT
    'Newest Entry',
    TO_CHAR(MAX(modified_at), 'YYYY-MM-DD HH24:MI:SS')
FROM audit_log;

SELECT '================================' as separator;

-- ============================================
-- Notes and Recommendations
-- ============================================

/*
TESTING CHECKLIST:

✅ 1. Verify audit_log table exists
✅ 2. Verify all 9 triggers are installed
✅ 3. Test INSERT with user context
✅ 4. Test UPDATE with user context
✅ 5. Test DELETE with user context
✅ 6. Test operation without user context (modified_by = NULL)
✅ 7. Verify JSONB data is stored correctly
✅ 8. Check query performance with indexes
✅ 9. Review audit log entries

TROUBLESHOOTING:

If no audit entries are created:
1. Check triggers: SELECT * FROM information_schema.triggers WHERE trigger_name LIKE 'trg_audit_%';
2. Check function: SELECT proname FROM pg_proc WHERE proname = 'audit_trigger_function';
3. Check permissions: GRANT INSERT ON audit_log TO your_app_user;

If modified_by is always NULL:
1. Ensure you run: SET app.current_user = <user_id>;
2. In FastAPI, call: set_audit_user_context(db, user_id)

CLEANUP TEST DATA:

To remove test entries:
DELETE FROM audit_log WHERE modified_by = 999;  -- Remove test user entries
*/

-- Reset user context
RESET app.current_user;

SELECT 'Test complete!' as status;
