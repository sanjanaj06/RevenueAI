import csv
import random
from datetime import datetime, timedelta


NUM_TRANSACTIONS = 500

FAILURE_REASONS = [
    "NETWORK_TIMEOUT",
    "GATEWAY_ERROR",
    "TEMPORARY_SERVER_ERROR",
    "CARD_DECLINED",
    "PAYMENT_EXPIRED",
    "INSUFFICIENT_FUNDS",
    "INVALID_CARD",
    "ACCOUNT_BLOCKED"
]

PAYMENT_METHODS = [
    "CARD",
    "UPI",
    "NET_BANKING",
    "WALLET"
]


def generate_transaction(transaction_number):
    customer_number = random.randint(1, 150)

    amount = random.randint(500, 20000)

    payment_method = random.choice(PAYMENT_METHODS)

    failure_reason = random.choice(FAILURE_REASONS)

    previous_successes = random.randint(0, 15)
    previous_failures = random.randint(0, 8)

    attempt_count = random.randint(0, 2)

    created_at = datetime.now() - timedelta(
        days=random.randint(0, 30),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    return {
        "transaction_id": f"TX{transaction_number:04d}",
        "customer_id": f"C{customer_number:03d}",
        "amount": amount,
        "payment_method": payment_method,
        "failure_reason": failure_reason,
        "previous_successes": previous_successes,
        "previous_failures": previous_failures,
        "attempt_count": attempt_count,
        "status": "FAILED",
        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
    }


def main():
    transactions = []

    for i in range(1, NUM_TRANSACTIONS + 1):
        transactions.append(generate_transaction(i))

    output_file = "transactions.csv"

    fieldnames = transactions[0].keys()

    with open(output_file, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(transactions)

    print(f"Generated {NUM_TRANSACTIONS} transactions.")
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    main()