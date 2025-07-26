from django.db import models
from .subject import Subject
from .image import Image
from .institution import Institution


class Exploration(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    annotation_group_count = models.IntegerField(default=0)
    annotation_count = models.IntegerField(default=0)
    is_exam = models.BooleanField(default=False)
    edu_id = models.CharField(max_length=20, blank=True)
    tags = models.JSONField(default=list)
    subjects = models.ManyToManyField(Subject, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=20, default='exploration')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Exploration"
        verbose_name_plural = "Explorations"