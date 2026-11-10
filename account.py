import re
import tkinter as tk
from tkinter import messagebox
 
import database
from config import BG, MUTED, WHITE
 
# ---- Look & feel (matches the CineScope screenshots, red instead of gold) ----
CARD_BG = "#1f262e"      # dark card
FIELD_BG = "#2f3a49"     # input fields
SUBTLE = "#b8c0cc"       # subtitles / small text
RED = "#e50914"          # main button + brand accent
RED_HOVER = "#b20710"
OK_GREEN = "#4ade80"
ERR = "#ff6b6b"          # inline error text / error border
 
 
class AccountMixin:
    # =====================================================
    # HELPERS
    # =====================================================
 
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
 
        entry.bind("<FocusIn>", focus_in, add="+")
        entry.bind("<FocusOut>", focus_out, add="+")
 
    # ---------- Validators: return a specific, friendly message or None ----------
 
    def name_error(self, name):
        if not name:
            return None
        digits = sorted({c for c in name if c.isdigit()})
        symbols = sorted({c for c in name if not c.isalpha() and not c.isdigit() and c != " "})
        if digits and symbols:
            return ("Names can only have letters and spaces. Please remove the "
                    f"numbers ({', '.join(digits)}) and symbols ({' '.join(symbols)}).")
        if digits:
            return (f"Names can't contain numbers (you typed {', '.join(digits)}). "
                    "Please use letters only, like Dorji Wangmo.")
        if symbols:
            return (f"Names can't contain symbols like {' '.join(symbols)}. "
                    "Please use letters and spaces only.")
        return None
 
    def email_error(self, email):
        if not email:
            return None
        example = "name@example.com"
        if " " in email:
            return "Emails can't contain spaces. Please remove the space and try again."
        if "@" not in email:
            return f"Your email is missing the @ symbol. It should look like {example}."
        if email.count("@") > 1:
            return "Your email has more than one @ symbol. Please keep just one."
        local, domain = email.split("@")
        if not local:
            return f"Please add your username before the @ (for example {example})."
        if not domain:
            return "Please add a domain after the @ (for example gmail.com)."
        if "." not in domain:
            return (f"The part after @ needs a dot, like gmail.com. "
                    f"Did you mean {domain}.com?")
        if domain.startswith(".") or domain.endswith(".") or ".." in domain:
            return "The domain can't start or end with a dot, or have two dots in a row."
        tld = domain.rsplit(".", 1)[1]
        if len(tld) < 2 or not tld.isalpha():
            return "The ending of your email (like .com or .bt) looks incomplete. Please check it."
        if re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email) is None:
            return "That email has a character we can't accept. Use letters, numbers, and . _ % + - only."
        return None
 
    def is_valid_email(self, email):
        return bool(email) and self.email_error(email) is None
 
    def is_valid_name(self, name):
        return bool(name) and self.name_error(name) is None
 
    def password_checks(self, password):
        """Returns the requirement results in display order."""
        return [
            len(password) >= 8,
            any(c.isupper() for c in password),
            any(c.islower() for c in password),
            any(c.isdigit() for c in password),
            any(not c.isalnum() and not c.isspace() for c in password),
        ]
 
    def is_valid_password(self, password):
        return all(self.password_checks(password))
 
    def _field_label(self, parent, text):
        tk.Label(
            parent,
            text=text.upper(),
            bg=CARD_BG,
            fg=WHITE,
            font=("Arial", 9, "bold"),
            anchor="w"
        ).pack(fill="x", pady=(8, 0))
 
    def _field_entry(self, parent, validator=None, live=False, required=None):
        """Entry field with inline feedback shown under it.
 
        - Required: leaving the field empty shows the `required` message.
        - Specific: the validator says exactly what is wrong and how to fix it.
        - Preserving: the user's input is never cleared.
        - Friendly: polite wording with an example.
        - Timely: checked when leaving the field (or as they type if live=True),
          and cleared the moment the problem is fixed.
        """
        entry = tk.Entry(
            parent,
            bg=FIELD_BG,
            fg=WHITE,
            insertbackground=WHITE,
            relief="flat",
            highlightthickness=1,
            highlightbackground=FIELD_BG,
            highlightcolor=FIELD_BG,
            font=("Arial", 11)
        )
        entry.pack(fill="x", pady=(4, 0), ipady=9)
 
        feedback = tk.Label(parent, text="", bg=CARD_BG, fg=ERR,
                            font=("Arial", 8), anchor="w", justify="left",
                            wraplength=560)
        feedback.pack(fill="x", pady=(2, 0))
 
        def set_feedback(message):
            try:
                feedback.config(text=f"⚠ {message}" if message else "")
                color = ERR if message else FIELD_BG
                entry.config(highlightbackground=color, highlightcolor=color)
            except tk.TclError:
                pass  # page was switched and widgets no longer exist
 
        def check(event=None):
            value = "" if entry.has_placeholder.get() else entry.get().strip()
            if not value:
                set_feedback(required)
            else:
                set_feedback(validator(value) if validator else None)
 
        def on_key(event):
            # Re-check while typing if live, or once a message is already showing
            if live or feedback.cget("text"):
                check()
 
        entry.set_feedback = set_feedback
        entry.show_required = lambda: set_feedback(required)
        entry.bind("<FocusOut>", check, add="+")
        entry.bind("<KeyRelease>", on_key, add="+")
        return entry
 
    def _red_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text.upper(),
            command=command,
            bg=RED,
            fg=WHITE,
            activebackground=RED_HOVER,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            font=("Arial", 11, "bold"),
            cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=RED_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=RED))
        btn.pack(fill="x", pady=(14, 8), ipady=10)
        return btn
 
    def _card(self):
        self.clear_content()
        card = tk.Frame(self.content, bg=CARD_BG, padx=30, pady=18)
        card.pack(fill="x", padx=80, pady=30)
        return card
 
    def _read(self, entry, strip=True):
        if entry.has_placeholder.get():
            return ""
        return entry.get().strip() if strip else entry.get()
 
    # =====================================================
    # LOGIN
    # =====================================================
 
    def show_login(self):
        card = self._card()
 
        tk.Label(card, text="CINESCOPE", bg=CARD_BG, fg=RED,
                 font=("Arial", 13, "bold")).pack(pady=(0, 6))
        tk.Label(card, text="Welcome Back", bg=CARD_BG, fg=WHITE,
                 font=("Arial", 22, "bold")).pack()
        tk.Label(card, text="Sign in to continue exploring CineScope.",
                 bg=CARD_BG, fg=SUBTLE, font=("Arial", 9)).pack(pady=(4, 10))
 
        self._field_label(card, "Email Address")
        email = self._field_entry(
            card, self.email_error,
            required="Please enter your email address, like name@example.com."
        )
        self.add_placeholder(email, "Enter your email address")
 
        self._field_label(card, "Password")
        password = self._field_entry(card, required="Please enter your password.")
        self.add_placeholder(password, "Enter your password", password=True)
 
        def login():
            login_email = self._read(email)
            login_password = self._read(password, strip=False)
 
            if not login_email or not login_password:
                if not login_email:
                    email.show_required()
                if not login_password:
                    password.show_required()
                messagebox.showwarning("Login", "Please enter both email and password.")
                return
 
            problem = self.email_error(login_email)
            if problem:
                email.set_feedback(problem)
                email.focus_set()
                messagebox.showwarning("Login", problem)
                return
 
            user = database.login_user(login_email, login_password)
 
            if user:
                self.current_user = user
                self.login_button.config(text=f"👤 {user[1]}")
                messagebox.showinfo("Login", f"Welcome back, {user[1]}!")
                self.show_home()
            else:
                messagebox.showerror("Login Failed", "Incorrect email or password.")
 
        self._red_button(card, "Log In", login)
 
        tk.Label(card, text="New to CineScope?", bg=CARD_BG, fg=SUBTLE,
                 font=("Arial", 9)).pack(pady=(4, 0))
 
        link = tk.Label(card, text="Create an Account", bg=CARD_BG, fg=RED,
                        font=("Arial", 10, "bold"), cursor="hand2")
        link.pack(pady=(2, 0))
        link.bind("<Button-1>", lambda e: self.show_signup())
 
    # =====================================================
    # SIGNUP
    # =====================================================
 
    def show_signup(self):
        card = self._card()
 
        tk.Label(card, text="Join CineScope", bg=CARD_BG, fg=WHITE,
                 font=("Arial", 18, "bold")).pack()
        tk.Label(card, text="Create your account and discover your next favourite movie.",
                 bg=CARD_BG, fg=SUBTLE, font=("Arial", 9)).pack(pady=(4, 6))
 
        self._field_label(card, "Full Name")
        name_e = self._field_entry(
            card, self.name_error, live=True,
            required="Please enter your full name. This field can't be left empty."
        )
        self.add_placeholder(name_e, "Enter your full name")
 
        self._field_label(card, "Email Address")
        email_e = self._field_entry(
            card, self.email_error,
            required="Please enter your email address, like name@example.com."
        )
        self.add_placeholder(email_e, "Enter your email address")
 
        self._field_label(card, "Password")
        pass_e = self._field_entry(card, required="Please create a password.")
        self.add_placeholder(pass_e, "Enter your password", password=True)
 
        self._field_label(card, "Confirm Password")
        confirm_e = self._field_entry(card, required="Please confirm your password by typing it again.")
        self.add_placeholder(confirm_e, "Enter your confirm password", password=True)
 
        # ---- Live password requirements checklist ----
        tk.Label(card, text="PASSWORD REQUIREMENTS", bg=CARD_BG, fg=SUBTLE,
                 font=("Arial", 9, "bold"), anchor="w").pack(fill="x", pady=(10, 2))
 
        requirement_texts = [
            "At least 8 characters",
            "Uppercase letter",
            "Lowercase letter",
            "Number",
            "Special character",
        ]
        req_labels = []
        for text in requirement_texts:
            lbl = tk.Label(card, text=f"○ {text}", bg=CARD_BG, fg=SUBTLE,
                           font=("Arial", 9), anchor="w")
            lbl.pack(fill="x")
            req_labels.append(lbl)
 
        def update_requirements(event=None):
            pwd = self._read(pass_e, strip=False)
            results = self.password_checks(pwd)
            for lbl, text, ok in zip(req_labels, requirement_texts, results):
                lbl.config(
                    text=f"{'●' if ok else '○'} {text}",
                    fg=OK_GREEN if ok else SUBTLE
                )
 
        pass_e.bind("<KeyRelease>", update_requirements, add="+")
 
        def signup():
            name = self._read(name_e)
            email = self._read(email_e)
            password = self._read(pass_e, strip=False)
            confirm = self._read(confirm_e, strip=False)
 
            if not name or not email or not password or not confirm:
                for value, field in ((name, name_e), (email, email_e),
                                     (password, pass_e), (confirm, confirm_e)):
                    if not value:
                        field.show_required()
                messagebox.showwarning("Signup", "Please fill all fields.")
                return
 
            problem = self.name_error(name)
            if problem:
                name_e.set_feedback(problem)
                name_e.focus_set()
                messagebox.showwarning("Signup", problem)
                return
 
            problem = self.email_error(email)
            if problem:
                email_e.set_feedback(problem)
                email_e.focus_set()
                messagebox.showwarning("Signup", problem)
                return
 
            if not self.is_valid_password(password):
                messagebox.showwarning(
                    "Signup",
                    "Password must be at least 8 characters and include an uppercase "
                    "letter, a lowercase letter, a number, and a special character."
                )
                return
 
            if password != confirm:
                messagebox.showwarning("Signup", "Passwords do not match.")
                return
 
            if database.create_user(name, email, password):
                messagebox.showinfo("Success", "Account created successfully!")
                self.show_login()
            else:
                messagebox.showerror("Signup Failed",
                                     "An account with this email already exists.")
 
        self._red_button(card, "Create Account", signup)
 
        back = tk.Label(card, text="Already have an account? Log in", bg=CARD_BG,
                        fg=RED, font=("Arial", 10, "bold"), cursor="hand2")
        back.pack(pady=(0, 0))
        back.bind("<Button-1>", lambda e: self.show_login())