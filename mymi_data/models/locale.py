from django.db import models


class Locale(models.Model):
    key = models.CharField(max_length=100, primary_key=True)
    value = models.TextField()
    
    def __str__(self):
        return self.key
    
    class Meta:
        verbose_name = "Locale"
        verbose_name_plural = "Locales"