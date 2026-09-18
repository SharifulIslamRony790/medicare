import sqlite3

def check_user():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, email, role FROM users_user WHERE email = 'rika12@gmail.com'")
    user = cursor.fetchone()
    
    if user:
        user_id, email, role = user
        print(f"User Found: {email}")
        print(f"Main Role: {role}")
        
        if role == 'staff':
            cursor.execute("SELECT sub_role FROM staff_staff WHERE user_id = ?", (user_id,))
            staff = cursor.fetchone()
            if staff:
                print(f"Staff Sub-role: {staff[0]}")
            else:
                print("Staff profile not found.")
    else:
        print("User rika12@gmail.com not found in the database.")
        
    conn.close()

if __name__ == '__main__':
    check_user()
