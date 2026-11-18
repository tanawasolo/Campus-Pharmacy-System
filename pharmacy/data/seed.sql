-- Fictional data only.
INSERT INTO branches (name) VALUES ('Main Campus'), ('Satellite Clinic');

INSERT INTO medicines (code, name, unit_price, reorder_level, is_controlled) VALUES
  ('MED-001', 'Paracetamol 500mg', 500, 50, 0),
  ('MED-002', 'Amoxicillin 250mg', 1500, 30, 0),
  ('MED-003', 'Ibuprofen 400mg', 800, 40, 0),
  ('MED-004', 'ORS Sachet', 300, 60, 0),
  ('MED-005', 'Cetirizine 10mg', 700, 20, 0),
  ('MED-006', 'Metformin 500mg', 1000, 25, 0),
  ('CTL-001', 'Morphine 10mg (fictional)', 9000, 10, 1),
  ('CTL-002', 'Diazepam 5mg (fictional)', 6000, 10, 1);

INSERT INTO stock (branch_id, medicine_code, quantity) VALUES
  (1, 'MED-001', 200), (1, 'MED-002', 80), (1, 'MED-003', 100),
  (1, 'MED-004', 150), (1, 'MED-005', 15),  -- MED-005 is below reorder level
  (1, 'MED-006', 60),  (1, 'CTL-001', 20),  (1, 'CTL-002', 10),
  (2, 'MED-001', 60),  (2, 'MED-002', 30),  (2, 'MED-004', 40),
  (2, 'CTL-001', 5);

INSERT INTO prescribers (code, name) VALUES
  ('PRB-001', 'Dr. Fictional One'),
  ('PRB-002', 'Dr. Fictional Two'),
  ('PRB-003', 'Dr. Fictional Three');

-- PRB-999 is deliberately NOT in prescribers (used for the rejection demo).
INSERT INTO prescriptions (patient_id, branch_id, prescriber_code, status) VALUES
  ('PT-0001', 1, 'PRB-001', 'pending'),
  ('PT-0002', 1, 'PRB-999', 'pending'),
  ('PT-0003', 2, NULL, 'pending');

INSERT INTO prescription_lines (prescription_id, medicine_code, quantity) VALUES
  (1, 'MED-001', 10), (1, 'CTL-001', 2),
  (2, 'CTL-002', 1),
  (3, 'MED-002', 5);
