import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from .serializers import CNRLookupSerializer
from .services import fetch_ecourts_data
from .models import TrackedCase, CaseHearing
from .ai_services import translate_legal_jargon

class CNRLookupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CNRLookupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        valid_data = serializer.validated_data
        if not isinstance(valid_data, dict):
                return Response(
                    {
                        "detail": "Critical Error: Data did not parse into a dictionary."
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        cnr_number = valid_data['cnr_number']

        if TrackedCase.objects.filter(user=request.user, cnr_number=cnr_number).exists():
            return Response(
                {
                    "detail": "You are already tracking this case."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ecourts_data = fetch_ecourts_data(cnr_number)
            if not ecourts_data:
                return Response(
                    {
                        "detail": "Failed to fetch data from eCourts.",
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            new_case = TrackedCase.objects.create(
                user = request.user,
                cnr_number = cnr_number,
                court_state = ecourts_data.get('state', 'Unknown'),
                court_district = ecourts_data.get('district', 'Unknown'),
                case_type = ecourts_data.get('case_type', 'Unknown'),
                case_number = ecourts_data.get('case_number', 'Unknown'),
                year = ecourts_data.get('year', 2026),
                petitioner = ecourts_data.get('petitioner', 'Unknown'),
                respondent = ecourts_data.get('respondent', 'Unknown'),
            )

            raw_data = ecourts_data.get('raw_data', {})
            hearings = list(raw_data.get('hearing_history'))  
            print(hearings[-1].get('date'))  
            ai_summary = translate_legal_jargon(raw_data)

            CaseHearing.objects.create(
                tracked_case = new_case,
                hearing_date = raw_data.get('hearing_history', [])[-1].get('date', '2026-01-01'),
                purpose = ai_summary,
                next_hearing_date = raw_data.get('next_hearing_date'),
                judge_name = raw_data.get('judge_assigned', 'Unknown'),
                raw_data = raw_data
            )

            return Response(
                {
                    "detail": "Case found and added to your tracking list.",
                    "cnr": new_case.cnr_number,
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
@api_view(['POST'])
@permission_classes([AllowAny])
def trigger_case_updates(request):
    """
    This endpoint will be hit by an external free cron service every 6 hours.
    """
    expected_secret = os.environ.get('CRON_SECRET_KEY')
    provided_secret = request.headers.get('Authorization')

    if provided_secret != f"Bearer {expected_secret}":
        return Response(
            {
                "detail": "Unauthorized"
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    active_cases = TrackedCase.objects.filter(is_active=True)
    updated_count = 0
    for case in active_cases:
        ecourts_data = fetch_ecourts_data(case.cnr_number)
        if not ecourts_data:
            continue
        raw_data = ecourts_data.get('raw_data', {})
        hearings = list(raw_data.get('hearing_history', []))
        if not hearings:
            continue
        latest_hearing_date = hearings[-1].get('date', '2026-01-01')
        if not CaseHearing.objects.filter(tracked_case=case, hearing_date=latest_hearing_date).exists():
            ai_summary = translate_legal_jargon(raw_data)
            CaseHearing.objects.create(
                tracked_case = case,
                hearing_date = latest_hearing_date,
                purpose = ai_summary,
                next_hearing_date = raw_data.get('next_hearing_date'),
                judge_name = raw_data.get('judge_assigned', 'Unknown'),
                raw_data = raw_data
            )
            updated_count += 1
            case.save()

        return Response(
            {
                "detail": f"Update complete. {updated_count} cases updated."
            },
            status=status.HTTP_200_OK
        )
    
