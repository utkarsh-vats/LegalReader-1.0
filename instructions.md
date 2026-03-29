# LegalReader Implementation Instructions

## 🗄️ Database Architecture (Core Models)
*File: `cases/models.py`*

### 1. The `TrackedCase` Model
> **Mental Model:** This is the master folder for a single lawsuit on a user's dashboard.

**Fields to create:**
* **`user`**: A ForeignKey relationship linking to Django's built-in `User` model. (Remember to handle `on_delete` and provide a `related_name`).
* **`cnr_number`**: A `CharField` (exactly 16 characters). Needs `db_index=True` for fast database lookups.
* **`court_state`**: A standard `CharField`.
* **`court_district`**: A standard `CharField`.
* **`case_type`**: A standard `CharField`.
* **`case_number`**: A standard `CharField`.
* **`year`**: An `IntegerField`.
* **`petitioner`**: A standard `CharField`.
* **`respondent`**: A standard `CharField`.
* **`is_active`**: A `BooleanField`, defaulting to `True`.
* **`last_checked`**: A `DateTimeField` that automatically sets itself when the object is created (`auto_now_add=True`).
* **`last_changed`**: A `DateTimeField` that automatically updates itself every time the object is saved (`auto_now=True`).

**Extra Configuration (`class Meta`):**
* Ensure a user cannot track the exact same CNR number twice using `unique_together`.
* Set the default `ordering` so the most recently changed cases appear first (`-last_changed`).

---

### 2. The `CaseHearing` Model
> **Mental Model:** A single court date. A `TrackedCase` will have many of these (One-to-Many).

**Fields to create:**
* **`tracked_case`**: A ForeignKey relationship linking back to the `TrackedCase` model. (Handle `on_delete` and provide a `related_name`).
* **`hearing_date`**: A standard `DateField`.
* **`purpose`**: A standard `CharField`.
* **`next_hearing_date`**: A `DateField`. (Must include `null=True, blank=True` since not all hearings have a next date yet).
* **`judge_name`**: A `CharField`. (Must include `null=True, blank=True`).
* **`raw_data`**: A `JSONField` designed to hold flexible JSON data. Give it a default of an empty dictionary `default=dict`.

**Extra Configuration (`class Meta`):**
* Set the default `ordering` so the newest hearings appear at the top (`-hearing_date`).

***

## ⚙️ API Architecture & Data Flow

### 1. The Waiter (`cases/serializers.py`)
> **The Mental Model:** This is the bouncer/waiter. When Next.js sends a JSON package saying "Track this case," this file intercepts it. It doesn't talk to the database. It just asks: *"Does this data look exactly like a 16-character Indian CNR number? Are there any illegal symbols?"*

**The Ingredients:**
```python
from rest_framework import serializers
```

What you need to write:

Create a class called CNRLookupSerializer that inherits from serializers.Serializer.

Field 1: Create a cnr_number field. It must be a character field with both a max_length and min_length of 16.

Custom Validation: DRF has a magic naming convention. If you write a method called validate_cnr_number(self, value), DRF runs it automatically. Inside this method:

Strip any accidental whitespace and convert the string to uppercase.

Check if the string is strictly alphanumeric (no dashes, no spaces). If it has symbols, raise a serializers.ValidationError.

Return the cleaned value.

2. The Kitchen (cases/services.py)
The Mental Model:
This handles the messy outside world. We isolate this logic in a standard Python function so that later, our 6-hour Celery cron job can use this exact same code without needing a fake web request.

The Ingredients:

Python
import requests
import time
from django.conf import settings
What you need to write:

Create a standard Python function called fetch_ecourts_data(cnr_number).

The URL: Build the target URL. (e.g., settings.ECOURTS_API_URL + "cases/cnr/" + cnr_number).

The Loop: Create a for loop that tries a maximum of 3 times. Government APIs drop connections often.

The Request: Use requests.get() to hit the URL. Crucial: You must pass timeout=10 as an argument so your server doesn't hang forever if eCourts is down.

The Logic:

If the status_code is 200 (Success), return the .json() response.

If the status_code is 429 (Rate Limited), tell Python to time.sleep() for a couple of seconds, then let the loop continue to try again.

If the loop finishes 3 attempts and still fails, return None.

3. The Manager (cases/views.py)
The Mental Model:
The View is the orchestrator. It receives the HTTP request, hands the data to the Serializer, takes the validated data to the Service, saves the result to the database, and replies to the frontend.

The Ingredients:

Python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import CNRLookupSerializer
from .services import fetch_ecourts_data
from .models import TrackedCase
What you need to write:

Create a class called CNRLookupView that inherits from APIView.

Security: Add permission_classes = [IsAuthenticated] so random bots can't spam your endpoint.

The Method: Define a post(self, request) method. Inside it:

Pass request.data to your CNRLookupSerializer.

Check if it is_valid(). If not, return a Response containing the errors and an HTTP_400_BAD_REQUEST status.

Extract the cleaned cnr_number from the serializer's .validated_data.

Database Check: Use TrackedCase.objects.filter(...) to check if this user is already tracking this exact CNR. If they are, return a 400 error saying "Already tracking."

Service Call: Call your fetch_ecourts_data(cnr_number) function. If it returns None, return a 404_NOT_FOUND response.

Save to DB: If the service returned data, use TrackedCase.objects.create(...) to save a new row. (Remember to link user=request.user). Tip: Use .get('key', 'Unknown') when pulling from the API dictionary so it doesn't crash if a field is missing.

The Victory: Return a Response with a success message and an HTTP_201_CREATED status.