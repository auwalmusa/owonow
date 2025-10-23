# OwoNow demo app (theme-aware + fixed NG phone validation)
import re
import os
import calendar
from datetime import datetime
import pandas as pd
import streamlit as st

# ---------- Page config ----------
st.set_page_config(
    page_title="OwoNow",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- Theme-aware colors ----------
def get_palette():
    base = "dark"
    try:
        base = st.get_option("theme.base") or "light"
    except Exception:
        pass
    if base == "dark":
        return {
            "title": "#EAF5EE",
            "text": "#ECECEC",
            "muted": "#B0B3B8",
            "accent": "#00A86B",
            "warn": "#FF6200",
        }
    else:
        return {
            "title": "#0A3D1E",
            "text": "#1A1A1A",
            "muted": "#555555",
            "accent": "#008753",
            "warn": "#D65100",
        }
C = get_palette()
st.markdown(
    f"""
    <style>
        .owonow-title {{ color: {C["accent"]}; text-align: center; font-size: 32px; font-weight: 700; margin: 0.25rem 0 0.5rem 0; }}
        .owonow-sub {{ color: {C["muted"]}; text-align: center; font-size: 14px; margin-top: -0.25rem; }}
        .owonow-h3 {{ color: {C["text"]}; font-size: 22px; font-weight: 700; margin-top: 1rem; }}
        .owonow-h4 {{ color: {C["text"]}; font-size: 18px; font-weight: 700; margin-top: 0.75rem; }}
        .owonow-muted {{ color: {C["muted"]}; font-size: 13px; margin: 0.2rem 0; }}
        .owonow-ok {{ color: {C["text"]}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Assets ----------
LOGO_PATH = "owonow_logo.png"
TX_CSV = "owonow_transactions.csv"

# ---------- Phone helpers ----------
LOCAL_RE = re.compile(r"^0[1-9]\d{9}$")
INTL_RE = re.compile(r"^(?:\+?234)[1-9]\d{9}$")  # Fixed space removal
INTL_RAW = re.compile(r"^234[1-9]\d{9}$")
def normalize_phone(s: str) -> str:
    if not s:
        return ""
    raw = re.sub(r"[^\d+]", "", s.strip())
    if LOCAL_RE.match(raw):
        return raw
    if INTL_RE.match(raw):
        return raw if raw.startswith("+") else f"+{raw}"
    if INTL_RAW.match(raw):
        return f"+{raw}"
    return ""
def is_valid_ng_phone(s: str) -> bool:
    return normalize_phone(s) != ""

# ---------- CSV helpers ----------
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
        pd.DataFrame(history).to_csv(TX_CSV, index=False)
    except Exception:
        pass
def money(n: float) -> str:
    return f"₦{n:,.0f}"

# ---------- Header / Branding ----------
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=150, caption="OwoNow - Owo in your pocket, now")
else:
    st.markdown("<div class='owonow-title'>OwoNow</div>", unsafe_allow_html=True)
    st.markdown("<div class='owonow-sub'>Owo in your pocket, now</div>", unsafe_allow_html=True)
    st.markdown("<div class='owonow-muted'>Tip: add <code>owonow_logo.png</code> for your logo.</div>", unsafe_allow_html=True)
st.markdown("<div class='owonow-muted'>Demo only, not CBN-regulated.</div>", unsafe_allow_html=True)

# ---------- State ----------
st.session_state.setdefault("auth_step", "signin")
st.session_state.setdefault("phone", "")
st.session_state.setdefault("otp_expected", "123456")
st.session_state.setdefault("history", load_tx_history())

# ---------- Auth: Sign in ----------
if st.session_state.auth_step == "signin":
    st.markdown("<div class='owonow-title'>OwoNow</div>", unsafe_allow_html=True)
    phone_input = st.text_input(
        "Enter your phone number",
        key="phone_input",
        placeholder="0803xxxxxxx, +234803xxxxxxx, or 234803xxxxxxx",
    )
    if st.button("Sign in"):
        norm = normalize_phone(phone_input)
        if not norm:
            st.error("Please enter a valid Nigerian phone number.")
        else:
            st.session_state.phone = norm
            st.info("We sent a 6-digit code to your phone. Use 123456 for the demo.")
            st.session_state.auth_step = "otp"
            st.rerun()

# ---------- Auth: OTP ----------
elif st.session_state.auth_step == "otp":
    st.subheader("Verify code")
    st.write(f"Phone: **{st.session_state.phone}**")
    otp = st.text_input("Enter 6-digit code", max_chars=6)
    c1, c2 = st.columns(2)
    if c1.button("Verify"):
        if otp == st.session_state.otp_expected:
            st.success("Verified. Welcome to OwoNow.")
            st.session_state.auth_step = "dashboard"
            st.rerun()
        else:
            st.error("Invalid code. Try 123456 for demo.")
    if c2.button("Change number"):
        st.session_state.auth_step = "signin"
        st.rerun()

# ---------- Dashboard ----------
elif st.session_state.auth_step == "dashboard":
    st.header("Dashboard")
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    # Sidebar policy controls for EWA-only demo
    st.sidebar.header("EWA Policy")
    cap_pct = st.sidebar.number_input("Cap percent of earned", 0.0, 100.0, 50.0, 5.0)
    hard_cap = st.sidebar.number_input("Hard cap per month (₦)", 0, 500000, 50000, 5000)
    monthly_base = st.sidebar.number_input("Monthly base salary (₦)", 10000, 1000000, 40000, 5000)
    # Date math
    now = datetime.now()
    y, m = now.year, now.month
    dim = calendar.monthrange(y, m)[1]
    worked = min(now.day, dim)
    payday = datetime(y, m, dim)
    # Accrual and available
    accrued = (monthly_base / dim) * worked
    available = min(accrued * (cap_pct / 100.0), hard_cap)
    st.markdown(f"<div class='owonow-h3'>Available Owo: <span class='owonow-ok'>{money(available)}</span></div>", unsafe_allow_html=True)
    st.progress(worked / dim)
    st.markdown(f"<div class='owonow-muted'>Next paycheck: {payday.strftime('%B %d, %Y')}</div>", unsafe_allow_html=True)
    st.subheader("Withdraw your Owo")
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    max_withdraw = int(available)
    disabled = max_withdraw <= 0
    step = 500 if max_withdraw >= 500 else 100 if max_withdraw > 0 else 0
    amount = st.slider(
        "Amount (₦)",
        0,
        max_withdraw if max_withdraw > 0 else 0,
        step=step,
        disabled=disabled
    )
    method = st.selectbox("Payout method", ["OPay (Instant)", "Paga (Instant)", "Bank transfer (1 day)"])
    if st.button("Withdraw now", disabled=disabled):
        if amount and amount > 0:
            rec = {"date": now.strftime("%Y-%m-%d %H:%M"), "amount": money(amount), "method": method}
            st.session_state.history.append(rec)
            save_tx_history(st.session_state.history)
            st.success(f"{money(amount)} sent to {method}. Will reconcile on {payday.strftime('%B %d, %Y')}.")
    st.subheader("Transaction history")
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history), hide_index=True, use_container_width=True)
    else:
        st.markdown("<div class='owonow-muted'>No withdrawals yet.</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("Sign out"):
        st.session_state.clear()
        st.session_state.auth_step = "signin"
        st.rerun()
    if c2.button("Reset demo data"):
        st.session_state.history = []
        save_tx_history([])
        st.success("History cleared.")

# ---------- Footer ----------
st.markdown(
    f"<p style='color: {C['muted']}; text-align: center; font-size: 10px;'>© 2025 OwoNow Ltd. All rights reserved. CBN-Compliant (Demo).</p>",
    unsafe_allow_html=True
)
