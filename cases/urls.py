from django.urls import path
from .views import CNRLookupView, trigger_case_updates

app_name = 'cases'

urlpatterns = [
    path('lookup/', CNRLookupView.as_view(), name='cnr-lookup'),
    path('cron/case_update/', trigger_case_updates, name='case-update')
]