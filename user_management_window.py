import customtkinter as ctk
import database_utils as db_manager
from CTkMessagebox import CTkMessagebox
import datetime
import tkinter.simpledialog as simpledialog

class UserManagementWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.parent = parent 
        self.current_user = current_user

        self.title("Manage Service Users")
        self.geometry("800x700") 
        self.resizable(False, False)
        self.grab_set()

        self.main_font = ctk.CTkFont(size=16)
        self.label_font = ctk.CTkFont(size=18, weight="bold")
        self.button_font = ctk.CTkFont(size=16, weight="bold")
        self.small_label_font = ctk.CTkFont(size=12)

        self.editing_user_id = None

        self.entry_frame = ctk.CTkFrame(self)
        self.entry_frame.pack(padx=20, pady=10, fill="x", side="top")
        self.entry_frame.grid_columnconfigure((1,2,3), weight=1)

        ctk.CTkLabel(self.entry_frame, text="Full Name:", font=self.main_font).grid(row=0, column=0, padx=10, pady=15, sticky="w")
        self.name_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Enter user's full name", font=self.main_font, height=40)
        self.name_entry.grid(row=0, column=1, columnspan=3, padx=10, pady=15, sticky="ew")

        ctk.CTkLabel(self.entry_frame, text="Date of Birth:", font=self.main_font).grid(row=1, column=0, padx=10, pady=15, sticky="w")
        
        ctk.CTkLabel(self.entry_frame, text="Day", font=self.small_label_font).grid(row=2, column=1, sticky="s", padx=5)
        ctk.CTkLabel(self.entry_frame, text="Month", font=self.small_label_font).grid(row=2, column=2, sticky="s", padx=5)
        ctk.CTkLabel(self.entry_frame, text="Year", font=self.small_label_font).grid(row=2, column=3, sticky="s", padx=5)

        current_year = datetime.datetime.now().year
        self.dob_years = [str(year) for year in range(current_year, 1920, -1)]
        self.months_list = [datetime.date(2000, i, 1).strftime('%b') for i in range(1, 13)]
        self.dob_days = [f"{day:02d}" for day in range(1, 32)]

        self.dob_day_menu = ctk.CTkOptionMenu(self.entry_frame, values=self.dob_days, font=self.main_font, height=40)
        self.dob_month_menu = ctk.CTkOptionMenu(self.entry_frame, values=self.months_list, font=self.main_font, height=40)
        self.dob_year_menu = ctk.CTkOptionMenu(self.entry_frame, values=self.dob_years, font=self.main_font, height=40)
        
        self.dob_day_menu.grid(row=3, column=1, padx=5, pady=(0,15), sticky="ew")
        self.dob_month_menu.grid(row=3, column=2, padx=5, pady=(0,15), sticky="ew")
        self.dob_year_menu.grid(row=3, column=3, padx=5, pady=(0,15), sticky="ew")

        self.action_button = ctk.CTkButton(self.entry_frame, text="Add New User", command=self.add_or_update_user, font=self.button_font, height=50)
        self.action_button.grid(row=4, column=0, columnspan=3, padx=10, pady=15, sticky="ew")
        
        self.cancel_button = ctk.CTkButton(self.entry_frame, text="Cancel Edit", fg_color="gray", command=self.cancel_edit_mode, font=self.button_font, height=50)

        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(side="bottom", fill="x", padx=20, pady=(10, 20))
        
        self.close_button = ctk.CTkButton(bottom_frame, text="Close Window", command=self.destroy, font=self.button_font, height=40, fg_color="gray20", border_width=2)
        self.close_button.pack(fill="x")

        separator = ctk.CTkFrame(self, height=2, corner_radius=0)
        separator.pack(side="bottom", fill="x", padx=20, pady=5)
        
        self.display_frame = ctk.CTkScrollableFrame(self, label_text="Existing Users", label_font=self.label_font)
        self.display_frame.pack(padx=20, pady=(10, 10), fill="both", expand=True)
        
        self.refresh_user_list()
        self.clear_entries()

    def refresh_user_list(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        users = db_manager.get_all_service_users()
        if not users:
            ctk.CTkLabel(self.display_frame, text="No users found. Add one above.", font=self.main_font).pack(pady=20)
        else:
            for user in users:
                user_id, name, dob = user
                
                row_frame = ctk.CTkFrame(self.display_frame)
                row_frame.pack(fill="x", pady=5, padx=5)
                row_frame.grid_columnconfigure(0, weight=1)

                info_label = ctk.CTkLabel(row_frame, text=f"{name} (DOB: {dob})", anchor="w", font=self.main_font)
                info_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

                edit_button = ctk.CTkButton(row_frame, text="Edit", width=80, font=self.main_font, height=35, command=lambda u=user: self.enter_edit_mode(u))
                edit_button.grid(row=0, column=1, padx=5, pady=5)
                
                delete_button = ctk.CTkButton(row_frame, text="Delete", width=80, font=self.main_font, height=35, fg_color="red", hover_color="#c40000", command=lambda i=user_id: self.delete_user(i))
                delete_button.grid(row=0, column=2, padx=5, pady=5)

    def add_or_update_user(self):
        name = self.name_entry.get().strip()
        month_abbr = self.dob_month_menu.get()
        month_num = datetime.datetime.strptime(month_abbr, "%b").strftime("%m")
        day = self.dob_day_menu.get()
        year = self.dob_year_menu.get()
        dob = f"{year}-{month_num}-{day}"

        if not name or "Year" in dob:
            CTkMessagebox(title="Error", message="Please fill in the name and select a full date of birth.", icon="cancel", font=self.main_font)
            return

        performed_by = self.current_user['username']

        if self.editing_user_id is not None:
            success = db_manager.update_service_user(self.editing_user_id, name, dob, performed_by)
            if success:
                CTkMessagebox(title="Success", message=f"User '{name}' updated successfully.", font=self.main_font)
                self.cancel_edit_mode()
            else:
                CTkMessagebox(title="Error", message=f"Failed to update user. Does another user have this name?", icon="cancel", font=self.main_font)
            return
        
        success = db_manager.add_service_user(name, dob, performed_by)
        if success:
            CTkMessagebox(title="Success", message=f"User '{name}' has been added.", icon="check", font=self.main_font)
            self.clear_entries()
            self.refresh_user_list()
        else:
            CTkMessagebox(title="Error", message=f"A user with the name '{name}' already exists.", icon="cancel", font=self.main_font)

    def delete_user(self, user_id):
        msg = CTkMessagebox(title="Confirm Delete", message="Are you sure you want to delete this user AND all their forms? This cannot be undone.",
                            icon="question", option_1="Cancel", option_2="Delete", font=self.main_font)
        if msg.get() == "Delete":
            # Secure delete: ask for password
            password = simpledialog.askstring("Password Required", f"Enter your password to confirm deletion:", show="*")
            if not password:
                return # User cancelled
            
            # Verify the current user's password
            user_data = db_manager.verify_user(self.current_user['username'], password)
            if user_data:
                db_manager.delete_service_user(user_id, self.current_user['username'])
                CTkMessagebox(title="Deleted", message="User has been deleted.", font=self.main_font)
                self.refresh_user_list()
                if self.editing_user_id == user_id:
                    self.cancel_edit_mode()
            else:
                CTkMessagebox(title="Error", message="Incorrect password. Deletion cancelled.", icon="cancel")
    
    def enter_edit_mode(self, user_data):
        user_id, name, dob = user_data
        self.editing_user_id = user_id
        
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, name)
        
        try:
            year, month_num, day = dob.split('-')
            month_abbr = datetime.datetime.strptime(month_num, "%m").strftime("%b")
            
            self.dob_day_menu.set(day)
            self.dob_month_menu.set(month_abbr)
            self.dob_year_menu.set(year)
        except (ValueError, IndexError):
            self.clear_entries()

        self.action_button.configure(text="Update User")
        self.cancel_button.grid(row=4, column=3, padx=10, pady=15, sticky="ew")

    def cancel_edit_mode(self):
        self.editing_user_id = None
        self.clear_entries()
        self.refresh_user_list()
        self.action_button.configure(text="Add New User")
        self.cancel_button.grid_forget()
        
    def clear_entries(self):
        self.name_entry.delete(0, "end")
        
        now = datetime.datetime.now()
        self.dob_day_menu.set(now.strftime("%d"))
        self.dob_month_menu.set(now.strftime("%b"))
        self.dob_year_menu.set(str(now.year))
