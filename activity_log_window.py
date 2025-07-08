import customtkinter as ctk
import database_utils as db_manager

class ActivityLogWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Activity Log")
        self.geometry("900x600") # Made wider to accommodate columns
        self.grab_set()

        self.main_font = ctk.CTkFont(size=14)
        self.header_font = ctk.CTkFont(size=14, weight="bold")

        # Create a scrollable frame to hold the table
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Configure the grid layout for the table
        self.scrollable_frame.grid_columnconfigure(0, weight=2) # Timestamp
        self.scrollable_frame.grid_columnconfigure(1, weight=2) # User
        self.scrollable_frame.grid_columnconfigure(2, weight=2) # Action
        self.scrollable_frame.grid_columnconfigure(3, weight=3) # Details

        self.load_logs()

    def load_logs(self):
        # --- Create Table Headers ---
        headers = ["Timestamp", "User", "Action", "Details"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(self.scrollable_frame, text=header, font=self.header_font)
            header_label.grid(row=0, column=i, padx=10, pady=5, sticky="w")
        
        # Add a separator line
        separator = ctk.CTkFrame(self.scrollable_frame, height=2)
        separator.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 5))

        # --- Populate Table with Log Data ---
        logs = db_manager.get_activity_log()
        if not logs:
            no_logs_label = ctk.CTkLabel(self.scrollable_frame, text="No activities have been logged yet.", font=self.main_font)
            no_logs_label.grid(row=2, column=0, columnspan=4, pady=20)
        else:
            for row_index, log_entry in enumerate(logs, start=2):
                timestamp, user, action, details = log_entry
                
                # Format the timestamp nicely
                formatted_time = timestamp.split('.')[0]

                # Create labels for each piece of data
                timestamp_label = ctk.CTkLabel(self.scrollable_frame, text=formatted_time, font=self.main_font, anchor="w")
                user_label = ctk.CTkLabel(self.scrollable_frame, text=user, font=self.main_font, anchor="w")
                action_label = ctk.CTkLabel(self.scrollable_frame, text=action, font=self.main_font, anchor="w")
                details_label = ctk.CTkLabel(self.scrollable_frame, text=details, font=self.main_font, anchor="w", wraplength=300, justify="left")

                # Place labels in the grid
                timestamp_label.grid(row=row_index, column=0, padx=10, pady=5, sticky="w")
                user_label.grid(row=row_index, column=1, padx=10, pady=5, sticky="w")
                action_label.grid(row=row_index, column=2, padx=10, pady=5, sticky="w")
                details_label.grid(row=row_index, column=3, padx=10, pady=5, sticky="w")
