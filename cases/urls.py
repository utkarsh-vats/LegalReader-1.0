from django.urls import path
from .views import CNRLookupView

app_name = 'cases'

urlpatterns = [
    path('lookup/', CNRLookupView.as_view(), name='cnr-lookup')
]