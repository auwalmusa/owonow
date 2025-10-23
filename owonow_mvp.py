import streamlit as st
from datetime import datetime
import calendar
import pandas as pd
import os

# ---------- Page config ----------
st.set_page_config(
    page_title="OwoNow",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- Logo / Header ----------
logo_path = "owonow_logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=150, caption="OwoNow - Owo in your pocket, now")
else:
    st.markdown("<h1 style='color: #008753; text-align: center; font-size: 32px;'>OwoNow</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666666; text-align: center;'>Owo in your pocket, now</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #FF6200; text-align: center; font-size: 12px;'>Note: Replace 'owonow_logo.png' with your AI-generated logo!</p>", unsafe_allow_html=True)

# ---------- Session state ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "history" not in st.session_state:
    st.session_state.history = []
if "phone" not in st.session_state:
    st.session_state.phone = ""

# ---------- Login ----------
if not st.session_state.logged_in:
    st.markdown("<h2 style='color: #008753; text-align: center;'>OwoNow</h2>", unsafe_allow_html=True)
    phone = st.text_input("Enter your phone number", key="phone_input")
    if st.button("Sign in"):
        if phone:
            st.session_state.logged_in = True
            st.session_state.phone = phone
            st.success("Signed in. Welcome to OwoNow.")
        else:
            st.error("Please enter a phone number.")
else:
    # ---------- Dashboard ----------
    st.markdown("<h2 style='color: #008753;'>Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Date math: days worked this month and next payday
    now = datetime.now()
    year, month = now.year, now.month
    days_in_month = calendar.monthrange(year, month)[1]
    day_of_month = now.day
    days_worked = min(day_of_month, days_in_month)

    # Last day of current month = next payday
    next_payday = datetime(year, month, days_in_month)

    # Earnings model
    monthly_base = 40_000  # ₦40,000 monthly base for lower-wage workers
    accrued = (monthly_base / days_in_month) * days_worked
    available = min(accrued * 0.5, 50_000)  # Up to 50% or ₦50,000 max

    st.markdown(f"<h3 style='color: #1A1A1A;'>Available Owo: ₦{available:,.0f}</h3>", unsafe_allow_html=True)
    st.progress(days_worked / days_in_month)
    st.markdown(f"<p style='color: #666666;'>Next paycheck: {next_payday.strftime('%B %d, %Y')}</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #008753; font-size: 12px;'>CBN-friendly prototype | No fees</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666666; font-size: 10px;'>Registered: OwoNow Ltd (Pending CAC Approval)</p>", unsafe_allow_html=True)

    # ---------- Withdraw ----------
    st.markdown("<h4 style='color: #1A1A1A;'>Withdraw Your Owo</h4>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    max_withdraw = int(available)
    slider_disabled = max_withdraw <= 0
    amount = st.slider(
        "Amount (₦)",
        0,
        max_withdraw if max_withdraw > 0 else 0,
        step=500 if max_withdraw >= 500 else 100 if max_withdraw > 0 else 0,
        key="withdraw_slider",
        disabled=slider_disabled
    )
    payout_method = st.selectbox(
        "Payout Method",
        ["OPay (Instant)", "Paga (Instant)", "Bank (1 day)"],
        key="payout_select"
    )

    if st.button("Withdraw Now", key="withdraw_button", help="Instant access to your Owo", disabled=slider_disabled):
        if amount and amount > 0:
            st.session_state.history.append({
                "date": now.strftime("%B %d, %Y"),
                "amount": f"₦{amount:,.0f}",
                "method": payout_method
            })
            st.success(f"₦{amount:,.0f} withdrawn to {payout_method}. Will be reconciled on {next_payday.strftime('%B %d, %Y')}.")
        else:
            st.error("Please select an amount to withdraw.")

    # ---------- History ----------
    st.markdown("<h4 style='color: #1A1A1A;'>Transaction History</h4>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.markdown("<p style='color: #666666;'>No withdrawals yet.</p>", unsafe_allow_html=True)

    # ---------- Logout ----------
    if st.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.rerun()

# ---------- Footer ----------
st.markdown(
    "<p style='color: #666666; text-align: center; font-size: 10px;'>© 2025 OwoNow Ltd. All rights reserved.</p>",
    unsafe_allow_html=True
)
