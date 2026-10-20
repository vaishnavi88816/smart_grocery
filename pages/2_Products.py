import streamlit as st  # Web interface ke liye
import sys              # Path manage karne ke liye
import os               # File path ke liye

# database folder ko path mein add karo
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "database"))

# db.py se product functions import karo
from db import add_product, get_all_products, delete_product

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Products — Smart Grocery System",
    page_icon  = "📦",
    layout     = "wide"
)

# ── Login check — agar logged in nahi hai toh yahan aane se rokko ─────────────
# session_state mein logged_in nahi hai matlab user ne login nahi kiya
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login first.")
    st.stop()  # Aage ka code execute mat karo

# ── Logged-in user ki details lo ─────────────────────────────────────────────
user    = st.session_state.user
user_id = user["user_id"]  # Foreign key ke liye user_id zaroori hai

# ── Page heading ──────────────────────────────────────────────────────────────
st.title("📦 Product Management")
st.caption("Add new grocery products and view your product list.")
st.divider()

# ── Do sections: Add Product | View Products ──────────────────────────────────
col_form, col_gap, col_list = st.columns([1.2, 0.1, 1.8])

# =============================================================================
#  LEFT SECTION — Add New Product Form
# =============================================================================
with col_form:
    st.subheader("Add New Product")

    # Product name input
    product_name = st.text_input(
        "Product Name",
        placeholder="e.g. Amul Milk, Parle-G, Toor Dal",
        key="prod_name"
    )

    # Category dropdown — predefined categories
    # Yeh categories synopsis ke hisaab se common grocery categories hain
    category = st.selectbox(
        "Category",
        options=[
            "Dairy",
            "Grains & Pulses",
            "Snacks & Biscuits",
            "Beverages",
            "Spices & Condiments",
            "Frozen Foods",
            "Personal Care",
            "Cleaning Products",
            "Other"
        ],
        key="prod_category"
    )

    st.markdown(" ")  # Thoda space

    # Save button
    if st.button("Save Product", type="primary", use_container_width=True):

        # Validation — product name khali nahi hona chahiye
        if not product_name.strip():
            st.warning("Please enter a product name.")
        else:
            # Database mein save karne ki koshish karo
            ok, result = add_product(user_id, product_name.strip(), category)

            if ok:
                st.success(f"Product **{product_name}** saved successfully!")
                st.rerun()  # List refresh karo
            else:
                # result mein error message hoga
                st.error(result)

# =============================================================================
#  RIGHT SECTION — Products List
# =============================================================================
with col_list:
    st.subheader("Your Products")

    # Database se is user ke saare products fetch karo
    products = get_all_products(user_id)

    if not products:
        # Koi product nahi hai abhi tak
        st.info("No products added yet. Add your first product from the left panel.")
    else:
        # Total product count dikhao
        st.caption(f"Total products: **{len(products)}**")
        st.markdown(" ")

        # Har product ke liye ek row dikhao
        for product in products:
            # Ek container mein product details aur delete button
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1.5, 0.8])

                # Column 1 — Product name
                with c1:
                    st.markdown(f"**{product['product_name']}**")

                # Column 2 — Category badge
                with c2:
                    st.caption(f"🏷️ {product['category']}")

                # Column 3 — Delete button
                with c3:
                    # Unique key zaroori hai har button ke liye
                    if st.button("Delete", key=f"del_{product['product_id']}",
                                 type="secondary"):
                        ok, msg = delete_product(product["product_id"])
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
