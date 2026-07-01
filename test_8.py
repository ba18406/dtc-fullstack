from tkinter import filedialog
import shutil
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
import os
import subprocess
import pandas as pd
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

def log_activity(user_id, action_type, target_file=""):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO activity_logs (user_id, action_type, target_file)
        VALUES (%s, %s, %s)
    """, (user_id, action_type, target_file))

    conn.commit()

    cur.close()
    conn.close()

def export_logs_to_excel():
    logs = get_activity_logs()

    if not logs:
        messagebox.showinfo("Export", "No logs to export.")
        return

    df = pd.DataFrame(
        logs,
        columns=["ID", "Username", "Action Type", "Target File", "Log Time"]
    )

    save_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx")]
    )

    if save_path:
        df.to_excel(save_path, index=False)
        messagebox.showinfo("Success", "Logs exported successfully.")

def show_charts_dashboard():
    try:
        logs = get_activity_logs()

        if not logs:
            messagebox.showinfo("Charts", "No activity logs found.")
            return

        df = pd.DataFrame(
            logs,
            columns=["ID", "Username", "Action Type", "Target File", "Log Time"]
        )

        win = tk.Toplevel()
        win.title("Charts Dashboard")
        win.geometry("900x600")

        action_counts = df["Action Type"].value_counts()

        fig, ax = plt.subplots(figsize=(6, 4))
        action_counts.plot(kind="bar", ax=ax)

        ax.set_title("Actions by Type")
        ax.set_xlabel("Action Type")
        ax.set_ylabel("Count")

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    except Exception as e:
        messagebox.showerror("Charts Error", str(e))

def open_dashboard(current_user):
    dashboard = tk.Toplevel()
    dashboard.geometry("1200x500")
    dashboard.configure(bg="#f3f4f6")
    dashboard.title("Data Tracking Center")
    
    # SIDEBAR
    sidebar = tk.Frame(dashboard, bg="#1e293b", width=220)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    
    # MAIN CONTENT
    main_content = tk.Frame(dashboard, bg="white")
    main_content.pack(side="right", fill="both", expand=True)

    welcome_card = tk.Frame(
        main_content,
        bg="#dbeafe",
        height=80
    )

    welcome_card.pack(fill="x", padx=15, pady=10)

    tk.Label(
        welcome_card,
        text=f"Welcome back, {current_user['full_name']}",
        bg="#dbeafe",
        font=("Arial", 16, "bold")
    ).pack(pady=20)

    # TITLE
    lbl_title = tk.Label(
        main_content,
        text="Dashboard",
        font=("Arial", 20, "bold"),
        bg="white"
    )
    lbl_title.pack(pady=10)

    # USER INFO
    lbl_info = tk.Label(
        main_content,
        text=f"Welcome: {current_user['username']} | Role: {current_user['role']}",
        font=("Arial", 12),
        bg="white"
    )
    lbl_info.pack(pady=5)

    # RECENT UPLOADS FRAME
    recent_frame = tk.Frame(main_content, bg="white")
    recent_frame.pack(fill="both", expand=True, padx=15, pady=10)

    tk.Label(
        recent_frame,
        text="Recent Uploads",
        font=("Arial", 13, "bold"),
        bg="white"
    ).pack(anchor="w")

    recent_tree = ttk.Treeview(
        recent_frame,
        columns=("file_name", "username", "uploaded_date"),
        show="headings",
        height=8
    )

    recent_scroll = ttk.Scrollbar(
        recent_frame,
        orient="vertical",
        command=recent_tree.yview
    )

    recent_tree.configure(
        yscrollcommand=recent_scroll.set
    )

    recent_scroll.pack(side="right", fill="y")

    def create_sidebar_button(text, command):
        btn = tk.Button(
            sidebar,
            text=text,
            command=command,
            bg="#334155",
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            relief="flat",
            font=("Arial", 11),
            width=20,
            height=2
        )

        btn.pack(pady=5)
        
    stats = get_dashboard_statistics(current_user)

    cards_frame = tk.Frame(dashboard, bg="white")
    cards_frame.pack(pady=15)

    # Total Users Card
    card_users = tk.Frame(cards_frame, bg="#dbeafe", width=150, height=80)
    card_users.pack(side="left", padx=10)

    tk.Label(
        card_users,
        text="Total Users",
        bg="#dbeafe",
        font=("Arial", 11, "bold")
    ).pack(pady=5)

    tk.Label(
        card_users,
        text=str(stats["total_users"]),
        bg="#dbeafe",
        font=("Arial", 20, "bold")
    ).pack()
    card_users.pack_propagate(False)

    # Total Files Card
    card_files = tk.Frame(cards_frame, bg="#dcfce7", width=150, height=80)
    card_files.pack(side="left", padx=10)

    tk.Label(
        card_files,
        text="Total Files",
        bg="#dcfce7",
        font=("Arial", 11, "bold")
    ).pack(pady=5)

    tk.Label(
        card_files,
        text=str(stats["total_files"]),
        bg="#dcfce7",
        font=("Arial", 20, "bold")
    ).pack()
    card_files.pack_propagate(False)

    # My Files Card
    card_myfiles = tk.Frame(cards_frame, bg="#fef3c7", width=150, height=80)
    card_myfiles.pack(side="left", padx=10)

    tk.Label(
        card_myfiles,
        text="My Files",
        bg="#fef3c7",
        font=("Arial", 11, "bold")
    ).pack(pady=5)

    tk.Label(
        card_myfiles,
        text=str(stats["my_files"]),
        bg="#fef3c7",
        font=("Arial", 20, "bold")
    ).pack()
    card_myfiles.pack_propagate(False)

    recent_frame = tk.Frame(dashboard, bg="white")
    recent_frame.pack(fill="both", expand=True, padx=15, pady=10)

    tk.Label(
        recent_frame,
        text="Recent Uploads",
        font=("Arial", 13, "bold"),
        bg="white"
    ).pack(anchor="w")

    recent_tree = ttk.Treeview(
        recent_frame,
        columns=("file_name", "username", "uploaded_date"),
        show="headings",
        height=6
    )

    recent_tree.pack(fill="both", expand=True, pady=5)

    recent_tree.heading("file_name", text="File Name")
    recent_tree.heading("username", text="Uploaded By")
    recent_tree.heading("uploaded_date", text="Upload Date")

    recent_tree.column("file_name", width=250)
    recent_tree.column("username", width=150, anchor="center")
    recent_tree.column("uploaded_date", width=180, anchor="center")

    recent_uploads = get_recent_uploads()

    for row in recent_uploads:
        recent_tree.insert("", tk.END, values=row)
    
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

    btn_upload = tk.Button(
        dashboard,
        text="Upload File",
        width=20,
        command=lambda: upload_file(current_user)
    )
    btn_upload.pack(pady=5)

    btn_view_files = tk.Button(
        dashboard,
        text="View Files",
        width=20,
        command=lambda: show_files_dashboard(current_user)
    )
    btn_view_files.pack(pady=5)

    create_sidebar_button(
        "Users",
        lambda: open_users_window(current_user)
    )

    create_sidebar_button(
        "Files",
        lambda: show_files_dashboard(current_user)
    )

    if current_user["role"] == "admin":

        create_sidebar_button(
            "Activity Logs",
            show_logs_dashboard
        )

        create_sidebar_button(
            "Charts Dashboard",
            show_charts_dashboard
        )

    def logout():
        dashboard.destroy()
        root.deiconify()

    create_sidebar_button("Logout", logout)
                
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
            root.withdraw()
            open_dashboard(current_user)

            log_activity(
                current_user["id"],
                "LOGIN",
                username
            )

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

UPLOAD_FOLDER = "uploads"

def upload_file(current_user):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    file_name = os.path.basename(file_path)
    save_path = os.path.abspath(
        os.path.join(UPLOAD_FOLDER, file_name)
    )
    shutil.copy(file_path, save_path)

    conn = get_connection()
    cur = conn.cursor()

    file_type = os.path.splitext(file_name)[1].lower()

    cur.execute("""
        INSERT INTO files (file_name, file_type, file_path, uploaded_by)
        VALUES (%s, %s, %s, %s)
    """, (file_name, file_type, save_path, current_user["id"]))

    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "File uploaded successfully")

    log_activity(
        current_user["id"],
        "UPLOAD",
        file_name
    )
    
def get_visible_files(current_user):
    conn = get_connection()
    cur = conn.cursor()

    if current_user["role"] == "admin":
        cur.execute("""
            SELECT f.id, f.file_name, f.file_type, f.file_path,
                   u.username AS uploaded_by,
                   f.uploaded_date
            FROM files f
            JOIN users u ON f.uploaded_by = u.id
            ORDER BY f.uploaded_date DESC
        """)

    elif current_user["role"] == "supervisor":
        cur.execute("""
            SELECT f.id, f.file_name, f.file_type, f.file_path,
                   u.username AS uploaded_by,
                   f.uploaded_date
            FROM files f
            JOIN users u ON f.uploaded_by = u.id
            WHERE f.uploaded_by = %s
               OR f.uploaded_by IN (
                    SELECT id FROM users WHERE supervisor_id = %s
               )
            ORDER BY f.uploaded_date DESC
        """, (current_user["id"], current_user["id"]))

    else:
        cur.execute("""
            SELECT f.id, f.file_name, f.file_type, f.file_path,
                   u.username AS uploaded_by,
                   f.uploaded_date
            FROM files f
            JOIN users u ON f.uploaded_by = u.id
            WHERE f.uploaded_by = %s
            ORDER BY f.uploaded_date DESC
        """, (current_user["id"],))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def show_files_dashboard(current_user):
    try:
        files = get_visible_files(current_user)

        win = tk.Toplevel()
        win.title("Files Dashboard")
        win.geometry("900x500")
        win.configure(bg="white")

        tk.Label(
            win,
            text="Files Dashboard",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=10)

        frame_table = tk.Frame(win, bg="white")
        frame_table.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "file_name", "file_type", "file_path", "uploaded_by", "uploaded_date")

        search_var = tk.StringVar()

        search_frame = tk.Frame(win, bg="white")
        search_frame.pack(fill="x", padx=10)

        tk.Label(search_frame, text="Search:", bg="white").pack(side="left")

        search_entry = tk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side="left", padx=5)

        tree = ttk.Treeview(frame_table, columns=columns, show="headings")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())

        tree.column("id", width=50, anchor="center")
        tree.column("file_name", width=180)
        tree.column("file_type", width=100, anchor="center")
        tree.column("file_path", width=250)
        tree.column("uploaded_by", width=120, anchor="center")
        tree.column("uploaded_date", width=150, anchor="center")

        for row in files:
            tree.insert("", tk.END, values=row)

        if not files:
            tree.insert("", tk.END, values=("", "No files found", "", "", "", ""))

        def open_selected_file(event=None):
            selected = tree.selection()
            if not selected:
                return

            values = tree.item(selected[0], "values")
            file_path = os.path.abspath(values[3])

            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"File not found:\n{file_path}")
                return

            try:
                ext = os.path.splitext(file_path)[1].lower()

                if ext == ".xlsx":
                    preview_excel_file(file_path)

                elif ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
                    preview_image_file(file_path)

                else:
                    os.startfile(file_path)

            except Exception as e:
                messagebox.showerror("Open Error", str(e))
                
        def download_file():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Select a file first.")
                return

            values = tree.item(selected[0], "values")
            source_path = values[3]
            file_name = values[1]

            if not os.path.exists(source_path):
                messagebox.showerror("Error", "File not found.")
                return

            save_path = filedialog.asksaveasfilename(initialfile=file_name)

            if save_path:
                shutil.copy(source_path, save_path)
                messagebox.showinfo("Success", "File downloaded.")

            log_activity(
                current_user["id"],
                "DOWNLOAD",
                file_name
            )

        def delete_file():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Select a file first.")
                return

            values = tree.item(selected[0], "values")
            file_id = values[0]
            uploaded_by = values[4]

            if current_user["role"] != "admin" and uploaded_by != current_user["username"]:
                messagebox.showerror("Permission Denied", "You cannot delete this file.")
                return

            confirm = messagebox.askyesno("Confirm", "Delete this file?")
            if not confirm:
                return

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("DELETE FROM files WHERE id = %s", (file_id,))
            conn.commit()

            cur.close()
            conn.close()

            log_activity(
                current_user["id"],
                "DELETE",
                values[1]
            )

            tree.delete(selected[0])
            messagebox.showinfo("Success", "File deleted.")

        tree.bind("<Double-1>", open_selected_file)

        btn_frame = tk.Frame(win, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Download",
            width=15,
            command=download_file
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Delete",
            width=15,
            command=delete_file
        ).pack(side="left", padx=5)

        def search_files():
            keyword = search_var.get().lower().strip()

            for item in tree.get_children():
                tree.delete(item)

            filtered = []

            for row in files:
                row_text = " ".join([str(x).lower() for x in row])

                if keyword in row_text:
                    filtered.append(row)

            if filtered:
                for row in filtered:
                    tree.insert("", tk.END, values=row)
            else:
                tree.insert("", tk.END, values=("", "No matching files", "", "", "", ""))

        tk.Button(
            search_frame,
            text="Search",
            command=search_files
        ).pack(side="left", padx=5)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def preview_image_file(file_path):
    win = tk.Toplevel()
    win.title("Image Preview")
    win.geometry("800x600")

    img = Image.open(file_path)
    img.thumbnail((760, 540))

    photo = ImageTk.PhotoImage(img)

    lbl = tk.Label(win, image=photo)
    lbl.image = photo
    lbl.pack(expand=True)
    
def get_dashboard_statistics(current_user):
    conn = get_connection()
    cur = conn.cursor()

    stats = {}

    # Total users
    cur.execute("SELECT COUNT(*) FROM users")
    stats["total_users"] = cur.fetchone()[0]

    # Total files
    cur.execute("SELECT COUNT(*) FROM files")
    stats["total_files"] = cur.fetchone()[0]

    # My files
    cur.execute("""
        SELECT COUNT(*)
        FROM files
        WHERE uploaded_by = %s
    """, (current_user["id"],))

    stats["my_files"] = cur.fetchone()[0]

    cur.close()
    conn.close()

    return stats

def get_recent_uploads(limit=5):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT f.file_name,
               u.username,
               f.uploaded_date
        FROM files f
        JOIN users u ON f.uploaded_by = u.id
        ORDER BY f.uploaded_date DESC
        LIMIT %s
    """, (limit,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

def preview_excel_file(file_path):
    try:
        df = pd.read_excel(file_path)

        preview_win = tk.Toplevel()
        preview_win.title("Excel Preview")
        preview_win.geometry("1000x600")

        frame = tk.Frame(preview_win)
        frame.pack(fill="both", expand=True)

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        tree = ttk.Treeview(frame)
        tree.grid(row=0, column=0, sticky="nsew")

        y_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        y_scrollbar.grid(row=0, column=1, sticky="ns")

        x_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        tree.configure(
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )

        tree["columns"] = list(df.columns)
        tree["show"] = "headings"

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, stretch=False)

        for _, row in df.head(100).iterrows():
            tree.insert("", tk.END, values=list(row))

    except Exception as e:
        messagebox.showerror("Preview Error", str(e))

def get_activity_logs():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            a.id,
            u.username,
            a.action_type,
            a.target_file,
            a.log_time
        FROM activity_logs a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.log_time DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

def show_logs_dashboard():
    try:
        logs = get_activity_logs()

        win = tk.Toplevel()
        win.title("Activity Logs")
        win.geometry("950x500")
        win.configure(bg="white")

        tk.Label(
            win,
            text="System Activity Logs",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=10)

        frame = tk.Frame(win, bg="white")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "username", "action_type", "target_file", "log_time")

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")

        tree.configure(yscrollcommand=scrollbar.set)

        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())

        tree.column("id", width=60, anchor="center")
        tree.column("username", width=140, anchor="center")
        tree.column("action_type", width=140, anchor="center")
        tree.column("target_file", width=260)
        tree.column("log_time", width=220, anchor="center")

        for row in logs:
            tree.insert("", tk.END, values=row)

        tk.Button(
            win,
            text="Export to Excel",
            width=20,
            command=export_logs_to_excel
        ).pack(pady=5)

    except Exception as e:
        messagebox.showerror("Logs Error", str(e))
        
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
