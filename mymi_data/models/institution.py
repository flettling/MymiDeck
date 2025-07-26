from django.db import models


class Institution(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=200)
    short_title = models.CharField(max_length=100, blank=True)
    acronym = models.CharField(max_length=20, blank=True)
    introduction = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    small_logo_url = models.URLField(blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"