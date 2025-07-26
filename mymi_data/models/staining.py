from django.db import models


class Staining(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=200)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Staining"
        verbose_name_plural = "Stainings"