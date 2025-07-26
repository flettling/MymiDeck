from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
import os
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
    list_display = ('id', 'title', 'species', 'staining', 'state', 'size', 'thumbnail_preview')
    list_filter = ('state', 'imaging_diagnostic', 'species', 'staining')
    search_fields = ('title', 'file_path')
    readonly_fields = ('id', 'title', 'checksum', 'size', 'file_path', 'thumbnail_small', 
                      'thumbnail_medium', 'thumbnail_large', 'thumbnail_small_display',
                      'thumbnail_medium_display', 'thumbnail_large_display', 'state', 'imaging_diagnostic', 
                      'staining', 'species', 'tile_server', 'tags', 'deleted_at')
    filter_horizontal = ('organ_systems',)
    
    def get_local_thumbnail_path(self, filename):
        """Check if thumbnail exists locally in media/thumbnails/"""
        if not filename:
            return None
        local_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', filename)
        if os.path.exists(local_path):
            return f"{settings.MEDIA_URL}thumbnails/{filename}"
        return None
    
    def thumbnail_preview(self, obj):
        """Small thumbnail for list view"""
        local_url = None
        if obj.thumbnail_small:
            local_url = self.get_local_thumbnail_path(obj.thumbnail_small)
        
        if local_url:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 80px;" />', local_url)
        elif obj.thumbnail_small_url:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 80px;" />', obj.thumbnail_small_url)
        return "No thumbnail"
    thumbnail_preview.short_description = "Preview"
    
    def thumbnail_small_display(self, obj):
        """Small thumbnail for detail view"""
        local_url = None
        if obj.thumbnail_small:
            local_url = self.get_local_thumbnail_path(obj.thumbnail_small)
        
        # Determine which image to show (prefer local)
        display_url = local_url if local_url else obj.thumbnail_small_url
        
        if display_url:
            html = f'<div><img src="{display_url}" style="max-height: 150px; max-width: 200px;" /><br/>'
            
            # Add local link if exists
            if local_url:
                html += f'<a href="{local_url}" target="_blank">Local: {obj.thumbnail_small}</a><br/>'
            
            # Add remote link if exists
            if obj.thumbnail_small_url:
                html += f'<a href="{obj.thumbnail_small_url}" target="_blank">Remote: {obj.thumbnail_small_url}</a>'
            
            html += '</div>'
            return format_html(html)
        
        return "No small thumbnail"
    thumbnail_small_display.short_description = "Small Thumbnail"
    
    def thumbnail_medium_display(self, obj):
        """Medium thumbnail for detail view"""
        local_url = None
        if obj.thumbnail_medium:
            local_url = self.get_local_thumbnail_path(obj.thumbnail_medium)
        
        # Determine which image to show (prefer local)
        display_url = local_url if local_url else obj.thumbnail_medium_url
        
        if display_url:
            html = f'<div><img src="{display_url}" style="max-height: 200px; max-width: 300px;" /><br/>'
            
            # Add local link if exists
            if local_url:
                html += f'<a href="{local_url}" target="_blank">Local: {obj.thumbnail_medium}</a><br/>'
            
            # Add remote link if exists
            if obj.thumbnail_medium_url:
                html += f'<a href="{obj.thumbnail_medium_url}" target="_blank">Remote: {obj.thumbnail_medium_url}</a>'
            
            html += '</div>'
            return format_html(html)
        
        return "No medium thumbnail"
    thumbnail_medium_display.short_description = "Medium Thumbnail"
    
    def thumbnail_large_display(self, obj):
        """Large thumbnail for detail view"""
        local_url = None
        if obj.thumbnail_large:
            local_url = self.get_local_thumbnail_path(obj.thumbnail_large)
        
        # Determine which image to show (prefer local)
        display_url = local_url if local_url else obj.thumbnail_large_url
        
        if display_url:
            html = f'<div><img src="{display_url}" style="max-height: 300px; max-width: 400px;" /><br/>'
            
            # Add local link if exists
            if local_url:
                html += f'<a href="{local_url}" target="_blank">Local: {obj.thumbnail_large}</a><br/>'
            
            # Add remote link if exists
            if obj.thumbnail_large_url:
                html += f'<a href="{obj.thumbnail_large_url}" target="_blank">Remote: {obj.thumbnail_large_url}</a>'
            
            html += '</div>'
            return format_html(html)
        
        return "No large thumbnail"
    thumbnail_large_display.short_description = "Large Thumbnail"
    
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
