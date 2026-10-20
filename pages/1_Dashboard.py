import streamlit as st          # Web interface ke liye
import sys                      # Path manage karne ke liye
import os                       # File path ke liye
from datetime import date       # Aaj ki date ke liye

# Required folders ko Python path mein add karo
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

# Database functions import karo
from db import get_all_products, get_all_batches_with_product

# Expiry status calculate karne ka function
from expiry_logic import calculate_expiry_status

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Dashboard — Smart Grocery System",
    page_icon  = "📊",
    layout     = "wide"
)

# ── Login check ───────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first.")
    st.stop()

# ── Logged-in user ki details ─────────────────────────────────────────────────
user    = st.session_state.user
user_id = user["user_id"]

# ── Page heading ──────────────────────────────────────────────────────────────
st.title("📊 Dashboard")
st.caption(f"Overview of your grocery inventory — as of **{date.today().strftime('%d %B %Y')}**")
st.divider()

# ── Database se data fetch karo ───────────────────────────────────────────────
products   = get_all_products(user_id)               # Saare products
all_batches = get_all_batches_with_product(user_id)  # Saari batches

# ── Har batch ka status fresh calculate karo (real-time) ─────────────────────
# Database mein stored status purana ho sakta hai
# Isliye display ke waqt dobara calculate karte hain
safe_batches     = []
expiring_batches = []
expired_batches  = []

for batch in all_batches:
    # Real-time status calculate karo
    status, days_left = calculate_expiry_status(
        batch["expiry_date"],
        batch["alert_preference"]
    )
    batch["expiry_status"] = status    # Updated status batch dict mein daalo
    batch["days_left"]     = days_left # Days left bhi save karo

    # Status ke hisaab se alag lists mein sort karo
    if status == "Safe":
        safe_batches.append(batch)
    elif status == "Expiring Soon":
        expiring_batches.append(batch)
    else:
        expired_batches.append(batch)

# =============================================================================
#  SECTION 1 — Summary Metric Cards
# =============================================================================
c1, c2, c3, c4, c5 = st.columns(5)

# Total products count
c1.metric(
    label = "📦 Total Products",
    value = len(products)
)

# Total batches count
c2.metric(
    label = "🗂️ Total Batches",
    value = len(all_batches)
)

# Safe batches
c3.metric(
    label = "✅ Safe",
    value = len(safe_batches)
)

# Expiring soon
c4.metric(
    label = "⚠️ Expiring Soon",
    value = len(expiring_batches)
)

# Expired
c5.metric(
    label = "❌ Expired",
    value = len(expired_batches)
)

st.divider()

# =============================================================================
#  SECTION 2 — Expiring Soon Alert Table (most urgent)
# =============================================================================
if expiring_batches:
    st.subheader("⚠️ Expiring Soon")
    st.caption("These batches need immediate attention.")

    for batch in sorted(expiring_batches, key=lambda x: x["days_left"]):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1])
            c1.markdown(f"**{batch['product_name']}**")
            c1.caption(f"🏷️ {batch['category']}")
            c2.caption(f"⏰ Expires: {batch['expiry_date']}")
            c2.caption(f"📅 Purchased: {batch['purchase_date']}")
            c3.caption(f"📦 Qty remaining: {batch['current_quantity']}")
            c3.caption(f"🔔 Alert set: {batch['alert_preference']} days")

            # Days left dikhao
            days = batch["days_left"]
            if days == 0:
                c4.warning("Expires TODAY")
            elif days == 1:
                c4.warning("1 day left")
            else:
                c4.warning(f"{days} days left")

    st.divider()

# =============================================================================
#  SECTION 3 — Expired Batches
# =============================================================================
if expired_batches:
    st.subheader("❌ Expired Batches")
    st.caption("These batches have passed their expiry date.")

    for batch in expired_batches:
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 1.5])
            c1.markdown(f"**{batch['product_name']}**")
            c1.caption(f"🏷️ {batch['category']}")
            c2.caption(f"⏰ Expired on: {batch['expiry_date']}")
            c2.caption(f"📦 Qty: {batch['current_quantity']}")
            c3.error(f"Expired {abs(batch['days_left'])} days ago")

    st.divider()

# =============================================================================
#  SECTION 4 — Safe Batches Table
# =============================================================================
if safe_batches:
    st.subheader("✅ Safe Batches")

    for batch in sorted(safe_batches, key=lambda x: x["days_left"]):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1])
            c1.markdown(f"**{batch['product_name']}**")
            c1.caption(f"🏷️ {batch['category']}")
            c2.caption(f"⏰ Expires: {batch['expiry_date']}")
            c3.caption(f"📦 Qty: {batch['current_quantity']}")
            c4.success(f"{batch['days_left']} days left")

# Agar koi bhi batch nahi hai
if not all_batches:
    st.info("No batches found. Go to **Products** to add a product, then add batches in **Batches** page.")
