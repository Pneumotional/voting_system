from django.db import models
from django.utils import timezone
from datetime import timedelta

class Code(models.Model):
    code = models.CharField(max_length=5, unique=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
    
    def __str__(self):
        return self.code
    
    

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='candidates', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Vote(models.Model):
    voter_code = models.ForeignKey(Code, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.candidate.name
    