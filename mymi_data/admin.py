from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django.db.models import Count
import os
from .models import (
    OrganSystem, Species, Staining, Subject, Institution, 
    TileServer, Image, Exploration, Annotation, AnnotationGroup, 
    Diagnosis, StructureSearch, Locale
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
                      'thumbnail_medium_display', 'thumbnail_large_display', 'mymi_link_display', 'state', 'imaging_diagnostic', 
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
    
    def mymi_link_display(self, obj):
        """Display MyMi link as clickable link"""
        return format_html('<a href="{}" target="_blank">{}</a>', obj.mymi_link, obj.mymi_link)
    mymi_link_display.short_description = "MyMi Link"
    
    def get_readonly_fields(self, request, obj=None):
        # Make organ_systems readonly too by overriding the field
        return self.readonly_fields + ('organ_systems',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class AnnotationCountConsistencyFilter(admin.SimpleListFilter):
    title = 'Annotation Count Consistency'
    parameter_name = 'annotation_count_consistent'

    def lookups(self, request, model_admin):
        return (
            ('consistent', 'Count matches (✅)'),
            ('inconsistent', 'Count mismatch (❌)'),
            ('not_crawled', 'Not crawled yet (⚠️)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'consistent':
            # Filter explorations where actual count matches stored count
            consistent_ids = []
            for exploration in queryset:
                actual_count = Annotation.objects.filter(exploration=exploration).count()
                if actual_count == exploration.annotation_count:
                    consistent_ids.append(exploration.id)
            return queryset.filter(id__in=consistent_ids)
        
        elif self.value() == 'inconsistent':
            # Filter explorations where actual count doesn't match stored count
            inconsistent_ids = []
            for exploration in queryset:
                actual_count = Annotation.objects.filter(exploration=exploration).count()
                if actual_count != exploration.annotation_count and exploration.annotation_count > 0:
                    inconsistent_ids.append(exploration.id)
            return queryset.filter(id__in=inconsistent_ids)
        
        elif self.value() == 'not_crawled':
            # Filter explorations that haven't been crawled yet (annotation_count > 0 but no actual annotations)
            not_crawled_ids = []
            for exploration in queryset:
                actual_count = Annotation.objects.filter(exploration=exploration).count()
                if actual_count == 0 and exploration.annotation_count > 0:
                    not_crawled_ids.append(exploration.id)
            return queryset.filter(id__in=not_crawled_ids)
        
        return queryset


class AnnotationGroupCountConsistencyFilter(admin.SimpleListFilter):
    title = 'Annotation Group Count Consistency'
    parameter_name = 'annotation_group_count_consistent'

    def lookups(self, request, model_admin):
        return (
            ('consistent', 'Count matches (✅)'),
            ('inconsistent', 'Count mismatch (❌)'),
            ('not_crawled', 'Not crawled yet (⚠️)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'consistent':
            # Filter explorations where actual count matches stored count
            consistent_ids = []
            for exploration in queryset:
                actual_count = AnnotationGroup.objects.filter(exploration=exploration).count()
                if actual_count == exploration.annotation_group_count:
                    consistent_ids.append(exploration.id)
            return queryset.filter(id__in=consistent_ids)
        
        elif self.value() == 'inconsistent':
            # Filter explorations where actual count doesn't match stored count
            inconsistent_ids = []
            for exploration in queryset:
                actual_count = AnnotationGroup.objects.filter(exploration=exploration).count()
                if actual_count != exploration.annotation_group_count and exploration.annotation_group_count > 0:
                    inconsistent_ids.append(exploration.id)
            return queryset.filter(id__in=inconsistent_ids)
        
        elif self.value() == 'not_crawled':
            # Filter explorations that haven't been crawled yet (annotation_group_count > 0 but no actual groups)
            not_crawled_ids = []
            for exploration in queryset:
                actual_count = AnnotationGroup.objects.filter(exploration=exploration).count()
                if actual_count == 0 and exploration.annotation_group_count > 0:
                    not_crawled_ids.append(exploration.id)
            return queryset.filter(id__in=not_crawled_ids)
        
        return queryset


@admin.register(Exploration)
class ExplorationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_active', 'image', 'institution', 'is_exam', 'actual_annotation_count', 'actual_annotation_group_count')
    list_filter = ('is_active', 'is_exam', 'institution', 'type', AnnotationCountConsistencyFilter, AnnotationGroupCountConsistencyFilter)
    search_fields = ('title', 'edu_id')
    readonly_fields = ('id', 'title', 'is_active', 'image', 'institution', 'annotation_group_count', 
                      'annotation_count', 'is_exam', 'edu_id', 'mymi_link_display', 'image_thumbnail_display', 
                      'tags', 'deleted_at', 'type', 'annotations_by_groups_display')
    
    def get_local_thumbnail_path(self, filename):
        """Check if thumbnail exists locally in media/thumbnails/"""
        if not filename:
            return None
        local_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', filename)
        if os.path.exists(local_path):
            return f"{settings.MEDIA_URL}thumbnails/{filename}"
        return None
    
    def mymi_link_display(self, obj):
        """Display MyMi link as clickable link"""
        return format_html('<a href="{}" target="_blank">{}</a>', obj.mymi_link, obj.mymi_link)
    mymi_link_display.short_description = "MyMi Link"
    
    def image_thumbnail_display(self, obj):
        """Display large thumbnail from related Image"""
        if not obj.image:
            return "No image"
        
        # Use the same logic as ImageAdmin for consistent display
        local_url = None
        if obj.image.thumbnail_large:
            local_url = self.get_local_thumbnail_path(obj.image.thumbnail_large)
        
        # Determine which image to show (prefer local)
        display_url = local_url if local_url else obj.image.thumbnail_large_url
        
        if display_url:
            html = f'<div><img src="{display_url}" style="max-height: 300px; max-width: 400px;" /><br/>'
            
            # Add local link if exists
            if local_url:
                html += f'<a href="{local_url}" target="_blank">Local: {obj.image.thumbnail_large}</a><br/>'
            
            # Add remote link if exists
            if obj.image.thumbnail_large_url:
                html += f'<a href="{obj.image.thumbnail_large_url}" target="_blank">Remote: {obj.image.thumbnail_large_url}</a>'
            
            html += '</div>'
            return format_html(html)
        
        return "No large thumbnail"
    image_thumbnail_display.short_description = "Image Thumbnail"
    
    def annotations_by_groups_display(self, obj):
        """Display all annotations grouped by annotation groups"""
        # Get all annotation groups for this exploration
        annotation_groups = AnnotationGroup.objects.filter(exploration=obj).order_by('taglabel', 'tagname')
        
        if not annotation_groups.exists():
            return "No annotation groups found"
        
        html_parts = []
        total_annotations = 0
        
        for group in annotation_groups:
            # Find annotations that belong to this group
            related_annotations = Annotation.objects.filter(
                exploration=obj,
                tag_ids__contains=[group.tagid]
            ).order_by('annotationname', 'id')
            
            # Group header
            group_name = group.taglabel or group.tagname or f"Group {group.id}"
            group_admin_url = f"/admin/mymi_data/annotationgroup/{group.id}/change/"
            html_parts.append(f'<h4><a href="{group_admin_url}" target="_blank">{group_name}</a></h4>')
            
            if related_annotations.exists():
                # List annotations in this group
                html_parts.append('<ul>')
                for annotation in related_annotations:
                    admin_url = f"/admin/mymi_data/annotation/{annotation.id}/change/"
                    name = annotation.annotationname or f"Annotation {annotation.id}"
                    html_parts.append(f'<li><a href="{admin_url}" target="_blank">{name}</a> (Type: {annotation.type})</li>')
                    total_annotations += 1
                html_parts.append('</ul>')
            else:
                html_parts.append('<p><em>No annotations in this group</em></p>')
        
        # Check for annotations without groups (tag_ids empty or not matching any group)
        all_group_tagids = list(annotation_groups.values_list('tagid', flat=True))
        ungrouped_annotations = Annotation.objects.filter(exploration=obj).exclude(
            tag_ids__overlap=all_group_tagids
        ).order_by('annotationname', 'id')
        
        if ungrouped_annotations.exists():
            html_parts.append('<h4>📌 Ungrouped Annotations</h4>')
            html_parts.append('<ul>')
            for annotation in ungrouped_annotations:
                admin_url = f"/admin/mymi_data/annotation/{annotation.id}/change/"
                name = annotation.annotationname or f"Annotation {annotation.id}"
                html_parts.append(f'<li><a href="{admin_url}" target="_blank">{name}</a> (Type: {annotation.type})</li>')
                total_annotations += 1
            html_parts.append('</ul>')
        
        # Summary
        html_parts.append(f'<hr><small><strong>Total: {total_annotations} annotation(s) in {annotation_groups.count()} group(s)</strong></small>')
        
        return format_html(''.join(html_parts))
    annotations_by_groups_display.short_description = "Annotations by Groups"
    
    def actual_annotation_count(self, obj):
        """Display actual count of annotations vs stored count"""
        actual_count = Annotation.objects.filter(exploration=obj).count()
        stored_count = obj.annotation_count
        
        if actual_count == stored_count:
            status = "✅"
            color = "green"
        elif actual_count == 0 and stored_count > 0:
            status = "⚠️"
            color = "orange"
        else:
            status = "❌"
            color = "red"
        
        return format_html(
            '<span style="color: {};">{} {} / {}</span>',
            color, status, actual_count, stored_count
        )
    actual_annotation_count.short_description = "Annotations (Actual/Expected)"
    
    def actual_annotation_group_count(self, obj):
        """Display actual count of annotation groups vs stored count"""
        actual_count = AnnotationGroup.objects.filter(exploration=obj).count()
        stored_count = obj.annotation_group_count
        
        if actual_count == stored_count:
            status = "✅"
            color = "green"
        elif actual_count == 0 and stored_count > 0:
            status = "⚠️"
            color = "orange"
        else:
            status = "❌"
            color = "red"
        
        return format_html(
            '<span style="color: {};">{} {} / {}</span>',
            color, status, actual_count, stored_count
        )
    actual_annotation_group_count.short_description = "Groups (Actual/Expected)"
    
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
                      'annotation_group_count', 'annotation_count', 'mymi_link_display', 'image_thumbnail_display', 'tags', 'deleted_at', 'type')
    
    def get_local_thumbnail_path(self, filename):
        """Check if thumbnail exists locally in media/thumbnails/"""
        if not filename:
            return None
        local_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', filename)
        if os.path.exists(local_path):
            return f"{settings.MEDIA_URL}thumbnails/{filename}"
        return None
    
    def mymi_link_display(self, obj):
        """Display MyMi link as clickable link"""
        return format_html('<a href="{}" target="_blank">{}</a>', obj.mymi_link, obj.mymi_link)
    mymi_link_display.short_description = "MyMi Link"
    
    def image_thumbnail_display(self, obj):
        """Display large thumbnail from related Image"""
        if not obj.image:
            return "No image"
        
        # Use the same logic as ImageAdmin for consistent display
        local_url = None
        if obj.image.thumbnail_large:
            local_url = self.get_local_thumbnail_path(obj.image.thumbnail_large)
        
        # Determine which image to show (prefer local)
        display_url = local_url if local_url else obj.image.thumbnail_large_url
        
        if display_url:
            html = f'<div><img src="{display_url}" style="max-height: 300px; max-width: 400px;" /><br/>'
            
            # Add local link if exists
            if local_url:
                html += f'<a href="{local_url}" target="_blank">Local: {obj.image.thumbnail_large}</a><br/>'
            
            # Add remote link if exists
            if obj.image.thumbnail_large_url:
                html += f'<a href="{obj.image.thumbnail_large_url}" target="_blank">Remote: {obj.image.thumbnail_large_url}</a>'
            
            html += '</div>'
            return format_html(html)
        
        return "No large thumbnail"
    image_thumbnail_display.short_description = "Image Thumbnail"
    
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('subjects',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AnnotationGroup)
class AnnotationGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'taglabel', 'tagname', 'exploration', 'creator_id')
    list_filter = ('exploration', 'creator_id')
    search_fields = ('taglabel', 'tagname', 'tagdescription')
    readonly_fields = ('id', 'external_id', 'tagid', 'tagname', 'revision', 'taggroup', 'taglabel', 
                      'tagdescription', 'creator_id', 'displaystyle', 'exploration', 'related_annotations_display')
    actions = ['delete_selected_annotation_groups']
    
    def related_annotations_display(self, obj):
        """Display all annotations that belong to this annotation group"""
        # Find annotations in the same exploration that have this tagid in their tag_ids
        related_annotations = Annotation.objects.filter(
            exploration=obj.exploration,
            tag_ids__contains=[obj.tagid]
        ).order_by('id')
        
        if not related_annotations.exists():
            return "No related annotations"
        
        # Create HTML list of related annotations
        html_items = []
        for annotation in related_annotations:
            # Create a link to the annotation in admin
            admin_url = f"/admin/mymi_data/annotation/{annotation.id}/change/"
            name = annotation.annotationname or f"Annotation {annotation.id}"
            html_items.append(f'<li><a href="{admin_url}" target="_blank">{name}</a> (Type: {annotation.type})</li>')
        
        html = f'<ul>{"".join(html_items)}</ul>'
        html += f'<small>Total: {related_annotations.count()} annotation(s)</small>'
        
        return format_html(html)
    related_annotations_display.short_description = "Related Annotations"
    
    def delete_selected_annotation_groups(self, request, queryset):
        """Custom delete action for annotation groups"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Successfully deleted {count} annotation group(s).')
    delete_selected_annotation_groups.short_description = "Delete selected annotation groups"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'annotationname', 'type', 'exploration', 'show', 'creator_id')
    list_filter = ('type', 'show', 'exploration', 'creator_id', 'exploration__institution')
    search_fields = ('annotationname', 'annotationdescription')
    readonly_fields = ('id', 'external_id', 'annotationid', 'annotationname', 'annotationdescription', 
                      'show', 'version', 'revision', 'type', 'coord_xmin', 'coord_xmax',
                      'coord_ymin', 'coord_ymax', 'coord_zmin', 'coord_zmax', 'coord_tmin',
                      'coord_tmax', 'geometry', 'rotation', 'displaystyle', 'tag_ids',
                      'channels', 'scope_id', 'creator_id', 'mousebinded', 'tagdescription',
                      'typespecificflags', 'exploration')
    actions = ['delete_selected_annotations']
    
    def delete_selected_annotations(self, request, queryset):
        """Custom delete action for annotations"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Successfully deleted {count} annotation(s).')
    delete_selected_annotations.short_description = "Delete selected annotations"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Locale)
class LocaleAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
    search_fields = ('key', 'value')
    readonly_fields = ('key', 'value')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
