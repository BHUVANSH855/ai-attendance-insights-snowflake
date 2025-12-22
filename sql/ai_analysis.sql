SELECT
  student_name,
  SNOWFLAKE.CORTEX.COMPLETE(
    'snowflake-arctic',
    CONCAT(
      'Student risk analysis. ',
      'Absent days: ',
      COUNT_IF(attendance = ''Absent''),
      '. Average marks: ',
      ROUND(AVG(marks), 2),
      '. Give a short recommendation.'
    )
  ) AS ai_recommendation
FROM SCHOOL_DB.PUBLIC.STUDENT_ATTENDANCE
GROUP BY student_name
HAVING COUNT_IF(attendance = 'Absent') >= 2
   OR AVG(marks) < 60;
