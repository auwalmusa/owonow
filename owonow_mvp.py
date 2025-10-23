import streamlit as st

st.set_page_config(page_title="OwoNow", layout="centered")
st.markdown("<h1 style='color: #008753; text-align: center;'>OwoNow</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #666666; text-align: center;'>Owo in your pocket, now</p>", unsafe_allow_html=True)

# Simulate login (replace with BVN API later)
if not st.session_state.get("logged_in", False):
    phone = st.text_input("Phone Number")
    if st.button("Verify BVN"):
        st.session_state.logged_in = True
        st.success("Verified! Welcome.")
else:
    # Dashboard
    earned = 50000
    available = earned * 0.5
    st.markdown(f"<h3 style='color: #1A1A1A;'>Available Owo: ₦{available:,.0f}</h3>", unsafe_allow_html=True)
    st.progress(0.4)  # 12/30 days
    st.markdown("<p style='color: #666666;'>Next paycheck: Oct 31</p>", unsafe_allow_html=True)

    # Withdrawal
    amount = st.slider("Withdraw Amount (₦)", 0, int(available), step=1000)
    payout = st.selectbox("Payout Method", ["OPay (Instant)", "Paga (Instant)", "Bank (1 day)"])
    if st.button("Withdraw Now"):
        st.success(f"₦{amount:,.0f} sent to {payout}! Deducted Oct 31.")
        # Simulate history
        st.session_state.setdefault("history", []).append({"date": "Oct 23", "amount": f"₦{amount:,.0f}", "method": payout})

    # History
    st.subheader("History")
    if st.session_state.get("history"):
        st.dataframe(st.session_state.history)
    else:
        st.write("No withdrawals yet.")
