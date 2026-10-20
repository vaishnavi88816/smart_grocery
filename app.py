import streamlit as st  # Web interface banane ke liye
import sys              # System path manage karne ke liye
import os               # File paths handle karne ke liye

# database folder ko import path mein add karo
sys.path.append(os.path.join(os.path.dirname(__file__), "database"))

# db.py se required functions import karo
from db import create_tables, login_user, register_user

# ── App configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Smart Grocery Expiry and Waste Management System",
    page_icon  = "🛒",
    layout     = "centered"
)

# ── Database tables banao (app start hote hi) ─────────────────────────────────
create_tables()

# ── Session state initialize karo ─────────────────────────────────────────────
# logged_in → user ka login status track karta hai
# user      → logged in user ki details store karta hai
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None


# =============================================================================
#  SCREEN 1 — LOGIN / REGISTER PAGE
# =============================================================================
if not st.session_state.logged_in:

    # Project title aur purpose
    st.title("🛒 Smart Grocery Expiry and Waste Management System")
    st.caption("*Reduce food wastage and financial loss.*")
    st.divider()

    # Login aur Register ke liye do alag tabs
    tab_login, tab_register = st.tabs(["Login", "Register"])

    # ── LOGIN TAB ──────────────────────────────────────────────────────────────
    with tab_login:
        st.subheader("Login to your account")

        # Email aur password input fields
        email    = st.text_input("Email Address",
                                  placeholder="you@example.com",
                                  key="login_email")
        password = st.text_input("Password",
                                  type="password",
                                  placeholder="Enter your password",
                                  key="login_pass")

        # Login button — full width
        if st.button("Login", type="primary",
                     use_container_width=True, key="btn_login"):

            # Validation — dono fields bhare hone chahiye
            if not email or not password:
                st.warning("Please fill in all fields.")
            else:
                # Database mein email + password match karo
                user = login_user(email, password)

                if user:
                    # Login successful — session mein save karo
                    st.session_state.logged_in = True
                    st.session_state.user      = user
                    st.rerun()  # Page reload karo
                else:
                    st.error("Incorrect email or password.")

    # ── REGISTER TAB ───────────────────────────────────────────────────────────
    with tab_register:
        st.subheader("Create a new account")

        # Registration ke liye 4 input fields
        reg_name = st.text_input("Full Name",
                                  placeholder="Your full name",
                                  key="reg_name")
        reg_email = st.text_input("Email Address",
                                   placeholder="you@example.com",
                                   key="reg_email")
        reg_pass = st.text_input("Password",
                                  type="password",
                                  placeholder="Minimum 4 characters",
                                  key="reg_pass")
        reg_conf = st.text_input("Confirm Password",
                                  type="password",
                                  placeholder="Re-enter your password",
                                  key="reg_conf")

        # Register button — full width
        if st.button("Create Account", type="primary",
                     use_container_width=True, key="btn_reg"):

            # Validation checks — ek ek condition check karo
            if not reg_name or not reg_email or not reg_pass:
                st.warning("All fields are required.")
            elif reg_pass != reg_conf:
                st.error("Passwords do not match.")
            elif len(reg_pass) < 4:
                st.warning("Password must be at least 4 characters.")
            else:
                # Sab theek hai — database mein save karo
                ok, msg = register_user(reg_name, reg_email, reg_pass)
                if ok:
                    st.success("Account created successfully! Please login.")
                else:
                    st.error(msg)  # Email already exists ya koi aur error


# =============================================================================
#  SCREEN 2 — HOME PAGE (After Login)
# =============================================================================
else:
    # Session se logged in user ki details lo
    user = st.session_state.user

    # Page title aur purpose line
    st.title("🛒 Smart Grocery Expiry and Waste Management System")
    st.caption("*Reduce food wastage and financial loss.*")

    # Welcome message — user ka naam dikhao
    st.success(f"✅ Welcome, **{user['name']}**!")
    st.divider()

    # ── Summary metrics — 4 columns mein ─────────────────────────────────────
    # Yeh numbers Stage 11 (Dashboard) mein real data se update honge
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(label="📦 Total Products", value="—")
    c2.metric(label="🗂️ Total Batches",  value="—")
    c3.metric(label="⏰ Expiring Soon",  value="—")
    c4.metric(label="⚠️ Expired",        value="—")

    st.divider()

    # Logout button — click karne par session clear hogi
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user      = None
        st.rerun()
