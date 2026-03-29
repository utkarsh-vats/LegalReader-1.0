# LegalReader-1.0

LegalReader is an AI-powered Django backend service designed to track Indian court cases, fetch hearing updates, and automatically translate complex legal jargon into plain, easy-to-understand English using Google's Gemini AI.

This API serves as the backend engine for the `elr.obtuse.in` micro-SaaS ecosystem.

## Table of Content
- [LegalReader-1.0](#legalreader-10)
	- [Table of Content](#table-of-content)
	- [Features](#features)
	- [Tech Stack](#tech-stack)
	- [Local Development Setup](#local-development-setup)
		- [1. Clone the repository](#1-clone-the-repository)
		- [2. Set up the Virtual Environment](#2-set-up-the-virtual-environment)
		- [3. Install Dependencies](#3-install-dependencies)
		- [4. Environment Variables](#4-environment-variables)
		- [5. Run Database Migrations](#5-run-database-migrations)
		- [6. Start the Development Server](#6-start-the-development-server)
	- [API Endpoints](#api-endpoints)
		- [1. Track a New Case](#1-track-a-new-case)
		- [2. Automated Background Updates](#2-automated-background-updates)
	- [System Architecture Notes](#system-architecture-notes)
	- [AI Integration \& Prompt Engineering](#ai-integration--prompt-engineering)
		- [The Translation Pipeline](#the-translation-pipeline)
	- [Security \& Performance](#security--performance)
	- [Future Roadmap](#future-roadmap)
	- [Database Architecture (Core Models)](#database-architecture-core-models)
		- [1. `TrackedCase`](#1-trackedcase)
		- [2. `CaseHearing`](#2-casehearing)
	- [API Architecture \& Data Flow (Separation of Concerns)](#api-architecture--data-flow-separation-of-concerns)
		- [1. The Validation Layer (`serializers.py`)](#1-the-validation-layer-serializerspy)
		- [2. The Business Logic Layer (`services.py`)](#2-the-business-logic-layer-servicespy)
		- [3. The Orchestration Layer (`views.py`)](#3-the-orchestration-layer-viewspy)

## Features

* **Automated Tracking:** Look up any case using its 16-character CNR number.
* **AI Legal Translation:** Integrates with the `google-genai` SDK (Gemini 1.5 Flash) to parse messy eCourts JSON data and generate concise, 3-sentence plain English summaries of court proceedings.
* **Serverless Automation:** Features a secured, token-protected Cron endpoint to update all active cases automatically without requiring expensive background worker servers (Celery/Redis).
* **Production-Ready Security:** Fully configured with `django-cors-headers` and environment-based secret management following the 12-Factor App methodology.
* **User-Specific Tracking:** Allows multiple users to track the same case independently while maintaining private notification preferences.
## Tech Stack

* **Framework:** Django & Django REST Framework (DRF)
* **Database:** PostgreSQL (Hosted on Supabase)
* **AI Engine:** Google Gemini (via `google-genai` SDK)
* **Production Server:** Gunicorn
* **Hosting:** Render (`api.elr.obtuse.in`)

## Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/legalreader-api.git
cd legalreader-api
```

### 2. Set up the Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Mac/Linux use:  source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Environment Variables
Create a `.env` file in the root directory and add the following keys. **Do not use quotation marks around the values.**

```
# Database (Supabase PostgreSQL connection string)
DATABASE_URL=postgresql://postgres.your_project_id:your_password@aws-0-region.pooler.supabase.com:6543/postgres

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Security & Cron Automation
CRON_SECRET_KEY=generate_a_random_secure_string
ALLOWED_HOSTS=127.0.0.1,localhost,[your_backend_url]
CORS_ALLOWED_ORIGINS=http://localhost:3000,[your_frontend_url]
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Start the Development Server
```bash
python manage.py runserver
```

## API Endpoints

### 1. Track a New Case
Fetches case data, translates the latest hearing via AI, and saves it to the database.
- **URL**: `/api/cases/lookup/`
- **Method**: `POST`
- **Auth**: Bearer Token (User JWT) or Session Auth
- **Payload**:
	```JSON
	{
		"cnr_number": "DLHC010123452024"
	}
	```

### 2. Automated Background Updates
Secured endpoint designed to be hit by an external Cron service (like `cron-job.org`) every 6 hours to find new hearings for all active cases.

- **URL**: `/api/cases/cron/update-cases/`
- **Method**: `POST`
- **Auth**: Bearer Token (Must match `CRON_SECRET_KEY` in `.env`
- **Headers**:
	```
	Authorization: Bearer <your_cron_secret_key>
	```

## System Architecture Notes
Currently, the `services.py` module utilizes a mocked response to simulate the Indian eCourts API. This ensures the AI translation pipeline and database routing can be developed and tested without triggering government firewall blocks or CAPTCHAs during local development. Once deployed to a cloud IP, the mock can be swapped for live HTTP requests.

## AI Integration & Prompt Engineering

The core value of LegalReader lies in its ability to demystify legal jargon. This is achieved through a specialized integration with the **Gemini 2.5 Flash** model.

### The Translation Pipeline
1.  **Data Extraction:** The system extracts the `business_on_date` and `case_status` fields from the eCourts JSON response.
2.  **Context Injection:** A system prompt is constructed that instructs the AI to act as a "Senior Legal Consultant for Laypeople."
3.  **Constraint Enforcement:** The AI is strictly instructed to:
    *   Avoid legalese (e.g., "interlocutory," "adjourned sine die").
    *   Limit the summary to exactly 3 bullet points.
    *   Focus on "What happened today" and "What happens next."
4.  **Token Optimization:** By using the Flash model, we achieve sub-2-second latency for translations, ensuring the UI remains responsive.

```python
# Example of the internal prompt logic
prompt = f"Translate this Indian court update into 3 simple sentences for a non-lawyer: {raw_legal_text}"
response = model.generate_content(prompt)
```

## Security & Performance

*   **Rate Limiting:** Implemented via DRF's `ScopedRateThrottle` to prevent API abuse and manage Gemini API costs.
*   **Database Indexing:** Composite indexes are applied to `user_id` and `cnr_number` to ensure that even with thousands of tracked cases, the background update script remains performant.
*   **Environment Isolation:** Uses `python-dotenv` to ensure that sensitive credentials like the `GEMINI_API_KEY` and `DATABASE_URL` are never committed to version control.

## Future Roadmap
- [ ] **PDF Parsing:** Automatically download and summarize "Daily Orders" (PDFs) using Gemini's multimodal capabilities.
- [ ] **WhatsApp Notifications:** Integration with Twilio to send hearing alerts directly to users.
- [ ] **Multi-language Support:** Translating legal summaries into Hindi and other regional Indian languages.


## Database Architecture (Core Models)

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

## API Architecture & Data Flow (Separation of Concerns)

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