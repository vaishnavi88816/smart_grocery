import streamlit as st          # Web interface ke liye
import sys                      # Path manage karne ke liye
import os                       # File path ke liye
from datetime import date       # Aaj ki date lene ke liye

# Required folders ko Python path mein add karo
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

# Database functions import karo
from db import get_all_products, add_batch, get_all_batches_with_product

# Expiry status calculate karne ka function import karo
from expiry_logic import calculate_expiry_status

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Batches — Smart Grocery System",
    page_icon  = "🗂️",
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
st.title("🗂️ Batch Management")
st.caption("Every purchase is tracked as a separate batch — with its own quantity, dates and expiry status.")
st.divider()

# ── Do sections: Add Batch | View All Batches ─────────────────────────────────
col_form, col_gap, col_list = st.columns([1.3, 0.1, 1.7])

# =============================================================================
#  LEFT — Add New Batch Form
# =============================================================================
with col_form:
    st.subheader("Add New Batch")

    # Pehle user ke saare products fetch karo — dropdown ke liye
    products = get_all_products(user_id)

    if not products:
        # Koi product nahi hai — pehle product add karna hoga
        st.info("No products found. Please add a product first from the Products page.")
        st.stop()

    # Product names ki list banao dropdown ke liye
    # Format: "Product Name (Category)"
    product_options = {
        f"{p['product_name']} ({p['category']})": p["product_id"]
        for p in products
    }

    # Product select karo — dropdown
    selected_label = st.selectbox(
        "Select Product",
        options=list(product_options.keys()),
        key="batch_product"
    )
    # Selected product ka ID lo
    selected_product_id = product_options[selected_label]

    # Purchase date — default aaj ki date
    purchase_date = st.date_input(
        "Purchase Date",
        value=date.today(),  # Aaj ki real date — hardcoded nahi
        key="batch_purchase_date"
    )

    # Manufacturing date — optional field
    mfg_date = st.date_input(
        "Manufacturing Date (Optional)",
        value=None,
        key="batch_mfg_date"
    )

    # Expiry date — zaroori field
    expiry_date = st.date_input(
        "Expiry Date",
        value=date.today(),
        key="batch_expiry_date"
    )

    # Initial quantity — kitne items kharide
    initial_qty = st.number_input(
        "Quantity (Number of items)",
        min_value=1,
        value=1,
        step=1,
        key="batch_qty"
    )

    # Alert preference — 1 se 7 dinn
    # Iska matlab: expiry se pehle kitne dinn mein alert dikhao
    alert_days = st.slider(
        "Expiry Alert (days before expiry)",
        min_value=1,
        max_value=7,
        value=3,
        help="e.g. if set to 3, batch will show 'Expiring Soon' when 3 or fewer days are left."
    )

    # Alert ka real time explanation dikhao
    st.caption(f"Alert will trigger when **{alert_days} or fewer days** remain before expiry.")

    st.markdown(" ")

    # Save Batch button
    if st.button("Save Batch", type="primary", use_container_width=True):

        # Validation — expiry date purchase date se pehle nahi honi chahiye
        if expiry_date < purchase_date:
            st.error("Expiry date cannot be before the purchase date.")

        else:
            # String format mein convert karo — SQLite ke liye
            expiry_str   = expiry_date.isoformat()    # "YYYY-MM-DD"
            purchase_str = purchase_date.isoformat()
            mfg_str      = mfg_date.isoformat() if mfg_date else None

            # Expiry status calculate karo — real logic use karo
            status, days_left = calculate_expiry_status(expiry_str, alert_days)

            # Database mein batch save karo
            ok, result = add_batch(
                product_id       = selected_product_id,
                initial_quantity = initial_qty,
                purchase_date    = purchase_str,
                expiry_date      = expiry_str,
                alert_preference = alert_days,
                expiry_status    = status,
                mfg_date         = mfg_str
            )

            if ok:
                st.success(f"Batch saved! Status: **{status}** ({days_left} days left)")
                st.rerun()
            else:
                st.error(result)

# =============================================================================
#  RIGHT — All Batches List
# =============================================================================
with col_list:
    st.subheader("All Batches")

    # User ki saari batches fetch karo — product name ke saath
    all_batches = get_all_batches_with_product(user_id)

    if not all_batches:
        st.info("No batches added yet.")
    else:
        st.caption(f"Total batches: **{len(all_batches)}**")
        st.markdown(" ")

        # Har batch ke liye ek card dikhao
        for batch in all_batches:
            with st.container(border=True):

                # Status ke hisaab se color decide karo
                status = batch["expiry_status"]
                if status == "Safe":
                    st.success(f"✅ {status}")
                elif status == "Expiring Soon":
                    st.warning(f"⚠️ {status}")
                else:
                    st.error(f"❌ {status}")

                # Batch ki details — 3 columns mein
                c1, c2, c3 = st.columns(3)

                with c1:
                    st.markdown(f"**{batch['product_name']}**")
                    st.caption(f"🏷️ {batch['category']}")

                with c2:
                    st.caption(f"📅 Purchased: {batch['purchase_date']}")
                    st.caption(f"⏰ Expires: {batch['expiry_date']}")

                with c3:
                    st.caption(f"📦 Qty: {batch['current_quantity']} / {batch['initial_quantity']}")
                    st.caption(f"🔔 Alert: {batch['alert_preference']} days")
