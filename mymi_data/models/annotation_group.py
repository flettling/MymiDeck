from django.db import models


class AnnotationGroup(models.Model):
    # MyMi ID fields
    id = models.IntegerField(primary_key=True)
    tagid = models.IntegerField()
    
    # Basic information
    tagname = models.CharField(max_length=255, blank=True)
    revision = models.CharField(max_length=20, blank=True)
    taggroup = models.CharField(max_length=255, blank=True)
    taglabel = models.CharField(max_length=255, blank=True)
    tagdescription = models.TextField(blank=True)
    
    # Creator information
    creator_id = models.IntegerField(default=0)
    
    # Display styling (optional, stored as JSON)
    displaystyle = models.JSONField(null=True, blank=True)
    
    # Relationship to exploration
    exploration = models.ForeignKey('Exploration', on_delete=models.CASCADE, related_name='annotation_groups')
    
    def __str__(self):
        return f"{self.taglabel or self.tagname} (ID: {self.id})"
    
    class Meta:
        verbose_name = "Annotation Group"
        verbose_name_plural = "Annotation Groups"
        unique_together = ['id', 'exploration']