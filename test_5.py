import tkinter as tk
from tkinter import ttk
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

def open_dashboard(current_user):
    dashboard = tk.Toplevel()
    dashboard.title("Dashboard")
    dashboard.geometry("500x400")
    dashboard.configure(bg="white")

    lbl_title = tk.Label(
        dashboard,
        text="Dashboard",
        font=("Arial", 16, "bold"),
        bg="white"
    )
    lbl_title.pack(pady=10)

    lbl_info = tk.Label(
        dashboard,
        text=f"Welcome: {current_user['username']}\n"
             f"Name: {current_user['full_name']}\n"
             f"Role: {current_user['role']}",
        font=("Arial", 12),
        bg="white",
        justify="left"
    )
    lbl_info.pack(pady=10)

    btn_manage_users = tk.Button(
        dashboard,
        text="Manage Users",
        width=20,
        command=lambda: open_users_window(current_user)
    )

    btn_manage_team = tk.Button(
        dashboard,
        text="Manage Team",
        width=20,
        command=lambda: open_users_window(current_user)
    )

    btn_view_own_data = tk.Button(
        dashboard,
        text="My Data",
        width=20,
        command=lambda: open_users_window(current_user)
    )

    if current_user["role"] == "admin":
        btn_manage_users.pack(pady=5)

    elif current_user["role"] == "supervisor":
        btn_manage_team.pack(pady=5)

    else:
        btn_view_own_data.pack(pady=5)

    # Load data
    users = get_visible_users(current_user)
    print(users)

def handle_login():
    username = user_name_entry.get().strip()
    password = password_entry.get().strip()

    try:
        user = authenticate_user(username, password)

        if user:
            user_id, username, full_name, role, supervisor_id = user

            current_user = {
                "id": user_id,
                "username": username,
                "full_name": full_name,
                "role": role,
                "supervisor_id": supervisor_id
            }

            open_dashboard(current_user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

def get_visible_users(current_user):
    conn = get_connection()
    cur = conn.cursor()

    if current_user["role"] == "admin":
        cur.execute("""
            SELECT id, username, full_name, role, supervisor_id
            FROM users
            ORDER BY id
        """)

    elif current_user["role"] == "supervisor":
        cur.execute("""
            SELECT id, username, full_name, role, supervisor_id
            FROM users
            WHERE supervisor_id = %s
            ORDER BY id
        """, (current_user["id"],))

    else:
        cur.execute("""
            SELECT id, username, full_name, role, supervisor_id
            FROM users
            WHERE id = %s
            ORDER BY id
        """, (current_user["id"],))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def show_visible_users(current_user):
    try:
        rows = get_visible_users(current_user)

        if not rows:
            messagebox.showinfo("Users", "No users found.")
            return

        text = ""
        for row in rows:
            user_id, username, full_name, role, supervisor_id = row
            text += (
                f"ID: {user_id}\n"
                f"Username: {username}\n"
                f"Full Name: {full_name}\n"
                f"Role: {role}\n"
                f"Supervisor ID: {supervisor_id}\n"
                f"{'-'*30}\n"
            )

        messagebox.showinfo("Visible Users", text)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def open_users_window(current_user):
    try:
        rows = get_visible_users(current_user)

        users_win = tk.Toplevel()
        users_win.title("Users")
        users_win.geometry("900x550")
        users_win.configure(bg="white")

        lbl_title = tk.Label(
            users_win,
            text="Visible Users",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        lbl_title.pack(pady=10)

        frame_table = tk.Frame(users_win, bg="white")
        frame_table.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("id", "username", "full_name", "role", "supervisor_id")

        tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=15)
        tree.pack(side="left", fill="both", expand=True)

        def load_users():
            for item in tree.get_children():
                tree.delete(item)

            fresh_rows = get_visible_users(current_user)

            if not fresh_rows:
                tree.insert("", tk.END, values=("", "No users found", "", "", ""))
            else:
                for row in fresh_rows:
                    tree.insert("", tk.END, values=row)
                    
        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")

        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("id", text="ID")
        tree.heading("username", text="Username")
        tree.heading("full_name", text="Full Name")
        tree.heading("role", text="Role")
        tree.heading("supervisor_id", text="Supervisor ID")

        tree.column("id", width=70, anchor="center")
        tree.column("username", width=150, anchor="center")
        tree.column("full_name", width=200, anchor="center")
        tree.column("role", width=120, anchor="center")
        tree.column("supervisor_id", width=120, anchor="center")

        load_users()

        def show_selected_user():
            selected_item = tree.selection()

            if not selected_item:
                messagebox.showwarning("Warning", "Please select a user first.")
                return

            values = tree.item(selected_item[0], "values")

            user_id = values[0]
            username = values[1]
            full_name = values[2]
            role = values[3]
            supervisor_id = values[4]

            messagebox.showinfo(
                "Selected User",
                f"ID: {user_id}\n"
                f"Username: {username}\n"
                f"Full Name: {full_name}\n"
                f"Role: {role}\n"
                f"Supervisor ID: {supervisor_id}"
            )

        def add_new_user():
            add_win = tk.Toplevel(users_win)
            add_win.title("Add New User")
            add_win.geometry("400x380")
            add_win.configure(bg="white")

            tk.Label(add_win, text="Username", bg="white").pack(pady=5)
            entry_username = tk.Entry(add_win)
            entry_username.pack(pady=5)

            tk.Label(add_win, text="Password", bg="white").pack(pady=5)
            entry_password = tk.Entry(add_win, show="*")
            entry_password.pack(pady=5)

            tk.Label(add_win, text="Full Name", bg="white").pack(pady=5)
            entry_full_name = tk.Entry(add_win)
            entry_full_name.pack(pady=5)

            tk.Label(add_win, text="Role", bg="white").pack(pady=5)

            if current_user["role"] == "admin":
                role_values = ["admin", "supervisor", "user"]
            else:
                role_values = ["user"]

            role_var = tk.StringVar(value=role_values[0])

            combo_role = ttk.Combobox(
                add_win,
                textvariable=role_var,
                values=role_values,
                state="readonly"
            )
            combo_role.pack(pady=5)

            tk.Label(add_win, text="Supervisor", bg="white").pack(pady=5)

            supervisors = get_supervisors_for_dropdown()
            supervisor_options = ["None"]
            supervisor_map = {"None": None}

            for sup_id, sup_username, sup_full_name in supervisors:
                label = f"{sup_id} - {sup_username} - {sup_full_name}"
                supervisor_options.append(label)
                supervisor_map[label] = sup_id

            supervisor_var = tk.StringVar(value="None")

            if current_user["role"] == "supervisor":
                current_label = f"{current_user['id']} - {current_user['username']} - {current_user['full_name']}"
                supervisor_options = [current_label]
                supervisor_map = {current_label: current_user["id"]}
                supervisor_var.set(current_label)

            combo_supervisor = ttk.Combobox(
                add_win,
                textvariable=supervisor_var,
                values=supervisor_options,
                state="readonly",
                width=35
            )
            combo_supervisor.pack(pady=5)

            def save_new_user():
                try:
                    new_username = entry_username.get().strip()
                    new_password = entry_password.get().strip()
                    new_full_name = entry_full_name.get().strip()
                    new_role = role_var.get().strip()
                    selected_supervisor = supervisor_var.get()
                    new_supervisor_id = supervisor_map[selected_supervisor]

                    if not new_username or not new_password or not new_full_name:
                        messagebox.showwarning("Warning", "Please fill all fields.")
                        return

                    if current_user["role"] == "supervisor":
                        new_role = "user"
                        new_supervisor_id = current_user["id"]

                    if new_role == "admin":
                        new_supervisor_id = None

                    elif new_role in ("supervisor", "user") and new_supervisor_id is None:
                        messagebox.showwarning("Warning", "Please select a supervisor.")
                        return

                    add_user_to_db(
                        new_username,
                        new_password,
                        new_full_name,
                        new_role,
                        new_supervisor_id
                    )

                    messagebox.showinfo("Success", "User added successfully.")
                    add_win.destroy()
                    load_users()

                except Exception as e:
                    messagebox.showerror("Error", str(e))

            tk.Button(
                add_win,
                text="Save New User",
                width=20,
                command=save_new_user
            ).pack(pady=15)
            
        def edit_selected_user():
            selected_item = tree.selection()

            if not selected_item:
                messagebox.showwarning("Warning", "Please select a user first.")
                return

            values = tree.item(selected_item[0], "values")

            if current_user["role"] == "supervisor":
                selected_supervisor_id = values[4]

                if str(selected_supervisor_id) != str(current_user["id"]):
                    messagebox.showwarning(
                        "Warning",
                        "You can edit only users under your supervision."
                    )
                    return
                
            user_id = values[0]
            username = values[1]
            full_name = values[2]
            role = values[3]
            supervisor_id = values[4]

            edit_win = tk.Toplevel(users_win)
            edit_win.title("Edit User")
            edit_win.geometry("400x360")
            edit_win.configure(bg="white")

            tk.Label(edit_win, text="User ID", bg="white").pack(pady=5)
            entry_user_id = tk.Entry(edit_win)
            entry_user_id.pack(pady=5)
            entry_user_id.insert(0, user_id)
            entry_user_id.config(state="readonly")

            tk.Label(edit_win, text="Username", bg="white").pack(pady=5)
            entry_username = tk.Entry(edit_win)
            entry_username.pack(pady=5)
            entry_username.insert(0, username)

            tk.Label(edit_win, text="Full Name", bg="white").pack(pady=5)
            entry_full_name = tk.Entry(edit_win)
            entry_full_name.pack(pady=5)
            entry_full_name.insert(0, full_name)

            tk.Label(edit_win, text="Role", bg="white").pack(pady=5)
            role_var = tk.StringVar(value=role)

            combo_role = ttk.Combobox(
                edit_win,
                textvariable=role_var,
                values=["admin", "supervisor", "user"],
                state="readonly"
            )
            combo_role.pack(pady=5)

            tk.Label(edit_win, text="Supervisor ID", bg="white").pack(pady=5)
            supervisors = get_supervisors_for_dropdown()

            supervisor_options = ["None"]
            supervisor_map = {"None": None}

            for sup_id, sup_username, sup_full_name in supervisors:
                label = f"{sup_id} - {sup_username} - {sup_full_name}"
                supervisor_options.append(label)
                supervisor_map[label] = sup_id

            current_supervisor_label = "None"

            for label, sup_id in supervisor_map.items():
                if str(sup_id) == str(supervisor_id):
                    current_supervisor_label = label
                    break

            supervisor_var = tk.StringVar(value=current_supervisor_label)

            combo_supervisor = ttk.Combobox(
                edit_win,
                textvariable=supervisor_var,
                values=supervisor_options,
                state="readonly",
                width=35
            )
            combo_supervisor.pack(pady=5)
                        
            def save_changes():
                try:
                    new_username = entry_username.get().strip()
                    new_full_name = entry_full_name.get().strip()
                    new_role = role_var.get().strip()

                    selected_supervisor_label = supervisor_var.get()
                    new_supervisor_id = supervisor_map[selected_supervisor_label]

                    if not new_username or not new_full_name or not new_role:
                        messagebox.showwarning("Warning", "Please fill all required fields.")
                        return

                    if new_role == "admin":
                        new_supervisor_id = None

                    elif new_role in ("supervisor", "user") and new_supervisor_id is None:
                        messagebox.showwarning("Warning", "Please select a supervisor.")
                        return

                    update_user_in_db(
                        int(user_id),
                        new_username,
                        new_full_name,
                        new_role,
                        new_supervisor_id
                    )

                    messagebox.showinfo("Success", "User updated successfully.")
                    edit_win.destroy()
                    load_users()

                except Exception as e:
                    messagebox.showerror("Error", str(e))
                    
            btn_save = tk.Button(
                edit_win,
                text="Save Changes",
                width=20,
                command=save_changes
            )
            btn_save.pack(pady=15)

        def delete_selected_user():
            selected_item = tree.selection()

            if not selected_item:
                messagebox.showwarning("Warning", "Please select a user first.")
                return

            values = tree.item(selected_item[0], "values")
            selected_user_id = int(values[0])

            if selected_user_id == current_user["id"]:
                messagebox.showwarning("Warning", "You cannot delete your own account.")
                return

            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete user: {values[1]}?"
            )
            
            if current_user["role"] == "supervisor":
                selected_supervisor_id = values[4]

                if str(selected_supervisor_id) != str(current_user["id"]):
                    messagebox.showwarning(
                        "Warning",
                        "You can delete only users under your supervision."
                    )
                    return

            if confirm:
                try:
                    delete_user_from_db(selected_user_id)
                    messagebox.showinfo("Success", "User deleted successfully.")
                    load_users()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        btn_frame = tk.Frame(users_win, bg="white")
        btn_frame.pack(pady=10)

        btn_show_selected = tk.Button(
            btn_frame,
            text="Show Selected User",
            width=20,
            command=show_selected_user
        )
        btn_show_selected.pack(side="left", padx=5)

        if current_user["role"] in ("admin", "supervisor"):
            btn_edit_selected = tk.Button(
                btn_frame,
                text="Edit Selected User",
                width=20,
                command=edit_selected_user
            )
            btn_edit_selected.pack(side="left", padx=5)

            btn_delete_selected = tk.Button(
                btn_frame,
                text="Delete Selected User",
                width=20,
                command=delete_selected_user
            )
            btn_delete_selected.pack(side="left", padx=5)

        if current_user["role"] in ("admin", "supervisor"):
            btn_add_user = tk.Button(
                btn_frame,
                text="Add New User",
                width=20,
                command=add_new_user
            )
            btn_add_user.pack(side="left", padx=5)
            
    except Exception as e:
        messagebox.showerror("Error", str(e))

def add_user_to_db(username, password, full_name, role, supervisor_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (username, password, full_name, role, supervisor_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (username, password, full_name, role, supervisor_id))

    conn.commit()
    cur.close()
    conn.close()

def get_supervisors_for_dropdown():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, full_name
        FROM users
        WHERE role IN ('admin', 'supervisor')
        ORDER BY role, id
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def delete_user_from_db(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()

    cur.close()
    conn.close()

def update_user_in_db(user_id, username, full_name, role, supervisor_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET username = %s,
            full_name = %s,
            role = %s,
            supervisor_id = %s
        WHERE id = %s
    """, (username, full_name, role, supervisor_id, user_id))

    conn.commit()
    cur.close()
    conn.close()
        
def get_visible_files(current_user):
    conn = get_connection()
    cur = conn.cursor()

    if current_user["role"] == "admin":
        cur.execute("SELECT * FROM files")

    elif current_user["role"] == "supervisor":
        cur.execute("""
            SELECT * FROM files
            WHERE uploaded_by = %s
            OR uploaded_by IN (
                SELECT id FROM users WHERE supervisor_id = %s
            )
        """, (current_user["id"], current_user["id"]))

    else:
        cur.execute("""
            SELECT * FROM files
            WHERE uploaded_by = %s
        """, (current_user["id"],))
        
    return cur.fetchall()

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
