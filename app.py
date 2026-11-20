import os
import pandas as pd
import streamlit as st
from data.generate_dataset import generate_attendance_data
from src.risk_model import AttendanceRiskPredictor

st.set_page_config(
    page_title="AI Attendance Insights | Snowflake & ML",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 AI-Based Student Attendance Insights & Risk System")
st.markdown(
    "Cloud-ready analytical warehouse (**Snowflake + Cortex AI**) paired with "
    "supervised detention-risk forecasting (**Random Forest**)."
)


@st.cache_data
def load_attendance_data():
    try:
        conn = st.connection("snowflake")
        df = conn.query("SELECT * FROM ATTENDANCE_AI_DB.ANALYTICS.ATTENDANCE_LOGS;", ttl="10m")
        df.columns = [c.lower() for c in df.columns]
        return df, "Connected to Live Snowflake Warehouse"
    except Exception:
        csv_path = os.path.join("data", "attendance_records.csv")
        if not os.path.exists(csv_path):
            df = generate_attendance_data()
        else:
            df = pd.read_csv(csv_path)
        return df, "Local Analytical Mode (CSV Fallback)"


df, connection_status = load_attendance_data()
st.info(f"**Data Pipeline Status:** {connection_status} | **Loaded Records:** {len(df):,}")

predictor = AttendanceRiskPredictor()
metrics = predictor.train(df)
df["risk_probability_pct"] = (predictor.predict_risk_prob(df) * 100).round(1)
df["risk_tier"] = df.apply(
    lambda r: predictor.assign_risk_tier(r["attendance_pct"], r["consecutive_absences"]),
    axis=1,
)

# Top-level KPI Summary
k1, k2, k3, k4 = st.columns(4)
k1.metric("Overall Mean Attendance", f"{df['attendance_pct'].mean():.2f}%")
k2.metric("Below 75% Threshold", int((df["attendance_pct"] < 75.0).sum()))
k3.metric("RF Model Accuracy", f"{metrics['accuracy']}%")
k4.metric("At-Risk Recall", f"{metrics['recall_risk']}%")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Departmental Analytics",
    "🤖 AI Mentor Interventions",
    "📈 ML Interpretability",
    "🧪 Live Scenario Simulator",
])

with tab1:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        selected_dept = st.selectbox(
            "Filter by Department", ["ALL"] + sorted(df["department"].unique().tolist())
        )
        selected_tier = st.multiselect(
            "Filter by Risk Tier",
            ["CRITICAL", "HIGH_RISK", "WARNING", "SAFE"],
            default=["CRITICAL", "HIGH_RISK", "WARNING"],
        )

    filtered = df.copy()
    if selected_dept != "ALL":
        filtered = filtered[filtered["department"] == selected_dept]
    if selected_tier:
        filtered = filtered[filtered["risk_tier"].isin(selected_tier)]

    with col_b:
        st.subheader("Subject-Wise Average Attendance (%)")
        subj_chart = filtered.groupby("subject_name")["attendance_pct"].mean()
        st.bar_chart(subj_chart)

    st.subheader(f"Filtered Student Risk Records ({len(filtered)} rows)")
    st.dataframe(
        filtered.sort_values(["attendance_pct", "consecutive_absences"], ascending=[True, False]),
        use_container_width=True,
    )

with tab2:
    st.subheader("Automated Academic Advisor Recommendations")
    actionable = df[df["risk_tier"].isin(["CRITICAL", "HIGH_RISK", "WARNING"])].copy()
    actionable = actionable.sort_values("attendance_pct").head(25)
    actionable["mentor_alert"] = actionable.apply(predictor.generate_mentor_alert, axis=1)
    st.dataframe(
        actionable[
            ["student_id", "student_name", "department", "subject_name", "attendance_pct", "risk_tier", "mentor_alert"]
        ],
        use_container_width=True,
    )

with tab3:
    st.subheader("Feature Importance Driving Detention Risk Predictions")
    imp_df = pd.DataFrame.from_dict(
        metrics["feature_importances"], orient="index", columns=["Importance"]
    ).sort_values("Importance", ascending=False)
    st.bar_chart(imp_df)
    st.write(
        f"**Validation Summary:** Precision = `{metrics['precision_risk']}%` | "
        f"Recall = `{metrics['recall_risk']}%` | F1-Score = `{metrics['f1_risk']}%`"
    )

with tab4:
    st.subheader("Test Custom Student Attendance Scenario")
    c1, c2, c3, c4 = st.columns(4)
    sim_total = c1.number_input("Total Classes Held", min_value=10, max_value=60, value=40)
    sim_attended = c2.number_input("Classes Attended", min_value=0, max_value=sim_total, value=29)
    sim_last7 = c3.slider("Last 5 Classes Attended", min_value=0, max_value=5, value=2)
    sim_streak = c4.slider("Consecutive Absences", min_value=0, max_value=10, value=3)

    sim_pct = round((sim_attended / sim_total) * 100, 2)
    sim_df = pd.DataFrame([{
        "attendance_pct": sim_pct,
        "last_7_days_attended": sim_last7,
        "consecutive_absences": sim_streak,
        "total_classes": sim_total,
    }])

    sim_prob = round(float(predictor.predict_risk_prob(sim_df).iloc[0]) * 100, 1)
    sim_tier = predictor.assign_risk_tier(sim_pct, sim_streak)

    st.metric("Calculated Attendance", f"{sim_pct}%", delta=f"{round(sim_pct - 75.0, 2)}% vs 75% Rule")
    st.warning(f"**Predicted Risk Tier:** `{sim_tier}` | **Detention Probability:** `{sim_prob}%`")