from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import CNRLookupSerializer
from .services import fetch_ecourts_data
from .models import TrackedCase

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
                court_state = ecourts_data.get('court_state', 'Unknown'),
                court_district = ecourts_data.get('court_district', 'Unknown'),
                case_type = ecourts_data.get('case_type', 'Unknown'),
                case_number = ecourts_data.get('case_number', 'Unknown'),
                year = ecourts_data.get('year', 2026),
                petitioner = ecourts_data.get('petitioner', 'Unknown'),
                respondent = ecourts_data.get('respondent', 'Unknown'),
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