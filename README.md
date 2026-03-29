# LegalReader-1.0

## Table of Content
- [LegalReader-1.0](#legalreader-10)
	- [Table of Content](#table-of-content)
	- [🗄️ Database Architecture (Core Models)](#️-database-architecture-core-models)
		- [1. `TrackedCase`](#1-trackedcase)
		- [2. `CaseHearing`](#2-casehearing)
	- [⚙️ API Architecture \& Data Flow (Separation of Concerns)](#️-api-architecture--data-flow-separation-of-concerns)
		- [1. The Validation Layer (`serializers.py`)](#1-the-validation-layer-serializerspy)
		- [2. The Business Logic Layer (`services.py`)](#2-the-business-logic-layer-servicespy)
		- [3. The Orchestration Layer (`views.py`)](#3-the-orchestration-layer-viewspy)


## 🗄️ Database Architecture (Core Models)

LegalReader uses a relational database (PostgreSQL) to manage users, track cases, and store highly variable court data. Below is the core entity-relationship structure:

### 1. `TrackedCase`
The master record for a lawsuit being monitored by a user.
* **`user`** (ForeignKey): Links the case to a specific account. Cascadable.
* **`cnr_number`** (String, Indexed): The unique 16-character Indian court ID. **Indexed for $O(1)$ fast lookups** during the 6-hour cron job sweeps.
* **`court_state` / `court_district` / `case_type`** (String): Cached locally to prevent unnecessary external API calls.
* **`is_active`** (Boolean): Acts as a circuit breaker. Closed cases are flagged `false` to prevent wasting eCourts API rate limits.

### 2. `CaseHearing`
Represents an individual court date. 
* **`tracked_case`** (ForeignKey): Creates a **One-to-Many** relationship back to the `TrackedCase`.
* **`hearing_date` / `next_hearing_date`** (Date): Used by the frontend to sort and highlight upcoming appearances.
* **`raw_data`** (JSONB): A flexible payload column. Since government APIs (eCourts) frequently change their response structures without warning, dumping the raw response here ensures no data is lost during parsing, and prevents the need for constant schema migrations.

## ⚙️ API Architecture & Data Flow (Separation of Concerns)

To ensure the codebase remains maintainable and scalable, the core business logic for processing cases is strictly decoupled into three distinct layers:

### 1. The Validation Layer (`serializers.py`)
Acts as the gatekeeper. 
* Uses Django REST Framework's `Serializer` class to rigorously sanitize incoming JSON payloads.
* Enforces strict data integrity (e.g., verifying the Indian CNR number is exactly 16 alphanumeric characters) *before* the server wastes any processing power.

### 2. The Business Logic Layer (`services.py`)
Encapsulates all external communication.
* Houses the `fetch_ecourts_data` function, isolating the messy logic of third-party API communication.
* **Resilience:** Implements an Exponential Backoff retry mechanism to gracefully handle rate limits (`HTTP 429`) and connection drops from the unpredictable eCourts government API.
* **Reusability:** By decoupling this from the View, this exact same function can be reused later by the Celery/Cron background workers.

### 3. The Orchestration Layer (`views.py`)
The HTTP controller.
* Secures the endpoint using DRF's `IsAuthenticated` permission class.
* Orchestrates the flow: Receives the request -> Calls the Serializer -> Passes validated data to the Service Layer -> Writes the result to PostgreSQL -> Returns a standardized `HTTP 201 Created` or appropriate error code to the Next.js frontend.