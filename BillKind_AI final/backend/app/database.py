import sqlite3
import os
import hashlib
import uuid
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "billbridge.db")

def hash_password(password: str) -> str:
    """Generate SHA-256 hash with salt for secure password storage."""
    salt = "billbridge_secure_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone_number TEXT NOT NULL,
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        postal_code TEXT NOT NULL,
        role TEXT NOT NULL, -- 'donor', 'beneficiary', 'admin'
        dob TEXT NOT NULL,
        hashed_password TEXT NOT NULL,
        is_email_verified BOOLEAN DEFAULT 0,
        created_at TEXT NOT NULL
    );
    """)

    # Create OTP verification table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS otp_verifications (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        otp_code TEXT NOT NULL,
        created_at TEXT NOT NULL,
        is_used BOOLEAN DEFAULT 0
    );
    """)

    # Create Bill Requests table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bill_requests (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        beneficiary_name TEXT,
        beneficiary_email TEXT,
        beneficiary_phone TEXT,
        location TEXT,
        category TEXT NOT NULL,
        provider TEXT NOT NULL,
        bill_number TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'INR',
        raised REAL DEFAULT 0,
        due_date TEXT NOT NULL,
        verification_status TEXT DEFAULT 'under_review',
        funding_status TEXT DEFAULT 'unfunded',
        description TEXT NOT NULL,
        document_name TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """)

    # Ensure columns exist in case of upgrading existing database
    for col, col_type in [
        ("beneficiary_name", "TEXT"),
        ("beneficiary_email", "TEXT"),
        ("beneficiary_phone", "TEXT"),
        ("location", "TEXT"),
        ("document_name", "TEXT"),
        ("document_url", "TEXT"),
        ("currency", "TEXT DEFAULT 'INR'")
    ]:
        try:
            cursor.execute(f"ALTER TABLE bill_requests ADD COLUMN {col} {col_type};")
        except sqlite3.OperationalError:
            pass  # Column already exists

    # Check and insert default Admin account (email: admin@123, password: Admin)
    cursor.execute("SELECT id FROM users WHERE email = ?", ("admin@123",))
    admin_exists = cursor.fetchone()
    if not admin_exists:
        admin_id = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO users (
            id, name, email, phone_number, address, city, state, postal_code, role, dob, hashed_password, is_email_verified, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            admin_id,
            "System Administrator",
            "admin@123",
            "+91 9876543210",
            "BillKind AI Administrative Center, Sector 4",
            "Guntur",
            "Andhra Pradesh",
            "522001",
            "admin",
            "1985-01-01",
            hash_password("Admin"),
            1,
            datetime.utcnow().isoformat()
        ))
        print("[Database] Seeded Admin account: email=admin@123, password=Admin")

    # Check and insert default Donor account (email: donor@123, password: Donor)
    cursor.execute("SELECT id FROM users WHERE email = ?", ("donor@123",))
    donor_exists = cursor.fetchone()
    if not donor_exists:
        donor_id = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO users (
            id, name, email, phone_number, address, city, state, postal_code, role, dob, hashed_password, is_email_verified, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            donor_id,
            "Sarah Jenkins (Donor - Australia)",
            "donor@123",
            "+61 412 345 678",
            "Level 12, 100 George Street, Sydney, NSW, Australia",
            "Sydney",
            "New South Wales",
            "2000",
            "donor",
            "1992-05-14",
            hash_password("Donor"),
            1,
            datetime.utcnow().isoformat()
        ))
        print("[Database] Seeded Donor account: email=donor@123, password=Donor")


    # Check and insert default Beneficiary account (email: beneficiary@123, password: Beneficiary)
    cursor.execute("SELECT id FROM users WHERE email = ?", ("beneficiary@123",))
    ben_exists = cursor.fetchone()
    if not ben_exists:
        ben_id = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO users (
            id, name, email, phone_number, address, city, state, postal_code, role, dob, hashed_password, is_email_verified, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ben_id,
            "Lakshmi Rao (Beneficiary)",
            "beneficiary@123",
            "+91 98765 43210",
            "Door No 12-4, Market Road",
            "Guntur",
            "Andhra Pradesh",
            "522002",
            "beneficiary",
            "1990-08-22",
            hash_password("Beneficiary"),
            1,
            datetime.utcnow().isoformat()
        ))
        print("[Database] Seeded Beneficiary account: email=beneficiary@123, password=Beneficiary")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"[Database] Initialized successfully at: {DB_FILE}")
