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
    
    # Raw API responses for annotations
    annotations_raw = models.JSONField(null=True, blank=True, help_text="Raw API response from /annotation/annotation endpoint")
    annotation_groups_raw = models.JSONField(null=True, blank=True, help_text="Raw API response from /annotation/annotation-group endpoint")
    
    @property
    def mymi_link(self):
        return f"https://mymi.uni-ulm.de/microscope/exploration/{self.id}"
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Exploration"
        verbose_name_plural = "Explorations"