from django.db import models


class Subject(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=100)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"