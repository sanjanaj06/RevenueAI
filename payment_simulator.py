import hashlib

def simulate_payment_recovery(transaction, action, attempt=1):

    failure_reason = transaction["failure_reason"]

    # Actions that do not attempt payment
    if action in ["STOP_RECOVERY", "SEND_REMINDER"]:
        return {
            "success": False,
            "recovered_amount": 0,
            "message": "No payment attempt was made."
        }

    # Base recovery probabilities
    recovery_probability = {
        "NETWORK_TIMEOUT": 0.80,
        "GATEWAY_ERROR": 0.75,
        "TEMPORARY_SERVER_ERROR": 0.75,
        "CARD_DECLINED": 0.45,
        "PAYMENT_EXPIRED": 0.50,
        "INSUFFICIENT_FUNDS": 0.25,
        "INVALID_CARD": 0.05,
        "ACCOUNT_BLOCKED": 0.02
    }

    probability = recovery_probability.get(
        failure_reason,
        0.10
    )

    # Include attempt number in hash so retries get independent chances!
    seed_string = f"{transaction['transaction_id']}_attempt_{attempt}"
    hash_value = hashlib.md5(seed_string.encode()).hexdigest()

    numeric_value = int(hash_value[:8], 16)
    random_value = numeric_value / 0xFFFFFFFF

    success = random_value < probability

    if success:
        return {
            "success": True,
            "recovered_amount": transaction["amount"],
            "message": "Payment successfully recovered."
        }

    return {
        "success": False,
        "recovered_amount": 0,
        "message": "Recovery attempt failed."
    }