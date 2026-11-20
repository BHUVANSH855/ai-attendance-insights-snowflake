USE DATABASE ATTENDANCE_AI_DB;
USE SCHEMA ANALYTICS;

-- 1. Department-Level Attendance & Risk Aggregation
SELECT
    department,
    COUNT(DISTINCT student_id) AS total_students,
    ROUND(AVG(overall_attendance_pct), 2) AS avg_dept_attendance,
    SUM(CASE WHEN risk_tier IN ('CRITICAL', 'HIGH_RISK') THEN 1 ELSE 0 END) AS at_risk_students
FROM VW_STUDENT_RISK_SUMMARY
GROUP BY department
ORDER BY avg_dept_attendance ASC;

-- 2. Top Lowest-Attendance Students Ranked per Department
SELECT
    student_id,
    student_name,
    department,
    overall_attendance_pct,
    max_absence_streak,
    risk_tier,
    DENSE_RANK() OVER (
        PARTITION BY department
        ORDER BY overall_attendance_pct ASC, max_absence_streak DESC
    ) AS dept_risk_rank
FROM VW_STUDENT_RISK_SUMMARY
QUALIFY dept_risk_rank <= 5;

-- 3. Automated Mentor Intervention Generation via Snowflake Cortex AI_COMPLETE
SELECT
    student_id,
    student_name,
    department,
    overall_attendance_pct,
    risk_tier,
    SNOWFLAKE.CORTEX.AI_COMPLETE(
        'mistral-large2',
        CONCAT(
            'You are a university academic advisor. Student ', student_name,
            ' (ID: ', student_id, ', Department: ', department, ') currently has ',
            overall_attendance_pct, '% overall attendance and a maximum absence streak of ',
            max_absence_streak, ' consecutive classes (Risk Tier: ', risk_tier, '). ',
            'Write a concise, actionable 2-sentence intervention recommendation for their faculty mentor.'
        )
    ) AS ai_mentor_recommendation
FROM VW_STUDENT_RISK_SUMMARY
WHERE risk_tier IN ('CRITICAL', 'HIGH_RISK', 'WARNING')
ORDER BY overall_attendance_pct ASC
LIMIT 20;