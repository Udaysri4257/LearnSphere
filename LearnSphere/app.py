import streamlit as st
import os
import csv
import pandas as pd
from datetime import datetime

# --- 1. THEME & ADVANCED CSS (The "Beauty" Logic) ---
st.set_page_config(page_title="LearnSphere Pro", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
    }

    /* Force visibility for all text */
    h1, h2, h3, p, label, .stMarkdown {
        color: #1e293b !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }

    /* Glassmorphism Cards */
    .main-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 25px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        color: white !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* Metric/Number Styling */
    [data-testid="stMetricValue"] {
        color: #2563eb !important;
        font-weight: 800 !important;
        font-size: 3rem !important;
    }

    /* Beautiful Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #2563eb, #3b82f6) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 30px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
    }
    
    /* Success Boxes */
    .stAlert {
        border-radius: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE FUNCTIONS ---
def save_user(uid, pwd, role):
    with open('users.csv', mode='a', newline='') as f:
        csv.writer(f).writerow([uid, pwd, role])

def save_request(topic, student_id, message):
    file_exists = os.path.isfile('mentor_requests.csv')
    with open('mentor_requests.csv', mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        if not file_exists: writer.writerow(['Date', 'Student', 'Topic', 'Question'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), student_id, topic, message])

def save_answer(student_name, mentor_reply):
    file_exists = os.path.isfile('mentor_answers.csv')
    with open('mentor_answers.csv', mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        if not file_exists: writer.writerow(['Date', 'Student Name', 'Mentor Reply'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), student_name, mentor_reply])

# --- 3. SESSION STATE & LOGIN ---
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center;'>🌐 LearnSphere Pro Login</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        t1, t2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
        with t2:
            n_id = st.text_input("Choose ID")
            n_pw = st.text_input("Password", type="password")
            n_role = st.selectbox("I am a...", ["Student", "Mentor", "Admin"])
            if st.button("Register"):
                save_user(n_id, n_pw, n_role); st.success("Account created! Go to Sign In.")
        with t1:
            l_id = st.text_input("User ID")
            l_pw = st.text_input("User Password", type="password")
            if st.button("Log In"):
                if os.path.exists('users.csv'):
                    u = pd.read_csv('users.csv', names=['UserID', 'Password', 'Role'], header=0)
                    match = u[(u['UserID'] == l_id) & (u['Password'] == str(l_pw))]
                    if not match.empty:
                        st.session_state.user = l_id
                        st.session_state.role = match.iloc[0]['Role']
                        st.rerun()
                    else: st.error("Wrong ID or Password")
    st.stop()

# --- 4. GREETING LOGIC ---
hour = datetime.now().hour
if 5 <= hour < 12: greeting = "☀️ Good Morning"
elif 12 <= hour < 18: greeting = "🌤️ Good Afternoon"
else: greeting = "🌙 Good Evening"

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"### {greeting}")
    st.markdown(f"## {st.session_state.user}")
    st.divider()
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.rerun()

# --- 6. MAIN DASHBOARDS ---

# --- STUDENT ---
if st.session_state.role == "Student":
    st.title(f"{greeting}, {st.session_state.user}! ✨")
    
    t_ask, t_inbox = st.tabs(["🚀 Ask a Mentor", "📥 My Inbox"])
    
    with t_ask:
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.subheader("Submit a New Question")
        topic = st.selectbox("Learning Area", ["Programming", "Career", "Soft Skills"])
        details = st.text_area("What can we help you with today?")
        if st.button("Send to Mentors"):
            if details:
                with st.spinner("Broadcasting to mentors..."):
                    save_request(topic, st.session_state.user, details)
                st.balloons()
                st.toast("Request Sent Successfully!", icon="✅")
            else: st.error("Please provide details.")
        st.markdown("</div>", unsafe_allow_html=True)

    with t_inbox:
        st.subheader("Your Personalized Feedback")
        if os.path.exists('mentor_answers.csv'):
            ans = pd.read_csv('mentor_answers.csv', names=['Date', 'Student', 'Reply'], header=0)
            my = ans[ans['Student'] == st.session_state.user]
            if not my.empty:
                for i, r in my.iterrows():
                    st.info(f"📅 **Date:** {r['Date']}\n\n**Advice:** {r['Reply']}")
            else: st.info("No replies yet. Our mentors are on the way!")

# --- MENTOR ---
elif st.session_state.role == "Mentor":
    st.title(f"👨‍🏫 Mentor Portal: {st.session_state.user}")
    if os.path.exists('mentor_requests.csv'):
        reqs = pd.read_csv('mentor_requests.csv', names=['Date', 'Student', 'Topic', 'Question'], header=0)
        for i, row in reqs.iterrows():
            with st.expander(f"Question from {row['Student']} ({row['Topic']})"):
                st.write(f"**Question:** {row['Question']}")
                reply = st.text_area("Your Expert Answer:", key=f"r_{i}")
                if st.button("Submit Response", key=f"b_{i}"):
                    save_answer(row['Student'], reply)
                    st.success(f"Response sent to {row['Student']}!")
    else: st.info("No students are waiting for help right now.")

# --- ADMIN ---
elif st.session_state.role == "Admin":
    st.title("🛡️ Admin Command Center")
    if os.path.exists('users.csv'):
        users = pd.read_csv('users.csv')
        c1, c2, c3 = st.columns(3)
        # These will now be visible in blue thanks to our CSS
        c1.metric("Total Members", len(users))
        c2.metric("Students", len(users[users['Role']=='Student']))
        c3.metric("Mentors", len(users[users['Role']=='Mentor']))
        
        st.subheader("Full User Database")
        st.dataframe(users, use_container_width=True)