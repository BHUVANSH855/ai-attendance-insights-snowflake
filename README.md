# AI-Based Student Attendance Insights & Risk System (Snowflake + Python)

An end-to-end cloud data warehousing and machine-learning analytics system built on **Snowflake**, **Snowflake Cortex AI**, **Python (scikit-learn)**, and **Streamlit** to monitor student attendance, forecast end-of-semester detention risk (`<75%` threshold), and generate automated, actionable mentor interventions.

---

## Key Features

- **Flexible Real-World Data Ingestion**: Supports three live data pipelines—(1) custom institutional attendance CSV uploads directly via the web sidebar, (2) live **Snowflake Cloud Data Warehouse** querying via `st.connection("snowflake")`, and (3) automatic fallback to the **UCI Student Performance Dataset (`649` real student records)**[cite: 42].
- **Cloud Data Warehouse Schema (`Snowflake`)**: Normalized database (`ATTENDANCE_AI_DB.ANALYTICS`) with primary-key constraints and analytical views (`VW_STUDENT_RISK_SUMMARY`) computing overall attendance percentages and consecutive absence streaks.
- **Snowflake Cortex AI Integration**: Executes `SNOWFLAKE.CORTEX.AI_COMPLETE` (`mistral-large2`) inside SQL queries to generate tailored 2-sentence academic advisor intervention plans for `CRITICAL`, `HIGH_RISK`, and `WARNING` students.
- **Supervised Detention-Risk Forecasting (`Random Forest`)**: Predicts end-of-semester detention probability based on cumulative attendance percentage, recent 7-day attendance, consecutive absence streaks, and total classes held (`85.38%` accuracy and `90.0%` precision on the UCI benchmark dataset)[cite: 42].
- **Automated Model Validation & Plotting**: Exports high-resolution evaluation figures (Feature Importance, Confusion Matrix, and Department-Wise Attendance vs. 75% Eligibility Threshold) for technical documentation[cite: 42, 43].

---

## Project Architecture & Directory Structure

```text
ai-attendance-insights-snowflake/
├── data/
│   ├── generate_dataset.py      # Fetches & normalizes the real UCI Student Performance dataset (649 records)
│   ├── attendance_records.csv   # Normalized real-world benchmark dataset
│   └── student_data.csv         # Initial seed sample dataset
├── sql/
│   ├── create_table.sql         # Snowflake DB, Schema, Table & VW_STUDENT_RISK_SUMMARY view
│   └── ai_analysis.sql          # Department aggregations, DENSE_RANK() & Cortex AI_COMPLETE queries
├── src/
│   └── risk_model.py            # RandomForestClassifier, risk-tier categorization & alert engine
├── evaluation/
│   └── benchmark_and_plots.py   # Model validation metrics & Chapter 4 evaluation plots
├── screenshots/                 # Snowflake query outputs & generated evaluation figures
├── app.py                       # Interactive multi-tab Streamlit dashboard with live CSV uploader
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules for secrets and cache files
└── README.md                    # Project documentation
```

---

## Risk Categorization Rules

| Risk Tier | Trigger Condition | Recommended Action |
| :--- | :--- | :--- |
| **CRITICAL** | Attendance `< 65.0%` | Immediate parent notification and HOD escalation |
| **HIGH_RISK** | Attendance `65.0% – 74.9%` | Mandatory faculty mentor counseling session |
| **WARNING** | Attendance `75.0% – 79.9%` AND `>= 3` consecutive absences | Early warning notice to prevent threshold breach |
| **SAFE** | Attendance `>= 80.0%` (or `>= 75.0%` with `< 3` consecutive absences) | Standard monitoring |

---

## Quick Start (Local Execution)

1. **Clone the Repository**
   ```bash
   git clone [https://github.com/BHUVANSH855/ai-attendance-insights-snowflake.git](https://github.com/BHUVANSH855/ai-attendance-insights-snowflake.git)
   cd ai-attendance-insights-snowflake
   ```

2. **Create Virtual Environment & Install Dependencies**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. **Fetch & Normalize the Real UCI Benchmark Dataset (649 Records)**
   ```bash
   .\.venv\Scripts\python.exe data/generate_dataset.py
   ```

4. **Run Model Evaluation & Export Validation Charts**
   ```bash
   .\.venv\Scripts\python.exe evaluation/benchmark_and_plots.py
   ```

5. **Launch the Interactive Web Dashboard**
   ```bash
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

---

## Snowflake Cloud Warehouse Setup

1. Log into your **Snowflake Snowsight** workspace and open a new SQL Worksheet.
2. Execute `sql/create_table.sql` to create `ATTENDANCE_AI_DB`, the `ANALYTICS` schema, the `ATTENDANCE_LOGS` table, and the `VW_STUDENT_RISK_SUMMARY` view.
3. Load `data/attendance_records.csv` into `ATTENDANCE_AI_DB.ANALYTICS.ATTENDANCE_LOGS`.
4. Execute `sql/ai_analysis.sql` to run department aggregations, window-function risk rankings (`DENSE_RANK()`), and `SNOWFLAKE.CORTEX.AI_COMPLETE` mentor recommendations.
5. *(Optional)* To connect `app.py` directly to your live Snowflake account, create `.streamlit/secrets.toml`:
   ```toml
   [connections.snowflake]
   account = "your_account_identifier"
   user = "your_username"
   password = "your_password"
   role = "ACCOUNTADMIN"
   warehouse = "COMPUTE_WH"
   database = "ATTENDANCE_AI_DB"
   schema = "ANALYTICS"
   ```

---

## Tech Stack

- **Cloud Data Warehouse & GenAI**: Snowflake, Snowflake SQL, Snowflake Cortex (`AI_COMPLETE`)
- **Machine Learning & Data Processing**: Python 3.10+, `scikit-learn`, `pandas`, `numpy`
- **Frontend & Visualization**: `Streamlit`, `Matplotlib`