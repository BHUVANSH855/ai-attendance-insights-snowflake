CREATE DATABASE IF NOT EXISTS ATTENDANCE_AI_DB;
USE DATABASE ATTENDANCE_AI_DB;

CREATE SCHEMA IF NOT EXISTS ANALYTICS;
USE SCHEMA ANALYTICS;

CREATE OR REPLACE TABLE ATTENDANCE_LOGS (
    student_id VARCHAR(20) NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    department VARCHAR(20) NOT NULL,
    subject_code VARCHAR(15) NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    total_classes INT NOT NULL,
    attended_classes INT NOT NULL,
    attendance_pct FLOAT NOT NULL,
    last_7_days_attended INT NOT NULL,
    consecutive_absences INT NOT NULL,
    detention_risk INT NOT NULL,
    ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (student_id, subject_code)
);

CREATE OR REPLACE VIEW VW_STUDENT_RISK_SUMMARY AS
SELECT
    student_id,
    student_name,
    department,
    ROUND(AVG(attendance_pct), 2) AS overall_attendance_pct,
    SUM(total_classes) AS total_classes_held,
    SUM(attended_classes) AS total_classes_attended,
    MAX(consecutive_absences) AS max_absence_streak,
    CASE
        WHEN AVG(attendance_pct) < 65.0 THEN 'CRITICAL'
        WHEN AVG(attendance_pct) < 75.0 THEN 'HIGH_RISK'
        WHEN AVG(attendance_pct) < 80.0 AND MAX(consecutive_absences) >= 3 THEN 'WARNING'
        ELSE 'SAFE'
    END AS risk_tier
FROM ATTENDANCE_LOGS
GROUP BY student_id, student_name, department;
