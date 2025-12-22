# 📊 AI Attendance & Performance Insight System  
**AI for Good Hackathon | Snowflake + Cortex AI**

---

## 🧩 Problem Statement
Schools often struggle to identify students who need early academic attention due to **irregular attendance** or **declining performance**.  
Manual monitoring is time-consuming, reactive, and error-prone, which delays timely intervention.

---

## 💡 Solution
This project leverages **Snowflake Cortex AI** to analyze student attendance and performance data and generate **human-readable explanations and recommendations** for at-risk students.  
The system enables educators to make **early, data-driven decisions** using AI-powered insights.

---

## 🛠 Tech Stack
- **Snowflake Data Warehouse**
- **Snowflake Cortex AI (snowflake-arctic)**
- **SQL**
- **Synthetic student dataset (CSV)**

---

## 📂 Dataset
**Fields used:**
- `student_id`
- `student_name`
- `class`
- `date`
- `attendance`
- `marks`

The dataset represents daily attendance and academic performance records for students.

---

## 🧠 AI Features
- ✅ Attendance anomaly detection  
- ✅ Performance risk identification  
- ✅ Natural-language explanations using **Snowflake Cortex AI**  
- ✅ Non-technical, easy-to-understand outputs  

---

## 🏗 Architecture / Workflow
1. Student attendance & performance data is stored in **Snowflake**
2. SQL queries aggregate attendance and marks
3. **Snowflake Cortex AI** generates explanations and recommendations
4. Educators receive clear, actionable insights

---

## 🔍 Sample AI Analysis Query
```sql
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
      '. Provide a short recommendation.'
    )
  ) AS ai_recommendation
FROM SCHOOL_DB.PUBLIC.STUDENT_ATTENDANCE
GROUP BY student_name
HAVING COUNT_IF(attendance = 'Absent') >= 2
   OR AVG(marks) < 60;
