## 🗄️ Database Architecture (Core Models)

### 1. The `TrackedCase` Model
**Mental Model**: This is the master folder for a single lawsuit on a user's dashboard.

**Fields to create:**
- **user**: A relationship linking to Django's built-in User model. (Remember to handle what happens if the user is deleted, and give it a related name).
- **cnr_number**: A string field (exactly 16 characters). Needs to be optimized for fast database lookups.
- **court_state**: A standard string field.
- **court_district**: A standard string field.
- **case_type**: A standard string field.
- **case_number**: A standard string field.
- **year**: An integer field.
- **petitioner**: A standard string field.
- **respondent**: A standard string field.
- **is_active**: A true/false field, defaulting to true.
- **last_checked**: A date/time field that automatically sets itself when the object is created.
- **last_changed**: A date/time field that automatically sets itself when the object is created.

**Extra Configuration (Meta class):**
- Ensure a user cannot track the exact same CNR number twice.
- Set the default sorting so the most recently changed cases appear first.

### 2. The `CaseHearing` Model
**Mental Model**: A single court date. A TrackedCase will have many of these.

**Fields to create:**
- **tracked_case**: A relationship linking back to the TrackedCase model. (Handle deletion and related name).
- **hearing_date**: A standard date field.
- **purpose**: A standard string field.
- **next_hearing_date**: A date field. (This one must be allowed to be empty or null, since not all hearings have a next date yet).
- **judge_name**: A string field. (Also must be allowed to be empty/null).
- **raw_data**: A field specifically designed to hold flexible JSON data. Give it a default of an empty dictionary.

**Extra Configuration (Meta class):**
- Set the default sorting so the newest hearings appear at the top.