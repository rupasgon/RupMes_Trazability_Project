CREATE INDEX IF NOT EXISTS ix_production_report_production_datetime
    ON public.production_report (production_datetime);

CREATE INDEX IF NOT EXISTS ix_production_report_serial_number
    ON public.production_report (serial_number);

CREATE INDEX IF NOT EXISTS ix_production_report_line_datetime
    ON public.production_report (line_code, production_datetime);

CREATE INDEX IF NOT EXISTS ix_production_report_result
    ON public.production_report (result);

CREATE INDEX IF NOT EXISTS ix_production_report_error_code
    ON public.production_report (error_code);
