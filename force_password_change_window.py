import customtkinter as ctk
import database_utils as db_manager
from CTkMessagebox import CTkMessagebox

class ForcePasswordChangeWindow(ctk.CTkToplevel):
    def __init__(self, parent, user_info):
        super().__init__(parent)
        self.parent = parent
        self.user_info = user_info
        self.password_changed_successfully = False

        self.title("Change Password")
        self.geometry("400x380") # Increased height for new label
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="First Login: Please Change Your Password", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkLabel(self, text=f"Username: {self.user_info['username']}", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=20, pady=5)

        ctk.CTkLabel(self, text="New Password:", anchor="w").grid(row=2, column=0, padx=20, pady=(10,0), sticky="ew")
        self.new_password_entry = ctk.CTkEntry(self, show="*")
        self.new_password_entry.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Confirm New Password:", anchor="w").grid(row=4, column=0, padx=20, pady=(10,0), sticky="ew")
        self.confirm_password_entry = ctk.CTkEntry(self, show="*")
        self.confirm_password_entry.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        self.confirm_password_entry.bind("<Return>", self.attempt_password_change)

        # NEW: Add instruction label for password length
        self.info_label = ctk.CTkLabel(self, text="(Password must be at least 6 characters)", text_color="gray50", font=ctk.CTkFont(size=12))
        self.info_label.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.change_button = ctk.CTkButton(self, text="Change Password and Login", command=self.attempt_password_change)
        self.change_button.grid(row=7, column=0, padx=20, pady=20, sticky="ew")

        self.focus_force()
        self.after(100, lambda: self.new_password_entry.focus_set())

    def attempt_password_change(self, event=None):
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not new_password or not confirm_password:
            CTkMessagebox(title="Error", message="Both password fields are required.", icon="cancel")
            return

        if len(new_password) < 6:
            CTkMessagebox(title="Error", message="Password must be at least 6 characters long.", icon="cancel")
            # Clear fields and refocus
            self.new_password_entry.delete(0, "end")
            self.confirm_password_entry.delete(0, "end")
            self.new_password_entry.focus_set()
            return

        if new_password != confirm_password:
            CTkMessagebox(title="Error", message="Passwords do not match.", icon="cancel")
            # Clear only the confirmation field and refocus
            self.confirm_password_entry.delete(0, "end")
            self.confirm_password_entry.focus_set()
            return

        if db_manager.change_user_password(self.user_info['id'], new_password):
            CTkMessagebox(title="Success", message="Password changed successfully. You can now use the application.")
            db_manager.log_activity(self.user_info['username'], "PASSWORD CHANGE", "User changed their initial password.")
            self.password_changed_successfully = True
            self.destroy()
        else:
            CTkMessagebox(title="Error", message="Failed to change password. Please contact a supervisor.", icon="cancel")

    def on_close(self):
        """Handle the user closing the window without changing the password."""
        if not self.password_changed_successfully:
            db_manager.log_activity(self.user_info['username'], "PASSWORD CHANGE", "User cancelled initial password change. Application terminated.")
            self.parent.destroy()
        self.destroy()
