from backend.database import get_connection

from backend.services.recovery_scoring import (
    calculate_recovery_score
)

from backend.services.ai_recovery import (
    get_ai_recovery_decision
)

from backend.services.local_decision import (
    get_local_recovery_decision
)

from backend.services.recovery_policy import (
    validate_recovery_action
)

from backend.services.payment_simulator import (
    simulate_payment_recovery
)


def process_transaction(transaction, use_ai=False):

    # ========================================
    # RECOVERY SCORE
    # ========================================

    recovery_analysis = calculate_recovery_score(
        transaction
    )


    # ========================================
    # AI OR LOCAL DECISION
    # ========================================

    if use_ai:

        ai_result = get_ai_recovery_decision(
            transaction
        )

        ai_decision = ai_result["ai_decision"]

    else:

        ai_decision = get_local_recovery_decision(
            transaction,
            recovery_analysis
        )


    # ========================================
    # SAFETY POLICY
    # ========================================

    policy_result = validate_recovery_action(
        transaction,
        ai_decision
    )


        # ========================================
    # PAYMENT RECOVERY
    # ========================================

    if policy_result["allowed"]:

        # STOP_RECOVERY means no payment attempt should be made
        if ai_decision["action"] == "STOP_RECOVERY":

            recovery_result = {
                "success": False,
                "recovered_amount": 0,
                "message": "Recovery stopped safely by AI decision."
            }

            attempts_made = transaction.get("attempt_count", 0)

        else:

            from backend.services.recovery_policy import MAX_RECOVERY_ATTEMPTS

            current_attempts = transaction.get("attempt_count", 0)

            # Safety check: Already reached maximum retry limit
            if current_attempts >= MAX_RECOVERY_ATTEMPTS:

                recovery_result = {
                    "success": False,
                    "recovered_amount": 0,
                    "message": f"Maximum recovery attempts ({MAX_RECOVERY_ATTEMPTS}) already reached."
                }

                attempts_made = current_attempts

            else:

                # Make exactly ONE attempt per recovery execution
                attempts_made = current_attempts + 1

                print(
                    f"Recovery attempt {attempts_made}/"
                    f"{MAX_RECOVERY_ATTEMPTS} for "
                    f"{transaction['transaction_id']}"
                )

                # 1. Pass attempt=attempts_made so each attempt gets an independent chance!
                recovery_result = simulate_payment_recovery(
                    transaction,
                    ai_decision["action"],
                    attempt=attempts_made
                )

                # 2. Determine new status
                new_status = "RECOVERED" if recovery_result["success"] else "FAILED"

                # 3. Save attempt count AND status to database
                connection = get_connection()
                cursor = connection.cursor()

                cursor.execute("""
                    UPDATE transactions
                    SET attempt_count = ?,
                        status = ?
                    WHERE transaction_id = ?
                """, (
                    attempts_made,
                    new_status,
                    transaction["transaction_id"]
                ))

                connection.commit()
                connection.close()

                # 4. Update in-memory dictionary returned to frontend
                transaction["attempt_count"] = attempts_made
                transaction["status"] = new_status

                # 5. Clear, helpful messages
                if not recovery_result["success"]:
                    if attempts_made >= MAX_RECOVERY_ATTEMPTS:
                        recovery_result["message"] = (
                            f"Recovery failed after "
                            f"{MAX_RECOVERY_ATTEMPTS} attempts."
                        )
                    else:
                        recovery_result["message"] = (
                            f"Attempt {attempts_made}/{MAX_RECOVERY_ATTEMPTS} failed."
                        )

    else:

        recovery_result = {
            "success": False,
            "recovered_amount": 0,
            "message": "Recovery blocked by safety policy."
        }

        attempts_made = transaction.get("attempt_count", 0)

    # ========================================
    # SAVE AUDIT LOG
    # ========================================

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO recovery_logs (
            transaction_id,
            amount,
            recovery_score,
            recovery_category,
            ai_decision,
            ai_action,
            ai_confidence,
            ai_reason,
            policy_allowed,
            policy_reason,
            recovery_success,
            recovered_amount,
            recovery_message,
            attempt_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        transaction["transaction_id"],
        transaction["amount"],
        recovery_analysis["score"],
        recovery_analysis["category"],
        ai_decision["decision"],
        ai_decision["action"],
        ai_decision["confidence"],
        ai_decision["reason"],
        int(policy_result["allowed"]),
        policy_result["reason"],
        int(recovery_result["success"]),
        recovery_result["recovered_amount"],
        recovery_result["message"],
        attempts_made
    ))

    connection.commit()
    connection.close()


    # ========================================
    # RETURN COMPLETE RESULT
    # ========================================

    return {
        "transaction": transaction,
        "transaction_id": transaction["transaction_id"],
        "amount": transaction["amount"],
        "recovery_analysis": recovery_analysis,
        "ai_decision": ai_decision,
        "policy_check": policy_result,
        "recovery_result": recovery_result,
        "recovery_attempts": attempts_made
    }