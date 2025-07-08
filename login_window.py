import customtkinter as ctk
import database_utils as db_manager
from CTkMessagebox import CTkMessagebox

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.user_info = None

        self.title("Login")
        self.geometry("350x300") # Increased height for better spacing
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.parent.destroy)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Please Login", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))

        ctk.CTkLabel(self, text="Username:").grid(row=1, column=0, padx=20, pady=(10,0), sticky="w")
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Enter username")
        self.username_entry.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Password:").grid(row=3, column=0, padx=20, pady=(10,0), sticky="w")
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Enter password", show="*")
        self.password_entry.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.password_entry.bind("<Return>", self.attempt_login)

        self.login_button = ctk.CTkButton(self, text="Login", command=self.attempt_login)
        self.login_button.grid(row=5, column=0, padx=20, pady=20, sticky="ew")

        self.username_entry.focus()

    def attempt_login(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            CTkMessagebox(title="Error", message="Please enter both username and password.", icon="cancel")
            return

        user_data = db_manager.verify_user(username, password)

        if user_data:
            self.user_info = user_data
            db_manager.log_activity(user_data['username'], "LOGIN", "Successful login.")
            self.destroy()
        else:
            CTkMessagebox(title="Login Failed", message="Incorrect username or password.", icon="cancel")
            db_manager.log_activity(username, "LOGIN FAILED", "Incorrect credentials provided.")
