# from backend.database import get_connection


# def get_recovery_metrics():

#     connection = get_connection()
#     cursor = connection.cursor()

#     # Total failed transactions
#     cursor.execute("""
#         SELECT COUNT(*)
#         FROM transactions
#         WHERE status = 'FAILED'
#     """)

#     total_failed = cursor.fetchone()[0]

#     # Total failed revenue
#     cursor.execute("""
#         SELECT COALESCE(SUM(amount), 0)
#         FROM transactions
#         WHERE status = 'FAILED'
#     """)

#     total_failed_revenue = cursor.fetchone()[0]

#     # Total recovery decisions
#     cursor.execute("""
#         SELECT COUNT(*)
#         FROM recovery_logs
#     """)

#     total_recovery_decisions = cursor.fetchone()[0]

#     # Successful recoveries
#     cursor.execute("""
#         SELECT COUNT(*)
#         FROM recovery_logs
#         WHERE recovery_success = 1
#     """)

#     successful_recoveries = cursor.fetchone()[0]

#     # Revenue recovered
#     cursor.execute("""
#         SELECT COALESCE(SUM(recovered_amount), 0)
#         FROM recovery_logs
#     """)

#     revenue_recovered = cursor.fetchone()[0]

#     connection.close()

#     if total_failed > 0:
#         recovery_rate = (
#             successful_recoveries / total_failed
#         ) * 100
#     else:
#         recovery_rate = 0

#     if total_failed_revenue > 0:
#         revenue_recovery_percentage = (
#             revenue_recovered / total_failed_revenue
#         ) * 100
#     else:
#         revenue_recovery_percentage = 0

#     return {
#         "total_failed_transactions": total_failed,
#         "total_failed_revenue": total_failed_revenue,
#         "recovery_decisions": total_recovery_decisions,
#         "successful_recoveries": successful_recoveries,
#         "revenue_recovered": revenue_recovered,
#         "recovery_rate": round(recovery_rate, 2),
#         "revenue_recovery_percentage": round(
#             revenue_recovery_percentage,
#             2
#         )
#     }

from backend.database import get_connection


def get_recovery_metrics():

    connection = get_connection()
    cursor = connection.cursor()

    # Total failed transactions
    cursor.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE status = 'FAILED'
    """)

    total_failed = cursor.fetchone()[0]

    # Total failed revenue
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE status = 'FAILED'
    """)

    total_failed_revenue = cursor.fetchone()[0]

    # Total recovery decisions
    cursor.execute("""
        SELECT COUNT(*)
        FROM recovery_logs
    """)

    total_recovery_decisions = cursor.fetchone()[0]

    # Successful recoveries
    cursor.execute("""
        SELECT COUNT(*)
        FROM recovery_logs
        WHERE recovery_success = 1
    """)

    successful_recoveries = cursor.fetchone()[0]

    # Revenue recovered
    cursor.execute("""
        SELECT COALESCE(SUM(recovered_amount), 0)
        FROM recovery_logs
    """)

    revenue_recovered = cursor.fetchone()[0]

    # Attempted recoveries (actions that could actually recover money)
    cursor.execute("""
        SELECT COUNT(*)
        FROM recovery_logs
        WHERE ai_action IN ('RETRY_PAYMENT', 'SEND_PAYMENT_LINK')
    """)

    attempted_recoveries = cursor.fetchone()[0]

    # Successful attempts, out of those attempted recoveries
    cursor.execute("""
        SELECT COUNT(*)
        FROM recovery_logs
        WHERE ai_action IN ('RETRY_PAYMENT', 'SEND_PAYMENT_LINK')
        AND recovery_success = 1
    """)

    successful_attempts = cursor.fetchone()[0]

    connection.close()

    if total_failed > 0:
        recovery_rate = (
            successful_recoveries / total_failed
        ) * 100
    else:
        recovery_rate = 0

    if total_failed_revenue > 0:
        revenue_recovery_percentage = (
            revenue_recovered / total_failed_revenue
        ) * 100
    else:
        revenue_recovery_percentage = 0

    if attempted_recoveries > 0:
        attempted_success_rate = (
            successful_attempts / attempted_recoveries
        ) * 100
    else:
        attempted_success_rate = 0

    return {
        "total_failed_transactions": total_failed,
        "total_failed_revenue": total_failed_revenue,
        "recovery_decisions": total_recovery_decisions,
        "successful_recoveries": successful_recoveries,
        "revenue_recovered": revenue_recovered,
        "recovery_rate": round(recovery_rate, 2),
        "revenue_recovery_percentage": round(
            revenue_recovery_percentage,
            2
        ),
        "attempted_recoveries": attempted_recoveries,
        "attempted_success_rate": round(
            attempted_success_rate,
            2
        )
    }