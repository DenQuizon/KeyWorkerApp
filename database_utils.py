import hashlib
import sqlite3

def log_activity(user, action, details=""):
    try:
        con = sqlite3.connect('alyson_house.db')
        cur = con.cursor()
        cur.execute("INSERT INTO activity_log (user, action, details) VALUES (?, ?, ?)", (user, action, details))
        con.commit()
        con.close()
    except sqlite3.Error as e:
        print(f"Database error while logging activity: {e}")

def get_activity_log():
    try:
        con = sqlite3.connect('alyson_house.db')
        cur = con.cursor()
        cur.execute("SELECT timestamp, user, action, details FROM activity_log ORDER BY timestamp DESC")
        logs = cur.fetchall()
        con.close()
        return logs
    except sqlite3.Error as e:
        print(f"Database error getting activity log: {e}")
        return []

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    con = sqlite3.connect('alyson_house.db')
    cur = con.cursor()
    cur.execute("SELECT id, username, password_hash, role, first_login FROM users WHERE username = ?", (username,))
    result = cur.fetchone()
    con.close()
    if result and result[2] == hash_password(password):
        return {"id": result[0], "username": result[1], "role": result[3], "first_login": result[4]}
    return None

def get_all_app_users():
    con = sqlite3.connect('alyson_house.db')
    cur = con.cursor()
    cur.execute("SELECT id, username, role FROM users ORDER BY username")
    users = cur.fetchall()
    con.close()
    return users

def add_app_user(username, password, role):
    try:
        con = sqlite3.connect('alyson_house.db')
        cur = con.cursor()
        # New users always start with first_login = 1
        cur.execute("INSERT INTO users (username, password_hash, role, first_login) VALUES (?, ?, ?, 1)", (username, hash_password(password), role))
        con.commit()
        con.close()
        return True
    except sqlite3.IntegrityError:
        con.close()
        return False

def delete_app_user(user_id):
    con = sqlite3.connect('alyson_house.db')
    cur = con.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    con.commit()
    con.close()

def reset_app_user_password(user_id, new_password):
    try:
        con = sqlite3.connect('alyson_house.db')
        cur = con.cursor()
        new_password_hash = hash_password(new_password)
        # When resetting, force user to change password on next login
        cur.execute("UPDATE users SET password_hash = ?, first_login = 1 WHERE id = ?", (new_password_hash, user_id))
        con.commit()
        con.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error resetting password: {e}")
        return False

def change_user_password(user_id, new_password):
    """Changes a user's password and sets their first_login flag to 0."""
    try:
        con = sqlite3.connect('alyson_house.db')
        cur = con.cursor()
        new_password_hash = hash_password(new_password)
        cur.execute("UPDATE users SET password_hash = ?, first_login = 0 WHERE id = ?", (new_password_hash, user_id))
        con.commit()
        con.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error changing password: {e}")
        return False

def add_service_user(name, dob, performed_by):
    if add_service_user_db(name, dob):
        log_activity(performed_by, "ADD SERVICE USER", f"Added: {name}")
        return True
    return False

def add_service_user_db(name, dob):
    try:
        con = sqlite3.connect('alyson_house.db')
        cur = con.cursor()
        cur.execute("INSERT INTO service_users (name, date_of_birth) VALUES (?, ?)", (name, dob))
        con.commit()
        con.close()
        return True
    except sqlite3.IntegrityError:
        con.close()
        return False

def get_all_service_users():
    con = sqlite3.connect('alyson_house.db')
    cur = con.cursor()
    cur.execute("SELECT id, name, date_of_birth FROM service_users ORDER BY name")
    users = cur.fetchall()
    con.close()
    return users

def update_service_user(user_id, new_name, new_dob, performed_by):
    if update_service_user_db(user_id, new_name, new_dob):
        log_activity(performed_by, "UPDATE SERVICE USER", f"Updated ID {user_id} to Name: {new_name}, DOB: {new_dob}")
        return True
    return False

def update_service_user_db(user_id, new_name, new_dob):
    try:
        con = sqlite3.connect('alyson_house.db')
        cur = con.cursor()
        cur.execute("UPDATE service_users SET name = ?, date_of_birth = ? WHERE id = ?", (new_name, new_dob, user_id))
        con.commit()
        con.close()
        return True
    except sqlite3.IntegrityError:
        con.close()
        return False

def delete_service_user(user_id, performed_by):
    con = sqlite3.connect('alyson_house.db')
    cur = con.cursor()
    cur.execute("SELECT name FROM service_users WHERE id = ?", (user_id,))
    user_to_delete = cur.fetchone()
    if user_to_delete:
        user_name = user_to_delete[0]
        cur.execute("DELETE FROM forms WHERE service_user_id = ?", (user_id,))
        cur.execute("DELETE FROM service_users WHERE id = ?", (user_id,))
        con.commit()
        log_activity(performed_by, "DELETE SERVICE USER", f"Deleted: {user_name} (ID: {user_id})")
    con.close()

def get_form_data(service_user_id, form_month_year):
    con = sqlite3.connect('alyson_house.db')
    con.row_factory = sqlite3.Row 
    cur = con.cursor()
    cur.execute("SELECT * FROM forms WHERE service_user_id = ? AND form_month_year = ?", (service_user_id, form_month_year))
    form_data = cur.fetchone()
    con.close()
    return dict(form_data) if form_data else None

def get_appointments(form_id):
    con = sqlite3.connect('alyson_house.db')
    cur = con.cursor()
    cur.execute("SELECT name, last_seen, next_due, booked FROM appointments WHERE form_id = ?", (form_id,))
    appointments = cur.fetchall()
    con.close()
    return appointments

def save_form_data(form_data_dict, performed_by):
    form_id = save_form_data_db(form_data_dict)
    if form_id:
        details = f"Saved form for {form_data_dict.get('service_user_name')} for month {form_data_dict.get('form_month_year')}"
        log_activity(performed_by, "SAVE FORM", details)
    return form_id

def save_form_data_db(form_data_dict):
    con = sqlite3.connect('alyson_house.db')
    cur = con.cursor()
    columns = [
        'service_user_id', 'form_month_year', 'key_worker_name', 'session_datetime',
        'weight', 'bp', 'weight_bp_comments', 'health_concerns', 'health_concerns_comments',
        'nails_check', 'nails_date', 'nails_comments', 'hair_check', 'hair_date', 'hair_comments',
        'mar_sheets_check', 'mar_sheets_comments', 'finance_cash_box', 'finance_top_up', 'finance_take_out',
        'finance_diary_datetime', 'finance_diary_staff', 'shop_q1_toiletries', 'shop_q2_clothes',
        'shop_q3_personal_items', 'caredocs_contacts', 'caredocs_careplan', 'caredocs_meds',
        'caredocs_bodymap', 'caredocs_charts', 'health_plan_file', 'actions_required',
        'family_comm_made', 'family_comm_datetime', 'family_comm_reason', 'family_comm_issues',
        'current_goal', 'last_goal_progress', 'feeling_response', 'happy_response', 'other_notes'
    ]
    cur.execute(
        "SELECT id FROM forms WHERE service_user_id = ? AND form_month_year = ?",
        (form_data_dict['service_user_id'], form_data_dict['form_month_year'])
    )
    result = cur.fetchone()
    existing_form_id = result[0] if result else None

    if existing_form_id:
        form_id = existing_form_id
        update_cols = [col for col in columns if col in form_data_dict]
        set_clause = ", ".join([f"{col} = ?" for col in update_cols])
        values = [form_data_dict.get(col) for col in update_cols]
        values.append(form_id)
        cur.execute(f"UPDATE forms SET {set_clause} WHERE id = ?", values)
    else:
        insert_cols = [col for col in columns if col in form_data_dict]
        placeholders = ", ".join(["?"] * len(insert_cols))
        cols_clause = ", ".join(insert_cols)
        values = [form_data_dict.get(col) for col in insert_cols]
        cur.execute(f"INSERT INTO forms ({cols_clause}) VALUES ({placeholders})", values)
        form_id = cur.lastrowid
    
    con.commit()
    con.close()
    return form_id

def save_appointments(form_id, appointments_list):
    con = sqlite3.connect('alyson_house.db')
    cur = con.cursor()
    cur.execute("DELETE FROM appointments WHERE form_id = ?", (form_id,))
    if appointments_list:
        cur.executemany(
            "INSERT INTO appointments (form_id, name, last_seen, next_due, booked) VALUES (?, ?, ?, ?, ?)",
            [(form_id, *appt) for appt in appointments_list]
        )
    con.commit()
    con.close()
