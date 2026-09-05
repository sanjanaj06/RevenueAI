from backend.database import get_connection


connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    DELETE FROM recovery_logs
""")

connection.commit()

print("All test recovery logs have been cleared.")

connection.close()