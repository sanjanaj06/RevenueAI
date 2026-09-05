import csv

from backend.database import get_connection


CSV_FILE = "transactions.csv"


def load_transactions():
    connection = get_connection()
    cursor = connection.cursor()

    with open(CSV_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cursor.execute("""
                INSERT OR IGNORE INTO transactions (
                    transaction_id,
                    customer_id,
                    amount,
                    payment_method,
                    failure_reason,
                    previous_successes,
                    previous_failures,
                    attempt_count,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["transaction_id"],
                row["customer_id"],
                float(row["amount"]),
                row["payment_method"],
                row["failure_reason"],
                int(row["previous_successes"]),
                int(row["previous_failures"]),
                int(row["attempt_count"]),
                row["status"],
                row["created_at"]
            ))

    connection.commit()

    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]

    connection.close()

    print(f"Transactions in database: {count}")


if __name__ == "__main__":
    load_transactions()