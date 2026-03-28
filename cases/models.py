from django.db import models
from django.contrib.auth.models import User

class TrackedCase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cases')
    cnr_number = models.CharField(max_length=16, db_index=True)
    court_state = models.CharField(max_length=100)
    court_district = models.CharField(max_length=100)
    case_type = models.CharField(max_length=100)
    case_number = models.CharField(max_length=50)
    year = models.IntegerField()
    petitioner = models.CharField(max_length=255)
    respondent = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    last_checked = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'cnr_number')
        ordering = ['-last_changed']

    def __str__(self):
        return f"{self.cnr_number} - {self.petitioner} vs. {self.respondent}"

class CaseHearing(models.Model):
    tracked_case = models.ForeignKey(TrackedCase, on_delete=models.CASCADE, related_name='hearings')
    hearing_date = models.DateField()
    purpose = models.CharField(max_length=255)
    next_hearing_date = models.DateField(null=True, blank=True)
    judge_name = models.CharField(max_length=255, null=True, blank=True)
    raw_data = models.JSONField(default=dict)

    class Meta:
        ordering = ['-hearing_date']

    def __str__(self):
        return f"Hearing on {self.hearing_date} for {self.tracked_case.cnr_number}"