DROP TABLE IF EXISTS docma.usage_elec CASCADE;

CREATE TABLE docma.usage_elec
(
    nmi             VARCHAR(10) NOT NULL,
    read_date       DATE,
    read_start_aest TIMESTAMP,
    import_kwh      DECIMAL(10, 4)
);

COPY docma.usage_elec FROM 'data/usage-elec.csv' CSV HEADER;

CREATE OR REPLACE VIEW docma.daily_usage_elec AS
SELECT nmi, read_date, SUM(import_kwh) AS import_kwh
FROM docma.usage_elec
GROUP BY nmi, read_date;

