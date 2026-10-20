import sqlite3
import os

# Database file ka path — database folder ke andar grocery.db file banegi
DB_PATH = os.path.join(os.path.dirname(__file__), "grocery.db")


def get_connection():
    """
    Database se connection banata hai.
    foreign_keys ON karta hai taaki relationships enforce hon.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # FK enforcement zaroori hai
    conn.row_factory = sqlite3.Row  # Results ko dictionary jaisa access milega
    return conn


def create_tables():
    """
    Agar tables pehle se exist nahi karti toh banata hai.
    App start hote hi yeh function call hota hai.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── Table 1: users ──────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            email    TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        )
    """)

    # ── Table 2: products ───────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            product_name TEXT    NOT NULL,
            category     TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # ── Table 3: batches ────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            batch_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id        INTEGER NOT NULL,
            initial_quantity  INTEGER NOT NULL,
            current_quantity  INTEGER NOT NULL,
            mfg_date          TEXT,
            purchase_date     TEXT    NOT NULL,
            expiry_date       TEXT    NOT NULL,
            alert_preference  INTEGER NOT NULL DEFAULT 3,
            expiry_status     TEXT    NOT NULL DEFAULT 'Safe',
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    # ── Table 4: batch_history ──────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batch_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id   INTEGER NOT NULL,
            event_type TEXT    NOT NULL,
            event_date TEXT    NOT NULL,
            details    TEXT,
            FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Saari tables successfully ban gayi!")


# ── Test function: sample data insert karke dekhte hain ─────────────────────
def test_database():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Ek test user insert karo
    cursor.execute("""
        INSERT OR IGNORE INTO users (name, email, password)
        VALUES (?, ?, ?)
    """, ("Vaishnavi", "vaishnavi@test.com", "test123"))

    # 2. User ka ID lo
    cursor.execute("SELECT user_id FROM users WHERE email = ?",
                   ("vaishnavi@test.com",))
    user = cursor.fetchone()
    user_id = user["user_id"]

    # 3. Ek test product insert karo
    cursor.execute("""
        INSERT INTO products (user_id, product_name, category)
        VALUES (?, ?, ?)
    """, (user_id, "Amul Milk", "Dairy"))
    product_id = cursor.lastrowid

    # 4. Ek test batch insert karo
    cursor.execute("""
        INSERT INTO batches
            (product_id, initial_quantity, current_quantity,
             purchase_date, expiry_date, alert_preference, expiry_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (product_id, 10, 10, "2026-10-20", "2026-10-25", 3, "Safe"))
    batch_id = cursor.lastrowid

    # 5. Batch history mein entry karo
    cursor.execute("""
        INSERT INTO batch_history (batch_id, event_type, event_date, details)
        VALUES (?, ?, ?, ?)
    """, (batch_id, "Batch Added", "2026-10-20", "Test batch added successfully"))

    conn.commit()

    # 6. Verify karo — sab fetch karke print karo
    print("\n── Users ──")
    for row in cursor.execute("SELECT * FROM users"):
        print(dict(row))

    print("\n── Products ──")
    for row in cursor.execute("SELECT * FROM products"):
        print(dict(row))

    print("\n── Batches ──")
    for row in cursor.execute("SELECT * FROM batches"):
        print(dict(row))

    print("\n── Batch History ──")
    for row in cursor.execute("SELECT * FROM batch_history"):
        print(dict(row))

    conn.close()
    print("\n✅ Database test complete! Sab records save aur retrieve ho gaye!")


# ── User Authentication Functions ────────────────────────────────────────────

def register_user(name, email, password):
    """
    Naya user register karta hai.
    Returns: (True, "message") ya (False, "error message")
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "This email is already registered. Please use a different email."
    except Exception as e:
        return False, f"Error: {str(e)}"


def login_user(email, password):
    """
    Email aur password se user dhundta hai.
    Returns: user dict agar sahi, warna None
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, password)
    )
    user = cursor.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None


# ── Product Functions ─────────────────────────────────────────────────────────

def add_product(user_id, product_name, category):
    """
    Naya product database mein save karta hai.
    Ek hi user ka same naam ka product dobara save nahi hoga.
    Returns: (True, product_id) ya (False, error message)
    """
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Check karo ki same user ka same product already exist toh nahi karta
        cursor.execute(
            "SELECT product_id FROM products WHERE user_id = ? AND LOWER(product_name) = LOWER(?)",
            (user_id, product_name)
        )
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return False, "This product already exists. You can add a new batch for it."

        # Product database mein insert karo
        cursor.execute(
            "INSERT INTO products (user_id, product_name, category) VALUES (?, ?, ?)",
            (user_id, product_name, category)
        )
        conn.commit()
        product_id = cursor.lastrowid  # Naye product ki auto-generated ID lo
        conn.close()
        return True, product_id

    except Exception as e:
        return False, f"Error: {str(e)}"


def get_all_products(user_id):
    """
    Logged-in user ke saare products fetch karta hai.
    Returns: list of product dicts
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE user_id = ? ORDER BY product_name ASC",
        (user_id,)
    )
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return products


def delete_product(product_id):
    """
    Ek product aur usse related saari batches delete karta hai.
    Returns: (True, message) ya (False, error)
    """
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Pehle is product ki saari batches ki history delete karo
        cursor.execute("""
            DELETE FROM batch_history
            WHERE batch_id IN (
                SELECT batch_id FROM batches WHERE product_id = ?
            )
        """, (product_id,))

        # Phir is product ki saari batches delete karo
        cursor.execute("DELETE FROM batches WHERE product_id = ?", (product_id,))

        # Ab product delete karo
        cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))

        conn.commit()
        conn.close()
        return True, "Product and all its batches deleted successfully."

    except Exception as e:
        return False, f"Error: {str(e)}"


# ── Batch Functions ───────────────────────────────────────────────────────────

def add_batch(product_id, initial_quantity, purchase_date,
              expiry_date, alert_preference, expiry_status, mfg_date=None):
    """
    Naya batch database mein save karta hai.
    Saath mein batch_history mein 'Batch Added' event bhi record karta hai.
    Returns: (True, batch_id) ya (False, error message)
    """
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Batch insert karo — current_quantity = initial_quantity se shuru hoti hai
        cursor.execute("""
            INSERT INTO batches
                (product_id, initial_quantity, current_quantity,
                 mfg_date, purchase_date, expiry_date,
                 alert_preference, expiry_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (product_id, initial_quantity, initial_quantity,
              mfg_date, purchase_date, expiry_date,
              alert_preference, expiry_status))

        batch_id = cursor.lastrowid  # Naye batch ki auto ID

        # Batch history mein pehli entry — "Batch Added"
        cursor.execute("""
            INSERT INTO batch_history (batch_id, event_type, event_date, details)
            VALUES (?, ?, ?, ?)
        """, (batch_id, "Batch Added", purchase_date,
              f"Batch added with quantity {initial_quantity}, "
              f"expiry {expiry_date}, status: {expiry_status}"))

        conn.commit()
        conn.close()
        return True, batch_id

    except Exception as e:
        return False, f"Error: {str(e)}"


def get_batches_by_product(product_id):
    """
    Ek product ki saari batches fetch karta hai.
    Returns: list of batch dicts
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM batches WHERE product_id = ? ORDER BY purchase_date DESC",
        (product_id,)
    )
    batches = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return batches


def get_all_batches_with_product(user_id):
    """
    User ki saari batches fetch karta hai — product name ke saath.
    Dashboard aur expiry monitor ke liye use hoga.
    Returns: list of dicts with batch + product info
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            b.batch_id,
            b.product_id,
            p.product_name,
            p.category,
            b.initial_quantity,
            b.current_quantity,
            b.mfg_date,
            b.purchase_date,
            b.expiry_date,
            b.alert_preference,
            b.expiry_status
        FROM batches b
        JOIN products p ON b.product_id = p.product_id
        WHERE p.user_id = ?
        ORDER BY b.expiry_date ASC
    """, (user_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def update_batch_status(batch_id, new_status):
    """
    Batch ka expiry_status update karta hai.
    Expiry monitor page se call hoga.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE batches SET expiry_status = ? WHERE batch_id = ?",
        (new_status, batch_id)
    )
    conn.commit()
    conn.close()


# Yeh block sirf tab run hoga jab hum directly 'python db.py' chalayein
if __name__ == "__main__":
    create_tables()
    test_database()

