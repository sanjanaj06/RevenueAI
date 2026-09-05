import os
import json

from dotenv import load_dotenv
from google import genai

from backend.services.recovery_scoring import calculate_recovery_score


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


def get_ai_recovery_decision(transaction):

    recovery_analysis = calculate_recovery_score(transaction)

    prompt = f"""
You are RevenueAI, an AI-powered payment recovery agent.

Analyze the following failed payment.

Transaction ID: {transaction["transaction_id"]}
Customer ID: {transaction["customer_id"]}
Amount: ₹{transaction["amount"]}
Payment Method: {transaction["payment_method"]}
Failure Reason: {transaction["failure_reason"]}

Previous Successful Payments: {transaction["previous_successes"]}
Previous Failed Payments: {transaction["previous_failures"]}
Previous Recovery Attempts: {transaction["attempt_count"]}

Recovery Score: {recovery_analysis["score"]}
Recovery Category: {recovery_analysis["category"]}

Choose ONE recommended action:

- RETRY_PAYMENT
- SEND_PAYMENT_LINK
- SEND_REMINDER
- STOP_RECOVERY

Rules:

1. Temporary technical failures such as NETWORK_TIMEOUT,
   GATEWAY_ERROR, and TEMPORARY_SERVER_ERROR are good
   candidates for RETRY_PAYMENT.

2. CARD_DECLINED or PAYMENT_EXPIRED may be better candidates
   for SEND_PAYMENT_LINK.

3. INSUFFICIENT_FUNDS should generally use SEND_REMINDER.

4. INVALID_CARD and ACCOUNT_BLOCKED should generally use
   STOP_RECOVERY.

5. If the recovery score is LOW, prefer STOP_RECOVERY.

6. Never recommend unlimited retries.

Return ONLY valid JSON using exactly this structure:

{{
    "decision": "RECOVER or STOP",
    "action": "RETRY_PAYMENT or SEND_PAYMENT_LINK or SEND_REMINDER or STOP_RECOVERY",
    "confidence": 0.0,
    "reason": "short explanation"
}}
"""

    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    response_text = interaction.output_text.strip()

    # Remove markdown code fences if Gemini adds them
    if response_text.startswith("```"):
        response_text = response_text.replace("```json", "")
        response_text = response_text.replace("```", "")
        response_text = response_text.strip()

    try:
        decision = json.loads(response_text)
    except json.JSONDecodeError:
        raise ValueError(
            f"Gemini returned invalid JSON: {response_text}"
        )

    return {
        "recovery_analysis": recovery_analysis,
        "ai_decision": decision
    }