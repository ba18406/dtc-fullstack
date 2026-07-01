
from tkinter import *

root = Tk()
root.title("Login window")

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

top_frame = Frame(root, bg="lightblue")
top_frame.grid(row=0, column=0, sticky="nsew")

bottom_frame = Frame(root, bg="lightgray")
bottom_frame.grid(row=1, column=0, sticky="nsew")

title_label = Label(top_frame, text="Data Tracking Center", bg="lightblue")
title_label.grid(row=0, column=0, padx=10, pady=10)

user_name_label = Label(bottom_frame, text="User name")
user_name_label.grid(row=0, column=0, padx=10, pady=10)
user_name_entry = Entry(bottom_frame)
user_name_entry.grid(row=0, column=1, padx=10, pady=10)

password_label = Label(bottom_frame, text="Password")
password_label.grid(row=1, column=0, padx=10, pady=10)
password_entry = Entry(bottom_frame, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=10)

login_button_label = Button(bottom_frame, text="Login_in")
login_button_label.grid(row=2, column=0, padx=10, pady=10)

root.mainloop()
