# Test checklist

Result: PASS / FAIL. Update after every run of `python -m unittest discover`, and for the manual rows after every demo rehearsal.
Last automated run: **\_\_** (date) Tests run: \_**\_ Result: \_\_\_\_**

## Automated (tests/)

| #   | Rule / case                                                                     | Test                                                                                                          | Result |
| --- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------ |
| 1   | Price must be greater than 0 (constructor and setter)                           | test_domain: test_invalid_price_rejected_in_constructor, test_setters_validate_after_construction             |        |
| 2   | Reorder level cannot be negative                                                | test_domain: test_negative_reorder_level_rejected                                                             |        |
| 3   | Stock quantity cannot be negative                                               | test_domain: test_negative_starting_quantity_rejected, test_quantity_has_no_setter                            |        |
| 4   | Stock add rejects 0 and negatives                                               | test_domain: test_add_rejects_zero_and_negative                                                               |        |
| 5   | Stock remove beyond available raises InsufficientStockError                     | test_domain: test_remove_more_than_available                                                                  |        |
| 6   | Prescription line quantity above 0                                              | test_domain: test_line_quantity_must_be_positive                                                              |        |
| 7   | Status changes only pending to dispensed/cancelled                              | test_domain: PrescriptionTests (transition tests)                                                             |        |
| 8   | requires_authorisation() False for Ordinary, True for Controlled                | test_domain: test_requires_authorisation_polymorphism                                                         |        |
| 9   | Allow-list is a real membership test                                            | test_domain: PrescriberRegistryTests                                                                          |        |
| 10  | Duplicate medicine code rejected                                                | test_repository: test_duplicate_code_raises_domain_error                                                      |        |
| 11  | Database CHECK / foreign-key constraints refuse bad rows                        | test_repository: ConstraintTests                                                                              |        |
| 12  | Repository never commits by itself; transaction() commits or rolls back         | test_repository: TransactionTests                                                                             |        |
| 13  | Prescription header and lines saved together                                    | test_repository: test_prescription_header_and_lines_saved_together, test_failed_prescription_leaves_no_header |        |
| 14  | Low stock uses quantity <= reorder level, branch filter works                   | test*repository: test_low_stock*\*                                                                            |        |
| 15  | Data survives closing and reopening the database                                | test_repository: test_data_survives_reconnect                                                                 |        |
| 16  | Successful dispense (all lines, status dispensed)                               | test*dispensing: test_successful_dispense*\*                                                                  |        |
| 17  | Oversell rejected, message shows requested vs available                         | test_dispensing: test_oversell_rejected                                                                       |        |
| 18  | Controlled + unlisted prescriber (PRB-999) rejected                             | test_dispensing: test_controlled_with_unlisted_prescriber_rejected                                            |        |
| 19  | Controlled + listed prescriber accepted                                         | test_dispensing: test_controlled_medicine_with_listed_prescriber                                              |        |
| 20  | Re-dispense rejected                                                            | test_dispensing: test_re_dispense_rejected                                                                    |        |
| 21  | Dispense a cancelled prescription rejected                                      | test_dispensing: test_dispense_cancelled_rejected                                                             |        |
| 22  | Cancel a dispensed prescription rejected                                        | test_dispensing: test_cancel_dispensed_rejected                                                               |        |
| 23  | Empty prescription rejected                                                     | test_dispensing: test_empty_prescription_rejected                                                             |        |
| 24  | Atomic rollback: line 2 oversells, line 1 stock unchanged, status still pending | test_dispensing: test_rollback_leaves_stock_untouched_when_line_2_oversells                                   |        |

## Manual (GUI and fresh clone)

| #   | Step                                                            | Expected                                     | Result |
| --- | --------------------------------------------------------------- | -------------------------------------------- | ------ |
| M1  | Fresh clone, follow README sections 1 to 3                      | Database created, data loaded, window opens  |        |
| M2  | Register Medicine with price 0                                  | Readable error box, no traceback             |        |
| M3  | Register Medicine with text in a number box                     | "must be a whole number" box                 |        |
| M4  | Register an existing code twice                                 | Duplicate error box                          |        |
| M5  | Receive Stock with quantity -5                                  | Error box                                    |        |
| M6  | Create Prescription: Save disabled until a line exists          | Button disabled, then enabled                |        |
| M7  | Dispense PT-0001 (PRB-001, controlled)                          | Success box, stock reduced                   |        |
| M8  | Dispense PT-0002 (PRB-999, controlled)                          | Unauthorised prescriber box, stock unchanged |        |
| M9  | Dispense a prescription that oversells                          | Insufficient stock box, nothing changed      |        |
| M10 | Cancel a pending prescription, then dispense it                 | Cancelled error box                          |        |
| M11 | Low Stock tab shows MED-005 at Main Campus; branch filter works | Rows shown, filter works                     |        |
| M12 | Close the app and reopen                                        | All data still there                         |        |
