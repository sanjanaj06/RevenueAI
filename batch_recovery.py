# from backend.database import get_connection
# from backend.services.orchestrator import process_transaction


# def process_all_transactions(limit=5, use_ai=False):

#     connection = get_connection()
#     cursor = connection.cursor()

#     cursor.execute("""
#         SELECT *
#         FROM transactions
#         WHERE status = 'FAILED'
#         AND transaction_id NOT IN (
#             SELECT transaction_id
#             FROM recovery_logs
#         )
#         ORDER BY transaction_id
#         LIMIT ?
#     """, (limit,))

#     transactions = cursor.fetchall()

#     connection.close()

#     results = []

#     for transaction in transactions:

#         transaction_data = dict(transaction)

#         result = process_transaction(
#             transaction_data,
#             use_ai=False
#         )

#         results.append(result)

#     return results

from backend.database import get_connection
from backend.services.orchestrator import process_transaction


def process_all_transactions(limit=5, use_ai=False):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE status = 'FAILED'
        AND transaction_id NOT IN (
            SELECT transaction_id
            FROM recovery_logs
        )
        ORDER BY transaction_id
        LIMIT ?
    """, (limit,))

    transactions = cursor.fetchall()

    connection.close()

    results = []

    for transaction in transactions:

        transaction_data = dict(transaction)

        result = process_transaction(
            transaction_data,
            use_ai=use_ai
        )

        results.append(result)

    return results