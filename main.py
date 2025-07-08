import customtkinter as ctk
import datetime
import database
import database_utils as db_manager
from form_window import FormWindow
from user_management_window import UserManagementWindow
from login_window import LoginWindow
from app_user_management_window import AppUserManagementWindow
from activity_log_window import ActivityLogWindow
from force_password_change_window import ForcePasswordChangeWindow # Import new window
from CTkMessagebox import CTkMessagebox

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()

        login = LoginWindow(self)
        self.wait_window(login)

        self.current_user = login.user_info
        if not self.current_user:
            self.destroy()
            return
            
        # --- Force password change on first login ---
        if self.current_user['first_login'] == 1:
            force_change_win = ForcePasswordChangeWindow(self, self.current_user)
            self.wait_window(force_change_win)
            
            # If the user closed the window without changing password, exit the app
            if not force_change_win.password_changed_successfully:
                self.destroy()
                return
            
            # Update the user's status in the current session
            self.current_user['first_login'] = 0

        # --- Build the main app window ---
        self.deiconify()
        self.title("Key Worker App - Main Menu")
        self.geometry("400x450")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)

        self.main_label = ctk.CTkLabel(self, text="Alyson House Records", font=ctk.CTkFont(size=16, weight="bold"))
        self.main_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        self.user_label = ctk.CTkLabel(self, text="Select Service User:")
        self.user_label.grid(row=1, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="w")
        
        self.user_dropdown = ctk.CTkOptionMenu(self, values=["No users found"])
        self.user_dropdown.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        ctk.CTkLabel(self, text="Select Month & Year:").grid(row=3, column=0, columnspan=2, padx=20, pady=(10,0), sticky="w")
        
        current_month_name = datetime.datetime.now().strftime("%B")
        self.months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        self.month_dropdown = ctk.CTkOptionMenu(self, values=self.months)
        self.month_dropdown.set(current_month_name)
        self.month_dropdown.grid(row=4, column=0, padx=(20,5), pady=5, sticky="ew")

        current_year = datetime.datetime.now().year
        years = [str(year) for year in range(current_year + 1, 2020, -1)]
        self.year_dropdown = ctk.CTkOptionMenu(self, values=years)
        self.year_dropdown.set(str(current_year))
        self.year_dropdown.grid(row=4, column=1, padx=(5,20), pady=5, sticky="ew")

        self.main_action_button = ctk.CTkButton(self, text="View / Create Form", command=self.process_form_request)
        self.main_action_button.grid(row=5, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="ew")
        
        self.manage_users_button = ctk.CTkButton(self, text="Manage Service Users", command=self.open_user_management)
        self.manage_users_button.grid(row=6, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        if self.current_user['role'] == 'supervisor':
            self.manage_app_users_button = ctk.CTkButton(self, text="Manage App Users", command=self.open_app_user_management)
            self.manage_app_users_button.grid(row=7, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
            
            self.view_log_button = ctk.CTkButton(self, text="View Activity Log", command=self.open_activity_log)
            self.view_log_button.grid(row=8, column=0, columnspan=2, padx=20, pady=5, sticky="ew")

        self.user_data_map = {}
        self.update_user_dropdown()

    def update_user_dropdown(self):
        self.user_data_map.clear()
        users = db_manager.get_all_service_users()
        
        if users:
            user_names = [user[1] for user in users]
            for user_id, name, dob in users:
                self.user_data_map[name] = {"id": user_id, "dob": dob}
            
            self.user_dropdown.configure(values=user_names)
            self.user_dropdown.set(user_names[0])
        else:
            self.user_dropdown.configure(values=["No users found"])
            self.user_dropdown.set("No users found")

    def open_user_management(self):
        user_window = UserManagementWindow(self, self.current_user)
        self.wait_window(user_window)
        self.update_user_dropdown()

    def open_app_user_management(self):
        app_user_window = AppUserManagementWindow(self, self.current_user)
        self.wait_window(app_user_window)

    def open_activity_log(self):
        log_window = ActivityLogWindow(self)
        self.wait_window(log_window)

    def process_form_request(self):
        selected_user_name = self.user_dropdown.get()
        if selected_user_name == "No users found":
            CTkMessagebox(title="Error", message="Please add a service user first via the 'Manage Users' screen.", icon="cancel")
            return
            
        user_info = self.user_data_map.get(selected_user_name)
        if not user_info:
            CTkMessagebox(title="Error", message="Could not find data for the selected user.", icon="cancel")
            return

        selected_month_str = self.month_dropdown.get()
        selected_year_int = int(self.year_dropdown.get())
        
        now = datetime.datetime.now()
        current_year = now.year
        current_month = now.month
        
        selected_month_num = self.months.index(selected_month_str) + 1
        
        if selected_year_int > current_year or \
           (selected_year_int == current_year and selected_month_num > current_month):
            CTkMessagebox(title="Future Date", 
                          message="You cannot create or view forms for a future month.", 
                          icon="warning")
            return
        
        form_month_year = f"{selected_month_str} {selected_year_int}"
        
        existing_form_data = db_manager.get_form_data(user_info["id"], form_month_year)
        
        form = FormWindow(
            self, 
            service_user_id=user_info["id"],
            service_user_name=selected_user_name, 
            dob=user_info["dob"],
            month=selected_month_str, 
            year=str(selected_year_int),
            form_data=existing_form_data,
            current_user=self.current_user
        )
        form.grab_set()

if __name__ == "__main__":
    database.initialize_db()
    app = App()
    app.mainloop()
