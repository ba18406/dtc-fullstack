import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import pandas as pd
import platform
import subprocess
from docx import Document
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import tempfile

API_BASE_URL = "https://dtc-api.onrender.com"

def open_file_cross_platform(file_path):

    system_name = platform.system()

    try:
        if system_name == "Windows":
            os.startfile(file_path)
            
        elif system_name == "Darwin":  # macOS
            subprocess.run(["open", file_path])

        elif system_name == "Linux":
            subprocess.run(["xdg-open", file_path])

        else:
            messagebox.showerror(
                "Unsupported System",
                f"System not supported: {system_name}"
            )

    except Exception as e:
        messagebox.showerror(
            "Open Error",
            str(e)
        )
        
def handle_login():
    username = user_name_entry.get().strip()
    password = password_entry.get().strip()

    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            json={
                "username": username,
                "password": password
            }
        )

        result = response.json()

        if result["success"]:

            current_user = result["user"]

            root.withdraw()

            open_dashboard(current_user)

            log_activity(
                current_user["id"],
                "LOGIN",
                username
            )

        else:
            messagebox.showerror(
                "Login Failed",
                result["message"]
            )

    except Exception as e:
        messagebox.showerror(
            "API Error",
            str(e)
        )

def get_visible_users(current_user):
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/visible/{current_user['id']}/{current_user['role']}"
        )

        result = response.json()

        if result["success"]:
            users = []

            for user in result["users"]:
                users.append((
                    user["id"],
                    user["username"],
                    user["full_name"],
                    user["role"],
                    user["supervisor_id"]
                ))

            return users

        else:
            messagebox.showerror("API Error", result["error"])
            return []

    except Exception as e:
        messagebox.showerror("API Error", str(e))
        return []

def get_supervisors_for_dropdown():
    try:
        response = requests.get(f"{API_BASE_URL}/supervisors")
        result = response.json()

        if result["success"]:
            return [
                (s["id"], s["username"], s["full_name"])
                for s in result["supervisors"]
            ]

        messagebox.showerror("API Error", result["error"])
        return []

    except Exception as e:
        messagebox.showerror("API Error", str(e))
        return []

def add_user_to_db(username, password, full_name, role, supervisor_id):
    response = requests.post(
        f"{API_BASE_URL}/users/add",
        json={
            "username": username,
            "password": password,
            "full_name": full_name,
            "role": role,
            "supervisor_id": supervisor_id
        }
    )

    result = response.json()

    if not result["success"]:
        raise Exception(result["error"])

def update_user_in_db(user_id, username, password, full_name, role, supervisor_id):
    response = requests.post(
        f"{API_BASE_URL}/users/update",
        json={
            "user_id": user_id,
            "username": username,
            "password": password,
            "full_name": full_name,
            "role": role,
            "supervisor_id": supervisor_id
        }
    )

    result = response.json()

    if not result["success"]:
        raise Exception(result["error"])

def delete_user_from_db(user_id):
    response = requests.delete(
        f"{API_BASE_URL}/users/delete/{user_id}"
    )

    result = response.json()

    if not result["success"]:
        raise Exception(result["error"])

def log_activity(user_id, action_type, target_file=""):
    response = requests.post(
        f"{API_BASE_URL}/logs/add",
        json={
            "user_id": user_id,
            "action_type": action_type,
            "target_file": target_file
        }
    )

    result = response.json()

    if not result["success"]:
        raise Exception(result["error"])

def get_activity_logs():
    response = requests.get(
        f"{API_BASE_URL}/logs"
    )

    result = response.json()

    if result["success"]:
        return [
            (
                log["id"],
                log["username"],
                log["action_type"],
                log["target_file"],
                log["log_time"]
            )
            for log in result["logs"]
        ]

    raise Exception(result["error"])

def get_dashboard_statistics(current_user):
    response = requests.get(
        f"{API_BASE_URL}/dashboard/stats/{current_user['id']}"
    )

    result = response.json()

    if result["success"]:
        return result["stats"]

    raise Exception(result["error"])

def get_recent_uploads(limit=5):
    response = requests.get(
        f"{API_BASE_URL}/uploads/recent?limit={limit}"
    )

    result = response.json()

    if result["success"]:
        return [
            (
                upload["file_name"],
                upload["username"],
                upload["uploaded_at"]
            )
            for upload in result["uploads"]
        ]

    raise Exception(result["error"])

def get_visible_files(current_user):
    try:
        response = requests.get(
            f"{API_BASE_URL}/files/visible/{current_user['id']}/{current_user['role']}/{current_user['username']}"
        )

        result = response.json()

        if result["success"]:
            return [
                (
                    f["id"],
                    f["file_name"],
                    f["file_type"],
                    f["file_path"],
                    f["uploaded_by"],
                    f["uploaded_at"]
                )
                for f in result["files"]
            ]

        raise Exception(result["error"])

    except Exception as e:
        messagebox.showerror("API Error", str(e))
        return []

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

        columns = ("id", "file_name", "file_type", "file_path", "uploaded_by", "uploaded_at")

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
        tree.column("uploaded_at", width=150, anchor="center")

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
                    ext = os.path.splitext(file_path)[1].lower()

                    if ext in (".xlsx", ".xls"):
                        preview_excel(file_path)
                    else:
                        download_url = f"{API_BASE_URL}/files/download/{file_id}"

                        response = requests.get(download_url)

                        save_path = filedialog.asksaveasfilename(
                            initialfile=file_name
                        )

                        with open(save_path, "wb") as f:
                            f.write(response.content)

                        open_file_cross_platform(save_path)                        

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

            confirm = messagebox.askyesno("Confirm", "Delete this file?")
            if not confirm:
                return

            try:
                response = requests.delete(
                    f"{API_BASE_URL}/files/delete/{file_id}/{current_user['id']}/{current_user['role']}/{current_user['username']}"
                )

                result = response.json()

                if result["success"]:
                    log_activity(
                        current_user["id"],
                        "DELETE",
                        result["file_name"]
                    )

                    tree.delete(selected[0])
                    messagebox.showinfo("Success", result["message"])
                else:
                    messagebox.showerror("Error", result["error"])

            except Exception as e:
                messagebox.showerror("API Error", str(e))

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

def upload_file(current_user):
    file_path = filedialog.askopenfilename()

    if not file_path:
        return

    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/files/upload",
                data={
                    "uploaded_by": current_user["id"]
                },
                files={
                    "file": f
                }
            )

        result = response.json()

        if result["success"]:
            messagebox.showinfo("Success", result["message"])

            log_activity(
                current_user["id"],
                "UPLOAD",
                result["file_name"]
            )

        else:
            messagebox.showerror("Upload Failed", result["error"])

    except Exception as e:
        messagebox.showerror("API Error", str(e))

def clear_main_content(main_content):
    for widget in main_content.winfo_children():
        widget.destroy()

def open_dashboard(current_user):
    dashboard = tk.Toplevel()
    dashboard.title("Data Tracking Center")
    dashboard.geometry("1200x700")
    dashboard.configure(bg="#f3f4f6")

    root.withdraw()

    # Sidebar
    sidebar = tk.Frame(dashboard, bg="#1e293b", width=230)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    # Main content
    main_content = tk.Frame(dashboard, bg="#f8fafc")
    main_content.pack(side="right", fill="both", expand=True)

    tk.Label(
        sidebar,
        text="DTC System",
        bg="#1e293b",
        fg="white",
        font=("Arial", 18, "bold")
    ).pack(pady=25)

    tk.Label(
        sidebar,
        text=f"{current_user['full_name']}\n({current_user['role']})",
        bg="#1e293b",
        fg="#cbd5e1",
        font=("Arial", 10)
    ).pack(pady=10)

    def sidebar_button(text, command):
        btn = tk.Button(
            sidebar,
            text=text,
            command=command,
            bg="#334155",
            fg="black",
            activebackground="#475569",
            activeforeground="white",
            relief="flat",
            font=("Arial", 11),
            width=22,
            height=2
        )
        btn.pack(pady=5)

    def show_home_page():
        clear_main_content(main_content)

        tk.Label(
            main_content,
            text="Dashboard",
            bg="#f8fafc",
            font=("Arial", 22, "bold")
        ).pack(anchor="w", padx=25, pady=20)

        stats = get_dashboard_statistics(current_user)

        cards_frame = tk.Frame(main_content, bg="#f8fafc")
        cards_frame.pack(fill="x", padx=25, pady=10)

        create_card(cards_frame, "Total Users", stats["total_users"], "#dbeafe")
        create_card(cards_frame, "Total Files", stats["total_files"], "#dcfce7")
        create_card(cards_frame, "My Files", stats["my_files"], "#fef3c7")

        show_recent_uploads_section(main_content)

    def logout():
        dashboard.destroy()
        root.deiconify()

    sidebar_button("Dashboard", show_home_page)
    sidebar_button("Users", lambda: show_users_page(main_content, current_user))
    sidebar_button("Files", lambda: show_files_page(main_content, current_user))

    if current_user["role"] == "admin":
        sidebar_button("Activity Logs", lambda: show_logs_page(main_content))

    sidebar_button("Logout", logout)

    show_home_page()

def create_card(parent, title, value, bg_color):
    card = tk.Frame(parent, bg=bg_color, width=180, height=90)
    card.pack(side="left", padx=10)
    card.pack_propagate(False)

    tk.Label(
        card,
        text=title,
        bg=bg_color,
        font=("Arial", 11, "bold")
    ).pack(pady=8)

    tk.Label(
        card,
        text=str(value),
        bg=bg_color,
        font=("Arial", 22, "bold")
    ).pack()

def show_recent_uploads_section(parent):
    frame = tk.Frame(parent, bg="white")
    frame.pack(fill="both", expand=True, padx=25, pady=20)

    tk.Label(
        frame,
        text="Recent Uploads",
        bg="white",
        font=("Arial", 14, "bold")
    ).pack(anchor="w", padx=10, pady=10)

    columns = ("file_name", "username", "uploaded_at")

    tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    tree.heading("file_name", text="File Name")
    tree.heading("username", text="Uploaded By")
    tree.heading("uploaded_at", text="Upload Date")

    for row in get_recent_uploads():
        tree.insert("", tk.END, values=row)

def preview_file_inside_tkinter(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext in (".xlsx", ".xls"):
        preview_excel(file_path)

    elif ext == ".docx":
        preview_docx(file_path)

    elif ext in (".txt", ".csv"):
        preview_text(file_path)

    elif ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
        preview_image(file_path)

    elif ext == ".pdf":
        preview_pdf(file_path)

    else:
        messagebox.showinfo(
            "Preview",
            "This file type cannot be previewed inside Tkinter yet."
        )

def preview_excel(file_path):

    df = pd.read_excel(file_path)

    preview_win = tk.Toplevel()
    preview_win.title("Excel Preview")
    preview_win.geometry("1000x600")

    frame = tk.Frame(preview_win)
    frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame)
    tree.pack(side="left", fill="both", expand=True)

    y_scroll = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )

    y_scroll.pack(side="right", fill="y")

    x_scroll = ttk.Scrollbar(
        preview_win,
        orient="horizontal",
        command=tree.xview
    )

    x_scroll.pack(fill="x")

    tree.configure(
        yscrollcommand=y_scroll.set,
        xscrollcommand=x_scroll.set
    )

    tree["columns"] = list(df.columns)
    tree["show"] = "headings"

    for col in df.columns:
        tree.heading(col, text=str(col))
        tree.column(col, width=150)

    for _, row in df.head(300).iterrows():
        tree.insert("", tk.END, values=list(row))

def preview_docx(file_path):
    win = tk.Toplevel()
    win.title("Word Preview")
    win.geometry("900x600")

    text = tk.Text(win, wrap="word")
    text.pack(fill="both", expand=True)

    doc = Document(file_path)

    for para in doc.paragraphs:
        text.insert("end", para.text + "\n\n")

def preview_text(file_path):
    win = tk.Toplevel()
    win.title("Text Preview")
    win.geometry("900x600")

    text = tk.Text(win, wrap="word")
    text.pack(fill="both", expand=True)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text.insert("end", f.read())

def preview_image(file_path):
    win = tk.Toplevel()
    win.title("Image Preview")
    win.geometry("900x600")

    img = Image.open(file_path)
    img.thumbnail((850, 550))

    photo = ImageTk.PhotoImage(img)

    lbl = tk.Label(win, image=photo)
    lbl.image = photo
    lbl.pack(expand=True)

def preview_pdf(file_path):
    win = tk.Toplevel()
    win.title("PDF Preview")
    win.geometry("900x600")

    doc = fitz.open(file_path)
    page = doc[0]
    pix = page.get_pixmap()

    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.thumbnail((850, 550))

    photo = ImageTk.PhotoImage(img)

    lbl = tk.Label(win, image=photo)
    lbl.image = photo
    lbl.pack(expand=True)

def show_users_page(main_content, current_user):
    clear_main_content(main_content)

    tk.Label(
        main_content,
        text="Users Management",
        bg="#f8fafc",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=25, pady=20)

    table_frame = tk.Frame(main_content, bg="white")
    table_frame.pack(fill="both", expand=True, padx=25, pady=10)

    columns = ("id", "username", "full_name", "role", "supervisor_id")

    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())

    tree.column("id", width=60, anchor="center")
    tree.column("username", width=150, anchor="center")
    tree.column("full_name", width=220)
    tree.column("role", width=120, anchor="center")
    tree.column("supervisor_id", width=120, anchor="center")

    for row in get_visible_users(current_user):
        tree.insert("", tk.END, values=row)

    def edit_selected_user():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user first.")
            return

        selected_user = tree.item(selected[0], "values")
        show_edit_user_form(main_content, current_user, selected_user)

    def delete_selected_user():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user first.")
            return

        values = tree.item(selected[0], "values")
        user_id = int(values[0])
        username = values[1]

        if user_id == current_user["id"]:
            messagebox.showwarning("Warning", "You cannot delete your own account.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete user: {username}?"
        )

        if not confirm:
            return

        try:
            delete_user_from_db(user_id)
            messagebox.showinfo("Success", "User deleted successfully.")
            show_users_page(main_content, current_user)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn_frame = tk.Frame(main_content, bg="#f8fafc")
    btn_frame.pack(fill="x", padx=25, pady=10)

    if current_user["role"] in ("admin", "supervisor"):
        tk.Button(
            btn_frame,
            text="Add User",
            width=15,
            command=lambda: show_add_user_form(main_content, current_user)
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Edit User",
            width=15,
            command=edit_selected_user
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Delete User",
            width=15,
            command=delete_selected_user
        ).pack(side="left", padx=5)

def show_add_user_form(main_content, current_user):
    clear_main_content(main_content)

    tk.Label(
        main_content,
        text="Add New User",
        bg="#f8fafc",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=25, pady=20)

    form = tk.Frame(main_content, bg="white")
    form.pack(padx=25, pady=10, anchor="w")

    tk.Label(form, text="Username", bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_username = tk.Entry(form, width=35)
    entry_username.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(form, text="Password", bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    entry_password = tk.Entry(form, width=35, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(form, text="Full Name", bg="white").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    entry_full_name = tk.Entry(form, width=35)
    entry_full_name.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(form, text="Role", bg="white").grid(row=3, column=0, padx=10, pady=10, sticky="w")

    if current_user["role"] == "admin":
        role_values = ["admin", "supervisor", "user"]
    else:
        role_values = ["user"]

    role_var = tk.StringVar(value=role_values[0])

    combo_role = ttk.Combobox(
        form,
        textvariable=role_var,
        values=role_values,
        state="readonly",
        width=32
    )
    combo_role.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(form, text="Supervisor", bg="white").grid(row=4, column=0, padx=10, pady=10, sticky="w")

    supervisors = get_supervisors_for_dropdown()
    supervisor_options = ["None"]
    supervisor_map = {"None": None}

    for sup_id, sup_username, sup_full_name in supervisors:
        label = f"{sup_id} - {sup_username} - {sup_full_name}"
        supervisor_options.append(label)
        supervisor_map[label] = sup_id

    supervisor_var = tk.StringVar(value="None")

    combo_supervisor = ttk.Combobox(
        form,
        textvariable=supervisor_var,
        values=supervisor_options,
        state="readonly",
        width=32
    )
    combo_supervisor.grid(row=4, column=1, padx=10, pady=10)

    if current_user["role"] == "supervisor":
        label = f"{current_user['id']} - {current_user['username']} - {current_user['full_name']}"
        supervisor_var.set(label)
        combo_supervisor["values"] = [label]
        supervisor_map[label] = current_user["id"]

    def save_user():
        username = entry_username.get().strip()
        password = entry_password.get().strip()
        full_name = entry_full_name.get().strip()
        role = role_var.get()
        supervisor_id = supervisor_map.get(supervisor_var.get())

        if not username or not password or not full_name:
            messagebox.showwarning("Warning", "Please fill all required fields.")
            return

        if role == "admin":
            supervisor_id = None
        elif supervisor_id is None:
            messagebox.showwarning("Warning", "Please select a supervisor.")
            return

        try:
            add_user_to_db(username, password, full_name, role, supervisor_id)
            messagebox.showinfo("Success", "User added successfully.")
            show_users_page(main_content, current_user)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(
        form,
        text="Save User",
        width=20,
        command=save_user
    ).grid(row=5, column=1, padx=10, pady=20, sticky="e")

    tk.Button(
        form,
        text="Back",
        width=15,
        command=lambda: show_users_page(main_content, current_user)
    ).grid(row=5, column=0, padx=10, pady=20, sticky="w")

def show_edit_user_form(main_content, current_user, selected_user):
    clear_main_content(main_content)

    user_id, username, full_name, role, supervisor_id = selected_user

    tk.Label(
        main_content,
        text="Edit User",
        bg="#f8fafc",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=25, pady=20)

    form = tk.Frame(main_content, bg="white")
    form.pack(padx=25, pady=10, anchor="w")

    tk.Label(form, text="Username", bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_username = tk.Entry(form, width=35)
    entry_username.grid(row=0, column=1, padx=10, pady=10)
    entry_username.insert(0, username)

    tk.Label(form, text="New Password", bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    entry_password = tk.Entry(form, width=35, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(form, text="Full Name", bg="white").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    entry_full_name = tk.Entry(form, width=35)
    entry_full_name.grid(row=2, column=1, padx=10, pady=10)
    entry_full_name.insert(0, full_name)

    tk.Label(form, text="Role", bg="white").grid(row=2, column=0, padx=10, pady=10, sticky="w")

    role_values = ["admin", "supervisor", "user"] if current_user["role"] == "admin" else ["user"]
    role_var = tk.StringVar(value=role)

    combo_role = ttk.Combobox(form, textvariable=role_var, values=role_values, state="readonly", width=32)
    combo_role.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(form, text="Supervisor", bg="white").grid(row=3, column=0, padx=10, pady=10, sticky="w")

    supervisors = get_supervisors_for_dropdown()
    supervisor_options = ["None"]
    supervisor_map = {"None": None}

    for sup_id, sup_username, sup_full_name in supervisors:
        label = f"{sup_id} - {sup_username} - {sup_full_name}"
        supervisor_options.append(label)
        supervisor_map[label] = sup_id

    current_label = "None"
    for label, sid in supervisor_map.items():
        if str(sid) == str(supervisor_id):
            current_label = label
            break

    supervisor_var = tk.StringVar(value=current_label)

    combo_supervisor = ttk.Combobox(
        form,
        textvariable=supervisor_var,
        values=supervisor_options,
        state="readonly",
        width=32
    )
    combo_supervisor.grid(row=4, column=1, padx=10, pady=10)

    def save_changes():
        new_username = entry_username.get().strip()
        new_password = entry_password.get().strip()
        new_full_name = entry_full_name.get().strip()
        new_role = role_var.get()
        new_supervisor_id = supervisor_map.get(supervisor_var.get())

        if not new_username or not new_full_name:
            messagebox.showwarning("Warning", "Please fill all required fields.")
            return

        if new_role == "admin":
            new_supervisor_id = None
        elif new_supervisor_id is None:
            messagebox.showwarning("Warning", "Please select a supervisor.")
            return

        try:
            update_user_in_db(
                int(user_id),
                new_username,
                new_password if new_password else None,
                new_full_name,
                new_role,
                new_supervisor_id
            )

            messagebox.showinfo("Success", "User updated successfully.")
            show_users_page(main_content, current_user)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(
        form,
        text="Save Changes",
        width=20,
        command=save_changes
    ).grid(row=5, column=1, padx=10, pady=20, sticky="e")

    tk.Button(
        form,
        text="Back",
        width=15,
        command=lambda: show_users_page(main_content, current_user)
    ).grid(row=5, column=0, padx=10, pady=20, sticky="w")

def show_files_page(main_content, current_user):
    clear_main_content(main_content)

    tk.Label(
        main_content,
        text="Files Management",
        bg="#f8fafc",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=25, pady=20)

    top_bar = tk.Frame(main_content, bg="#f8fafc")
    top_bar.pack(fill="x", padx=25)

    search_var = tk.StringVar()

    tk.Label(
        top_bar,
        text="Search:",
        bg="#f8fafc",
        font=("Arial", 11)
    ).pack(side="left")

    search_entry = tk.Entry(
        top_bar,
        textvariable=search_var,
        width=40
    )
    search_entry.pack(side="left", padx=8)

    table_frame = tk.Frame(main_content, bg="white")
    table_frame.pack(fill="both", expand=True, padx=25, pady=15)

    columns = (
        "id",
        "file_name",
        "file_type",
        "file_path",
        "uploaded_by",
        "uploaded_at"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    scrollbar.pack(side="right", fill="y")

    tree.configure(yscrollcommand=scrollbar.set)

    headings = {
        "id": "ID",
        "file_name": "File Name",
        "file_type": "Type",
        "file_path": "Path",
        "uploaded_by": "Uploaded By",
        "uploaded_at": "Upload Date"
    }

    for col in columns:
        tree.heading(col, text=headings[col])

    tree.column("id", width=60, anchor="center")
    tree.column("file_name", width=220)
    tree.column("file_type", width=100, anchor="center")
    tree.column("file_path", width=300)
    tree.column("uploaded_by", width=140, anchor="center")
    tree.column("uploaded_at", width=180, anchor="center")

    files = get_visible_files(current_user)

    for row in files:
        tree.insert("", tk.END, values=row)

    def refresh_files():
        for item in tree.get_children():
            tree.delete(item)

        refreshed_files = get_visible_files(current_user)

        for row in refreshed_files:
            tree.insert("", tk.END, values=row)

    def search_files():
        keyword = search_var.get().lower().strip()

        for item in tree.get_children():
            tree.delete(item)

        filtered = []

        for row in files:
            row_text = " ".join([str(x).lower() for x in row])

            if keyword in row_text:
                filtered.append(row)

        for row in filtered:
            tree.insert("", tk.END, values=row)

    def download_selected_file():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning("Warning", "Please select a file first.")
            return

        values = tree.item(selected[0], "values")
        file_id = values[0]
        file_name = values[1]

        save_path = filedialog.asksaveasfilename(initialfile=file_name)

        if not save_path:
            return

        try:
            response = requests.get(
                f"{API_BASE_URL}/files/download/{file_id}"
            )

            if response.status_code != 200:
                messagebox.showerror("Download Error", response.text)
                return

            if len(response.content) < 100:
                messagebox.showerror(
                    "Download Error",
                    "The downloaded file is too small. Server probably returned an error."
                )
                return

            with open(save_path, "wb") as f:
                f.write(response.content)

            messagebox.showinfo("Success", "File downloaded successfully.")

            log_activity(
                current_user["id"],
                "DOWNLOAD",
                file_name
            )

        except Exception as e:
            messagebox.showerror("API Error", str(e))
            
    def download_to_temp(file_id, file_name):
        response = requests.get(f"{API_BASE_URL}/files/download/{file_id}")

        if response.status_code != 200:
            raise Exception(response.text)

        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file_name)

        with open(temp_path, "wb") as f:
            f.write(response.content)

        return temp_path

    def open_selected_file(event=None):
        selected = tree.selection()
        if not selected:
            return

        values = tree.item(selected[0], "values")
        file_id = values[0]
        file_name = values[1]

        try:
            temp_path = download_to_temp(file_id, file_name)
            preview_file_inside_tkinter(temp_path)

        except Exception as e:
            messagebox.showerror("Preview Error", str(e))
            
    tk.Button(
        top_bar,
        text="Search",
        command=search_files
    ).pack(side="left", padx=5)

    btn_frame = tk.Frame(main_content, bg="#f8fafc")
    btn_frame.pack(fill="x", padx=25, pady=10)

    tk.Button(
        btn_frame,
        text="Upload File",
        width=15,
        command=lambda: [
            upload_file(current_user),
            refresh_files()
        ]
    ).pack(side="left", padx=5)

    tk.Button(
        btn_frame,
        text="Download File",
        width=15,
        command=download_selected_file
    ).pack(side="left", padx=5)

    tree.bind("<Double-1>", open_selected_file)

    def delete_selected_file():
        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a file first."
            )
            return

        values = tree.item(selected[0], "values")
        file_id = values[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete file: {values[1]}?"
        )

        if not confirm:
            return

        try:
            response = requests.delete(
                f"{API_BASE_URL}/files/delete/{file_id}/{current_user['id']}/{current_user['role']}/{current_user['username']}"
            )

            result = response.json()

            if result["success"]:

                log_activity(
                    current_user["id"],
                    "DELETE",
                    result["file_name"]
                )

                messagebox.showinfo(
                    "Success",
                    result["message"]
                )

                refresh_files()

            else:
                messagebox.showerror(
                    "Error",
                    result["error"]
                )

        except Exception as e:
            messagebox.showerror(
                "API Error",
                str(e)
            )

    tk.Button(
        btn_frame,
        text="Delete File",
        width=15,
        command=delete_selected_file
    ).pack(side="left", padx=5)

    def open_file_normally():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file first.")
            return

        values = tree.item(selected[0], "values")
        file_id = values[0]
        file_name = values[1]

        try:
            temp_path = download_to_temp(file_id, file_name)
            open_file_cross_platform(temp_path)

            log_activity(
                current_user["id"],
                "OPEN",
                file_name
            )

        except Exception as e:
            messagebox.showerror("Open Error", str(e))

    tk.Button(
        btn_frame,
        text="Preview File",
        width=15,
        command=open_file_normally
    ).pack(side="left", padx=5)

def show_logs_page(main_content):
    clear_main_content(main_content)

    tk.Label(
        main_content,
        text="Activity Logs",
        bg="#f8fafc",
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=25, pady=20)

    table_frame = tk.Frame(main_content, bg="white")
    table_frame.pack(fill="both", expand=True, padx=25, pady=15)

    columns = (
        "id",
        "username",
        "action_type",
        "target_file",
        "log_time"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    scrollbar.pack(side="right", fill="y")

    tree.configure(
        yscrollcommand=scrollbar.set
    )

    headings = {
        "id": "ID",
        "username": "Username",
        "action_type": "Action",
        "target_file": "Target File",
        "log_time": "Log Time"
    }

    for col in columns:
        tree.heading(col, text=headings[col])

    tree.column("id", width=60, anchor="center")
    tree.column("username", width=140, anchor="center")
    tree.column("action_type", width=140, anchor="center")
    tree.column("target_file", width=280)
    tree.column("log_time", width=220, anchor="center")

    logs = get_activity_logs()

    for row in logs:
        tree.insert("", tk.END, values=row)

    btn_frame = tk.Frame(main_content, bg="#f8fafc")
    btn_frame.pack(fill="x", padx=25, pady=10)

    tk.Button(
        btn_frame,
        text="Refresh Logs",
        width=15,
        command=lambda: refresh_logs()
    ).pack(side="left", padx=5)

    def refresh_logs():
        for item in tree.get_children():
            tree.delete(item)

        refreshed_logs = get_activity_logs()

        for row in refreshed_logs:
            tree.insert("", tk.END, values=row)

# LOGIN WINDOW
root = tk.Tk()
root.title("DTC Login")
root.geometry("420x260")
root.configure(bg="#f1f5f9")

tk.Label(
    root,
    text="Data Tracking Center",
    bg="#f1f5f9",
    font=("Arial", 18, "bold")
).pack(pady=20)

form = tk.Frame(root, bg="#f1f5f9")
form.pack(pady=10)

tk.Label(
    form,
    text="Username",
    bg="#f1f5f9"
).grid(row=0, column=0, padx=10, pady=10)

user_name_entry = tk.Entry(form, width=30)
user_name_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(
    form,
    text="Password",
    bg="#f1f5f9"
).grid(row=1, column=0, padx=10, pady=10)

password_entry = tk.Entry(form, width=30, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Button(
    root,
    text="Login",
    width=20,
    command=handle_login
).pack(pady=20)

root.mainloop()
