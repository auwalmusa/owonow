import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# Set page configuration for a mobile-like experience
st.set_page_config(
    page_title="OwoNow",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Simulate logo placeholder (replace with your generated logo file)
st.image("owonow_logo.png", width=150, caption="OwoNow - Owo in your pocket, now")  # Add your logo PNG here

# Session state for user persistence
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'history' not in st.session_state:
    st.session_state.history = []

# Login Screen
if not st.session_state.logged_in:
    st.markdown("<h1 style='color: #008753; text-align: center;'>OwoNow</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666666; text-align: center;'>Owo in your pocket, now</p>", unsafe_allow_html=True)
    phone = st.text_input("Enter your Phone Number", key="phone_input")
    if st.button("Verify BVN"):
        if phone:  # Basic validation for now
            st.session_state.logged_in = True
            st.session_state.phone = phone
            st.success("BVN Verified! Welcome to OwoNow.")
        else:
            st.error("Please enter a phone number.")
else:
    # Dashboard
    st.markdown("<h2 style='color: #008753;'>Dashboard</h2>", unsafe_allow_html=True)

    # Simulate earned wages (based on 30-day cycle, adjustable)
    earned = 50000  # ₦50,000 monthly base (adjust per user later)
    days_worked = 12  # Current date: Oct 23, assume 30-day pay cycle
    available = (earned / 30) * days_worked * 0.5  # Up to 50% of earned wages

    st.markdown(f"<h3 style='color: #1A1A1A;'>Available Owo: ₦{available:,.0f}</h3>", unsafe_allow_html=True)
    st.progress(days_worked / 30)  # Progress bar for days worked
    next_payday = datetime(2025, 10, 31)  # Next paycheck date (adjustable)
    st.markdown(f"<p style='color: #666666;'>Next paycheck: {next_payday.strftime('%B %d, %Y')}</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #008753; font-size: 12px;'>CBN-Compliant | No Fees</p>", unsafe_allow_html=True)

    # Withdrawal Section
    st.markdown("<h4 style='color: #1A1A1A;'>Withdraw Your Owo</h4>", unsafe_allow_html=True)
    amount = st.slider("Amount (₦)", 0, int(available), step=1000, key="withdraw_slider")
    payout_method = st.selectbox("Payout Method", ["OPay (Instant)", "Paga (Instant)", "Bank (1 day)"], key="payout_select")
    if st.button("Withdraw Now", key="withdraw_button"):
        if amount > 0:
            st.session_state.history.append({
                "date": datetime.now().strftime("%B %d, %Y"),
                "amount": f"₦{amount:,.0f}",
                "method": payout_method
            })
            st.success(f"₦{amount:,.0f} withdrawn to {payout_method}! Deducted on {next_payday.strftime('%B %d, %Y')}.")
        else:
            st.error("Please select an amount to withdraw.")

    # History Section
    st.markdown("<h4 style='color: #1A1A1A;'>Transaction History</h4>", unsafe_allow_html=True)
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.markdown("<p style='color: #666666;'>No withdrawals yet.</p>", unsafe_allow_html=True)

    # Logout Option
    if st.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# Footer (optional, for branding)
st.markdown("<p style='color: #666666; text-align: center; font-size: 10px;'>© 2025 OwoNow Ltd. All rights reserved.</p>", unsafe_allow_html=True)
