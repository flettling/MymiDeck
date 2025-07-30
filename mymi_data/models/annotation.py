from django.db import models


class Annotation(models.Model):
    # Django auto-generated primary key
    # id = models.AutoField(primary_key=True)  # This is implicit
    
    # MyMi ID fields (from API)
    external_id = models.IntegerField(null=True, blank=True, help_text="Original ID from MyMi API")
    annotationid = models.IntegerField()
    
    # Basic information
    annotationname = models.CharField(max_length=500, blank=True)
    annotationdescription = models.TextField(blank=True)
    
    # Visibility and display
    show = models.BooleanField(default=True)
    version = models.IntegerField(default=1)
    revision = models.CharField(max_length=20, blank=True)
    
    # Geometry type
    type = models.IntegerField(help_text="Annotation geometry type (e.g., 3=polygon, 100=line, 101=point)")
    
    # Spatial coordinates (prefixed to avoid PostgreSQL system column conflicts)
    coord_xmin = models.IntegerField(default=0)
    coord_xmax = models.IntegerField(default=0)
    coord_ymin = models.IntegerField(default=0)
    coord_ymax = models.IntegerField(default=0)
    coord_zmin = models.IntegerField(default=0)
    coord_zmax = models.IntegerField(default=0)
    coord_tmin = models.IntegerField(default=0)
    coord_tmax = models.IntegerField(default=0)
    
    # Geometry data (coordinate array)
    geometry = models.JSONField(default=list, help_text="Array of coordinate pairs")
    
    # Rotation and transformation
    rotation = models.FloatField(default=0)
    
    # Display styling
    displaystyle = models.JSONField(null=True, blank=True)
    
    # Tag associations (stored as array of IDs)
    tag_ids = models.JSONField(default=list, help_text="Array of associated tag IDs")
    
    # Channel information
    channels = models.JSONField(default=list)
    
    # Additional fields
    scope_id = models.IntegerField(null=True, blank=True)
    creator_id = models.IntegerField(default=0)
    mousebinded = models.BooleanField(default=False)
    tagdescription = models.TextField(blank=True)
    typespecificflags = models.TextField(blank=True)
    
    # Relationship to exploration
    exploration = models.ForeignKey('Exploration', on_delete=models.CASCADE, related_name='annotations')
    
    def __str__(self):
        return f"{self.annotationname} (External ID: {self.external_id})"
    
    @property
    def associated_groups(self):
        """Return annotation groups associated with this annotation via tag_ids"""
        from .annotation_group import AnnotationGroup
        if not self.tag_ids:
            return AnnotationGroup.objects.none()
        return AnnotationGroup.objects.filter(
            exploration=self.exploration,
            tagid__in=self.tag_ids
        )
    
    class Meta:
        verbose_name = "Annotation"
        verbose_name_plural = "Annotations"
        # unique_together = ['external_id', 'exploration']  # Will be re-added after data migration