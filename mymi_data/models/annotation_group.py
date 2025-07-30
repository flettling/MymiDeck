from django.db import models


class AnnotationGroup(models.Model):
    # Django auto-generated primary key
    # id = models.AutoField(primary_key=True)  # This is implicit
    
    # MyMi ID fields (from API)
    external_id = models.IntegerField(null=True, blank=True, help_text="Original ID from MyMi API")
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
        return f"{self.taglabel or self.tagname} (External ID: {self.external_id})"
    
    class Meta:
        verbose_name = "Annotation Group"
        verbose_name_plural = "Annotation Groups"
        # unique_together = ['external_id', 'exploration']  # Will be re-added after data migration