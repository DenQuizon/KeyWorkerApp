# Key Worker Review Form Application

A secure, standalone desktop application built with Python and CustomTkinter to streamline the process of managing and recording monthly key worker review forms for service users in a care home environment.

---

## 🚀 Key Features

* **Secure Authentication:** A robust login system with differentiated user roles ('Supervisor' and 'Staff').
* **Forced Password Policy:** New users are required to change their temporary password upon their first login, enhancing security.
* **Supervisor Dashboard:** Supervisors have exclusive access to administrative functions, including app user management and activity logging.
* **User & Profile Management:**
    * **Service Users:** Full CRUD (Create, Read, Update, Delete) functionality for service user profiles.
    * **App Users:** Supervisors can create new staff accounts with standardized usernames (`firstname.lastname`) and reset their passwords.
* **Secure Deletion:** Critical actions, such as deleting a service user, require the current user to re-enter their password for confirmation.
* **Dynamic Form Creation:** An intuitive multi-tabbed interface allows for the easy creation, viewing, and saving of detailed monthly review forms.
* **Automated PDF Reporting:** Generates professional, multi-page A4 PDF reports of completed forms that dynamically adjust their length based on the content.
* **Comprehensive Activity Logging:** A detailed, table-based activity log tracks all significant user actions (logins, data entry, deletions) for complete accountability.

---

## 🛠️ Built With

This project was built using the following technologies:

* **Language:** Python
* **GUI Framework:** CustomTkinter
* **Database:** SQLite
* **PDF Generation:** ReportLab
* **Packaging:** PyInstaller

---

## ⚙️ Installation & Setup

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/DenQuizon/KeyWorkerApp.git](https://github.com/DenQuizon/KeyWorkerApp.git)
    cd KeyWorkerApp
    ```
2.  **Install dependencies:**
    It is recommended to use a virtual environment. Once activated, install the required packages.
    ```sh
    pip install -r requirements.txt
    ```
3.  **Run the application:**
    ```sh
    python3 main.py
    ```

---
