# Development Execution Roadmap, Testing Strategy & Assumptions
## Project Name: BillKind AI
### AI-Powered Essential Bills Crowdfunding & Financial Assistance Platform
**Document Version:** 1.0.0  
**Status:** Approved for Implementation (Phase 1 Deliverable)  
**Date:** November 2026  

---

## 1. Incremental Development Execution Plan

### Phase 1: Planning & Architectural Foundations (Current)
- Complete SRS, Architecture specification, Database ER diagram, API contracts, Security plan, and AI strategy.
- Approval milestone: User review and sign-off on Phase 1 planning artifacts before generating application code.

### Phase 2: Backend Core & Data Persistence
- FastAPI application scaffolding (`backend/app`).
- PostgreSQL database engine and async session factories.
- Complete SQLAlchemy 2.0 models for all 18 tables with constraints and indexes.
- Alembic migration scripts.
- Authentication module: Argon2 password hashing, JWT issue/refresh token rotation, RBAC dependencies (`get_current_user`, `require_role`).
- Backend unit and integration test suite (`tests/test_auth.py`).

### Phase 3: Frontend Foundation & Design System
- React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui component scaffolding (`frontend/`).
- Routing tree: Public, Auth, Beneficiary, Donor, and Admin layouts.
- API client abstraction (Axios + TanStack Query) with authentication interceptors.
- Authentication views: Login, Register, Forgot Password, Reset Password.
- Core layout shells and navigation headers.

### Phase 4: Bill Ingestion, Document Processing & OCR
- Object storage abstraction: Local file system vault for offline development; S3/GCS adapters for production.
- Document upload endpoints with MIME validation, file hash de-duplication, and presigned URL previews.
- Multimodal extraction pipeline: PyMuPDF text layer extraction and LLM structured parser.
- Pydantic extraction schema validation and diff viewer in UI.

### Phase 5: AI/ML Verification, Fraud Detection & RAG
- Rule-based validation engine.
- Synthetic training dataset generator for utility and medical bills.
- Scikit-learn Isolation Forest and XGBoost/Random Forest fraud scoring models.
- LangGraph 10-node state machine orchestration with checkpointing.
- Donor matching engine using Sentence Transformers semantic embeddings.
- RAG Policy chatbot indexing platform guidelines into `pgvector`.

### Phase 6: Payment Processing & Financial Ledgers
- Payment gateway abstraction: Razorpay sandbox, Stripe sandbox, and offline Mock provider.
- Concurrency-safe donation checkout with row-level locks preventing overfunding.
- Webhook signature verification and idempotent ledger settlements.
- PDF donation receipt generator with Section 80G tax reference format.

### Phase 7: Interactive Dashboards & Admin Portals
- Beneficiary dashboard: Active bills, funding bars, recent contributions.
- Donor dashboard: Total impact, supported bills, matching recommendations feed, tax receipts.
- Admin dashboard: Verification queue, fraud risk inspector, payment transaction audit, and user management.

### Phase 8: Hardening, Testing & Containerized Deployment
- Comprehensive test runs: Pytest (backend), Vitest/RTL (frontend), security checks.
- Dockerfile definitions for frontend, backend, and celery workers.
- Docker Compose configuration orchestrating PostgreSQL, Redis, backend, frontend, and worker.
- Cloud deployment scripts for AWS (ECS/RDS/S3) and GCP (Cloud Run/Cloud SQL/GCS).

---

## 2. Multi-Tier Testing Strategy

### 2.1 Backend Tests (`backend/tests/`)
- **Unit Tests:** Individual utility functions, password hashing, token validation, Pydantic schemas, and rule engine predicates.
- **Integration Tests:** FastAPI `TestClient` / `httpx.AsyncClient` testing complete API flows against an in-memory or test PostgreSQL database.
- **Financial Concurrency Tests:** Simulating concurrent donations to verify database pessimistic locking (`SELECT FOR UPDATE`) prevents overfunding.
- **Idempotency Tests:** Replaying identical webhook payloads to assert zero duplicate ledger entries.

### 2.2 Frontend Tests (`frontend/src/**/*.test.tsx`)
- **Unit & Component Tests:** Vitest + React Testing Library for form validation, progress bar calculations, and state renders.
- **Hook & API Tests:** Mocking Axios responses to verify TanStack Query cache invalidation and error boundary handling.

### 2.3 Security & Penetration Tests
- **IDOR Tests:** Attempting to retrieve another user's bill document with non-owner credentials.
- **Role Escalation:** Beneficiary attempting to access `/api/v1/admin/*` endpoints.
- **Malicious Uploads:** Executable scripts masquerading as `.png` files.
- **Prompt Injection:** Submitting invoices containing LLM instruction overrides.

### 2.4 AI/ML Evaluation Framework
- **Extraction Accuracy:** Field-level Exact Match (EM) and Levenshtein distance on test invoice ground truth.
- **Fraud Engine Metrics:** Precision, Recall, F1 score, and False Positive Rate evaluated on a synthetic benchmark dataset.
- **RAG Groundedness:** Evaluation of policy chatbot answers against ground-truth policy citations to verify zero hallucination.

---

## 3. Assumptions & Unresolved Decisions

### 3.1 Documented Engineering Assumptions
1. **Primary Currency & Default Locale:** Default currency is Indian Rupee (`INR`), matching the India-oriented Razorpay sandbox integration, with multi-currency schema readiness (`USD`, `EUR`).
2. **Disbursement Model:** To comply with financial regulations and eliminate intermediary fund diversion risks, donations are earmarked directly to specific verified provider invoices. Direct utility API remittance or verified escrow disbursement is simulated in local development via the sandbox ledger.
3. **Local Development Self-Containment:** Developers can run and test the complete platform locally without cloud credentials, using the built-in Mock Payment Gateway, Local File System Object Storage, and Local Fallback LLM/Mock responses.
4. **LLM Provider Flexibility:** The AI module supports both Google Gemini and OpenAI API via an abstract interface, configurable through `LLM_PROVIDER=gemini` or `LLM_PROVIDER=openai`.

### 3.2 Key Open Questions for User Alignment
1. **Disbursement Target:** In Phase 6, should disbursement support direct bill-payment settlement (uploading proof of payment directly to the electricity board / school / hospital), or bank transfer to the beneficiary's verified account once 100% funded? *(Default assumption: Direct bill settlement with utility verification)*.
2. **KYC Requirement Timing:** Should beneficiaries complete government ID verification prior to uploading their first bill, or only before receiving public donations? *(Default assumption: Basic profile first; KYC mandatory before public listing)*.

---
*End of Development Execution Roadmap*
