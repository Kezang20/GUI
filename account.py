
import re
import tkinter as tk
from tkinter import messagebox

import database
from config import ACCENT, ACCENT_HOVER, BG, CARD, CARD_HOVER, MUTED, TEXT, WHITE


class AccountMixin:
    def add_placeholder(self, entry, placeholder, password=False):
        entry.placeholder = placeholder
        entry.has_placeholder = tk.BooleanVar(value=True)
        entry.insert(0, placeholder)
        entry.config(fg=MUTED)

        if password:
            entry.config(show="")

        def focus_in(event):
            if entry.has_placeholder.get():
                entry.delete(0, tk.END)
                entry.config(fg=WHITE)

                if password:
                    entry.config(show="*")

                entry.has_placeholder.set(False)

        def focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=MUTED)
                entry.has_placeholder.set(True)

                if password:
                    entry.config(show="")

        entry.bind("<FocusIn>", focus_in)
        entry.bind("<FocusOut>", focus_out)

    def is_valid_email(self, email):
        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        return re.match(pattern, email) is not None

    def is_valid_name(self, name):
        return bool(name) and all(
            character.isalpha() or character == " "
            for character in name
        )

    def is_valid_password(self, password):
        return (
            len(password) >= 8
            and any(character.isupper() for character in password)
            and any(character.islower() for character in password)
            and any(character.isdigit() for character in password)
        )

    # =====================================================
    # LOGIN
    # =====================================================

    def show_login(self):
        self.clear_content()

        title = tk.Label(
            self.content,
            text="🔐 Login",
            bg=BG,
            fg=WHITE,
            font=("Arial", 30, "bold")
        )
        title.pack(pady=(50, 30))

        form = tk.Frame(
            self.content,
            bg=CARD,
            padx=40,
            pady=40
        )
        form.pack(ipadx=100)

        tk.Label(
            form,
            text="Email (e.g. Dorji@gmail.com: must contain @ and a domain)",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 11)
        ).pack(anchor="w")

        email = tk.Entry(
            form,
            bg="#202832",
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Arial", 12)
        )
        email.pack(
            fill="x",
            pady=(5, 20),
            ipady=8
        )
        self.add_placeholder(
            email,
            "Enter your email (e.g. Dorji@gmail.com)"
        )

        tk.Label(
            form,
            text="Password",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 11)
        ).pack(anchor="w")

        password = tk.Entry(
            form,
            show="*",
            bg="#202832",
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            font=("Arial", 12)
        )
        password.pack(
            fill="x",
            pady=(5, 20),
            ipady=8
        )
        self.add_placeholder(
            password,
            "Enter your password",
            password=True
        )

        def login():
            login_email = (
                "" if email.has_placeholder.get()
                else email.get().strip()
            )

            login_password = (
                "" if password.has_placeholder.get()
                else password.get()
            )

            if not login_email or not login_password:
                messagebox.showwarning(
                    "Login",
                    "Please enter both email and password."
                )
                return

            if not self.is_valid_email(login_email):
                messagebox.showwarning(
                    "Login",
                    "Enter a valid email address."
                )
                return

            user = database.login_user(
                login_email,
                login_password
            )

            if user:
                self.current_user = user

                self.login_button.config(
                    text=f"👤 {user[1]}"
                )

                messagebox.showinfo(
                    "Login",
                    f"Welcome back, {user[1]}!"
                )

                self.show_home()

            else:
                messagebox.showerror(
                    "Login Failed",
                    "Incorrect email or password."
                )

        tk.Button(
            form,
            text="Log In",
            command=login,
            bg=ACCENT,
            fg=WHITE,
            activebackground=ACCENT_HOVER,
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        ).pack(
            fill="x",
            pady=10,
            ipady=8
        )

        tk.Button(
            form,
            text="Create Account",
            command=self.show_signup,
            bg="#252f3b",
            fg=WHITE,
            activebackground=CARD_HOVER,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2"
        ).pack(
            fill="x",
            ipady=8
        )

    # =====================================================
    # SIGNUP
    # =====================================================

    def show_signup(self):
        self.clear_content()

        title = tk.Label(
            self.content,
            text="Create Account",
            bg=BG,
            fg=WHITE,
            font=("Arial", 30, "bold")
        )
        title.pack(pady=30)

        form = tk.Frame(
            self.content,
            bg=CARD,
            padx=40,
            pady=40
        )
        form.pack(ipadx=100)

        entries = {}

        fields = [
            ("Full Name (letters and spaces only)", "name"),
            ("Email (e.g. Dorji@gmail.com: must contain @ and a domain)", "email"),
            ("Password (8+ characters: uppercase, lowercase, and number)", "password")
        ]

        for label_text, key in fields:
            tk.Label(
                form,
                text=label_text,
                bg=CARD,
                fg=TEXT,
                font=("Arial", 11)
            ).pack(anchor="w")

            entry = tk.Entry(
                form,
                bg="#202832",
                fg=WHITE,
                insertbackground=WHITE,
                relief="flat",
                font=("Arial", 12)
            )

            if key == "password":
                entry.config(show="*")

            entry.pack(
                fill="x",
                pady=(5, 15),
                ipady=8
            )

            entries[key] = entry

        placeholders = {
            "name": "Enter your name",
            "email": "Enter your email (e.g. Dorji@gmail.com)",
            "password": "Enter your password"
        }

        for key, placeholder in placeholders.items():
            self.add_placeholder(
                entries[key],
                placeholder,
                password=(key == "password")
            )

        def signup():
            name = (
                "" if entries["name"].has_placeholder.get()
                else entries["name"].get().strip()
            )

            email = (
                "" if entries["email"].has_placeholder.get()
                else entries["email"].get().strip()
            )

            password = (
                "" if entries["password"].has_placeholder.get()
                else entries["password"].get()
            )

            if not name or not email or not password:
                messagebox.showwarning(
                    "Signup",
                    "Please fill all fields."
                )
                return

            if not self.is_valid_name(name):
                messagebox.showwarning(
                    "Signup",
                    "Your name must contain only letters and spaces."
                )
                return

            if not self.is_valid_email(email):
                messagebox.showwarning(
                    "Signup",
                    "Enter a valid email address."
                )
                return

            if not self.is_valid_password(password):
                messagebox.showwarning(
                    "Signup",
                    "Password must be at least 8 characters and include an uppercase letter, a lowercase letter, and a number."
                )
                return

            success = database.create_user(
                name,
                email,
                password
            )

            if success:
                messagebox.showinfo(
                    "Success",
                    "Account created successfully!"
                )

                self.show_login()

            else:
                messagebox.showerror(
                    "Signup Failed",
                    "An account with this email already exists."
                )

        tk.Button(
            form,
            text="Create Account",
            command=signup,
            bg=ACCENT,
            fg=WHITE,
            activebackground=ACCENT_HOVER,
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        ).pack(
            fill="x",
            ipady=8
        )
