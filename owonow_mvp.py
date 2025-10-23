import re
import os
import calendar
from datetime import datetime
import pandas as pd
import streamlit as st

# =========================
# Page config
# =========================
st.set_page_config(
    page_title="OwoNow",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# Helpers
# =========================
PHONE_REGEX = re.compile(r"^(?:0\d{10}|(?:\+?234)\d{10})$")  # NG: 11 digits starting 0, or +234 + 10
TX_CSV = "owonow_transactions.csv"
LOGO_PATH = "owonow_logo.png"

def is_valid_ng_phone(s: str) -> bool:
    if not s:
        return False
    s = s.strip().replace(" ", "")
    return bool(PHONE_REGEX.match(s))

def load_tx_history() -> list[dict]:
    if os.path.exists(TX_CSV):
        try:
            df = pd.read_csv(TX_CSV)
            return df.to_dict(orient="records")
        except Exception:
            return []
    return []

def save_tx_history(history: list[dict]) -> None:
    try:
        df = pd.DataFrame(history)
        df.to_csv(TX_CSV, index=False)
    except Exception:
        pass

def money(n: float) -> str:
    return f"₦{n:,.0f}"

# =========================
# Header / Branding
# =========================
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=150, caption="OwoNow - Owo in your pocket, now")
else:
    st.markdown("<h1 style='color: #008753; text-align: center; font-size: 32px;'>OwoNow</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666; text-align: center;'>Owo in your pocket, now</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #FF6200; text-align: center; font-size: 12px;'>Tip: add 'owonow_logo.png' for your logo.</p>", unsafe_allow_html=True)

# =========================
# Session state
# =========================
st.session_state.setdefault("auth_step", "signin")  # signin -> otp -> dashboard
st.session_state.setdefault("phone", "")
st.session_state.setdefault("otp_expected", "123456")  # demo
st.session_state.setdefault("history", load_tx_history())

# =========================
# Auth: Sign in
# =========================
if st.session_state.auth_step == "signin":
    st.markdown("<h2 style='color: #008753; text-align: center;'>OwoNow</h2>", unsafe_allow_html=True)
    phone = st.text_input("Enter your phone number", key="phone_input", placeholder="e.g., 0803xxxxxxx or +234803xxxxxxx")

    sign_in = st.button("Sign in")
    if sign_in:
        if not is_valid_ng_phone(phone):
            st.error("Please enter a valid Nigerian phone number.")
        else:
            st.session_state.phone = phone.strip()
            # In production, send OTP here
            st.info("We sent a 6-digit code to your phone.")
            st.session_state.auth_step = "otp"
            st.rerun()

# =========================
# Auth: OTP
# =========================
elif st.session_state.auth_step == "otp":
    st.markdown("<h3 style='color: #008753; text-align: left;'>Verify code</h3>", unsafe_allow_html=True)
    st.caption(f"Phone: {st.session_state.phone}")
    otp = st.text_input("Enter 6-digit code", max_chars=6)
    cols = st.columns(2)
    with cols[0]:
        verify = st.button("Verify")
    with cols[1]:
        back = st.button("Change number")

    if back:
        st.session_state.auth_step = "signin"
        st.rerun()

    if verify:
        if otp == st.session_state.otp_expected:
            st.success("Verified. Welcome to OwoNow.")
            st.session_state.auth_step = "dashboard"
            st.rerun()
        else:
            st.error("Invalid code. Try 123456 for demo.")

# =========================
# Dashboard
# =========================
elif st.session_state.auth_step == "dashboard":
    st.markdown("<h2 style='color: #008753;'>Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Date math
    now = datetime.now()
    year, month = now.year, now.month
    days_in_month = calendar.monthrange(year, month)[1]
    days_worked = min(now.day, days_in_month)
    next_payday = datetime(year, month, days_in_month)

    # Earnings model
    monthly_base = 40_000  # demo
    accrued = (monthly_base / days_in_month) * days_worked
    available = min(accrued * 0.5, 50_000)

    # Top card
    st.markdown(f"<h3 style='color: #1A1A1A;'>Available Owo: {money(available)}</h3>", unsafe_allow_html=True)
    st.progress(days_worked / days_in_month)
    st.markdown(f"<p style='color: #666;'>Next paycheck: {next_payday.strftime('%B %d, %Y')}</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #008753; font-size: 12px;'>Prototype, CBN-friendly | No fees</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #666; font-size: 10px;'>Registered: OwoNow Ltd (Pending CAC approval)</p>", unsafe_allow_html=True)

    # Withdraw
    st.markdown("<h4 style='color: #1A1A1A;'>Withdraw your Owo</h4>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    max_withdraw = int(available)
    slider_disabled = max_withdraw <= 0
    step = 500 if max_withdraw >= 500 else 100 if max_withdraw > 0 else 0

    amount = st.slider(
        "Amount (₦)",
        0,
        max_withdraw if max_withdraw > 0 else 0,
        step=step,
        key="withdraw_slider",
        disabled=slider_disabled
    )

    payout_method = st.selectbox("Payout method", ["OPay (Instant)", "Paga (Instant)", "Bank transfer (1 day)"])

    withdraw = st.button("Withdraw now", help="Instant access to your Owo", disabled=slider_disabled)

    if withdraw:
        if amount and amount > 0:
            record = {
                "date": now.strftime("%Y-%m-%d %H:%M"),
                "amount": money(amount),
                "method": payout_method
            }
            st.session_state.history.append(record)
            save_tx_history(st.session_state.history)
            st.success(f"{money(amount)} sent to {payout_method}. Will reconcile on {next_payday.strftime('%B %d, %Y')}.")
        else:
            st.error("Please select an amount to withdraw.")

    # History
    st.markdown("<h4 style='color: #1A1A1A;'>Transaction history</h4>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.markdown("<p style='color: #666;'>No withdrawals yet.</p>", unsafe_allow_html=True)

    # Auth controls
    cols = st.columns(2)
    with cols[0]:
        if st.button("Sign out"):
            st.session_state.clear()
            st.session_state.auth_step = "signin"
            st.rerun()
    with cols[1]:
        if st.button("Reset demo data"):
            st.session_state.history = []
            save_tx_history([])
            st.success("History cleared.")

# =========================
# Footer
# =========================
st.markdown(
    "<p style='color: #666; text-align: center; font-size: 10px;'>© 2025 OwoNow Ltd. All rights reserved.</p>",
    unsafe_allow_html=True
)
