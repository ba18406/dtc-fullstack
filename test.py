
from tkinter import *
import tkinter.messagebox as messagebox

#from users_roles import load_users_from_excel
#USERS = load_users_from_excel("users_roles_template.xlsx")

TEXTS = {
    "en": {
        "user_title": "User panel",
        "username": "User name",
        "password": "Password",
        "login": "Login",
        "title": "Data Tracking Center",
        "main_title": "Main panel",
        "main_sub_message": "Logged in as: {username} (role: {role})",
        "error_title": "Login failed",
        "error_login": "Username or password is incorrect",
        "menu": "Menu",
        "dashboard": "Dashboard",
        "users":"Users",
        "settings":"Settings",
        "logout":"Logout"
    },
    "ar": {
        "user_title": "واجهة المستخدم",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "login": "تسجيل الدخول",
        "title": "مركز متابعة البيانات",
        "main_title": "الواجهة الرئيسية",
        "main_sub_message": "تم تسجيل الدخول باسم: {username} (الدور: {role})",
        "error_title": "فشل تسجيل الدخول",
        "error_login": "اسم المستخدم أو كلمة المرور غير صحيحة",
        "menu": "القائمة",
        "dashboard": "لوحة التحكم",
        "users":"المستخدمين",
        "settings":"الاعدادات",
        "logout":"تسجيل الخروج"
    }
}

root = Tk()
root.geometry("500x350")
root.resizable(False, False)

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

user_top_frame = Frame(root, bg="white")
user_top_frame.grid(row=0, column=0, sticky="nsew")
user_top_frame.columnconfigure(0, weight=1)

user_bottom_frame = Frame(root, bg="lightgray")
user_bottom_frame.grid(row=1, column=0, sticky="nsew")
user_bottom_frame.columnconfigure(0, weight=1)
user_bottom_frame.columnconfigure(1, weight=1)

lang_frame = Frame(user_bottom_frame, bg="lightgray")
lang_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

lang_var = StringVar(value="en")
def update_language():
    lang = lang_var.get()

    user_title = TEXTS[lang]["user_title"]
    root.title(user_title)
    user_name_label.config(text=TEXTS[lang]["username"])
    password_label.config(text=TEXTS[lang]["password"])
    login_button_label.config(text=TEXTS[lang]["login"])
    title_label.config(text=TEXTS[lang]["title"])
    
    if lang == "en":
        user_name_label.grid_configure(row=1, column=0, sticky="we")
        user_name_entry.grid_configure(row=1, column=1, sticky="we")
        password_label.grid_configure(row=2, column=0, sticky="we")
        password_entry.grid_configure(row=2, column=1, sticky="we")
        login_button_label.grid_configure(row=3, column=0, columnspan=2, sticky="w")
        title_label.grid_configure(sticky="n")
    else:
        user_name_label.grid_configure(row=1, column=1, sticky="ew")
        user_name_entry.grid_configure(row=1, column=0, sticky="ew")
        password_label.grid_configure(row=2, column=1, sticky="ew")
        password_entry.grid_configure(row=2, column=0, sticky="ew")
        login_button_label.grid_configure(row=3, column=0, columnspan=2, sticky="e")
        title_label.grid_configure(sticky="n")        

#logo_image = PhotoImage(master=root, file="ministrylogo.png")
#logo_image = logo_image.subsample(2, 2)

#logo_label = Label(user_top_frame, image=logo_image, bg="white")
#logo_label.image = logo_image
#logo_label.grid(row=0, column=0, pady=(10, 5))

title_label = Label(user_top_frame, text="Data Tracking Center",
                    font=("Arial", 18, "bold"), bg="white")
title_label.grid(row=1, column=0, padx=10, pady=10, sticky="n")

rb_en = Radiobutton(lang_frame, text="EN", variable=lang_var, value="en",
                    bg="lightgray", command=update_language)
rb_en.pack(side="left")
rb_ar = Radiobutton(lang_frame, text="AR", variable=lang_var, value="ar",
                    bg="lightgray", command=update_language)
rb_ar.pack(side="left")

user_name_label = Label(user_bottom_frame, text="User name")
user_name_label.grid(row=1, column=0, padx=10, pady=10)
user_name_entry = Entry(user_bottom_frame)
user_name_entry.grid(row=1, column=1, padx=10, pady=10)

password_label = Label(user_bottom_frame, text="Password")
password_label.grid(row=2, column=0, padx=10, pady=10)
password_entry = Entry(user_bottom_frame, show="*")
password_entry.grid(row=2, column=1, padx=10, pady=10)

def handle_login():
    username = user_name_entry.get().strip()
    password = password_entry.get().strip()

    # Look up the user in the USERS dict
    user_info = USERS.get(username)

    if user_info is not None and user_info["password"] == password:
        lang = lang_var.get()

        main_title = TEXTS[lang]["main_title"]
        main_sub_message = TEXTS[lang]["main_sub_message"].format(
            username=username,
            role=user_info.get("role", "")
        )

        main_win = Toplevel(root)
        main_win.title(main_title)
        screen_width = main_win.winfo_screenwidth()
        screen_height = main_win.winfo_screenheight()
        win_width = int(screen_width * 0.5)
        win_height = int(screen_height * 0.9)
        x = (screen_width - win_width) // 1
        y = (screen_height - win_height) // 2
        main_win.geometry(f"{win_width}x{win_height}+{x}+{y}")
        
        main_win.rowconfigure(0, weight=1)
        main_win.rowconfigure(1, weight=10)
        main_win.columnconfigure(0, weight=1)

        main_top_frame = Frame(main_win, bg="white")
        main_top_frame.grid(row=0, column=0, sticky="nsew")
        main_top_frame.columnconfigure(0, weight=1)

        main_bottom_frame = Frame(main_win, bg="lightgray")
        main_bottom_frame.grid(row=1, column=0, sticky="nsew")
        main_bottom_frame.rowconfigure(0, weight=1)
        main_bottom_frame.columnconfigure(0, weight=1)
        main_bottom_frame.columnconfigure(1, weight=5)

        logo_label = Label(main_top_frame, image=logo_image, bg="white")
        logo_label.image = logo_image
        logo_label.grid(row=0, column=0, pady=(10, 5))
        main_label = Label(main_top_frame, text=main_sub_message,
                           font=("Arial", 14), bg="white")
        main_label.grid(row=1, column=0, pady=20)

        menu_frame = Frame(main_bottom_frame, bg="white")
        content_frame = Frame(main_bottom_frame, bg="#d0d0d0")
        if lang == "en":
            menu_frame.grid(row=0, column=0, sticky="nsew")
            content_frame.grid(row=0, column=1, sticky="nsew")
        else:
            menu_frame.grid(row=0, column=1, sticky="nsew")
            content_frame.grid(row=0, column=0, sticky="nsew")
            main_bottom_frame.columnconfigure(0, weight=5)
            main_bottom_frame.columnconfigure(1, weight=1)

        lang_frame = Frame(menu_frame, bg="white")
        lang_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")    
        rb_en = Radiobutton(lang_frame, text="EN", variable=lang_var, value="en",
                            bg="white", command=update_language)
        rb_en.pack(side="left")
        rb_ar = Radiobutton(lang_frame, text="AR", variable=lang_var, value="ar",
                            bg="white", command=update_language)
        rb_ar.pack(side="left")
        menu_title = Label(menu_frame, text="Menu", bg="white", font=("Arial", 12, "bold"))
        menu_title.pack(fill="x", pady=(10, 5))
        btn_dashboard = Button(menu_frame, text="Dashboard")
        btn_dashboard.pack(fill="x", padx=10, pady=5)
        btn_users = Button(menu_frame, text="Users")
        btn_users.pack(fill="x", padx=10, pady=5)
        btn_settings = Button(menu_frame, text="Settings")
        btn_settings.pack(fill="x", padx=10, pady=5)
        btn_logout = Button(menu_frame, text="Logout")
        btn_logout.pack(fill="x", padx=10, pady=(20, 10))

    else:
        lang = lang_var.get()
        err_title = TEXTS[lang]["error_title"]
        err_msg = TEXTS[lang]["error_login"]
        messagebox.showerror(err_title, err_msg)
    
login_button_label = Button(user_bottom_frame, text="Login_in", command=handle_login)
login_button_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

update_language()
root.mainloop()
