-- =========================
-- CLEAN EXISTING DATA
-- =========================
DELETE FROM transactions;
DELETE FROM lifecycle_logs;
DELETE FROM inventory;
DELETE FROM components;
DELETE FROM users;

-- =========================
-- RESET SEQUENCES
-- =========================
ALTER SEQUENCE users_id_seq RESTART WITH 1;

-- =========================
-- USERS
-- =========================
INSERT INTO users (id, username, password, role) VALUES
(1, 'admin', 'admin', 'admin'),
(2, 'officer_armaan', '1234', 'officer'),
(3, 'store_incharge', 'store123', 'officer');

-- =========================
-- COMPONENTS (REALISTIC GENERIC DEFENSE)
-- =========================
INSERT INTO components (component_id, name, state) VALUES
(1, 'Barrel Assembly', 'manufactured'),
(2, 'Trigger Mechanism', 'stored'),
(3, 'Bolt Carrier Group', 'stored'),
(4, 'Gas Regulator Unit', 'stored'),
(5, 'Recoil Spring Assembly', 'stored'),
(6, 'Magazine Housing', 'stored'),
(7, 'Firing Pin', 'stored'),
(8, 'Upper Receiver', 'stored'),
(9, 'Lower Receiver', 'stored'),
(10, 'Optical Sight Mount', 'stored'),
(11, 'Thermal Sensor Unit', 'stored'),
(12, 'Cooling Module', 'stored'),
(13, 'Hydraulic Stabilizer', 'stored'),
(14, 'Servo Motor Unit', 'stored'),
(15, 'Targeting Control Panel', 'stored');

-- =========================
-- INVENTORY (REALISTIC LOCATIONS)
-- =========================
INSERT INTO inventory (component_id, quantity, location) VALUES
(1, 25, 'Central Ordnance Depot'),
(2, 40, 'Field Storage Unit A'),
(3, 30, 'Field Storage Unit B'),
(4, 20, 'Maintenance Bay'),
(5, 35, 'Central Ordnance Depot'),
(6, 50, 'Depot Section C'),
(7, 100, 'Ammunition Storage'),
(8, 15, 'Assembly Unit'),
(9, 15, 'Assembly Unit'),
(10, 10, 'Optics Lab'),
(11, 8, 'Electronics Unit'),
(12, 18, 'Cooling Systems Unit'),
(13, 12, 'Heavy Equipment Storage'),
(14, 14, 'Mechanical Unit'),
(15, 6, 'Control Systems Lab');

-- =========================
-- LIFECYCLE LOGS
-- =========================
INSERT INTO lifecycle_logs (component_id, old_state, new_state) VALUES
(1, 'manufactured', 'stored'),
(3, 'manufactured', 'stored'),
(5, 'manufactured', 'stored'),
(8, 'manufactured', 'stored'),
(11, 'manufactured', 'stored'),
(13, 'manufactured', 'stored');

-- =========================
-- TRANSACTIONS
-- =========================
INSERT INTO transactions (component_id, action, user_id) VALUES
(1, 'stored', 1),
(2, 'issued', 2),
(3, 'stored', 3),
(4, 'issued', 2),
(5, 'stored', 1),
(7, 'issued', 3),
(10, 'stored', 1),
(11, 'issued', 2),
(13, 'stored', 3);