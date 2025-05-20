# insurance_claims_app.py

import streamlit as st
import datetime
from collections import defaultdict

st.set_page_config(page_title="Insurance Dashboard", layout="wide")

# ------------------ Persistent Storage ------------------
if "policyholders" not in st.session_state:
    st.session_state.policyholders = {}

if "claims" not in st.session_state:
    st.session_state.claims = []

# ------------------ Classes ------------------
class Policyholder:
    def __init__(self, policyholder_id, name, age, policy_type, sum_insured):
        self.id = policyholder_id
        self.name = name
        self.age = age
        self.policy_type = policy_type
        self.sum_insured = sum_insured

class Claim:
    def __init__(self, claim_id, policyholder_id, amount, reason, status, date):
        self.claim_id = claim_id
        self.policyholder_id = policyholder_id
        self.amount = amount
        self.reason = reason
        self.status = status
        self.date = date

# ------------------ Utility Functions ------------------
def get_claims_by_policyholder(policyholder_id):
    return [c for c in st.session_state.claims if c.policyholder_id == policyholder_id]

def claim_frequency(policyholder_id):
    return len(get_claims_by_policyholder(policyholder_id))

def claim_amount_sum(policyholder_id):
    return sum(c.amount for c in get_claims_by_policyholder(policyholder_id))

def high_risk_policyholders():
    high_risk = []
    for policyholder in st.session_state.policyholders.values():
        policy_claims = get_claims_by_policyholder(policyholder.id)
        one_year_ago = datetime.date.today() - datetime.timedelta(days=365)
        recent_claims = [c for c in policy_claims if c.date >= one_year_ago]
        total_claim_amount = sum(c.amount for c in policy_claims)
        if len(recent_claims) > 3 or total_claim_amount > 0.8 * policyholder.sum_insured:
            high_risk.append(policyholder)
    return high_risk

def claims_by_policy_type():
    result = defaultdict(int)
    for c in st.session_state.claims:
        if c.policyholder_id in st.session_state.policyholders:
            result[st.session_state.policyholders[c.policyholder_id].policy_type] += 1
    return result

def monthly_claims():
    result = defaultdict(int)
    for c in st.session_state.claims:
        key = c.date.strftime("%Y-%m")
        result[key] += 1
    return result

def average_claim_by_type():
    totals = defaultdict(list)
    for c in st.session_state.claims:
        if c.policyholder_id in st.session_state.policyholders:
            policy_type = st.session_state.policyholders[c.policyholder_id].policy_type
            totals[policy_type].append(c.amount)
    return {k: sum(v)/len(v) if v else 0 for k, v in totals.items()}

def highest_claim():
    return max(st.session_state.claims, key=lambda c: c.amount, default=None)

def pending_claims():
    return [c for c in st.session_state.claims if c.status == "Pending"]

# ------------------ Streamlit Interface ------------------
st.markdown("""
    <style>
        .main { background-color: #f9fafc; }
        .block-container { padding: 2rem 3rem; }
        h1, h2, h3, h4, h5, h6 { color: #1a202c; }
        .stButton>button { background-color: #2563eb; color: white; border-radius: 8px; padding: 0.5rem 1rem; }
        .stSelectbox, .stTextInput, .stNumberInput, .stDateInput { padding: 0.5rem !important; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

st.title("\U0001F4B0 Insurance Claims Management & Risk Analysis")

menu = st.sidebar.selectbox("\U0001F4DD Menu", [
    "Register Policyholder", "Add Claim", "Risk Analysis", "Reports"
])

if menu == "Register Policyholder":
    st.header("Register Policyholder")
    with st.form("register_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1)
        policy_type = st.selectbox("Policy Type", ["Health", "Vehicle", "Life"])
        sum_insured = st.number_input("Sum Insured", min_value=0)
        submitted = st.form_submit_button("Register")
        if submitted:
            pid = len(st.session_state.policyholders) + 1
            st.session_state.policyholders[pid] = Policyholder(pid, name, age, policy_type, sum_insured)
            st.success(f"Registered Policyholder ID: {pid}")

elif menu == "Add Claim":
    st.header("Add Claim")
    if not st.session_state.policyholders:
        st.warning("Please register at least one policyholder.")
    else:
        with st.form("claim_form"):
            policyholder_id = st.selectbox("Policyholder ID", list(st.session_state.policyholders.keys()))
            claim_id = len(st.session_state.claims) + 1
            amount = st.number_input("Claim Amount", min_value=0)
            reason = st.text_input("Reason")
            status = st.selectbox("Claim Status", ["Pending", "Approved", "Rejected"])
            date = st.date_input("Date of Claim", value=datetime.date.today())
            submitted = st.form_submit_button("Add Claim")
            if submitted:
                st.session_state.claims.append(Claim(claim_id, policyholder_id, amount, reason, status, date))
                st.success(f"Claim {claim_id} added.")

elif menu == "Risk Analysis":
    st.header("Risk Analysis")
    st.subheader("High Risk Policyholders")
    risky = high_risk_policyholders()
    if risky:
        for r in risky:
            st.markdown(f"- **{r.name}** (ID: {r.id})")
    else:
        st.info("No high-risk policyholders identified.")

    st.subheader("Claims by Policy Type")
    st.json(claims_by_policy_type())

elif menu == "Reports":
    st.header("Reports")
    st.subheader("Total Claims per Month")
    st.json(monthly_claims())

    st.subheader("Average Claim Amount by Policy Type")
    st.json(average_claim_by_type())

    st.subheader("Highest Claim Filed")
    hc = highest_claim()
    if hc:
        st.markdown(f"- Claim ID: **{hc.claim_id}**, Amount: **₹{hc.amount}**, Policyholder ID: **{hc.policyholder_id}**")
    else:
        st.write("No claims available")

    st.subheader("Policyholders with Pending Claims")
    pending = pending_claims()
    if pending:
        for c in pending:
            st.markdown(f"- Claim ID: {c.claim_id}, Policyholder ID: {c.policyholder_id}, Amount: ₹{c.amount}")
    else:
        st.info("No pending claims.")