# def get_local_recovery_decision(transaction, recovery_analysis):

#     score = recovery_analysis["score"]
#     category = recovery_analysis["category"]
#     failure_reason = transaction["failure_reason"]
#     attempts = transaction["attempt_count"]

#     # Very low recovery potential
#     if category == "LOW":
#         return {
#             "decision": "STOP",
#             "action": "STOP_RECOVERY",
#             "confidence": 0.90,
#             "reason": (
#                 f"Recovery score is LOW ({score}), "
#                 "so further recovery attempts are not recommended."
#             )
#         }

#     # Temporary technical failures
#     if failure_reason in [
#         "NETWORK_TIMEOUT",
#         "GATEWAY_ERROR",
#         "TEMPORARY_SERVER_ERROR"
#     ]:
#         if attempts < 2:
#             return {
#                 "decision": "RECOVER",
#                 "action": "RETRY_PAYMENT",
#                 "confidence": 0.85,
#                 "reason": (
#                     f"{failure_reason} is a temporary failure "
#                     "and the transaction is eligible for retry."
#                 )
#             }

#     # Card-related failures
#     if failure_reason in [
#         "CARD_DECLINED",
#         "PAYMENT_EXPIRED"
#     ]:
#         return {
#             "decision": "RECOVER",
#             "action": "SEND_PAYMENT_LINK",
#             "confidence": 0.80,
#             "reason": (
#                 f"{failure_reason} may require the customer "
#                 "to provide updated payment information."
#             )
#         }

#     # Insufficient funds
#     if failure_reason == "INSUFFICIENT_FUNDS":
#         return {
#             "decision": "RECOVER",
#             "action": "SEND_REMINDER",
#             "confidence": 0.75,
#             "reason": (
#                 "Insufficient funds may be temporary, "
#                 "so a payment reminder is recommended."
#             )
#         }

#     # Invalid card / blocked account
#     if failure_reason in [
#         "INVALID_CARD",
#         "ACCOUNT_BLOCKED"
#     ]:
#         return {
#             "decision": "STOP",
#             "action": "STOP_RECOVERY",
#             "confidence": 0.90,
#             "reason": (
#                 f"{failure_reason} requires customer intervention "
#                 "before another recovery attempt."
#             )
#         }

#     # Medium/high score fallback
#     if category in ["MEDIUM", "HIGH"]:
#         return {
#             "decision": "RECOVER",
#             "action": "SEND_PAYMENT_LINK",
#             "confidence": 0.70,
#             "reason": (
#                 f"Recovery score is {category} ({score}), "
#                 "so an additional recovery action is justified."
#             )
#         }

#     return {
#         "decision": "STOP",
#         "action": "STOP_RECOVERY",
#         "confidence": 0.60,
#         "reason": "No suitable recovery action identified."
#     }

def get_local_recovery_decision(transaction, recovery_analysis):
    score = recovery_analysis["score"]
    category = recovery_analysis["category"]
    failure_reason = transaction["failure_reason"]
    attempts = transaction["attempt_count"]

    if failure_reason in ["NETWORK_TIMEOUT", "GATEWAY_ERROR", "TEMPORARY_SERVER_ERROR"]:
        if attempts < 2:
            return {
                "decision": "RECOVER", "action": "RETRY_PAYMENT",
                "confidence": 0.85,
                "reason": f"{failure_reason} is a temporary failure and eligible for retry."
            }

    if failure_reason in ["CARD_DECLINED", "PAYMENT_EXPIRED"]:
        return {
            "decision": "RECOVER", "action": "SEND_PAYMENT_LINK",
            "confidence": 0.80,
            "reason": f"{failure_reason} may require updated payment information."
        }

    if failure_reason == "INSUFFICIENT_FUNDS":
        return {
            "decision": "RECOVER", "action": "SEND_REMINDER",
            "confidence": 0.75,
            "reason": "Insufficient funds may be temporary; reminder recommended."
        }

    if failure_reason in ["INVALID_CARD", "ACCOUNT_BLOCKED"]:
        return {
            "decision": "STOP", "action": "STOP_RECOVERY",
            "confidence": 0.90,
            "reason": f"{failure_reason} requires customer intervention."
        }

    # Only now fall back to score-based stop, for anything not already handled
    if category == "LOW":
        return {
            "decision": "STOP", "action": "STOP_RECOVERY",
            "confidence": 0.90,
            "reason": f"Recovery score is LOW ({score}); no clear recovery path."
        }

    if category in ["MEDIUM", "HIGH"]:
        return {
            "decision": "RECOVER", "action": "SEND_PAYMENT_LINK",
            "confidence": 0.70,
            "reason": f"Recovery score is {category} ({score}); action justified."
        }

    return {
        "decision": "STOP", "action": "STOP_RECOVERY",
        "confidence": 0.60,
        "reason": "No suitable recovery action identified."
    }