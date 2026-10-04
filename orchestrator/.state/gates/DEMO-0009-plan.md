## Plan

1. Add ExportTooLateError and check_export_age(export_date, run_date, config).
2. age_days <= 0 -> on time; 0 < age_days <= allowed_late_days -> late but accepted (logged); beyond that -> raise.
3. Tests for all three cases.
