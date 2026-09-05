from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.database import create_tables, get_connection
from backend.services.recovery_scoring import calculate_recovery_score
from backend.services.orchestrator import process_transaction
from backend.services.metrics import get_recovery_metrics

from backend.services.batch_recovery import process_all_transactions




# ========================================
# APPLICATION LIFESPAN
# ========================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    create_tables()

    yield


# ========================================
# FASTAPI APPLICATION
# ========================================

app = FastAPI(
    title="RevenueAI",
    description="AI-powered payment recovery system",
    version="1.0.0",
    lifespan=lifespan
)


# ========================================
# CORS
# ========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# HOME
# ========================================

@app.get("/")
def home():

    return {
        "message": "RevenueAI API is running!"
    }


# ========================================
# GET TRANSACTIONS
# ========================================

@app.get("/transactions")
def get_transactions():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 
            t.*,
            r.recovery_score,
            r.recovery_category,
            r.ai_decision,
            r.ai_action,
            r.recovery_success
        FROM transactions t
        LEFT JOIN (
            SELECT 
                transaction_id,
                recovery_score,
                recovery_category,
                ai_decision,
                ai_action,
                recovery_success
            FROM recovery_logs
            WHERE id IN (
                SELECT MAX(id)
                FROM recovery_logs
                GROUP BY transaction_id
            )
        ) r ON t.transaction_id = r.transaction_id
        ORDER BY t.created_at DESC
        LIMIT 500
    """)

    transactions = cursor.fetchall()

    connection.close()

    return {
        "count": len(transactions),
        "transactions": [
            dict(transaction)
            for transaction in transactions
        ]
    }

# ========================================
# TRANSACTION ANALYSIS
# ========================================

@app.get("/transactions/{transaction_id}/analysis")
def analyze_transaction(transaction_id: str):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE transaction_id = ?
    """, (transaction_id,))

    transaction = cursor.fetchone()

    if transaction is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    transaction_data = dict(transaction)

    # Calculate the recovery score
    recovery_analysis = calculate_recovery_score(transaction_data)

    # Get the latest saved recovery result
    cursor.execute("""
        SELECT *
        FROM recovery_logs
        WHERE transaction_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (transaction_id,))

    recovery_log = cursor.fetchone()

    connection.close()

    return {
        "transaction": transaction_data,
        "recovery_analysis": recovery_analysis,
        "recovery_log": dict(recovery_log) if recovery_log else None
    }


# ========================================
# RECOVER TRANSACTION
# ========================================

@app.post("/transactions/{transaction_id}/recover")
def recover_transaction(transaction_id: str):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE transaction_id = ?
    """, (transaction_id,))

    transaction = cursor.fetchone()

    connection.close()

    if transaction is None:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    transaction_data = dict(transaction)


    # --------------------------------
    # Run AI recovery
    # --------------------------------

    result = process_transaction(
        transaction_data,
        use_ai=True
    )


    return result


@app.post("/batch-recovery")
def batch_recovery(limit: int = 500, use_ai: bool = True):

    results = process_all_transactions(
        limit=limit,
        use_ai=use_ai
    )

    successful = sum(
        1 for result in results
        if result["recovery_result"]["success"]
    )

    recovered_amount = sum(
        result["recovery_result"]["recovered_amount"]
        for result in results
    )

    return {
        "processed": len(results),
        "successful_recoveries": successful,
        "recovered_amount": recovered_amount,
        "results": results
    }


# ========================================
# RECOVERY LOGS
# ========================================

@app.get("/recovery-logs")
def get_recovery_logs():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM recovery_logs
        ORDER BY created_at DESC
    """)

    logs = cursor.fetchall()

    connection.close()

    return {
        "count": len(logs),
        "logs": [
            dict(log)
            for log in logs
        ]
    }


# ========================================
# METRICS
# ========================================

@app.get("/metrics")
def metrics():

    return get_recovery_metrics()

@app.post("/reset")
def reset_system():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM recovery_logs")
    cur.execute("UPDATE transactions SET status = 'FAILED', attempt_count = 0")
    conn.commit()
    conn.close()
    return {"message": "System reset successfully!"}