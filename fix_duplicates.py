import sqlite3

def fix_duplicates():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Find duplicate time slots
    query = """
    SELECT doctor_id, date, time, COUNT(*) 
    FROM appointments_appointment 
    WHERE status != 'cancelled' 
    GROUP BY doctor_id, date, time 
    HAVING COUNT(*) > 1
    """
    
    cursor.execute(query)
    duplicates = cursor.fetchall()
    
    if not duplicates:
        print("No duplicate appointments found. You should be able to run migrations.")
        return

    print(f"Found {len(duplicates)} duplicate time slots. Fixing...")

    for dup in duplicates:
        doctor_id, date, time, count = dup
        
        # Get all appointments for this slot ordered by id
        cursor.execute("""
            SELECT id FROM appointments_appointment 
            WHERE doctor_id = ? AND date = ? AND time = ? AND status != 'cancelled'
            ORDER BY id
        """, (doctor_id, date, time))
        
        appts = cursor.fetchall()
        
        # Keep the first one, cancel the rest
        first = True
        for appt in appts:
            if first:
                first = False
                continue
            
            appt_id = appt[0]
            print(f"Cancelling duplicate appointment ID {appt_id}...")
            cursor.execute("UPDATE appointments_appointment SET status = 'cancelled' WHERE id = ?", (appt_id,))
            
    conn.commit()
    conn.close()
    print("Done! You can now run 'python manage.py migrate' again.")

if __name__ == '__main__':
    fix_duplicates()
