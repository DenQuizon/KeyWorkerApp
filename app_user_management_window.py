import customtkinter as ctk
import database_utils as db_manager
from CTkMessagebox import CTkMessagebox
import tkinter.simpledialog as simpledialog

class AppUserManagementWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.parent = parent
        self.current_user = current_user

        self.title("Manage App Users")
        self.geometry("700x600")
        self.resizable(False, False)
        self.grab_set()

        self.main_font = ctk.CTkFont(size=14)
        self.label_font = ctk.CTkFont(size=16, weight="bold")
        self.button_font = ctk.CTkFont(size=14, weight="bold")

        # --- Top frame for adding users ---
        self.entry_frame = ctk.CTkFrame(self)
        self.entry_frame.pack(padx=20, pady=10, fill="x", side="top")
        self.entry_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.entry_frame, text="First Name:", font=self.main_font).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.first_name_entry = ctk.CTkEntry(self.entry_frame, font=self.main_font, height=35)
        self.first_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.entry_frame, text="Last Name:", font=self.main_font).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.last_name_entry = ctk.CTkEntry(self.entry_frame, font=self.main_font, height=35)
        self.last_name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.entry_frame, text="Initial Password:", font=self.main_font).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = ctk.CTkEntry(self.entry_frame, font=self.main_font, height=35)
        self.password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.entry_frame, text="Role:", font=self.main_font).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.role_menu = ctk.CTkOptionMenu(self.entry_frame, values=["staff", "supervisor"], font=self.main_font, height=35)
        self.role_menu.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        self.add_user_button = ctk.CTkButton(self.entry_frame, text="Add New App User", command=self.add_user, font=self.button_font, height=40)
        self.add_user_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # --- Bottom frame for user list ---
        self.display_frame = ctk.CTkScrollableFrame(self, label_text="Existing App Users", label_font=self.label_font)
        self.display_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.refresh_user_list()

    def refresh_user_list(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        users = db_manager.get_all_app_users()
        for user_id, username, role in users:
            row_frame = ctk.CTkFrame(self.display_frame)
            row_frame.pack(fill="x", pady=5, padx=5)
            row_frame.grid_columnconfigure(0, weight=1)

            info_label = ctk.CTkLabel(row_frame, text=f"{username} (Role: {role})", anchor="w", font=self.main_font)
            info_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

            if username != self.current_user['username']:
                reset_button = ctk.CTkButton(row_frame, text="Reset Password", width=120, font=self.main_font, height=35, command=lambda u_id=user_id, u_name=username: self.reset_password(u_id, u_name))
                reset_button.grid(row=0, column=1, padx=5, pady=5)
                
                delete_button = ctk.CTkButton(row_frame, text="Delete", width=80, font=self.main_font, height=35, fg_color="red", hover_color="#c40000", command=lambda u_id=user_id, u_name=username: self.delete_user(u_id, u_name))
                delete_button.grid(row=0, column=2, padx=5, pady=5)

    def add_user(self):
        first_name = self.first_name_entry.get().strip().lower()
        last_name = self.last_name_entry.get().strip().lower()
        password = self.password_entry.get()
        role = self.role_menu.get()

        if not first_name or not last_name or not password:
            CTkMessagebox(title="Error", message="First name, last name, and password cannot be empty.", icon="cancel")
            return
        
        # Generate the username automatically
        username = f"{first_name}.{last_name}"

        if db_manager.add_app_user(username, password, role):
            CTkMessagebox(title="Success", message=f"User '{username}' added successfully.", icon="check")
            db_manager.log_activity(self.current_user['username'], "ADD APP USER", f"Added user: {username} with role: {role}")
            self.first_name_entry.delete(0, 'end')
            self.last_name_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.refresh_user_list()
        else:
            CTkMessagebox(title="Error", message=f"User '{username}' already exists.", icon="cancel")

    def delete_user(self, user_id, username):
        msg = CTkMessagebox(title="Confirm Delete", message=f"Are you sure you want to delete the app user '{username}'? This cannot be undone.",
                            icon="question", option_1="Cancel", option_2="Delete")
        if msg.get() == "Delete":
            db_manager.delete_app_user(user_id)
            db_manager.log_activity(self.current_user['username'], "DELETE APP USER", f"Deleted user: {username} (ID: {user_id})")
            CTkMessagebox(title="Deleted", message=f"User '{username}' has been deleted.")
            self.refresh_user_list()
            
    def reset_password(self, user_id, username):
        new_password = simpledialog.askstring("Reset Password", f"Enter a new temporary password for {username}:", show="*")
        
        if not new_password:
            CTkMessagebox(title="Cancelled", message="Password reset cancelled.", icon="cancel")
            return
            
        if db_manager.reset_app_user_password(user_id, new_password):
            CTkMessagebox(title="Success", message=f"Password for {username} has been reset.", icon="check")
            db_manager.log_activity(self.current_user['username'], "RESET PASSWORD", f"Reset password for user: {username}")
        else:
            CTkMessagebox(title="Error", message="Failed to reset password.", icon="cancel")
