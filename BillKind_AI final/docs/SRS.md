# Software Requirements Specification (SRS)
## Project Name: BillKind AI
### AI-Powered Essential Bills Crowdfunding & Financial Assistance Platform
**Document Version:** 1.0.0  
**Status:** Approved for Implementation (Phase 1 Deliverable)  
**Date:** November 2026  

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) describes the functional, non-functional, security, compliance, and architectural requirements for **BillKind AI**. BillKind AI is a production-grade, AI-powered social-impact crowdfunding and financial assistance platform designed to help individuals experiencing acute financial hardship upload verified essential household bills (electricity, water, healthcare, tuition/education, housing/rent) and receive voluntary, transparent financial assistance from donors.

### 1.2 Scope of the System
BillKind AI bridges the trust and verification gap between vulnerable beneficiaries and charitable donors by employing:
- **Intelligent Document Ingestion & Multimodal OCR:** Optical Character Recognition and LLM structured extraction from PDF and image bills.
- **Multilayer AI/ML Fraud & Tamper Detection:** Rule-based checks, perceptual hashing for duplicate detection, and ML anomaly scoring (Isolation Forest and XGBoost) to detect fabricated invoices, altered figures, and suspicious submission patterns.
- **Human-in-the-Loop Review Pipeline:** Orchestrated with LangGraph state machines, ensuring high-risk or ambiguous requests are escalated to trained human administrators before public listing.
- **Intelligent Donor Recommendation Engine:** Multi-criteria weighted matching combining donor preferences, geographical affinity, urgency, and Sentence Transformer semantic similarity.
- **RAG-Powered Policy Chatbot:** Grounded in platform policies, eligibility requirements, and dispute rules using `pgvector` to ensure transparent, hallucination-free guidance.
- **Secure Sandbox & Multi-Gateway Payment Ledger:** Idempotent payment processing via Razorpay (India-oriented), Stripe, and local mock sandbox with atomic double-entry transaction ledgers, prevention of overfunding, and automated receipt generation.

### 1.3 Target Audience & Stakeholders
1. **Beneficiaries:** Individuals or families facing financial distress seeking community funding for verified essential bills.
2. **Donors:** Philanthropic individuals and corporate social responsibility (CSR) entities seeking transparent, fraud-screened micro-impact opportunities.
3. **Platform Administrators / Verification Officers:** Case reviewers and risk analysts managing verification queues, fraud triage, user profiles, and audit trails.
4. **Regulators & Payment Partners:** Entities requiring strict compliance with Know-Your-Customer (KYC), anti-money laundering (AML), and data privacy standards (e.g., India DPDP Act 2023, RBI payment settlement rules, and GDPR principles).

### 1.4 Regulatory & Legal Boundaries
- **Direct-to-Utility vs. Intermediary Fund Handling:** To comply with financial regulations and avoid unregulated deposit taking, BillKind AI implements an audited payment escrow ledger model. Contributions are earmarked directly to specific verified invoices.
- **Data Protection & PII Minimization:** Beneficiary sensitive identifiers (consumer account numbers, full home addresses, national ID numbers) are redacted or hashed. Donor-facing views display masked identifiers (e.g., `EB-****-4912`, "Ward 4, Guntur").
- **No Automated Rejection:** In compliance with ethical AI principles, model predictions (fraud risk scores) never trigger automatic punitive rejection of human applicants. All medium/high-risk scores route requests to manual review.

---

## 2. Overall System Description

### 2.1 User Personas & Characteristics

| Persona | Role | Key Motivations | Technical Proficiency | Primary Workflows |
| :--- | :--- | :--- | :--- | :--- |
| **P1: Lakshmi (Beneficiary)** | Beneficiary | Facing power disconnection; needs immediate financial help for an electricity bill. | Low to Moderate (Smartphone user) | Upload bill photo, review extracted figures, monitor funding progress, receive notifications. |
| **P2: Rajesh (Donor)** | Donor | Wants to fund genuine medical and education needs with full transparency and proof of payment. | Moderate to High (Web & Mobile user) | Browse verified bills, apply category/location filters, receive personalized matches, checkout securely, download tax receipts. |
| **P3: Sarah (Admin/Reviewer)** | Platform Admin | Ensure zero fraudulent payouts, maintain compliance, audit anomalies, inspect flagged bills. | High (Professional operational staff) | Review escalated queues, inspect OCR vs. user input diffs, evaluate ML risk scores, approve/reject/request edits. |

### 2.2 System Operating Context
BillKind AI operates as a cloud-native, responsive web application accessible over HTTPS via modern web browsers (Chrome, Firefox, Safari, Edge) across desktop, tablet, and mobile form factors. Local development is fully self-contained using Docker Compose, providing local PostgreSQL, Redis, Celery workers, and mock payment/AI services.

---

## 3. Functional Requirements Catalog

### 3.1 Module 1: Authentication & User Management
- **FR-AUTH-01:** System shall support user registration with email, password, full name, phone number, and primary role (`beneficiary`, `donor`, `admin`).
- **FR-AUTH-02:** Passwords must be hashed using `Argon2id` or `bcrypt` (minimum work factor 12). Plaintext passwords must never touch logs, storage, or external APIs.
- **FR-AUTH-03:** System shall issue short-lived JWT access tokens (15-30 minutes) and cryptographically secure refresh tokens stored as HTTP-only, SameSite cookies with refresh token rotation and revocation.
- **FR-AUTH-04:** System shall enforce Role-Based Access Control (RBAC) via FastAPI dependencies on all protected endpoints.
- **FR-AUTH-05:** System shall provide secure password reset flows using cryptographically random, one-time, time-expiring tokens sent via email.
- **FR-AUTH-06:** System shall allow administrators to suspend or deactivate accounts, instantly invalidating active sessions.
- **FR-AUTH-07:** System shall apply IP- and user-based rate limiting on all authentication routes (e.g., max 5 login attempts per minute per IP).

### 3.2 Module 2: Bill Upload & Document Storage
- **FR-BILL-01:** Beneficiaries shall be able to create a bill request with metadata: Category (`electricity`, `water`, `medical`, `education`, `rent`, `other`), Bill Provider, Total Amount, Due Date, Assistance Needed, Description, and Currency (default `INR`).
- **FR-BILL-02:** System shall accept document uploads in PDF, PNG, JPG, and JPEG formats up to a maximum file size of 10 MB.
- **FR-BILL-03:** System shall validate file magic bytes (signatures) to prevent executable masquerading.
- **FR-BILL-04:** System shall compute SHA-256 and perceptual hashes (`pHash`) on ingestion to detect identical and visually near-duplicate document submissions.
- **FR-BILL-05:** Documents must be stored in private object storage (AWS S3 or Google Cloud Storage in production, secure local disk volume in development). No document shall be accessible via public, unauthenticated URLs.
- **FR-BILL-06:** Document previews must be served exclusively through short-lived presigned URLs (TTL ≤ 15 minutes) authorized only for the owning beneficiary and authorized administrators.
- **FR-BILL-07:** Beneficiaries may withdraw or edit pending requests prior to administrative verification or initial donation. Once funded or verified, changes require administrative re-verification.

### 3.3 Module 3: OCR & AI-Based Structured Extraction
- **FR-OCR-01:** Uploaded documents shall be preprocessed using PyMuPDF (fitz) and Pillow/OpenCV for deskewing, grayscale normalization, and text layer extraction.
- **FR-OCR-02:** System shall extract raw textual content via PyMuPDF or OCR engines (AWS Textract, Document AI, or local Tesseract fallback).
- **FR-OCR-03:** Extracted text shall be passed to an LLM extraction chain with prompt delimiters and strict JSON output schemas.
- **FR-OCR-04:** Output must be validated against a Pydantic `ExtractedBillDataSchema` containing:
  - `bill_type`, `provider_name`, `customer_name`, `bill_number`, `account_number`, `billing_period`, `bill_amount`, `outstanding_amount`, `due_date`, `currency`, `confidence_score`.
- **FR-OCR-05:** System shall compute field-by-field consistency metrics comparing user-entered values with LLM-extracted values, highlighting discrepancies in amount, due date, or provider name.
- **FR-OCR-06:** Beneficiaries and administrators shall have an interface to review discrepancies and confirm or correct extracted fields.

### 3.4 Module 4: AI/ML Fraud & Tamper Detection
- **FR-FRD-01:** System shall execute a multi-tier fraud assessment on every submitted bill:
  - *Tier A (Rule Engine):* Exact bill number matching, duplicate account IDs across different users, due date in the past (> 30 days) or implausible future (> 180 days), requested amount exceeding bill total.
  - *Tier B (Perceptual & Text Similarity):* Levenshtein distance on provider/account strings and Hamming distance on image `pHash`.
  - *Tier C (ML Anomaly Scoring):* Isolation Forest anomaly model and Scikit-learn/XGBoost classifier analyzing submission frequency, amount deviations from category medians, and extraction confidence.
- **FR-FRD-02:** The engine shall calculate a composite `risk_score` (0.0 to 1.0) and assign a `risk_level` (`low`, `medium`, `high`).
- **FR-FRD-03:** Detailed explainable risk reasons must be logged with each assessment (e.g., `["Duplicate bill number detected across User X", "Amount discrepancy exceeds 15%"]`).
- **FR-FRD-04:** High-risk requests (`risk_score` ≥ 0.70) and Medium-risk requests (0.40 ≤ `risk_score` < 0.70) must be automatically placed into the administrator review queue with recommended triage actions (`manual_review`). No automatic rejection is permitted.
- **FR-FRD-05:** System shall record model version, feature vector, and prediction timestamp for auditability.

### 3.5 Module 5: Intelligent Donor Matching & Recommendations
- **FR-REC-01:** System shall store donor preferences: preferred categories, target geographies/cities, preferred contribution range (min/max), urgency threshold, and anonymity preference.
- **FR-REC-02:** System shall retrieve active, verified, unexpired, and under-funded bill requests.
- **FR-REC-03:** Engine shall apply a hybrid recommendation algorithm:
  - Rule-based hard filtering (category inclusion, active status).
  - Weighted feature scoring (due date urgency, funding gap percentage, geographic match).
  - Semantic vector similarity using Sentence Transformers (`all-MiniLM-L6-v2`) between donor interest profiles and bill narrative summaries.
- **FR-REC-04:** System shall generate human-readable match explanations (e.g., *"Matched because you support education in Andhra Pradesh and this bill is due in 4 days"*).
- **FR-REC-05:** System shall mask all sensitive beneficiary PII in recommendation payloads.

### 3.6 Module 6: Secure Payments & Financial Ledger
- **FR-PAY-01:** System shall provide a unified payment gateway abstraction supporting Razorpay (orders, signatures, webhooks), Stripe (PaymentIntents, webhooks), and a Local Mock Provider for automated tests and offline development.
- **FR-PAY-02:** System shall enforce database row-level locking (`SELECT ... FOR UPDATE`) on the target `bill_requests` row during donation checkout initiation and webhook processing to prevent overfunding.
- **FR-PAY-03:** Checkout shall validate that `donation_amount` is positive and `donation_amount ≤ (requested_amount - raised_amount)`.
- **FR-PAY-04:** Webhooks from payment gateways must be validated using HMAC-SHA256 signature verification against configured webhook secrets.
- **FR-PAY-05:** System shall implement strict payment idempotency using unique payment event identifiers to prevent double-crediting or duplicate balance increments.
- **FR-PAY-06:** System shall maintain an append-only `payment_events` and `payment_transactions` ledger for auditability.
- **FR-PAY-07:** Upon verified payment capture, the system shall transition `donation_status` to `completed`, increment `raised_amount`, update `funding_status` to `partially_funded` or `fully_funded`, and generate a cryptographically verifiable donation receipt.
- **FR-PAY-08:** System shall support administrator-initiated refund processing through the payment gateway abstraction, recording offsetting debit transactions in the ledger.

### 3.7 Module 7: LangGraph Workflow & Policy RAG Chatbot
- **FR-AI-01:** Bill verification shall be implemented as a stateful LangGraph workflow containing nodes: `document_ingestion` → `ocr_extraction` → `llm_field_extraction` → `schema_validation` → `duplicate_detection` → `rule_validation` → `ml_fraud_scoring` → `risk_classification` → `human_review_routing` → `final_decision`.
- **FR-AI-02:** LangGraph workflow shall support state checkpointing, error recovery, and administrative resume hooks.
- **FR-AI-03:** System shall provide an interactive RAG policy assistant chatbot that indexes platform policy documents (eligibility guidelines, refund policy, verification SLA, privacy charter) stored in PostgreSQL with `pgvector`.
- **FR-AI-04:** Chatbot queries shall retrieve relevant document chunks using cosine similarity, inject them into a grounded prompt template, and return answers with cited policy sections.
- **FR-AI-05:** Chatbot shall have strict guardrails preventing execution of financial actions, status modifications, or policy hallucinations.

### 3.8 Module 8: Interactive Dashboards & Analytics
- **FR-DASH-01 (Beneficiary Dashboard):** Display total assistance requested, total raised, balance remaining, active bill statuses, due date countdown, recent donations, and notifications.
- **FR-DASH-02 (Donor Dashboard):** Display total donated, number of bills supported, donation history, downloadable receipts, personalized recommendations, and impact metrics.
- **FR-DASH-03 (Admin Dashboard):** Real-time analytics of registered users, active bills by category, pending verification queue, fraud risk distribution, payment success/failure rates, refund ledger, and audit log explorer.

---

## 4. Non-Functional Requirements (NFR)

### 4.1 Performance & Scalability
- **NFR-PERF-01 (API Latency):** 95th percentile latency for read endpoints shall be ≤ 200 ms under standard load.
- **NFR-PERF-02 (Asynchronous Heavy Jobs):** Document OCR, LLM extraction, and ML scoring must run asynchronously via Celery worker queues without blocking the HTTP request thread.
- **NFR-PERF-03 (Database Connection Pooling):** Async SQLAlchemy connection pools configured with sensible min/max pool sizes (10-50 connections) and statement timeouts (10 seconds).
- **NFR-PERF-04 (Caching):** Frequently queried public listings and donor recommendation vectors shall be cached in Redis with appropriate invalidation triggers.

### 4.2 Security & Integrity
- **NFR-SEC-01 (OWASP Top 10):** Defenses against SQL Injection (parameterized queries via SQLAlchemy), XSS (React sanitization & CSP), CSRF (secure cookies and token headers), and Broken Access Control (strict dependency checks).
- **NFR-SEC-02 (IDOR Protection):** Every bill document access request must verify ownership or admin role. UUIDv4 primary keys prevent predictable enumeration.
- **NFR-SEC-03 (Encrypted Storage & Transit):** All data in transit encrypted via TLS 1.3. Object storage encrypted at rest via AES-256 (SSE-S3 / GCS-KMS).
- **NFR-SEC-04 (Prompt Injection Defense):** Bill text passed to LLMs is wrapped in strict boundary delimiters with system prompt anchoring forbidding instruction override.

### 4.3 Reliability & Fault Tolerance
- **NFR-REL-01 (Graceful Degradation):** If cloud OCR or LLM providers experience outages, fallback mechanisms (local PyMuPDF text extract or queue retry with exponential backoff) must activate without crashing the API.
- **NFR-REL-02 (Database Transactions):** All financial operations must execute within ACID transactions with rollback on failure.
- **NFR-REL-03 (Audit Trail):** All state changes (bill approval, rejection, edits, payments, refunds) must write immutable records to the `audit_logs` table.

### 4.4 Maintainability & Code Quality
- **NFR-MAINT-01:** Codebase must adhere to PEP 8 standards, enforce strict typing in Python (mypy/pydantic) and TypeScript (strict mode enabled), and maintain unit/integration test coverage > 80% for core business logic.
- **NFR-MAINT-02:** Containerized with Docker Compose for single-command developer setup (`docker compose up --build`).

---

## 5. Traceability Matrix

| Requirement ID | Module | Key Architectural Component | Verification Method |
| :--- | :--- | :--- | :--- |
| `FR-AUTH-01..07` | Auth & RBAC | FastAPI OAuth2/JWT + Argon2id | Integration & Unit Tests |
| `FR-BILL-01..07` | Bill Ingestion | Object Storage + PyMuPDF + Presigned URLs | File Upload Integration Tests |
| `FR-OCR-01..06` | Document Extraction | LangChain + Pydantic Schema Validator | Pipeline Unit Tests + Extraction Eval |
| `FR-FRD-01..05` | Fraud Detection | Scikit-learn + XGBoost + Rule Engine | Fraud Test Harness & Metrics |
| `FR-REC-01..05` | Matching Engine | SentenceTransformer + Cosine Similarity | Match Evaluation Tests |
| `FR-PAY-01..08` | Payment Ledger | Razorpay/Stripe/Mock + DB Pessimistic Lock | Idempotency & Concurrency Tests |
| `FR-AI-01..05` | LangGraph & RAG | LangGraph State Machine + pgvector | Workflow State & Groundedness Tests |
| `FR-DASH-01..03` | UI & Dashboards | React + Vite + Tailwind + TanStack Query | End-to-End Cypress/Playwright & Vitest |

---
*End of Software Requirements Specification (SRS)*
