from django.contrib import admin
from django.utils.html import format_html
from .models import (
    OrganSystem, Species, Staining, Subject, Institution, 
    TileServer, Image, Exploration, Diagnosis, StructureSearch, Locale
)


@admin.register(OrganSystem)
class OrganSystemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    readonly_fields = ('id', 'title')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    readonly_fields = ('id', 'title')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Staining)
class StainingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    readonly_fields = ('id', 'title')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    readonly_fields = ('id', 'title')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'short_title', 'acronym')
    search_fields = ('title', 'short_title', 'acronym')
    readonly_fields = ('id', 'title', 'short_title', 'acronym', 'introduction', 'logo_url', 'small_logo_url')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TileServer)
class TileServerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'institution')
    list_filter = ('institution',)
    search_fields = ('title',)
    readonly_fields = ('id', 'title', 'institution', 'public_urls')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'species', 'staining', 'state', 'size')
    list_filter = ('state', 'imaging_diagnostic', 'species', 'staining')
    search_fields = ('title', 'file_path')
    readonly_fields = ('id', 'title', 'checksum', 'size', 'file_path', 'thumbnail_small', 
                      'thumbnail_medium', 'thumbnail_large', 'thumbnail_small_link',
                      'thumbnail_medium_link', 'thumbnail_large_link', 'state', 'imaging_diagnostic', 
                      'staining', 'species', 'tile_server', 'tags', 'deleted_at')
    filter_horizontal = ('organ_systems',)
    
    def thumbnail_small_link(self, obj):
        if obj.thumbnail_small_url:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.thumbnail_small_url, obj.thumbnail_small_url)
        return "No thumbnail"
    thumbnail_small_link.short_description = "Thumbnail Small URL"
    
    def thumbnail_medium_link(self, obj):
        if obj.thumbnail_medium_url:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.thumbnail_medium_url, obj.thumbnail_medium_url)
        return "No thumbnail"
    thumbnail_medium_link.short_description = "Thumbnail Medium URL"
    
    def thumbnail_large_link(self, obj):
        if obj.thumbnail_large_url:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.thumbnail_large_url, obj.thumbnail_large_url)
        return "No thumbnail"
    thumbnail_large_link.short_description = "Thumbnail Large URL"
    
    def get_readonly_fields(self, request, obj=None):
        # Make organ_systems readonly too by overriding the field
        return self.readonly_fields + ('organ_systems',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Exploration)
class ExplorationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_active', 'image', 'institution', 'is_exam')
    list_filter = ('is_active', 'is_exam', 'institution', 'type')
    search_fields = ('title', 'edu_id')
    readonly_fields = ('id', 'title', 'is_active', 'image', 'institution', 'annotation_group_count', 
                      'annotation_count', 'is_exam', 'edu_id', 'tags', 'deleted_at', 'type')
    
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('subjects',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'institution', 'is_active', 'is_exam')
    list_filter = ('is_active', 'is_exam', 'institution')
    readonly_fields = ('id', 'is_active', 'image', 'institution', 'is_exam', 'deleted_at', 'type')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StructureSearch)
class StructureSearchAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_active', 'image', 'institution', 'is_exam')
    list_filter = ('is_active', 'is_exam', 'institution')
    search_fields = ('title',)
    readonly_fields = ('id', 'title', 'is_active', 'image', 'institution', 'is_exam', 
                      'annotation_group_count', 'annotation_count', 'tags', 'deleted_at', 'type')
    
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('subjects',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Locale)
class LocaleAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key', 'value')
    readonly_fields = ('key', 'value')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
