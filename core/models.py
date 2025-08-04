from django.contrib.auth.models import User
from django.db import models

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_language = models.CharField(max_length=30, default='English')
    progress = models.JSONField(default=dict)
    score = models.IntegerField(default=0)
    last_quiz_topic = models.CharField(max_length=200, blank=True,null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
