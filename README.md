# LegalReader-1.0

## Table of Content
- [LegalReader-1.0](#legalreader-10)
	- [Table of Content](#table-of-content)
	- [🗄️ Database Architecture (Core Models)](#️-database-architecture-core-models)
		- [1. `TrackedCase`](#1-trackedcase)
		- [2. `CaseHearing`](#2-casehearing)


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