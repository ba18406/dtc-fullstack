import tkinter as tk
from tkinter import messagebox
import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        dbname="dtc",
        user="dtc_user",
        password="1234"
    )

def init_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'supervisor', 'user')),
            supervisor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            file_name VARCHAR(255) NOT NULL,
            file_type VARCHAR(50),
            file_path TEXT,
            uploaded_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
            owner_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            drive_file_id TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

def create_default_admin():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE username = %s", ("admin",))
    existing = cur.fetchone()

    if not existing:
        cur.execute("""
            INSERT INTO users (username, password, full_name, role)
            VALUES (%s, %s, %s, %s)
        """, ("admin", "1212", "System Administrator", "admin"))
        conn.commit()

    cur.close()
    conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, full_name, role, supervisor_id
        FROM users
        WHERE username = %s AND password = %s AND is_active = TRUE
    """, (username, password))

    user = cur.fetchone()

    cur.close()
    conn.close()
    return user

def open_dashboard(user_id, username, full_name, role, supervisor_id):
    messagebox.showinfo(
        "Success",
        f"Logged in successfully\n\nUser: {username}\nName: {full_name}\nRole: {role}"
    )

def handle_login():
    username = user_name_entry.get().strip()
    password = password_entry.get().strip()

    try:
        user = authenticate_user(username, password)

        if user:
            user_id, username, full_name, role, supervisor_id = user
            open_dashboard(user_id, username, full_name, role, supervisor_id)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

print("Functions loaded successfully")
print(init_database)
print(create_default_admin)

# Setup database before opening UI
try:
    init_database()
    create_default_admin()
    print("Database ready")
except Exception as e:
    print("Database setup failed:", e)

# UI
root = tk.Tk()
root.title("Login window")
root.geometry("420x220")

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

top_frame = tk.Frame(root, bg="lightblue")
top_frame.grid(row=0, column=0, sticky="nsew")

bottom_frame = tk.Frame(root, bg="lightgray")
bottom_frame.grid(row=1, column=0, sticky="nsew")

title_label = tk.Label(
    top_frame,
    text="Data Tracking Center",
    bg="lightblue",
    font=("Arial", 14, "bold")
)
title_label.grid(row=0, column=0, padx=10, pady=10)

user_name_label = tk.Label(bottom_frame, text="User name")
user_name_label.grid(row=0, column=0, padx=10, pady=10)

user_name_entry = tk.Entry(bottom_frame)
user_name_entry.grid(row=0, column=1, padx=10, pady=10)

password_label = tk.Label(bottom_frame, text="Password")
password_label.grid(row=1, column=0, padx=10, pady=10)

password_entry = tk.Entry(bottom_frame, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=10)

login_button = tk.Button(bottom_frame, text="Login", command=handle_login)
login_button.grid(row=2, column=0, columnspan=2, pady=15)

root.mainloop()

'''
import tkinter as tk
from tkinter import messagebox
import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        dbname="dtc_postgres",
        user="postgres",
        password="YOUR_REAL_PASSWORD"
    )

def init_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'supervisor', 'user')),
            supervisor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            file_name VARCHAR(255) NOT NULL,
            file_type VARCHAR(50),
            file_path TEXT,
            uploaded_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
            owner_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            drive_file_id TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

def create_default_admin():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE username = %s", ("admin",))
    existing = cur.fetchone()

    if not existing:
        cur.execute("""
            INSERT INTO users (username, password, full_name, role)
            VALUES (%s, %s, %s, %s)
        """, ("admin", "1212", "System Administrator", "admin"))
        conn.commit()

    cur.close()
    conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, full_name, role, supervisor_id
        FROM users
        WHERE username = %s AND password = %s AND is_active = TRUE
    """, (username, password))

    user = cur.fetchone()

    cur.close()
    conn.close()

    return user

def open_dashboard(user_id, username, full_name, role, supervisor_id):
    messagebox.showinfo(
        "Success",
        f"Logged in successfully\n\nUser: {username}\nName: {full_name}\nRole: {role}"
    )

def handle_login():
    username = user_name_entry.get().strip()
    password = password_entry.get().strip()

    try:
        user = authenticate_user(username, password)

        if user:
            user_id, username, full_name, role, supervisor_id = user
            open_dashboard(user_id, username, full_name, role, supervisor_id)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# database setup first
try:
    init_database()
    create_default_admin()
    print("Database ready")
except Exception as e:
    print("Database setup failed:", e)
    
def can_manage_users(role):
    return role == "admin"

def can_view_all_files(role):
    return role == "admin"

def can_view_subordinate_files(role):
    return role == "supervisor"

def can_delete_file(role, file_owner_id, current_user_id, subordinate_ids=None):
    if role == "admin":
        return True
    if role == "user":
        return file_owner_id == current_user_id
    if role == "supervisor":
        subordinate_ids = subordinate_ids or []
        return file_owner_id == current_user_id or file_owner_id in subordinate_ids
    return False

def get_subordinate_user_ids(supervisor_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM users
        WHERE supervisor_id = %s AND is_active = TRUE
    """, (supervisor_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [row[0] for row in rows]

def get_files_for_user(current_user_id, role):
    conn = get_connection()
    cur = conn.cursor()

    if role == "admin":
        cur.execute("""
            SELECT f.id, f.file_name, f.file_type, f.uploaded_at, u.username
            FROM files f
            LEFT JOIN users u ON f.owner_user_id = u.id
            ORDER BY f.uploaded_at DESC
        """)

    elif role == "supervisor":
        subordinate_ids = get_subordinate_user_ids(current_user_id)
        allowed_ids = [current_user_id] + subordinate_ids

        cur.execute(f"""
            SELECT f.id, f.file_name, f.file_type, f.uploaded_at, u.username
            FROM files f
            LEFT JOIN users u ON f.owner_user_id = u.id
            WHERE f.owner_user_id = ANY(%s)
            ORDER BY f.uploaded_at DESC
        """, (allowed_ids,))

    else:
        cur.execute("""
            SELECT f.id, f.file_name, f.file_type, f.uploaded_at, u.username
            FROM files f
            LEFT JOIN users u ON f.owner_user_id = u.id
            WHERE f.owner_user_id = %s
            ORDER BY f.uploaded_at DESC
        """, (current_user_id,))

    records = cur.fetchall()

    cur.close()
    conn.close()

    return records

def save_file_record(file_name, file_type, file_path, uploaded_by, owner_user_id, drive_file_id=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO files (file_name, file_type, file_path, uploaded_by, owner_user_id, drive_file_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (file_name, file_type, file_path, uploaded_by, owner_user_id, drive_file_id))

    conn.commit()
    cur.close()
    conn.close()

def create_user(username, password, full_name, role, supervisor_id=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (username, password, full_name, role, supervisor_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (username, password, full_name, role, supervisor_id))

    conn.commit()
    cur.close()
    conn.close()

def open_dashboard(user_id, username, full_name, role, supervisor_id):
    if role == "admin":
        open_admin_panel(user_id, username, full_name)
    elif role == "supervisor":
        open_supervisor_panel(user_id, username, full_name)
    else:
        open_user_panel(user_id, username, full_name)

import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

print("Step 1: file started")

init_database()
print("Step 2: database initialized")

create_default_admin()
print("Step 3: admin created")

# UI
root = tk.Tk()
print("Step 4: root created")

root.title("Login window")
root.geometry("420x220")

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

top_frame = tk.Frame(root, bg="lightblue")
top_frame.grid(row=0, column=0, sticky="nsew")

bottom_frame = tk.Frame(root, bg="lightgray")
bottom_frame.grid(row=1, column=0, sticky="nsew")

title_label = tk.Label(top_frame, text="Data Tracking Center", bg="lightblue", font=("Arial", 14, "bold"))
title_label.grid(row=0, column=0, padx=10, pady=10)

user_name_label = tk.Label(bottom_frame, text="User name")
user_name_label.grid(row=0, column=0, padx=10, pady=10)

user_name_entry = tk.Entry(bottom_frame)
user_name_entry.grid(row=0, column=1, padx=10, pady=10)

password_label = tk.Label(bottom_frame, text="Password")
password_label.grid(row=1, column=0, padx=10, pady=10)

password_entry = tk.Entry(bottom_frame, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=10)

login_button = tk.Button(bottom_frame, text="Login", command=handle_login)
login_button.grid(row=2, column=0, columnspan=2, pady=15)

print("Step 5: before mainloop")
root.mainloop()
print("Step 6: after mainloop")
'''
