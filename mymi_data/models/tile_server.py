from django.db import models
from .institution import Institution


class TileServer(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=100)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    public_urls = models.JSONField(default=list)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Tile Server"
        verbose_name_plural = "Tile Servers"