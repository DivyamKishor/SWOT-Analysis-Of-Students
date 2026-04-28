# 🎓 Student SWOT Analyzer

An automated student performance analysis tool that takes student academic data and generates SWOT analysis (Strengths, Weaknesses, Opportunities, Threats), performance scores across 6 dimensions, radar charts, and risk predictions — all through a web interface.

---

## 📋 Prerequisites

Make sure you have **Python 3.8 or above** installed. You can check by running:

```bash
python --version
```

---

## 📦 Installation

Install all required dependencies by running the following commands one by one in your terminal:

```bash
pip install streamlit
pip install pandas
pip install numpy
pip install matplotlib
pip install scikit-learn
```

Or install everything in one single command:

```bash
pip install streamlit pandas numpy matplotlib scikit-learn
```

---

## 🚀 Running the App

**Step 1** — Open your terminal and navigate to the project folder:

```bash
cd path/to/SWOT-Analysis-Of-Students
```

For example on Windows:
```bash
cd C:\Users\YourName\Desktop\SWOT-Analysis-Of-Students
```

**Step 2** — Start the app:

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

---

## 📁 Preparing Your Data

The app expects a CSV file named `master_student_data.csv` with the following columns:

| Column | Description |
|---|---|
| `student_id` | Unique student identifier |
| `student_name` | Full name of the student |
| `avg_cgpa` | Average CGPA (0–10 scale) |
| `latest_cgpa` | Most recent semester CGPA |
| `avg_external_marks` | External exam marks (out of 50) |
| `avg_iat_score` | Internal assessment score (0–100) |
| `latest_iat_score` | Most recent IAT score |
| `overall_attendance` | Attendance percentage |
| `sslc_percentage` | 10th grade marks percentage |
| `puc_percentage` | 12th grade marks percentage |
| `internship_count` | Number of internships completed |
| `activity_count` | Number of extracurricular activities |
| `tyl_skills_tracked` | Number of tracked skills |
| `fail_count` | Number of failed subjects |
| `cgpa_trend` | CGPA trend: `improving` / `stable` / `declining` |
| `attendance_trend` | Attendance trend: `improving` / `stable` / `declining` |
| `iat_trend` | IAT trend: `improving` / `stable` / `declining` |
| `consistency_index` | Consistency score (0–100) |
| `attendance_consistency_score` | Attendance consistency (0–100) |
| `pass_rate` | Pass rate percentage |

> A sample dataset `master_student_data.csv` is included in the repository for testing purposes.

---

## 🖥️ Using the App

1. Upload your CSV file using the **sidebar on the left**
2. Use the **Risk Level** filter to view High / Medium / Low risk students
3. Use the **Sort By** dropdown to reorder the student list
4. Click any student name from the list to view their full analysis
5. Navigate between the three tabs:
   - **Scores & Chart** — 6 dimension scores + radar chart
   - **SWOT Analysis** — Strengths, Weaknesses, Opportunities, Threats
   - **Recommendations** — Priority actions and suggestions
6. Use the **Download Full Results CSV** button at the bottom to export the analysis

---

## 📊 What the App Analyzes

Each student is scored across 6 dimensions:

| Dimension | What it measures |
|---|---|
| External Exam Performance | Semester marks + CGPA |
| Attendance Discipline | Attendance % + trend |
| Internal Assessment | IAT scores + trend |
| Foundation Strength | SSLC + PUC marks |
| Holistic Development | Internships + activities + skills |
| Consistency | Stability across all academic trends |

These are combined into an **Overall Performance Index** and used to generate a full SWOT analysis and risk prediction per student.

---

## 🗂️ Project Structure

```
SWOT-Analysis-Of-Students/
│
├── app.py                            # Main Streamlit web app
├── master_student_data.csv           # Sample student dataset
├── upgraded_hybrid_datamerger.ipynb  # Data cleaning & enrichment notebook
├── hybrid_skill_scoring_v2.ipynb     # Scoring, ML & SWOT generation notebook
├── utils/
│   └── helpers.py                    # Utility functions
└── README.md                         # This file
```

---

## ⚙️ Running the Jupyter Notebooks (Optional)

If you want to run the full ML pipeline instead of just the web app:

**Step 1** — Install Jupyter:
```bash
pip install notebook
```

**Step 2** — Launch Jupyter:
```bash
python -m notebook
```

**Step 3** — Run the notebooks in this order:
1. `upgraded_hybrid_datamerger.ipynb` — cleans and enriches your CSV
2. `hybrid_skill_scoring_v2.ipynb` — trains ML models and generates full analysis

---

## 🛠️ Troubleshooting

**`streamlit` is not recognized:**
```bash
python -m streamlit run app.py
```

**`jupyter` is not recognized:**
```bash
python -m notebook
```

**Missing module error:**
```bash
pip install <module-name>
```
