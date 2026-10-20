from datetime import date  # Current date aur date comparison ke liye


def calculate_expiry_status(expiry_date_str, alert_days):
    """
    Batch ka expiry status calculate karta hai.

    Rules (synopsis se confirmed):
    - Agar expiry date aaj se pehle hai → "Expired"
    - Agar baaki dinn <= alert_days hain → "Expiring Soon"
    - Warna → "Safe"

    Parameters:
        expiry_date_str : string format mein expiry date "YYYY-MM-DD"
        alert_days      : user ka alert preference (1 to 7)

    Returns:
        status      : "Safe", "Expiring Soon", ya "Expired"
        days_left   : kitne dinn baaki hain (negative agar expired)
    """

    # String date ko Python date object mein convert karo
    expiry_date = date.fromisoformat(expiry_date_str)

    # Aaj ki actual date lo — hardcoded nahi, real date
    today = date.today()

    # Kitne dinn baaki hain calculate karo
    days_left = (expiry_date - today).days

    # Status decide karo — teen conditions
    if expiry_date < today:
        # Expiry date kal ya usse pehle thi — already expired
        status = "Expired"

    elif days_left <= alert_days:
        # Baaki dinn alert_days se kam ya barabar hain — alert zone
        status = "Expiring Soon"

    else:
        # Kafi time baaki hai — safe hai
        status = "Safe"

    return status, days_left


def status_color(status):
    """
    Status ke hisaab se color return karta hai — UI mein dikhane ke liye.
    Streamlit ke st.success / st.warning / st.error ke liye use hoga.
    """
    if status == "Safe":
        return "green"
    elif status == "Expiring Soon":
        return "orange"
    else:
        return "red"
