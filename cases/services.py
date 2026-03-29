import requests
import time
from django.conf import settings

def fetch_ecourts_data(cnr_number):
    """
    MOCKED SERVICE: Temporarily bypassing the real eCourts API for local testing.
    """
    mock_response = {
        "state": "Delhi",
        "district": "New Delhi",
        "case_type": "Civil Suit",
        "case_number": "CS/123/2024",
        "year": 2024,
        "petitioner": "Rahul Sharma",
        "respondent": "State of Delhi",
        "raw_data": {
            "current_status": "Pending",
            "judge_assigned": "Hon'ble Mr. Justice A.K. Singh",
            "next_hearing_date": "2024-04-15",
            "hearing_history": [
                {
                    "date": "2024-01-15", 
                    "business_recorded": "Summons issued. Returnable by next date. IA 45/2024 filed under Order XXXIX Rule 1 & 2 CPC for ex-parte ad-interim injunction."
                },
                {
                    "date": "2024-03-01", 
                    "business_recorded": "Respondent counsel seeks time to file WS. Granted 4 weeks subject to cost of Rs. 2000. Matter relisted for framing of issues."
                }
            ]
        }
    }
    return mock_response

# def fetch_ecourts_data(cnr_number):

    # base_url = getattr(settings, 'ECOURTS_API_URL', 'https://services.ecourts.gov.in/ecourtindiaapi/')
    # url = f"{base_url}cases/cnr/{cnr_number}/"

    # max_attemps = 3
    # for attempt in range(max_attemps):
    #     try:
    #         response = requests.get(url, timeout=10)
            
    #         if response.status_code == 200:
    #             return response.json()
    #         elif response.status_code == 429: # Rate Limited
    #             time.sleep(2 ** attempt)
    #             continue
    #         else:
    #             return None
            
    #     except requests.exceptions.RequestException as e:
    #         if attempt == max_attemps - 1:
    #             raise Exception(f"Failed to connect to eCourts: {str(e)}")
    #         time.sleep(2 ** attempt)
    
    # return None