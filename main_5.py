"""
MPLAD AI FRAUD DETECTION SYSTEM - COMPLETE APPLICATION
Smart India Hackathon 2026
Single-file implementation with Streamlit UI

FEATURES:
- Data collection simulation
- AI fraud detection (4 modules)
- Beautiful dashboard with charts
- Project management
- Alert system
- Report generation

INSTALL REQUIREMENTS:
pip install streamlit pandas numpy scikit-learn plotly openpyxl Pillow requests

RUN COMMAND:
streamlit run mplad_fraud_detection_complete.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json
from io import BytesIO
from PIL import Image
import requests

# ================================================================
# PAGE CONFIGURATION
# ================================================================

st.set_page_config(
    page_title="MPLAD Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# CUSTOM CSS STYLING
# ================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #FAFAFA;
    background-image:
        radial-gradient(circle at 20% 0%, rgba(20,184,166,0.06) 0%, rgba(20,184,166,0) 40%),
        radial-gradient(circle at 100% 30%, rgba(17,24,39,0.04) 0%, rgba(17,24,39,0) 45%),
        radial-gradient(#E5E7EB 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 22px 22px;
    background-position: 0 0, 0 0, 0 0;
}

section[data-testid="stSidebar"] {
    background: #111827;
}
section[data-testid="stSidebar"] * {
    color: #D1D5DB !important;
}
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: #F9FAFB !important;
}

h1, h2, h3 { color: #111827; font-weight: 800; letter-spacing: -0.02em; }

.app-header {
    background: #111827;
    background-image: radial-gradient(circle at 15% 30%, #1F2937 0%, #111827 60%);
    padding: 22px 28px;
    border-radius: 16px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    border: 1px solid #1F2937;
}
.app-header::after {
    content: "";
    position: absolute;
    top: -40%; right: -10%;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(20,184,166,0.35) 0%, rgba(20,184,166,0) 70%);
    border-radius: 50%;
}
.app-header h1 {
    color: #FFFFFF;
    margin: 0;
    font-size: 25px;
}
.app-header p {
    color: #9CA3AF;
    margin: 5px 0 0 0;
    font-size: 13px;
    font-weight: 500;
}

.metric-card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 8px 20px rgba(0,0,0,0.04);
    border: 1px solid #EEEFF1;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 14px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.06), 0 12px 24px rgba(0,0,0,0.06);
}
.metric-icon {
    width: 46px; height: 46px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
}
.metric-label {
    font-size: 11.5px;
    color: #9CA3AF;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 2px;
}
.metric-value {
    font-size: 26px;
    font-weight: 800;
    color: #111827;
    line-height: 1.1;
}
.metric-sub {
    font-size: 11.5px;
    margin-top: 3px;
    font-weight: 600;
}

div.block-container {
    padding-top: 1.4rem;
    padding-bottom: 1.5rem;
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(6px);
    border-radius: 18px;
}
div[data-testid="stVerticalBlock"] > div {
    gap: 0.5rem;
}
div[data-testid="column"] {
    padding: 0 6px;
}

div[data-testid="stExpander"] {
    background: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #EEEFF1;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.stButton > button {
    border-radius: 8px;
    font-weight: 700;
    border: none;
    background-color: #111827;
    color: #FFFFFF;
    transition: background-color 0.15s ease;
}
.stButton > button:hover {
    background-color: #14B8A6;
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)

# ================================================================
# DATA GENERATION & MANAGEMENT
# ================================================================

class DataGenerator:
    """Generate realistic sample data for MPLAD projects"""

    @staticmethod
    def generate_sample_projects(n=100):
        """Generate sample project data"""

        states = ['Maharashtra', 'Uttar Pradesh', 'Karnataka', 'Tamil Nadu', 'Gujarat',
                   'Rajasthan', 'West Bengal', 'Madhya Pradesh', 'Bihar', 'Andhra Pradesh']

        project_types = ['School Building', 'Road Construction', 'Water Supply',
                          'Community Hall', 'Health Center', 'Drainage System',
                          'Street Lights', 'Park Development']

        mp_names = ['Rajesh Kumar', 'Priya Sharma', 'Amit Patel', 'Sunita Singh',
                     'Vijay Rao', 'Anjali Verma', 'Ravi Reddy', 'Meena Gupta']

        contractors = ['ABC Constructions', 'XYZ Builders', 'PQR Infra',
                        'LMN Developers', 'RST Engineering']

        projects = []

        for i in range(n):
            # Basic info
            project_id = f"MP/2024/{1000+i}"
            state = random.choice(states)
            district = f"District {chr(65+random.randint(0,25))}"

            # Financial
            sanctioned = random.randint(30, 100) * 100000  # 30L to 1Cr
            released_pct = random.randint(60, 100)
            released = sanctioned * released_pct / 100

            # Timeline
            start_date = datetime.now() - timedelta(days=random.randint(180, 730))
            expected_months = random.randint(6, 18)
            expected_completion = start_date + timedelta(days=expected_months*30)

            # Progress
            completion = random.randint(0, 100)

            # Location
            gps_lat = 20 + random.random() * 10
            gps_lon = 72 + random.random() * 10

            # Create anomalies in some projects
            is_anomaly = random.random() < 0.15  # 15% anomalous

            if is_anomaly:
                # Make it suspicious
                if random.random() < 0.5:
                    sanctioned *= 1.8  # High cost
                if random.random() < 0.5:
                    completion = random.randint(5, 20)  # Stuck
                if random.random() < 0.3:
                    released_pct = 95  # High release, low completion

            project = {
                'project_id': project_id,
                'name': f"{random.choice(project_types)} - {district}",
                'mp_name': random.choice(mp_names),
                'state': state,
                'district': district,
                'project_type': random.choice(project_types),
                'sanctioned_amount': sanctioned,
                'released_amount': released,
                'released_pct': released_pct,
                'completion': completion,
                'start_date': start_date,
                'expected_completion': expected_completion,
                'contractor': random.choice(contractors),
                'gps_lat': gps_lat,
                'gps_lon': gps_lon,
                'status': 'Active' if completion < 100 else 'Completed'
            }

            projects.append(project)

        return pd.DataFrame(projects)

# ================================================================
# AI/ML FRAUD DETECTION MODULES
# ================================================================

class FraudDetector:
    """AI-powered fraud detection system"""

    @staticmethod
    def detect_cost_anomaly(project, all_projects):
        """Check 1: Cost Anomaly Detection"""

        # Find similar projects
        similar = all_projects[
            (all_projects['project_type'] == project['project_type']) &
            (all_projects['state'] == project['state'])
        ]

        if len(similar) < 5:
            return {'score': 0, 'flag': False, 'reason': 'Not enough data'}

        median_cost = similar['sanctioned_amount'].median()
        threshold = median_cost * 1.5

        is_anomaly = project['sanctioned_amount'] > threshold
        ratio = project['sanctioned_amount'] / median_cost if median_cost > 0 else 1

        score = min(30, int((ratio - 1) * 30)) if is_anomaly else 0

        return {
            'score': score,
            'flag': is_anomaly,
            'reason': f"Cost is {ratio:.1f}x the median (₹{median_cost/100000:.1f}L)",
            'median': median_cost,
            'ratio': ratio
        }

    @staticmethod
    def detect_timeline_delay(project):
        """Check 2: Timeline Delay Detection"""

        days_elapsed = (datetime.now() - project['start_date']).days
        expected_days = (project['expected_completion'] - project['start_date']).days

        # Calculate completion velocity
        velocity = project['completion'] / (days_elapsed / 30) if days_elapsed > 0 else 0

        # Check if delayed
        is_delayed = days_elapsed > expected_days * 1.5

        # Check if stagnant (low velocity)
        is_stagnant = velocity < 2  # Less than 2% per month

        delay_months = max(0, (days_elapsed - expected_days) / 30)

        flag = is_delayed or (is_stagnant and project['completion'] < 80)
        score = min(25, int(delay_months * 2)) if flag else 0

        reason = []
        if is_delayed:
            reason.append(f"Delayed by {delay_months:.0f} months")
        if is_stagnant:
            reason.append(f"Low velocity ({velocity:.1f}% per month)")

        return {
            'score': score,
            'flag': flag,
            'reason': '; '.join(reason) if reason else 'On track',
            'delay_months': delay_months,
            'velocity': velocity
        }

    @staticmethod
    def detect_ghost_project(project):
        """Check 3: Ghost Project Detection (Simulated)"""

        # Simulate satellite check
        # In real system, this would call Google Maps API

        completion = project['completion']
        released_pct = project['released_pct']

        # Suspicious if high funds released but low completion
        is_ghost = (released_pct > 80) and (completion < 20)

        # Random factor for demo
        if not is_ghost:
            is_ghost = random.random() < 0.05  # 5% random false positives

        score = 15 if is_ghost else 0

        reason = "No structure visible in satellite imagery" if is_ghost else "Structure detected"

        return {
            'score': score,
            'flag': is_ghost,
            'reason': reason,
            'funds_released': released_pct,
            'completion': completion
        }

    @staticmethod
    def calculate_contractor_risk(contractor_name, all_projects):
        """Check 4: Contractor History Check"""

        contractor_projects = all_projects[all_projects['contractor'] == contractor_name]

        if len(contractor_projects) < 3:
            return {'score': 5, 'reason': 'Limited history'}

        avg_completion = contractor_projects['completion'].mean()

        # Poor performance if avg completion < 60%
        poor_performance = avg_completion < 60

        score = 15 if poor_performance else 5

        return {
            'score': score,
            'flag': poor_performance,
            'reason': f"Average completion: {avg_completion:.0f}%",
            'total_projects': len(contractor_projects)
        }

    @staticmethod
    def calculate_risk_score(project, all_projects):
        """Calculate final risk score (0-100)"""

        # Run all checks
        cost_result = FraudDetector.detect_cost_anomaly(project, all_projects)
        timeline_result = FraudDetector.detect_timeline_delay(project)
        ghost_result = FraudDetector.detect_ghost_project(project)
        contractor_result = FraudDetector.calculate_contractor_risk(
            project['contractor'], all_projects
        )

        # Location risk (simplified)
        location_score = 5

        # Total score
        total_score = (
            cost_result['score'] +
            timeline_result['score'] +
            ghost_result['score'] +
            contractor_result['score'] +
            location_score
        )

        # Determine risk level
        if total_score >= 60:
            risk_level = 'HIGH'
            color = '🔴'
        elif total_score >= 30:
            risk_level = 'MEDIUM'
            color = '🟡'
        else:
            risk_level = 'LOW'
            color = '🟢'

        return {
            'total_score': total_score,
            'risk_level': risk_level,
            'color': color,
            'cost': cost_result,
            'timeline': timeline_result,
            'ghost': ghost_result,
            'contractor': contractor_result,
            'location_score': location_score
        }

# ================================================================
# VISUALIZATION FUNCTIONS
# ================================================================

class Visualizations:
    """Create charts and visualizations"""

    @staticmethod
    def create_gauge_chart(score, title="Risk Score"):
        """Create a gauge chart for risk score"""

        if score >= 60:
            color = "red"
        elif score >= 30:
            color = "orange"
        else:
            color = "green"

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 24}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1},
                'bar': {'color': color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 30], 'color': '#D1FAE5'},
                    {'range': [30, 60], 'color': '#FEF3C7'},
                    {'range': [60, 100], 'color': '#FEE2E2'}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="white"
        )

        return fig

    @staticmethod
    def create_risk_breakdown_chart(risk_analysis):
        """Create horizontal bar chart for risk breakdown"""

        categories = ['Cost', 'Timeline', 'Ghost', 'Contractor', 'Location']
        scores = [
            risk_analysis['cost']['score'],
            risk_analysis['timeline']['score'],
            risk_analysis['ghost']['score'],
            risk_analysis['contractor']['score'],
            risk_analysis['location_score']
        ]
        max_scores = [30, 25, 15, 20, 10]

        colors = ['#EF4444' if s > m*0.6 else '#F59E0B' if s > m*0.3 else '#10B981'
                   for s, m in zip(scores, max_scores)]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=categories,
            x=scores,
            orientation='h',
            marker=dict(color=colors),
            text=[f"{s}/{m}" for s, m in zip(scores, max_scores)],
            textposition='auto',
        ))

        fig.update_layout(
            title="Risk Breakdown by Category",
            xaxis_title="Score",
            yaxis_title="Category",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="white"
        )

        return fig

    @staticmethod
    def create_pie_chart(df):
        """Create pie chart for risk distribution"""

        # Calculate risk levels
        risk_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}

        for _, project in df.iterrows():
            risk = FraudDetector.calculate_risk_score(project, df)
            risk_counts[risk['risk_level']] += 1

        fig = px.pie(
            values=list(risk_counts.values()),
            names=list(risk_counts.keys()),
            title="Risk Distribution",
            color_discrete_map={'LOW': '#10B981', 'MEDIUM': '#F59E0B', 'HIGH': '#EF4444'}
        )

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="white"
        )

        return fig

    @staticmethod
    def create_map(df):
        """Create geographic map of projects"""

        # Calculate risk for each project
        df_map = df.copy()
        df_map['risk_score'] = df_map.apply(
            lambda row: FraudDetector.calculate_risk_score(row, df)['total_score'],
            axis=1
        )

        fig = px.scatter_geo(
            df_map,
            lat='gps_lat',
            lon='gps_lon',
            color='risk_score',
            size='sanctioned_amount',
            hover_name='name',
            hover_data=['state', 'district', 'completion'],
            color_continuous_scale=['green', 'yellow', 'red'],
            height=400
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="white"
        )

        return fig

    @staticmethod
    def create_timeline_chart(df):
        """Create timeline trend chart"""

        df_sorted = df.sort_values('start_date')
        df_sorted['month'] = df_sorted['start_date'].dt.to_period('M').astype(str)

        monthly_counts = df_sorted.groupby('month').size().reset_index(name='count')

        fig = px.line(
            monthly_counts,
            x='month',
            y='count',
            title='Projects Started Over Time',
            markers=True
        )

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="white",
            xaxis_title="Month",
            yaxis_title="Number of Projects"
        )

        return fig

# ================================================================
# INITIALIZE SESSION STATE
# ================================================================

if 'projects_df' not in st.session_state:
    st.session_state.projects_df = DataGenerator.generate_sample_projects(100)

if 'selected_project' not in st.session_state:
    st.session_state.selected_project = None

if 'user_role' not in st.session_state:
    st.session_state.user_role = 'ministry'  # Default role

if 'user_district' not in st.session_state:
    st.session_state.user_district = 'District A'  # Default district

# ================================================================
# PAGE: DASHBOARD
# ================================================================

def show_dashboard():
    """Main dashboard page"""

    st.subheader("📊 Dashboard")

    # Filter data based on role
    full_df = st.session_state.projects_df
    if st.session_state.user_role == 'district':
        df = full_df[full_df['district'] == st.session_state.user_district]
    else:
        df = full_df

    # Calculate statistics
    total_projects = len(df)

    # Calculate high risk projects
    high_risk_count = 0
    for _, project in df.iterrows():
        risk = FraudDetector.calculate_risk_score(project, full_df)
        if risk['risk_level'] == 'HIGH':
            high_risk_count += 1

    active_investigations = high_risk_count
    total_sanctioned = df['sanctioned_amount'].sum()
    funds_saved = high_risk_count * 2500000  # Assuming avg 25L saved per detection
    if funds_saved >= 10000000:
        funds_saved_display = f"₹{funds_saved / 10000000:.2f}Cr"
    else:
        funds_saved_display = f"₹{funds_saved / 100000:.2f}L"

    # Stats Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background:#CCFBF1;color:#0F766E;">📁</div>
            <div>
                <div class="metric-label">Total Projects</div>
                <div class="metric-value">{total_projects}</div>
                <div class="metric-sub" style="color:#16A34A;">✓ Monitoring</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background:#FEE2E2;color:#DC2626;">⚠️</div>
            <div>
                <div class="metric-label">High Risk</div>
                <div class="metric-value" style="color:#DC2626;">{high_risk_count}</div>
                <div class="metric-sub" style="color:#DC2626;">🔴 Urgent</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background:#FEF3C7;color:#D97706;">🔎</div>
            <div>
                <div class="metric-label">Investigations</div>
                <div class="metric-value" style="color:#D97706;">{active_investigations}</div>
                <div class="metric-sub" style="color:#D97706;">⚡ Active</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background:#D1FAE5;color:#059669;">💰</div>
            <div>
                <div class="metric-label">Funds Saved</div>
                <div class="metric-value" style="color:#059669;">{funds_saved_display}</div>
                <div class="metric-sub" style="color:#9CA3AF;">This Month</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Charts Row 1
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(Visualizations.create_pie_chart(df), use_container_width=True)

    with col2:
        st.plotly_chart(Visualizations.create_timeline_chart(df), use_container_width=True)

    # Map
    st.subheader("🗺️ Geographic Risk Distribution")
    st.plotly_chart(Visualizations.create_map(df), use_container_width=True)

    # Recent High Risk Projects
    st.subheader("🚨 Recent High Risk Alerts")

    high_risk_projects = []
    for _, project in df.iterrows():
        risk = FraudDetector.calculate_risk_score(project, df)
        if risk['risk_level'] == 'HIGH':
            high_risk_projects.append({
                'Project ID': project['project_id'],
                'Name': project['name'],
                'Location': f"{project['district']}, {project['state']}",
                'Risk Score': risk['total_score'],
                'Issues': ', '.join([
                    'Cost' if risk['cost']['flag'] else '',
                    'Timeline' if risk['timeline']['flag'] else '',
                    'Ghost' if risk['ghost']['flag'] else ''
                ]).strip(', ')
            })

    if high_risk_projects:
        st.dataframe(
            pd.DataFrame(high_risk_projects[:5]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ No high-risk projects detected!")

# ================================================================
# PAGE: PROJECTS LIST
# ================================================================

def show_projects_list():
    """Projects list page"""

    st.subheader("📋 Projects List")

    # Filter data based on role
    full_df = st.session_state.projects_df
    if st.session_state.user_role == 'district':
        df = full_df[full_df['district'] == st.session_state.user_district]
    else:
        df = full_df

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        state_filter = st.selectbox("State", ["All"] + sorted(df['state'].unique().tolist()))

    with col2:
        type_filter = st.selectbox("Project Type", ["All"] + sorted(df['project_type'].unique().tolist()))

    with col3:
        risk_filter = st.selectbox("Risk Level", ["All", "HIGH", "MEDIUM", "LOW"])

    # Apply filters
    filtered_df = df.copy()

    if state_filter != "All":
        filtered_df = filtered_df[filtered_df['state'] == state_filter]

    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['project_type'] == type_filter]

    # Calculate risk for filtering
    if risk_filter != "All":
        filtered_projects = []
        for idx, project in filtered_df.iterrows():
            risk = FraudDetector.calculate_risk_score(project, full_df)
            if risk['risk_level'] == risk_filter:
                filtered_projects.append(idx)
        filtered_df = filtered_df.loc[filtered_projects]

    st.markdown(f"**Showing {min(20, len(filtered_df))} of {len(filtered_df)} projects**")

    # Display table
    for _, project in filtered_df.head(20).iterrows():
        risk = FraudDetector.calculate_risk_score(project, full_df)

        with st.expander(f"{risk['color']} {project['name']} - Risk: {risk['total_score']}/100"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Project ID:** {project['project_id']}")
                st.markdown(f"**Location:** {project['district']}, {project['state']}")
                st.markdown(f"**Type:** {project['project_type']}")
                st.markdown(f"**MP:** {project['mp_name']}")
                st.markdown(f"**Contractor:** {project['contractor']}")
                st.markdown(f"**Budget:** ₹{project['sanctioned_amount']/100000:.2f} Lakhs")
                st.markdown(f"**Released:** ₹{project['released_amount']/100000:.2f} Lakhs ({project['released_pct']:.0f}%)")
                st.markdown(f"**Completion:** {project['completion']}%")

                if risk['risk_level'] == 'HIGH':
                    st.error("🚨 **HIGH RISK** - Immediate investigation required!")

                issues = []
                if risk['cost']['flag']:
                    issues.append(f"❌ {risk['cost']['reason']}")
                if risk['timeline']['flag']:
                    issues.append(f"❌ {risk['timeline']['reason']}")
                if risk['ghost']['flag']:
                    issues.append(f"❌ {risk['ghost']['reason']}")

                for issue in issues:
                    st.markdown(issue)

            with col2:
                st.plotly_chart(
                    Visualizations.create_gauge_chart(risk['total_score']),
                    use_container_width=True,
                    key=f"gauge_{project['project_id']}"
                )

                if st.button(f"View Details", key=f"view_{project['project_id']}"):
                    st.session_state.selected_project = project
                    show_project_detail(project, risk)

# ================================================================
# PAGE: PROJECT DETAIL (Modal)
# ================================================================

def show_project_detail(project, risk):
    """Show detailed project view"""
    st.markdown("---")
    st.subheader(f"🔍 Project Details: {project['name']}")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📋 Basic Information")
        st.markdown(f"**Project ID:** {project['project_id']}")
        st.markdown(f"**Name:** {project['name']}")
        st.markdown(f"**Location:** {project['district']}, {project['state']}")
        st.markdown(f"**MP:** {project['mp_name']}")
        st.markdown(f"**Type:** {project['project_type']}")
        st.markdown(f"**Contractor:** {project['contractor']}")
        st.markdown("### 💰 Financial Details")
        st.markdown(f"**Sanctioned:** ₹{project['sanctioned_amount']/100000:.2f} Lakhs")
        st.markdown(f"**Released:** ₹{project['released_amount']/100000:.2f} Lakhs ({project['released_pct']:.0f}%)")
        st.markdown(f"**Utilized:** Pending field verification")
        st.markdown("### 🕒 Timeline")
        st.markdown(f"**Start Date:** {project['start_date'].strftime('%d-%b-%Y')}")
        st.markdown(f"**Expected Completion:** {project['expected_completion'].strftime('%d-%b-%Y')}")
        st.markdown(f"**Current Progress:** {project['completion']}%")
        st.markdown(f"**Status:** {project['status']}")
        st.markdown("### 📍 Location")
        st.markdown(f"**GPS Coordinates:** {project['gps_lat']:.4f}°N, {project['gps_lon']:.4f}°E")
        st.markdown("### 🛰️ Satellite Imagery")
        if risk['ghost']['flag']:
            st.warning("⚠️ No structure visible in satellite imagery!")
            st.image("https://via.placeholder.com/400x300.png?text=Empty+Land+(Simulated)",
                      caption="Satellite view shows empty land", use_container_width=True)
        else:
            st.success("✓ Structure detected in satellite imagery")
            st.image("https://via.placeholder.com/400x300.png?text=Construction+Visible+(Simulated)",
                      caption="Satellite view shows construction", use_container_width=True)
    with col2:
        st.plotly_chart(Visualizations.create_gauge_chart(risk['total_score'], "Risk Score"), use_container_width=True)
        st.plotly_chart(Visualizations.create_risk_breakdown_chart(risk), use_container_width=True)
        st.markdown("### ⚙️ Actions")
        if st.button("👷 Assign to Field Team", use_container_width=True):
            st.success("✅ Assigned to Field Team Delhi")
        if st.button("📧 Send Alert Email", use_container_width=True):
            st.success("✅ Alert email sent to officer@mospi.gov.in")
        if st.button("📄 Generate Report", use_container_width=True):
            st.success("✅ PDF report generated")
        if st.button("✓ Mark as False Positive", use_container_width=True):
            st.info("ℹ️ Case closed as false positive")

# ================================================================
# PAGE: ALERTS
# ================================================================

def show_alerts():
    """Alerts page listing all high and medium risk projects with full details"""

    st.subheader("🚨 Alerts")

    full_df = st.session_state.projects_df
    if st.session_state.user_role == 'district':
        df = full_df[full_df['district'] == st.session_state.user_district]
    else:
        df = full_df

    alerts = []
    for _, project in df.iterrows():
        risk = FraudDetector.calculate_risk_score(project, full_df)
        if risk['risk_level'] in ('HIGH', 'MEDIUM'):
            alerts.append((project, risk))

    alerts.sort(key=lambda x: x[1]['total_score'], reverse=True)

    if not alerts:
        st.success("✅ No active alerts")
        return

    st.markdown(f"**{len(alerts)} project(s) flagged**")

    for project, risk in alerts:
        with st.expander(f"{risk['color']} {project['name']} - Risk: {risk['total_score']}/100"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Project ID:** {project['project_id']}")
                st.markdown(f"**Location:** {project['district']}, {project['state']}")
                st.markdown(f"**Type:** {project['project_type']}")
                st.markdown(f"**MP:** {project['mp_name']}")
                st.markdown(f"**Contractor:** {project['contractor']}")
                st.markdown(f"**Budget:** ₹{project['sanctioned_amount']/100000:.2f} Lakhs")
                st.markdown(f"**Released:** ₹{project['released_amount']/100000:.2f} Lakhs ({project['released_pct']:.0f}%)")
                st.markdown(f"**Completion:** {project['completion']}%")
                st.markdown(f"**Start Date:** {project['start_date'].strftime('%d-%b-%Y')}")
                st.markdown(f"**Expected Completion:** {project['expected_completion'].strftime('%d-%b-%Y')}")
                st.markdown(f"**Status:** {project['status']}")

                if risk['risk_level'] == 'HIGH':
                    st.error("🚨 **HIGH RISK** - Immediate investigation required!")
                elif risk['risk_level'] == 'MEDIUM':
                    st.warning("⚠️ **MEDIUM RISK** - Review recommended")

                issues = []
                if risk['cost']['flag']:
                    issues.append(f"❌ {risk['cost']['reason']}")
                if risk['timeline']['flag']:
                    issues.append(f"❌ {risk['timeline']['reason']}")
                if risk['ghost']['flag']:
                    issues.append(f"❌ {risk['ghost']['reason']}")
                if risk['contractor'].get('flag'):
                    issues.append(f"❌ {risk['contractor']['reason']}")

                for issue in issues:
                    st.markdown(issue)

            with col2:
                st.plotly_chart(
                    Visualizations.create_gauge_chart(risk['total_score']),
                    use_container_width=True,
                    key=f"alert_gauge_{project['project_id']}"
                )

                if st.button("View Details", key=f"alert_view_{project['project_id']}"):
                    st.session_state.selected_project = project
                    show_project_detail(project, risk)

# ================================================================
# PAGE: ANALYTICS
# ================================================================

def show_analytics():
    """Analytics page with aggregate charts"""

    st.subheader("📈 Analytics")

    full_df = st.session_state.projects_df
    if st.session_state.user_role == 'district':
        df = full_df[full_df['district'] == st.session_state.user_district]
    else:
        df = full_df

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(Visualizations.create_pie_chart(df), use_container_width=True)
    with col2:
        st.plotly_chart(Visualizations.create_timeline_chart(df), use_container_width=True)

    st.plotly_chart(Visualizations.create_map(df), use_container_width=True)

    st.subheader("📊 Project Type Distribution")
    type_counts = df['project_type'].value_counts().reset_index()
    type_counts.columns = ['project_type', 'count']
    fig = px.bar(type_counts, x='project_type', y='count', title="Projects by Type")
    st.plotly_chart(fig, use_container_width=True)

# ================================================================
# PAGE: ABOUT
# ================================================================

def show_about():
    """About page"""

    st.subheader("ℹ️ About")
    st.markdown("""
    ### MPLAD AI Fraud Detection System
    Built for Smart India Hackathon 2026.

    This system uses AI-powered checks to detect anomalies in MPLAD
    (Member of Parliament Local Area Development) fund utilization:

    - **Cost Anomaly Detection** — flags projects sanctioned at unusually high cost vs similar projects
    - **Timeline Delay Detection** — flags stagnant or delayed projects
    - **Ghost Project Detection** — flags high fund release with low physical completion (simulated satellite check)
    - **Contractor History Check** — flags contractors with poor average completion records

    Risk scores (0-100) combine all checks to classify projects as LOW, MEDIUM, or HIGH risk.
    """)

# ================================================================
# MAIN APPLICATION
# ================================================================

def main():
    """Main application logic"""

    # Title
    st.markdown("""
    <div class="app-header">
        <h1>🛡️ MPLAD AI Fraud Detection System</h1>
        <p>Smart India Hackathon 2026 · AI-Powered Fund Monitoring & Anomaly Detection</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar - Role Selection
    st.sidebar.title("👤 Select Role")
    role = st.sidebar.radio(
        "View as:",
        ["Ministry/Central Authority", "District Authority"],
        key="role_selector"
    )

    # Set role in session state
    if role == "Ministry/Central Authority":
        st.session_state.user_role = 'ministry'
    else:
        st.session_state.user_role = 'district'
        # Select district for district role
        df = st.session_state.projects_df
        districts = sorted(df['district'].unique().tolist())
        st.session_state.user_district = st.sidebar.selectbox("Select District", districts)

    st.sidebar.markdown("---")

    # Navigation
    st.sidebar.title("🔍 Navigation")
    if st.session_state.user_role == 'ministry':
        page = st.sidebar.radio("Go to", ["📊 Dashboard", "📋 Projects List", "🚨 Alerts", "📈 Analytics", "ℹ️ About"])
    else:
        page = st.sidebar.radio("Go to", ["📊 Dashboard", "📋 Projects List", "📈 Analytics", "ℹ️ About"])

    # Refresh data button
    if st.sidebar.button("🔄 Refresh Data"):
        st.session_state.projects_df = DataGenerator.generate_sample_projects(100)
        st.rerun()

    # Page routing
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📋 Projects List":
        show_projects_list()
    elif page == "🚨 Alerts":
        show_alerts()
    elif page == "📈 Analytics":
        show_analytics()
    elif page == "ℹ️ About":
        show_about()


if __name__ == "__main__":
    main()