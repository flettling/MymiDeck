import json
import time
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from mymi_data.models import Exploration, AnnotationGroup, Annotation


class Command(BaseCommand):
    help = 'Crawl annotations and annotation groups for all explorations from MyMi API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of explorations to process (for testing)',
        )
        parser.add_argument(
            '--exploration-id',
            type=str,
            help='Process only specific exploration ID',
        )
        parser.add_argument(
            '--cookies',
            type=str,
            help='JWT token directly (mymi_jwt=...)',
        )

    def handle(self, *args, **options):
        limit = options.get('limit')
        exploration_id = options.get('exploration_id')
        jwt_token = options.get('cookies')

        # Get JWT token if not provided
        if not jwt_token:
            self.stdout.write(self.style.HTTP_INFO('🔐 MyMi JWT Token Required'))
            self.stdout.write('1. Go to https://mymi.uni-ulm.de/ and login')
            self.stdout.write('2. Press F12 → Application → Cookies → mymi_jwt')
            self.stdout.write('3. Copy the JWT token value and paste below:')
            jwt_token = input('JWT Token: ').strip()

        # Clean JWT token format
        if jwt_token.startswith('mymi_jwt='):
            jwt_token = jwt_token[9:]  # Remove prefix

        # Setup session with cookies
        session = requests.Session()
        session.cookies.set('mymi_jwt', jwt_token, domain='mymi.uni-ulm.de')

        # Get explorations to process
        if exploration_id:
            try:
                explorations = Exploration.objects.filter(id=exploration_id)
                if not explorations.exists():
                    self.stdout.write(self.style.ERROR(f'Exploration {exploration_id} not found'))
                    return
            except Exploration.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Exploration {exploration_id} not found'))
                return
        else:
            explorations = Exploration.objects.all()
            if limit:
                explorations = explorations[:limit]

        total_count = explorations.count()
        self.stdout.write(f'Processing {total_count} exploration(s)...')

        success_count = 0
        error_count = 0

        for i, exploration in enumerate(explorations, 1):
            try:
                self.stdout.write(f'[{i}/{total_count}] Processing {exploration.id}: {exploration.title}')
                
                success = self.crawl_exploration_annotations(session, exploration)
                if success:
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Successfully processed {exploration.id}'))
                else:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'  ❌ Failed to process {exploration.id}'))

                # Rate limiting - be nice to the server
                time.sleep(0.5)

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'  ❌ Error processing {exploration.id}: {str(e)}'))

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Processed: {total_count} explorations')
        self.stdout.write(self.style.SUCCESS(f'Success: {success_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))

    def crawl_exploration_annotations(self, session, exploration):
        """Crawl annotations and annotation groups for a single exploration"""
        try:
            with transaction.atomic():
                # URLs for API endpoints
                annotations_url = f"https://mymi.uni-ulm.de/api/exploration/{exploration.id}/annotation/annotation"
                groups_url = f"https://mymi.uni-ulm.de/api/exploration/{exploration.id}/annotation/annotation-group"

                # Fetch annotations
                annotations_response = session.get(annotations_url)
                if annotations_response.status_code != 200:
                    self.stdout.write(f'    ⚠️ Failed to fetch annotations: HTTP {annotations_response.status_code}')
                    return False

                # Fetch annotation groups
                groups_response = session.get(groups_url)
                if groups_response.status_code != 200:
                    self.stdout.write(f'    ⚠️ Failed to fetch annotation groups: HTTP {groups_response.status_code}')
                    return False

                # Parse JSON responses
                try:
                    annotations_data = annotations_response.json()
                    groups_data = groups_response.json()
                except json.JSONDecodeError as e:
                    self.stdout.write(f'    ⚠️ Failed to parse JSON: {str(e)}')
                    return False

                # Store raw API responses in exploration
                exploration.annotations_raw = annotations_data
                exploration.annotation_groups_raw = groups_data
                exploration.save()

                # Process annotation groups first (needed for foreign key relationships)
                self.process_annotation_groups(exploration, groups_data)
                
                # Process annotations
                self.process_annotations(exploration, annotations_data)

                self.stdout.write(f'    📊 Saved {len(groups_data)} groups, {len(annotations_data)} annotations')
                return True

        except Exception as e:
            self.stdout.write(f'    ❌ Database error: {str(e)}')
            return False

    def process_annotation_groups(self, exploration, groups_data):
        """Process and save annotation groups"""
        if not isinstance(groups_data, list):
            return

        # Clear existing groups for this exploration
        AnnotationGroup.objects.filter(exploration=exploration).delete()

        for group_data in groups_data:
            try:
                AnnotationGroup.objects.create(
                    id=group_data.get('id'),
                    tagid=group_data.get('tagid', group_data.get('id')),
                    tagname=group_data.get('tagname', ''),
                    revision=group_data.get('revision', ''),
                    taggroup=group_data.get('taggroup', ''),
                    taglabel=group_data.get('taglabel', ''),
                    tagdescription=group_data.get('tagdescription', ''),
                    creator_id=group_data.get('creator_id', 0),
                    displaystyle=group_data.get('displaystyle'),
                    exploration=exploration
                )
            except Exception as e:
                self.stdout.write(f'    ⚠️ Failed to save annotation group {group_data.get("id")}: {str(e)}')

    def process_annotations(self, exploration, annotations_data):
        """Process and save annotations"""
        if not isinstance(annotations_data, list):
            return

        # Clear existing annotations for this exploration
        Annotation.objects.filter(exploration=exploration).delete()

        for annotation_data in annotations_data:
            try:
                Annotation.objects.create(
                    id=annotation_data.get('id'),
                    annotationid=annotation_data.get('annotationid', annotation_data.get('id')),
                    annotationname=annotation_data.get('annotationname', ''),
                    annotationdescription=annotation_data.get('annotationdescription', ''),
                    show=annotation_data.get('show', True),
                    version=annotation_data.get('version', 1),
                    revision=annotation_data.get('revision', ''),
                    type=annotation_data.get('type', 0),
                    coord_xmin=annotation_data.get('xmin', 0),
                    coord_xmax=annotation_data.get('xmax', 0),
                    coord_ymin=annotation_data.get('ymin', 0),
                    coord_ymax=annotation_data.get('ymax', 0),
                    coord_zmin=annotation_data.get('zmin', 0),
                    coord_zmax=annotation_data.get('zmax', 0),
                    coord_tmin=annotation_data.get('tmin', 0),
                    coord_tmax=annotation_data.get('tmax', 0),
                    geometry=annotation_data.get('geometry', []),
                    rotation=annotation_data.get('rotation', 0),
                    displaystyle=annotation_data.get('displaystyle'),
                    tag_ids=annotation_data.get('tag_ids', []),
                    channels=annotation_data.get('channels', []),
                    scope_id=annotation_data.get('scope_id', 0),
                    creator_id=annotation_data.get('creator_id', 0),
                    mousebinded=annotation_data.get('mousebinded', False),
                    tagdescription=annotation_data.get('tagdescription', ''),
                    typespecificflags=annotation_data.get('typespecificflags', ''),
                    exploration=exploration
                )
            except Exception as e:
                self.stdout.write(f'    ⚠️ Failed to save annotation {annotation_data.get("id")}: {str(e)}')