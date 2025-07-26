from django.db import models
from .organ_system import OrganSystem
from .species import Species
from .staining import Staining
from .tile_server import TileServer


class Image(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=300)
    checksum = models.CharField(max_length=32)
    size = models.BigIntegerField()
    file_path = models.CharField(max_length=500)
    thumbnail_small = models.CharField(max_length=100, blank=True)
    thumbnail_medium = models.CharField(max_length=100, blank=True)
    thumbnail_large = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=20, default='active')
    imaging_diagnostic = models.CharField(max_length=50)
    staining = models.ForeignKey(Staining, on_delete=models.CASCADE, null=True, blank=True)
    species = models.ForeignKey(Species, on_delete=models.CASCADE, null=True, blank=True)
    organ_systems = models.ManyToManyField(OrganSystem, blank=True)
    tile_server = models.ForeignKey(TileServer, on_delete=models.CASCADE, null=True, blank=True)
    tags = models.JSONField(default=list)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    @property
    def thumbnail_small_url(self):
        if self.thumbnail_small:
            return f"https://mymi.uni-ulm.de/assets/thumbnails/{self.thumbnail_small}"
        return None
    
    @property
    def thumbnail_medium_url(self):
        if self.thumbnail_medium:
            return f"https://mymi.uni-ulm.de/assets/thumbnails/{self.thumbnail_medium}"
        return None
    
    @property
    def thumbnail_large_url(self):
        if self.thumbnail_large:
            return f"https://mymi.uni-ulm.de/assets/thumbnails/{self.thumbnail_large}"
        return None
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"