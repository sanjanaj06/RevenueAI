FAILURE_SCORES = {
    "NETWORK_TIMEOUT": 40,
    "GATEWAY_ERROR": 35,
    "TEMPORARY_SERVER_ERROR": 35,
    "CARD_DECLINED": 25,
    "PAYMENT_EXPIRED": 25,
    "INSUFFICIENT_FUNDS": 10,
    "INVALID_CARD": 5,
    "ACCOUNT_BLOCKED": 0
}


def calculate_recovery_score(transaction):
    # 1. Failure reason score
    failure_score = FAILURE_SCORES.get(
        transaction["failure_reason"],
        0
    )

    # 2. Customer history score
    successes = transaction["previous_successes"]
    failures = transaction["previous_failures"]

    total_history = successes + failures

    if total_history == 0:
        history_score = 15
    else:
        success_rate = successes / total_history
        history_score = round(success_rate * 30)

    # 3. Previous failure score
    previous_failures_score = max(
        20 - (failures * 5),
        0
    )

    # 4. Previous recovery attempt score
    attempts = transaction["attempt_count"]

    if attempts == 0:
        attempt_score = 10
    elif attempts == 1:
        attempt_score = 5
    else:
        attempt_score = 0

    # Final score
    total_score = (
        failure_score
        + history_score
        + previous_failures_score
        + attempt_score
    )

    # Make sure score stays between 0 and 100
    total_score = min(max(total_score, 0), 100)

    if total_score >= 80:
        category = "HIGH"
    elif total_score >= 60:
        category = "MEDIUM"
    else:
        category = "LOW"

    return {
        "score": total_score,
        "category": category,
        "breakdown": {
            "failure_reason": failure_score,
            "customer_history": history_score,
            "previous_failures": previous_failures_score,
            "recovery_attempts": attempt_score
        }
    }