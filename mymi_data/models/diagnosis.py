from django.db import models
from .image import Image
from .institution import Institution


class Diagnosis(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    is_active = models.BooleanField(default=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    is_exam = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=20, default='diagnosis')
    
    def __str__(self):
        return f"Diagnosis {self.id}"
    
    class Meta:
        verbose_name = "Diagnosis"
        verbose_name_plural = "Diagnoses"