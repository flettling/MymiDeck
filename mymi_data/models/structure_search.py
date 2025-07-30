from django.db import models
from .subject import Subject
from .image import Image
from .institution import Institution


def structure_search_solution_upload_path(instance, filename):
    """
    Upload path for structure search solution images.
    Files will be saved to media/structure_searches_solutions/<filename>
    """
    return f'structure_searches_solutions/{filename}'


class StructureSearch(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    is_exam = models.BooleanField(default=False)
    annotation_group_count = models.IntegerField(default=0)
    annotation_count = models.IntegerField(default=0)
    tags = models.JSONField(default=list)
    subjects = models.ManyToManyField(Subject, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=20, default='structure-search')
    solution_image = models.ImageField(
        upload_to=structure_search_solution_upload_path,
        null=True,
        blank=True,
        help_text="Upload solution image for this structure search"
    )
    
    @property
    def mymi_link(self):
        return f"https://mymi.uni-ulm.de/microscope/structure-search/{self.id}"
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Structure Search"
        verbose_name_plural = "Structure Searches"