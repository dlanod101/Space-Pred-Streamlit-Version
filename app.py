import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Space Pred | Telecom Event Prediction",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS (Glassmorphism & Space Theme) ---
def local_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');

        /* Background and Global Styles */
        .stApp {
            background: radial-gradient(circle at center, #111827 0%, #000000 100%);
            color: #E2E8F0;
            font-family: 'Inter', sans-serif;
        }

        /* Headers with Orbitron font */
        h1, h2, h3 {
            font-family: 'Orbitron', sans-serif !important;
            letter-spacing: 2px;
            color: #00f2ff !important;
            text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
        }

        /* Glassmorphism Containers */
        [data-testid="stVerticalBlock"] > div:has(div.metric-container) {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.95);
            border-right: 1px solid rgba(0, 242, 255, 0.2);
        }

        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #00f2ff 0%, #0066ff 100%);
            color: white;
            border: none;
            padding: 0.6rem 2rem;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            width: 100%;
        }
        .stButton > button:hover {
            box-shadow: 0 0 20px rgba(0, 242, 255, 0.6);
            transform: translateY(-2px);
        }

        /* Status Cards */
        .event-card {
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 1rem;
        }
        .event-normal { background: rgba(16, 185, 129, 0.1); border-color: #10b981; }
        .event-scintillation { background: rgba(245, 158, 11, 0.1); border-color: #f59e0b; }
        .event-congestion { background: rgba(239, 68, 68, 0.1); border-color: #ef4444; }
        .event-rainfade { background: rgba(59, 130, 246, 0.1); border-color: #3b82f6; }

        </style>
    """, unsafe_allow_html=True)

local_css()

# --- Helpers & Constants ---
CHARGE_PER_CALL = 2500  # Cost in Naira

if 'balance' not in st.session_state:
    st.session_state.balance = 100000

EVENT_INFO = {
    "Normal": {"icon": "✅", "color": "#10b981", "class": "event-normal", "desc": "Network operating within optimal parameters."},
    "Scintillation": {"icon": "⚡", "color": "#f59e0b", "class": "event-scintillation", "desc": "Rapid fluctuations in signal phase or amplitude."},
    "Congestion": {"icon": "🚦", "color": "#ef4444", "class": "event-congestion", "desc": "High traffic volume causing packet delays or loss."},
    "Rain Fade": {"icon": "🌧️", "color": "#3b82f6", "class": "event-rainfade", "desc": "Absorption of signal by atmospheric precipitation."}
}

def display_charge_card(amount, is_refund=False):
    color = "#F87171" if not is_refund else "#10B981"
    title = "UNSUCCESSFUL SESSION (REFUND)" if is_refund else "SESSION CHARGE"
    icon = "➕" if is_refund else "➖"
    st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; border-left: 5px solid {color}; margin-top: 10px;">
            <p style="margin: 0; font-size: 0.8rem; opacity: 0.7; color: {color};">{title}</p>
            <h3 style="margin: 0; color: white !important;">{icon} ₦{amount:,.2f}</h3>
        </div>
    """, unsafe_allow_html=True)

def get_prediction(endpoint, params, base_url):
    try:
        response = requests.get(f"{base_url}/{endpoint}", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}", "predicted_event": "Error", "predicted_vulnerability": 0.0}
    except Exception as e:
        return {"error": f"Connection Failed: {str(e)}", "predicted_event": "Error", "predicted_vulnerability": 0.0}

def create_gauge(value, title):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 20, 'color': '#00f2ff', 'family': 'Orbitron'}},
        gauge = {
            'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#00f2ff"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "rgba(255,255,255,0.1)",
            'steps': [
                {'range': [0, 0.3], 'color': 'rgba(16, 185, 129, 0.2)'},
                {'range': [0.3, 0.7], 'color': 'rgba(245, 158, 11, 0.2)'},
                {'range': [0.7, 1.0], 'color': 'rgba(239, 68, 68, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.8
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Inter"},
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

# --- Sidebar ---
with st.sidebar:
    st.markdown("# 🚀 Control Center")
    st.divider()
    
    # Billing Section
    st.markdown("### 💰 Billing & Credits")
    st.metric("Balance", f"₦{st.session_state.balance:,.2f}")
    if st.button("Top Up Credits"):
        st.session_state.balance += 50000
        st.rerun()
    st.divider()
    
    base_url = st.text_input("📡 Backend URL", value="https://couchpotato101-space-network-pred.hf.space", help="Address of the hosted ML API")
    
    st.markdown("### 📊 Dataset Info")
    sample_idx = st.number_input("Sample Index(Day)", min_value=0, value=200, help="Index of the telecom sample in the dataset")
    
    st.divider()
    st.markdown("### 🛠️ Help")
    st.info("""
        **Billing Info:**
        Each prediction call costs **₦2,500**. 
        Scintillation events are eligible for instant refunds.
    """)

# --- Main Content ---
st.title("📡 SPACE PRED")
st.markdown("#### PROXIMA GEN-4 TELECOM EVENT PREDICTION SYSTEM")
st.write("---")

tab1, tab2 = st.tabs(["🎯 Moment Prediction", "📈 Segment Analysis"])

# --- Tab 1: Moment Prediction ---
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuration")
        moment_idx = st.slider("Moment Index (0-143)", 0, 143, 0, help="Single time point index")
        
        predict_btn = st.button("RUN PREDICTION", key="btn_moment")
        
    with col2:
        if predict_btn:
            with st.spinner("Analyzing neural streams..."):
                res = get_prediction("predict_moment", {"sample_idx": sample_idx, "moment_idx": moment_idx}, base_url)
                
                if "error" in res and res["predicted_event"] == "Error":
                    st.error(res["error"])
                else:
                    event = res.get("predicted_event", "Normal")
                    vulnerability = res.get("predicted_vulnerability", 0.0)
                    
                    # Only deduct if NOT Scintillation
                    if event != "Scintillation":
                        st.session_state.balance -= CHARGE_PER_CALL
                    
                    info = EVENT_INFO.get(event, EVENT_INFO["Normal"])
                    
                    m_col1, m_col2 = st.columns(2)
                    
                    with m_col1:
                        st.markdown(f"""
                            <div class="event-card {info['class']}">
                                <h1 style="font-size: 3rem; margin-bottom: 0;">{info['icon']}</h1>
                                <h2 style="color: {info['color']} !important;">{event.upper()}</h2>
                                <p style="font-size: 0.9rem; opacity: 0.8;">{info['desc']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if event != "Scintillation":
                            display_charge_card(CHARGE_PER_CALL)
                        else:
                            st.info("✅ No charge for Scintillation events!")
                        
                        if event == "Scintillation":
                            st.warning("⚠️ Scintillation detected. Signal quality is compromised.")
                        
                    with m_col2:
                        st.plotly_chart(create_gauge(vulnerability, "VULNERABILITY INDEX"), use_container_width=True)
        else:
            st.info("Configure parameters and click 'RUN PREDICTION' to begin analysis.")

# --- Tab 2: Segment Analysis ---
with tab2:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuration")
        start_time = st.slider("Start Time Index", 0, 143, 0)
        duration = st.number_input("Duration (10-min intervals)", min_value=1, max_value=144, value=1)
        
        seg_btn = st.button("ANALYZE SEGMENT", key="btn_segment")
        
    with col2:
        if seg_btn:
            with st.spinner("Processing temporal data..."):
                res = get_prediction("predict_segment", {
                    "sample_idx": sample_idx, 
                    "start_time_idx": start_time,
                    "duration_in_10min_intervals": duration
                }, base_url)
                
                if "error" in res and res["predicted_event"] == "Error":
                    st.error(res["error"])
                else:
                    event = res.get("predicted_event", "Normal")
                    vulnerability = res.get("predicted_vulnerability", 0.0)
                    
                    # Only deduct if NOT Scintillation
                    if event != "Scintillation":
                        st.session_state.balance -= CHARGE_PER_CALL
                    
                    info = EVENT_INFO.get(event, EVENT_INFO["Normal"])
                    
                    s_col1, s_col2 = st.columns(2)
                    
                    with s_col1:
                        st.markdown(f"""
                            <div class="event-card {info['class']}">
                                <h1 style="font-size: 3rem; margin-bottom: 0;">{info['icon']}</h1>
                                <h2 style="color: {info['color']} !important;">{event.upper()}</h2>
                                <p style="font-size: 0.9rem; opacity: 0.8;">{info['desc']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if event != "Scintillation":
                            display_charge_card(CHARGE_PER_CALL)
                        else:
                            st.info("✅ No charge for Scintillation events!")
                        
                        if event == "Scintillation":
                            st.warning("⚠️ Scintillation detected. Data reliability is low.")
                        
                    with s_col2:
                        st.plotly_chart(create_gauge(vulnerability, "AGGREGATED RISK"), use_container_width=True)
        else:
            st.info("Set the time window to analyze trends over a specific duration.")

# --- Footer ---
st.write("---")
st.markdown("""
<div style="text-align: center; opacity: 0.5; font-size: 0.8rem;">
    📡 Space Pred v1.0.0 | Powered by Proxima Neural Engine & Streamlit
</div>
""", unsafe_allow_html=True)
