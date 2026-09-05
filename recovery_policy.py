MAX_RECOVERY_ATTEMPTS = 2
MAX_TRANSACTION_AMOUNT = 10000


ALLOWED_ACTIONS = {
    "NETWORK_TIMEOUT": ["RETRY_PAYMENT"],
    "GATEWAY_ERROR": ["RETRY_PAYMENT"],
    "TEMPORARY_SERVER_ERROR": ["RETRY_PAYMENT"],
    "CARD_DECLINED": ["SEND_PAYMENT_LINK"],
    "PAYMENT_EXPIRED": ["SEND_PAYMENT_LINK"],
    "INSUFFICIENT_FUNDS": ["SEND_REMINDER"],
    "INVALID_CARD": ["STOP_RECOVERY"],
    "ACCOUNT_BLOCKED": ["STOP_RECOVERY"]
}


def validate_recovery_action(transaction, ai_decision):

    action = ai_decision.get("action")
    failure_reason = transaction["failure_reason"]

    # STOP_RECOVERY is always safe
    if action == "STOP_RECOVERY":
        return {
            "allowed": True,
            "reason": "Recovery stopped safely by AI decision."
    }

    # Rule 1: Never exceed maximum recovery attempts
    if transaction["attempt_count"] >= MAX_RECOVERY_ATTEMPTS:
        return {
            "allowed": False,
            "reason": "Maximum recovery attempts reached."
        }

    # Rule 2: High-value transactions require additional protection
    if transaction["amount"] > MAX_TRANSACTION_AMOUNT:
        return {
            "allowed": False,
            "reason": "Transaction amount exceeds automatic recovery limit."
        }

    # Rule 3: Check whether AI selected an allowed action
    # STOP_RECOVERY is always a safe action
    if action == "STOP_RECOVERY":
        return {
            "allowed": True,
            "reason": "Recovery stopped safely by AI decision."
        }

    allowed_actions = ALLOWED_ACTIONS.get(
        failure_reason,
        ["STOP_RECOVERY"]
    )

    if action not in allowed_actions:
        return {
            "allowed": False,
            "reason": (
                f"Action '{action}' is not allowed for "
                f"failure reason '{failure_reason}'."
            )
        }

    # Rule 4: Low-score transactions should not be automatically recovered
    if ai_decision.get("decision") == "RECOVER":
        # We'll retrieve the score from the AI pipeline later.
        pass

    return {
        "allowed": True,
        "reason": "Recovery action passed all safety checks."
    }