import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Student SWOT Analyzer", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background: #0f1117; color: #e8eaf0; }
.hero { background: linear-gradient(135deg, #1a1f2e 0%, #0f1117 60%, #0d1a2e 100%); border: 1px solid #1e3a5f; border-radius: 16px; padding: 2.5rem 3rem; margin-bottom: 2rem; position: relative; overflow: hidden; }
.hero h1 { font-size: 2.2rem; font-weight: 700; color: #ffffff; margin: 0 0 0.4rem 0; letter-spacing: -0.5px; }
.hero p { color: #8892a4; font-size: 1rem; margin: 0; font-weight: 300; }
.hero .accent { color: #3b82f6; }
.metric-card { background: #161b27; border: 1px solid #1e293b; border-radius: 12px; padding: 1.2rem 1.5rem; text-align: center; }
.metric-card .val { font-size: 2rem; font-weight: 700; color: #3b82f6; font-family: 'JetBrains Mono', monospace; }
.metric-card .label { font-size: 0.78rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.2rem; }
.swot-box { border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 0.8rem; }
.swot-s { background: rgba(34,197,94,0.07); border: 1px solid rgba(34,197,94,0.25); }
.swot-w { background: rgba(239,68,68,0.07); border: 1px solid rgba(239,68,68,0.25); }
.swot-o { background: rgba(59,130,246,0.07); border: 1px solid rgba(59,130,246,0.25); }
.swot-t { background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.25); }
.swot-title { font-weight: 700; font-size: 0.8rem; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 0.6rem; }
.swot-s .swot-title { color: #22c55e; }
.swot-w .swot-title { color: #ef4444; }
.swot-o .swot-title { color: #3b82f6; }
.swot-t .swot-title { color: #f59e0b; }
.swot-item { font-size: 0.88rem; color: #cbd5e1; padding: 0.25rem 0; }
.score-bar-wrap { margin: 0.4rem 0; }
.score-label { font-size: 0.8rem; color: #94a3b8; display: flex; justify-content: space-between; margin-bottom: 3px; }
.score-bar-bg { background: #1e293b; border-radius: 4px; height: 7px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 4px; }
.section-title { font-size: 1rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 2px; margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 1px solid #1e293b; }
.rec-item { background: #161b27; border-left: 3px solid #3b82f6; border-radius: 0 8px 8px 0; padding: 0.7rem 1rem; margin-bottom: 0.5rem; font-size: 0.88rem; color: #cbd5e1; }
.rec-urgent { border-left-color: #ef4444 !important; background: rgba(239,68,68,0.05) !important; }
.stat-pill { display: inline-block; background: #1e293b; border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; color: #94a3b8; margin: 3px; font-family: 'JetBrains Mono', monospace; }
.risk-high { color: #ef4444; background: rgba(239,68,68,0.1); padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.risk-medium { color: #f59e0b; background: rgba(245,158,11,0.1); padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.risk-low { color: #22c55e; background: rgba(34,197,94,0.1); padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
div[data-testid="stSidebar"] { background: #0d1117; border-right: 1px solid #1e293b; }
</style>
""", unsafe_allow_html=True)

def to_num(val, default=0):
    try:
        v = float(val)
        return default if (v != v) else v
    except: return default

def calc_external(row):
    ext = to_num(row.get('avg_external_marks', 0))
    ext_norm = (ext / 50.0) * 100.0
    cgpa = to_num(row.get('avg_cgpa', 0))
    score = (ext_norm * 0.60) + ((cgpa / 10.0) * 40.0)
    trend = str(row.get('cgpa_trend', '')).lower()
    if trend == 'improving': score += 5
    elif trend == 'declining': score -= 5
    return float(max(0, min(round(score, 2), 100)))

def calc_attendance(row):
    att = to_num(row.get('overall_attendance', 0))
    if att >= 90: score = 90
    elif att >= 80: score = 80
    elif att >= 70: score = 65
    elif att >= 60: score = 50
    else: score = max(25, att * 0.7)
    trend = str(row.get('attendance_trend', '')).lower()
    if trend == 'improving': score += 10
    elif trend == 'declining': score -= 10
    elif trend == 'stable': score += 3
    consistency = to_num(row.get('attendance_consistency_score', 50))
    score += (consistency / 100.0) * 5
    return float(max(0, min(round(score, 2), 100)))

def calc_iat(row):
    avg_iat = to_num(row.get('avg_iat_score', 0))
    score = avg_iat
    trend = str(row.get('iat_trend', '')).lower()
    latest = to_num(row.get('latest_iat_score', 0))
    if trend == 'improving': score += 7
    elif trend == 'declining': score -= 7
    if latest > avg_iat + 5: score += 3
    elif latest < avg_iat - 5: score -= 3
    return float(max(0, min(round(score, 2), 100)))

def calc_foundation(row):
    sslc = to_num(row.get('sslc_percentage', 0))
    puc = to_num(row.get('puc_percentage', 0))
    return float(max(0, min(round((sslc * 0.40) + (puc * 0.60), 2), 100)))

def calc_holistic(row):
    score = 20.0
    internships = int(to_num(row.get('internship_count', 0)))
    activities = int(to_num(row.get('activity_count', 0)))
    tyl = int(to_num(row.get('tyl_skills_tracked', 0)))
    if internships >= 3: score += 30
    elif internships == 2: score += 22
    elif internships == 1: score += 12
    if activities >= 8: score += 25
    elif activities >= 5: score += 18
    elif activities >= 3: score += 10
    elif activities >= 1: score += 4
    if tyl >= 5: score += 20
    elif tyl >= 3: score += 13
    elif tyl >= 1: score += 6
    return float(max(0, min(round(score, 2), 100)))

def calc_consistency(row):
    trends = [str(row.get('attendance_trend', '')).lower(), str(row.get('iat_trend', '')).lower(), str(row.get('cgpa_trend', '')).lower()]
    improving = trends.count('improving')
    declining = trends.count('declining')
    score = 50 + (improving * 15) - (declining * 15)
    ci = to_num(row.get('consistency_index', 50))
    score += (ci - 50) * 0.3
    return float(max(0, min(round(score, 2), 100)))

WEIGHTS = {'external_exam_performance': 0.40, 'attendance_discipline': 0.25, 'internal_assessment': 0.15, 'foundation_strength': 0.10, 'holistic_development': 0.05, 'consistency': 0.05}

def score_row(row):
    r = dict(row)
    r['external_exam_performance'] = calc_external(r)
    r['attendance_discipline'] = calc_attendance(r)
    r['internal_assessment'] = calc_iat(r)
    r['foundation_strength'] = calc_foundation(r)
    r['holistic_development'] = calc_holistic(r)
    r['consistency'] = calc_consistency(r)
    r['overall_performance_index'] = round(sum(r[k] * v for k, v in WEIGHTS.items()), 2)
    risk = 0
    if r['overall_performance_index'] < 50: risk += 35
    if to_num(r.get('avg_cgpa', 0)) < 5.0: risk += 25
    if to_num(r.get('overall_attendance', 0)) < 75: risk += 25
    if to_num(r.get('fail_count', 0)) > 2: risk += 15
    r['ml_risk_probability'] = min(risk, 100)
    cgpa_now = to_num(r.get('latest_cgpa', 0)) or to_num(r.get('avg_cgpa', 0))
    trend = str(r.get('cgpa_trend', '')).lower()
    delta = 0.3 if trend == 'improving' else (-0.3 if trend == 'declining' else 0)
    r['ml_predicted_next_cgpa'] = round(cgpa_now + delta, 2)
    r['academic_momentum'] = delta
    return r

def generate_swot(row):
    s, w, o, t = [], [], [], []
    ext = to_num(row.get('external_exam_performance', 0))
    cgpa = to_num(row.get('avg_cgpa', 0))
    cgpa_trend = str(row.get('cgpa_trend', '')).lower()
    if ext >= 80:
        s.append(f"Excellent external performance (CGPA {cgpa:.2f})")
        if cgpa_trend == 'improving': s.append("Strong upward CGPA trend")
    if ext < 50:
        w.append("Weak external exam performance")
        if cgpa_trend == 'declining': w.append("Declining CGPA trend detected")
    att = to_num(row.get('overall_attendance', 0))
    att_d = to_num(row.get('attendance_discipline', 0))
    att_trend = str(row.get('attendance_trend', '')).lower()
    if att_d >= 85: s.append(f"Excellent attendance ({att:.1f}%)")
    if att_d < 75:
        w.append(f"Low attendance ({att:.1f}%)")
        t.append("Attendance risk — possible detention")
    if att_trend == 'declining': t.append("Declining attendance trend")
    iat = to_num(row.get('internal_assessment', 0))
    iat_trend = str(row.get('iat_trend', '')).lower()
    if iat >= 70: s.append("Strong internal assessment performance")
    if iat < 50: w.append("Weak internal assessment performance")
    if iat_trend == 'declining': t.append("IAT score trend declining")
    elif iat_trend == 'improving': o.append("Improving IAT trend")
    internships = int(to_num(row.get('internship_count', 0)))
    activities = int(to_num(row.get('activity_count', 0)))
    holistic = to_num(row.get('holistic_development', 0))
    if holistic >= 65:
        s.append("Good holistic development profile")
        if internships > 0: s.append(f"Completed {internships} internship(s)")
        if activities >= 5: s.append(f"Active in {activities} extracurricular activities")
    else:
        if internships == 0: w.append("No internship experience")
        if activities < 2: w.append("Limited extracurricular participation")
    ci = to_num(row.get('consistency_index', 50))
    momentum = to_num(row.get('academic_momentum', 0))
    if ci >= 70: s.append("Consistent academic performance")
    if momentum > 0: o.append("Positive academic momentum — maintain progress")
    elif momentum < 0: t.append("Negative academic momentum detected")
    ml_risk = to_num(row.get('ml_risk_probability', 0))
    pred_cgpa = to_num(row.get('ml_predicted_next_cgpa', 0))
    latest_cgpa = to_num(row.get('latest_cgpa', 0))
    if ml_risk > 70: t.append(f"⚠ HIGH Risk: {ml_risk:.0f}% probability of poor performance")
    elif ml_risk > 40: o.append("Medium risk — early intervention recommended")
    if pred_cgpa and latest_cgpa:
        if pred_cgpa > latest_cgpa + 0.5: o.append(f"Projected CGPA improvement to {pred_cgpa:.2f}")
        elif pred_cgpa < latest_cgpa - 0.5: t.append(f"Predicted CGPA drop to {pred_cgpa:.2f}")
    if not s: s.append("Shows potential for improvement with guidance")
    if not w: w.append("No major weaknesses detected")
    if not o: o.append("Can benefit from structured academic planning")
    if not t: t.append("No immediate threats detected")
    return {'strengths': s, 'weaknesses': w, 'opportunities': o, 'threats': t}

def generate_recs(row):
    priority, recs = [], []
    ml_risk = to_num(row.get('ml_risk_probability', 0))
    ext = to_num(row.get('external_exam_performance', 0))
    att = to_num(row.get('overall_attendance', 0))
    holistic = to_num(row.get('holistic_development', 0))
    pred = to_num(row.get('ml_predicted_next_cgpa', 0))
    latest = to_num(row.get('latest_cgpa', 0))
    if ml_risk > 70:
        priority.append("🚨 Schedule immediate meeting with academic advisor")
        priority.append("Enroll in academic support program")
    if ext < 50: priority.append("URGENT: Focus on improving external exam preparation")
    if att < 75: priority.append("CRITICAL: Improve attendance above 75% immediately")
    if ext < 65: recs.append("Practice PYQs weekly to strengthen exam performance")
    if holistic < 50:
        if int(to_num(row.get('internship_count', 0))) == 0: recs.append("Apply for internships to gain real-world experience")
        if int(to_num(row.get('activity_count', 0))) < 3: recs.append("Participate in at least one technical/cultural club")
    if pred and latest:
        if pred < latest - 0.3: recs.append("Increase study hours — CGPA risk detected")
        elif pred > latest + 0.3: recs.append("Great potential! Maintain consistency")
    if not priority and not recs: recs.append("Continue current performance trajectory")
    return priority, recs

def make_spider(row, name="Student"):
    labels = ['External\nExams', 'Attendance\nDiscipline', 'Internal\nAssessment', 'Foundation\nStrength', 'Holistic\nDevelopment', 'Consistency']
    keys = ['external_exam_performance', 'attendance_discipline', 'internal_assessment', 'foundation_strength', 'holistic_development', 'consistency']
    values = [to_num(row.get(k, 0)) for k in keys]
    N = len(labels)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    vals = values + values[:1]
    fig, ax = plt.subplots(figsize=(5.5, 5.5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#161b27')
    ax.set_facecolor('#0f1117')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color='#94a3b8', size=8.5)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], color='#475569', size=7)
    ax.spines['polar'].set_color('#1e293b')
    ax.grid(color='#1e293b', linewidth=0.8)
    opi = to_num(row.get('overall_performance_index', 50))
    if opi >= 70: fill_color, line_color = '#22c55e', '#4ade80'
    elif opi >= 50: fill_color, line_color = '#3b82f6', '#60a5fa'
    else: fill_color, line_color = '#ef4444', '#f87171'
    ax.plot(angles, vals, color=line_color, linewidth=2.2, linestyle='solid', zorder=3)
    ax.fill(angles, vals, color=fill_color, alpha=0.18, zorder=2)
    for angle, val in zip(angles[:-1], values):
        ax.plot(angle, val, 'o', color=line_color, markersize=5, zorder=4)
    ax.set_title(name, color='#e2e8f0', pad=18, fontsize=10, fontweight='bold')
    plt.tight_layout()
    return fig

def score_bar(label, value, color="#3b82f6"):
    return f'<div class="score-bar-wrap"><div class="score-label"><span>{label}</span><span style="font-family:JetBrains Mono,monospace;color:#e2e8f0">{value:.1f}</span></div><div class="score-bar-bg"><div class="score-bar-fill" style="width:{value}%;background:{color}"></div></div></div>'

def score_color(val):
    if val >= 70: return "#22c55e"
    elif val >= 50: return "#3b82f6"
    elif val >= 35: return "#f59e0b"
    return "#ef4444"

@st.cache_data
def process_df(df_json):
    import io
    df = pd.read_json(io.StringIO(df_json))
    records = []
    for _, row in df.iterrows():
        r = score_row(row.to_dict())
        swot = generate_swot(r)
        r['swot_json'] = json.dumps(swot)
        records.append(r)
    return pd.DataFrame(records)

# ─── UI ───────────────────────────────────────────────────────────────────────

st.markdown('<div class="hero"><h1>🎓 Student <span class="accent">SWOT</span> Analyzer</h1><p>Upload student data → get instant performance scores, SWOT analysis &amp; radar charts</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📂 Data Input")
    uploaded = st.file_uploader("Upload master_student_data.csv", type=["csv"])
    st.markdown("---")
    st.markdown("### 🔍 Filter & Sort")
    risk_filter = st.selectbox("Risk Level", ["All", "High Risk (>70)", "Medium Risk (40-70)", "Low Risk (<40)"])
    sort_by = st.selectbox("Sort By", ["Overall Score ↓", "Overall Score ↑", "Name A-Z", "Risk ↓"])
    st.markdown("---")
    st.markdown("<p style='color:#475569;font-size:0.75rem'>SWOT Analysis Tool · v1.0</p>", unsafe_allow_html=True)

if uploaded:
    raw_df = pd.read_csv(uploaded)
    df = process_df(raw_df.to_json())

    view_df = df.copy()
    if risk_filter == "High Risk (>70)": view_df = view_df[view_df['ml_risk_probability'] > 70]
    elif risk_filter == "Medium Risk (40-70)": view_df = view_df[(view_df['ml_risk_probability'] >= 40) & (view_df['ml_risk_probability'] <= 70)]
    elif risk_filter == "Low Risk (<40)": view_df = view_df[view_df['ml_risk_probability'] < 40]
    if sort_by == "Overall Score ↓": view_df = view_df.sort_values('overall_performance_index', ascending=False)
    elif sort_by == "Overall Score ↑": view_df = view_df.sort_values('overall_performance_index', ascending=True)
    elif sort_by == "Name A-Z": view_df = view_df.sort_values('student_name' if 'student_name' in view_df.columns else view_df.columns[0])
    elif sort_by == "Risk ↓": view_df = view_df.sort_values('ml_risk_probability', ascending=False)

    total = len(df)
    avg_opi = df['overall_performance_index'].mean()
    high_risk = (df['ml_risk_probability'] > 70).sum()
    top_performers = (df['overall_performance_index'] >= 70).sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card"><div class="val">{total}</div><div class="label">Total Students</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="val">{avg_opi:.1f}</div><div class="label">Avg Performance</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="val" style="color:#ef4444">{high_risk}</div><div class="label">High Risk</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card"><div class="val" style="color:#22c55e">{top_performers}</div><div class="label">Top Performers</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    name_col = 'student_name' if 'student_name' in view_df.columns else view_df.columns[0]
    id_col = 'student_id' if 'student_id' in view_df.columns else None

    col_list, col_detail = st.columns([1, 2])
    with col_list:
        st.markdown('<div class="section-title">Students</div>', unsafe_allow_html=True)
        student_names = view_df[name_col].tolist()
        selected_name = st.radio("", student_names, label_visibility="collapsed")

    selected_row = view_df[view_df[name_col] == selected_name].iloc[0].to_dict()
    swot = json.loads(selected_row.get('swot_json', '{}'))
    priority_recs, recs = generate_recs(selected_row)

    with col_detail:
        opi = to_num(selected_row.get('overall_performance_index', 0))
        risk = to_num(selected_row.get('ml_risk_probability', 0))
        risk_label = '<span class="risk-high">HIGH RISK</span>' if risk > 70 else ('<span class="risk-medium">MEDIUM RISK</span>' if risk > 40 else '<span class="risk-low">LOW RISK</span>')
        sid = f'<span style="font-size:0.78rem;color:#64748b;font-family:monospace">{selected_row.get(id_col, "")}</span>' if id_col else ''
        st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem"><div><div style="font-size:1.3rem;font-weight:600;color:#e2e8f0">{selected_name}</div>{sid}</div><div style="text-align:right">{risk_label}<div style="font-size:1.6rem;font-weight:700;color:#3b82f6;font-family:monospace">{opi:.1f}<span style="font-size:0.9rem;color:#64748b">/100</span></div><div style="font-size:0.7rem;color:#64748b;text-transform:uppercase;letter-spacing:1px">Overall Score</div></div></div>', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📊 Scores & Chart", "🔍 SWOT Analysis", "💡 Recommendations"])

        with tab1:
            left, right = st.columns([1, 1])
            with left:
                dims = [('External Exams', 'external_exam_performance'), ('Attendance', 'attendance_discipline'), ('Internal Assessment', 'internal_assessment'), ('Foundation', 'foundation_strength'), ('Holistic Dev', 'holistic_development'), ('Consistency', 'consistency')]
                bars_html = ""
                for label, key in dims:
                    val = to_num(selected_row.get(key, 0))
                    bars_html += score_bar(label, val, score_color(val))
                st.markdown(bars_html, unsafe_allow_html=True)
                cgpa = to_num(selected_row.get('avg_cgpa', 0))
                att = to_num(selected_row.get('overall_attendance', 0))
                pred = to_num(selected_row.get('ml_predicted_next_cgpa', 0))
                st.markdown(f'<br><span class="stat-pill">CGPA {cgpa:.2f}</span><span class="stat-pill">Att {att:.1f}%</span><span class="stat-pill">Pred CGPA {pred:.2f}</span><span class="stat-pill">Risk {risk:.0f}%</span>', unsafe_allow_html=True)
            with right:
                fig = make_spider(selected_row, selected_name)
                st.pyplot(fig, use_container_width=True)
                plt.close()

        with tab2:
            s2a, s2b = st.columns(2)
            with s2a:
                items = "".join(f'<div class="swot-item">✦ {i}</div>' for i in swot.get('strengths', []))
                st.markdown(f'<div class="swot-box swot-s"><div class="swot-title">Strengths</div>{items}</div>', unsafe_allow_html=True)
                items = "".join(f'<div class="swot-item">→ {i}</div>' for i in swot.get('opportunities', []))
                st.markdown(f'<div class="swot-box swot-o"><div class="swot-title">Opportunities</div>{items}</div>', unsafe_allow_html=True)
            with s2b:
                items = "".join(f'<div class="swot-item">✗ {i}</div>' for i in swot.get('weaknesses', []))
                st.markdown(f'<div class="swot-box swot-w"><div class="swot-title">Weaknesses</div>{items}</div>', unsafe_allow_html=True)
                items = "".join(f'<div class="swot-item">⚠ {i}</div>' for i in swot.get('threats', []))
                st.markdown(f'<div class="swot-box swot-t"><div class="swot-title">Threats</div>{items}</div>', unsafe_allow_html=True)

        with tab3:
            if priority_recs:
                st.markdown('<div class="section-title" style="color:#ef4444">🚨 Priority Actions</div>', unsafe_allow_html=True)
                for r in priority_recs:
                    st.markdown(f'<div class="rec-item rec-urgent">{r}</div>', unsafe_allow_html=True)
            if recs:
                st.markdown('<div class="section-title">💡 Recommendations</div>', unsafe_allow_html=True)
                for r in recs:
                    st.markdown(f'<div class="rec-item">{r}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:2rem">📋 All Students</div>', unsafe_allow_html=True)
    display_cols = [name_col] + ([id_col] if id_col else []) + ['overall_performance_index', 'external_exam_performance', 'attendance_discipline', 'internal_assessment', 'foundation_strength', 'holistic_development', 'consistency', 'ml_risk_probability', 'ml_predicted_next_cgpa']
    display_cols = [c for c in display_cols if c in view_df.columns]
    st.dataframe(view_df[display_cols].round(2).reset_index(drop=True), use_container_width=True, height=300)
    csv_out = view_df.drop(columns=['swot_json'], errors='ignore').to_csv(index=False)
    st.download_button("⬇ Download Full Results CSV", csv_out, "swot_results.csv", "text/csv")

else:
    st.markdown('<div style="border: 2px dashed #1e3a5f; border-radius: 14px; padding: 2.5rem; text-align: center; background: rgba(59,130,246,0.03); margin: 1rem 0"><p style="font-size:2.5rem;margin:0">📁</p><p style="color:#94a3b8"><strong style="color:#e2e8f0">Upload your CSV file</strong> using the sidebar to get started</p><p style="color:#64748b;font-size:0.85rem">Expected file: <code style="color:#3b82f6">master_student_data.csv</code></p></div>', unsafe_allow_html=True)
