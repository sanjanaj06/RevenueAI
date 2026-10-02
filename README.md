# RevenueAI – AI Revenue Recovery System

RevenueAI is an AI-powered payment recovery system designed to analyze failed transactions, determine the likelihood of successful recovery, and recommend safe recovery actions. The system combines rule-based business logic, recovery scoring, AI-based decision-making, and policy validation to automate payment recovery while maintaining safety and auditability.

## 🚀 Problem Statement

Failed payments can result in significant revenue loss for businesses. Manually analyzing every failed transaction and deciding whether to retry, send a payment link, or stop recovery can be inefficient.

RevenueAI addresses this problem by:

- Analyzing failed transactions automatically
- Calculating a recovery score for each transaction
- Using AI to recommend an appropriate recovery action
- Applying deterministic safety and business rules before execution
- Simulating recovery attempts
- Maintaining audit logs of every recovery decision

## 🎯 Objectives

- Automate the analysis of failed payment transactions
- Estimate the possibility of successful recovery
- Recommend appropriate recovery actions
- Prevent unsafe or invalid recovery attempts
- Simulate the payment recovery process
- Maintain an auditable record of recovery decisions
- Provide a scalable backend architecture for AI-driven revenue recovery

## 🔄 System Workflow

```text
Failed Transaction
        ↓
Transaction Analysis
        ↓
Recovery Score Calculation
        ↓
AI / Rule-Based Recovery Decision
        ↓
Recovery Policy Validation
        ↓
 ┌──────┴─────────┐
 ↓                ↓
Allowed          Blocked
 ↓                ↓
Recovery         Stop Recovery
Simulation       Safely
 ↓
Recovery Result
 ↓
Audit Log
````

## 🧠 Recovery Scoring

RevenueAI calculates a recovery score based on transaction-related factors such as:

* Failure reason
* Customer payment history
* Previous payment failures
* Number of recovery attempts

The score is used to classify transactions into categories such as:

```text
LOW
MEDIUM
HIGH
```

The score helps the system determine whether a transaction should be considered for recovery.

## 🤖 AI Recovery Decision

The AI layer analyzes the transaction and recommends an action such as:

```text
RECOVER
STOP_RECOVERY
```

For recovery cases, the system can recommend actions such as:

```text
SEND_PAYMENT_LINK
RETRY_PAYMENT
```

However, AI decisions are not executed directly.

## 🛡️ Recovery Policy & Safety Layer

RevenueAI uses a deterministic policy layer between the AI decision and the recovery execution.

```text
AI Decision
     ↓
Recovery Policy
     ↓
Allowed? ── No ──→ Block Action
     │
    Yes
     ↓
Execute Recovery
```

This prevents the AI from performing actions that violate predefined business and safety rules.

For example:

* Invalid payment methods may prevent automatic retry
* Transactions exceeding the maximum number of recovery attempts can be stopped
* Unsafe recovery actions can be blocked
* Every decision is recorded for auditing

This hybrid approach combines AI flexibility with deterministic business rules.

## 💳 Payment Recovery Simulation

RevenueAI includes a payment simulator to demonstrate the recovery process without processing real payments.

When a simulated recovery succeeds:

```text
Recovered Amount = Transaction Amount
```

When recovery fails or is stopped:

```text
Recovered Amount = ₹0
```

## 📊 Audit Logging

Every recovery decision is stored in the recovery logs.

The audit information includes details such as:

* Transaction ID
* Recovery decision
* Recommended action
* Policy validation result
* Recovery success/failure
* Recovered amount
* Confidence
* Decision message

This provides traceability and makes the system easier to monitor and debug.

## ⚙️ Tech Stack

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic

### Data Processing

* Pandas
* NumPy

### AI

* Google Gemini API
* Local rule-based fallback

### Database / Logging

* Transaction data storage
* Recovery audit logs

### Development Tools

* VS Code
* Git
* GitHub
* Python Virtual Environment

## 🔌 API

RevenueAI provides a FastAPI backend.

## 🛠️ Installation

Clone the repository:

```bash
git clone https://github.com/sanjanaj06/RevenueAI.git
cd RevenueAI
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🔑 Environment Variables

Create a `.env` file and add the required API configuration:

```env
GEMINI_API_KEY=your_api_key_here
```

Do not commit API keys or other sensitive credentials to GitHub.

## ▶️ Running the Application

Start the FastAPI server:

```bash
python -m uvicorn backend.main:app --reload
```

The API will be available locally at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```
## 🚀 Future Enhancements

Possible future improvements include:

* Real payment gateway integration
* Real-time transaction monitoring
* Advanced customer segmentation
* More sophisticated recovery prediction models
* Dashboard for recovery analytics
* Email/SMS/WhatsApp recovery notifications
* Machine-learning-based recovery probability
* A/B testing of recovery strategies
* Advanced revenue forecasting
* Cloud deployment and scalable processing
