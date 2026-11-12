# RESTful API Contract Specification
## Project Name: BillKind AI
### AI-Powered Essential Bills Crowdfunding & Financial Assistance Platform
**Document Version:** 1.0.0  
**Status:** Approved for Implementation (Phase 1 Deliverable)  
**Base URL:** `http://localhost:8000/api/v1` (Production: `https://api.billkind.ai/api/v1`)  
**Date:** November 2026  

---

## 1. Global API Standards & Conventions

### 1.1 Headers & Content Negotiation
- **Content-Type:** `application/json` (except file uploads which use `multipart/form-data`).
- **Authorization:** Bearer token in standard HTTP header: `Authorization: Bearer <access_token>`.
- **Idempotency-Key:** Header required on financial mutations (`POST /payments/checkout`, `POST /donations`).

### 1.2 Unified Success & Error Schemas

#### Standard Success Response Structure
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 142
  }
}
```

#### Standard Error Response Structure (RFC 7807 Compliant)
```json
{
  "success": false,
  "error": {
    "code": "BILL_OVERFUNDING_PROHIBITED",
    "message": "Donation amount of ₹2,500 exceeds the remaining funding balance of ₹1,800.",
    "status": 400,
    "timestamp": "2026-11-08T10:15:30Z",
    "field_errors": [
      {
        "field": "amount",
        "issue": "Exceeds remaining bill capacity"
      }
    ]
  }
}
```

---

## 2. Authentication & User Management Endpoints

| Method | Path | Auth / Role | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Public | Register new user (`beneficiary`, `donor`, `admin`) |
| `POST` | `/auth/login` | Public | Authenticate user, return JWT access token & set refresh cookie |
| `POST` | `/auth/refresh` | Cookie (Refresh Token) | Rotate refresh token and issue new access token |
| `POST` | `/auth/logout` | Authenticated | Revoke refresh token and clear session cookies |
| `POST` | `/auth/forgot-password` | Public | Request password reset email token |
| `POST` | `/auth/reset-password` | Public | Verify reset token and set new password |
| `GET` | `/users/me` | Authenticated | Retrieve authenticated user profile and roles |
| `PATCH` | `/users/me` | Authenticated | Update user name, phone, or notification preferences |
| `GET` | `/users/{user_id}` | Admin | Retrieve user details with audit history |

### Sample: `POST /auth/register`
**Request Payload:**
```json
{
  "email": "beneficiary@example.com",
  "password": "SecurePassword123!",
  "full_name": "Lakshmi Rao",
  "phone_number": "+919876543210",
  "role": "beneficiary",
  "city": "Guntur",
  "state": "Andhra Pradesh",
  "postal_code": "522001"
}
```
**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "email": "beneficiary@example.com",
    "full_name": "Lakshmi Rao",
    "role": "beneficiary",
    "is_email_verified": false,
    "created_at": "2026-11-08T10:00:00Z"
  },
  "message": "Account registered successfully. Please verify your email."
}
```

---

## 3. Bill Ingestion & Management Endpoints

| Method | Path | Auth / Role | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/bills` | Beneficiary | Create a new draft bill assistance request |
| `POST` | `/bills/{bill_id}/upload` | Beneficiary | Upload bill document (PDF/Image multipart) |
| `GET` | `/bills` | Public | Browse verified public bill requests (filtered & paginated) |
| `GET` | `/bills/{bill_id}` | Public / Authenticated | Get bill details (PII redacted for public) |
| `PATCH` | `/bills/{bill_id}` | Beneficiary / Admin | Update narrative or bill fields before verification |
| `DELETE` | `/bills/{bill_id}` | Beneficiary / Admin | Withdraw or delete unverified request |
| `GET` | `/bills/{bill_id}/document-url` | Owner / Admin | Generate short-lived presigned document preview URL |

### Sample: `POST /bills`
**Request Payload:**
```json
{
  "category": "electricity",
  "bill_provider": "APCPDCL - Southern Power",
  "bill_number": "EB-987452",
  "bill_amount": 5200.00,
  "requested_amount": 5200.00,
  "currency": "INR",
  "due_date": "2026-11-20",
  "narrative_description": "Single parent experiencing temporary income loss due to medical leave. Requesting support to keep electricity on."
}
```
**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "7ca8b820-9dad-11d1-80b4-00c04fd430c9",
    "category": "electricity",
    "bill_provider": "APCPDCL - Southern Power",
    "bill_amount": 5200.00,
    "requested_amount": 5200.00,
    "raised_amount": 0.00,
    "currency": "INR",
    "due_date": "2026-11-20",
    "verification_status": "submitted",
    "funding_status": "unfunded"
  }
}
```

---

## 4. Verification, Review & Fraud Triage Endpoints

| Method | Path | Auth / Role | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/bills/{bill_id}/verify` | System / Admin | Trigger LangGraph verification pipeline |
| `GET` | `/bills/{bill_id}/verification` | Owner / Admin | Retrieve verification & fraud assessment status |
| `GET` | `/admin/review-queue` | Admin | List flagged and pending bills requiring manual review |
| `POST` | `/admin/bills/{bill_id}/approve` | Admin | Authorize bill request for public listing |
| `POST` | `/admin/bills/{bill_id}/reject` | Admin | Reject bill request with explanation notes |
| `POST` | `/admin/bills/{bill_id}/request-corrections`| Admin | Request beneficiary to re-upload or correct values |

### Sample: `GET /bills/{bill_id}/verification`
**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "bill_id": "7ca8b820-9dad-11d1-80b4-00c04fd430c9",
    "verification_status": "under_review",
    "extracted_data": {
      "provider_name": "APCPDCL - Southern Power",
      "bill_number": "EB-987452",
      "extracted_amount": 5200.00,
      "due_date": "2026-11-20",
      "ocr_confidence": 0.96,
      "extraction_confidence": 0.94
    },
    "fraud_assessment": {
      "risk_score": 0.12,
      "risk_level": "low",
      "recommended_action": "auto_proceed",
      "risk_reasons": [],
      "evaluated_at": "2026-11-08T10:05:12Z"
    }
  }
}
```

---

## 5. Intelligent Donor Matching Endpoints

| Method | Path | Auth / Role | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/matching/recommendations` | Donor | Retrieve personalized bill recommendations |
| `POST` | `/matching/preferences` | Donor | Update donor category, urgency, and location preferences |
| `GET` | `/matching/preferences` | Donor | Fetch current donor preference profile |

### Sample: `GET /matching/recommendations`
**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "bill_id": "7ca8b820-9dad-11d1-80b4-00c04fd430c9",
      "category": "electricity",
      "title": "Electricity bill assistance",
      "location": "Guntur, Andhra Pradesh",
      "bill_amount": 5200.00,
      "raised_amount": 3400.00,
      "remaining_amount": 1800.00,
      "due_date": "2026-11-20",
      "match_score": 0.94,
      "match_reason": "Matches your preference for urgent utility bills in Andhra Pradesh."
    }
  ]
}
```

---

## 6. Payments, Webhooks & Ledgers Endpoints

| Method | Path | Auth / Role | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/payments/checkout` | Donor | Initialize payment order (Razorpay/Stripe/Mock) |
| `POST` | `/payments/webhook` | External Gateway | Verify HMAC signature & settle payment idempotently |
| `GET` | `/payments/{payment_id}` | Authenticated | Inspect payment transaction and settlement status |
| `POST` | `/admin/refunds` | Admin | Execute gateway refund and update ledger |
| `GET` | `/donations/{donation_id}/receipt` | Donor / Admin | Download signed PDF tax donation receipt |

### Sample: `POST /payments/checkout`
**Request Payload:**
```json
{
  "bill_id": "7ca8b820-9dad-11d1-80b4-00c04fd430c9",
  "amount": 1800.00,
  "currency": "INR",
  "is_anonymous": false,
  "donor_message": "Stay strong!",
  "gateway": "razorpay"
}
```
**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "donation_id": "8da9c930-9dad-11d1-80b4-00c04fd430ca",
    "gateway": "razorpay",
    "gateway_order_id": "order_NX82910398",
    "amount": 1800.00,
    "currency": "INR",
    "key_id": "rzp_test_SampleKeyId",
    "checkout_mode": "sandbox"
  }
}
```

---

## 7. AI & RAG Assistance Endpoints

| Method | Path | Auth / Role | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/ai/extract-bill` | Admin / Internal | Trigger synchronous LLM extraction on text payload |
| `POST` | `/ai/assess-fraud` | Admin / Internal | Evaluate fraud features against Scikit-learn/XGBoost models |
| `POST` | `/ai/match-donors` | Internal | Compute batch embeddings and recommendation ranks |
| `POST` | `/ai/chat` | Public / Auth | RAG policy assistant chat with pgvector citations |

### Sample: `POST /ai/chat`
**Request Payload:**
```json
{
  "message": "What happens if a bill is not fully funded before its due date?",
  "conversation_id": "f5e921c0-9dad-11d1-80b4-00c04fd430cb"
}
```
**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "reply": "According to BillKind AI Platform Policy Section 4.2 ('Partial Funding & Due Date Extensions'): if a bill reaches its due date while partially funded, the collected funds are either remitted directly to the utility board toward partial payment, or the beneficiary is granted an administrative extension upon providing updated billing status.",
    "citations": [
      {
        "document_title": "BillKind AI Beneficiary Terms & Disbursement Policy",
        "section": "Section 4.2: Partial Funding & Due Dates",
        "similarity_score": 0.89
      }
    ]
  }
}
```

---

## 8. Dashboard & Aggregated Analytics Endpoints

| Method | Path | Auth / Role | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/dashboard/beneficiary` | Beneficiary | Metric cards, active bills, donations received |
| `GET` | `/dashboard/donor` | Donor | Contribution stats, supported bills, tax summaries |
| `GET` | `/dashboard/admin` | Admin | Platform-wide KPIs, fraud breakdown, transaction health |

---
*End of RESTful API Contract Specification*
