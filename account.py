import tkinter as tk
from tkinter import messagebox

import database
from config import ACCENT, ACCENT_HOVER, BG, CARD, CARD_HOVER, TEXT, WHITE


class AccountMixin:

    def show_login(self):

        self.clear_content()


        title = tk.Label(
            self.content,
            text="🔐 Login",
            bg=BG,
            fg=WHITE,
            font=("Arial", 30, "bold")
        )

        title.pack(
            pady=(50, 30)
        )


        form = tk.Frame(
            self.content,
            bg=CARD,
            padx=40,
            pady=40
        )

        form.pack(
            ipadx=100
        )


        tk.Label(
            form,
            text="Email",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 11)
        ).pack(
            anchor="w"
        )


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


        tk.Label(
            form,
            text="Password",
            bg=CARD,
            fg=TEXT,
            font=("Arial", 11)
        ).pack(
            anchor="w"
        )


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


        def login():

            user = database.login_user(
                email.get(),
                password.get()
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

        title.pack(
            pady=30
        )


        form = tk.Frame(
            self.content,
            bg=CARD,
            padx=40,
            pady=40
        )

        form.pack(
            ipadx=100
        )


        entries = {}


        fields = [
            ("Full Name", "name"),
            ("Email", "email"),
            ("Password", "password")
        ]


        for label_text, key in fields:

            tk.Label(
                form,
                text=label_text,
                bg=CARD,
                fg=TEXT,
                font=("Arial", 11)
            ).pack(
                anchor="w"
            )


            entry = tk.Entry(
                form,
                bg="#202832",
                fg=WHITE,
                insertbackground=WHITE,
                relief="flat",
                font=("Arial", 12)
            )


            if key == "password":

                entry.config(
                    show="*"
                )


            entry.pack(
                fill="x",
                pady=(5, 15),
                ipady=8
            )


            entries[key] = entry


        def signup():

            name = entries[
                "name"
            ].get().strip()


            email = entries[
                "email"
            ].get().strip()


            password = entries[
                "password"
            ].get()


            if (
                not name
                or not email
                or not password
            ):

                messagebox.showwarning(
                    "Signup",
                    "Please fill all fields."
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


