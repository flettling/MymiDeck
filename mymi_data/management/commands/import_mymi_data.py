import json
from django.core.management.base import BaseCommand
from django.db import transaction
from mymi_data.models import (
    OrganSystem, Species, Staining, Subject, Institution, 
    TileServer, Image, Exploration, Diagnosis, StructureSearch, Locale
)


class Command(BaseCommand):
    help = 'Import MyMi data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/import_data.json',
            help='Path to JSON file to import (default: data/import_data.json)'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        self.stdout.write(f'Importing data from {file_path}...')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File {file_path} not found')
            )
            return
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Invalid JSON: {e}')
            )
            return

        with transaction.atomic():
            # Import organ systems
            if 'organsystems' in data:
                self.import_organ_systems(data['organsystems'])
            
            # Import species
            if 'species' in data:
                self.import_species(data['species'])
            
            # Import stainings
            if 'stainings' in data:
                self.import_stainings(data['stainings'])
            
            # Import subjects
            if 'subjects' in data:
                self.import_subjects(data['subjects'])
            
            # Import institutions
            if 'institutions' in data:
                self.import_institutions(data['institutions'])
            
            # Import tile servers
            if 'tileservers' in data:
                self.import_tile_servers(data['tileservers'])
            
            # Import images
            if 'images' in data:
                self.import_images(data['images'])
            
            # Import explorations
            if 'explorations' in data:
                self.import_explorations(data['explorations'])
            
            # Import diagnoses
            if 'diagnoses' in data:
                self.import_diagnoses(data['diagnoses'])
            
            # Import structure searches
            if 'structureSearches' in data:
                self.import_structure_searches(data['structureSearches'])
            
            # Import locales
            if 'locales' in data and isinstance(data['locales'], dict):
                self.import_locales(data['locales'])

        self.stdout.write(
            self.style.SUCCESS('Successfully imported all data')
        )

    def import_organ_systems(self, items):
        self.stdout.write(f'Importing {len(items)} organ systems...')
        for item in items:
            OrganSystem.objects.update_or_create(
                id=item['id'],
                defaults={'title': item['title']}
            )
        self.stdout.write(self.style.SUCCESS(f'Imported {len(items)} organ systems'))

    def import_species(self, items):
        self.stdout.write(f'Importing {len(items)} species...')
        for item in items:
            Species.objects.update_or_create(
                id=item['id'],
                defaults={'title': item['title']}
            )
        self.stdout.write(self.style.SUCCESS(f'Imported {len(items)} species'))

    def import_stainings(self, items):
        self.stdout.write(f'Importing {len(items)} stainings...')
        for item in items:
            Staining.objects.update_or_create(
                id=item['id'],
                defaults={'title': item['title']}
            )
        self.stdout.write(self.style.SUCCESS(f'Imported {len(items)} stainings'))

    def import_subjects(self, items):
        self.stdout.write(f'Importing {len(items)} subjects...')
        for item in items:
            Subject.objects.update_or_create(
                id=item['id'],
                defaults={'title': item['title']}
            )
        self.stdout.write(self.style.SUCCESS(f'Imported {len(items)} subjects'))

    def import_institutions(self, items):
        self.stdout.write(f'Importing {len(items)} institutions...')
        for item in items:
            Institution.objects.update_or_create(
                id=item['id'],
                defaults={
                    'title': item['title'],
                    'short_title': item.get('shortTitle', ''),
                    'acronym': item.get('acronym', ''),
                    'introduction': item.get('introduction', ''),
                    'logo_url': item.get('logoUrl', ''),
                    'small_logo_url': item.get('smallLogoUrl', ''),
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Imported {len(items)} institutions'))

    def import_tile_servers(self, items):
        self.stdout.write(f'Importing {len(items)} tile servers...')
        for item in items:
            try:
                institution = Institution.objects.get(id=item['institutionId'])
                TileServer.objects.update_or_create(
                    id=item['id'],
                    defaults={
                        'title': item['title'],
                        'institution': institution,
                        'public_urls': item.get('publicUrls', []),
                    }
                )
            except Institution.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Institution {item["institutionId"]} not found for tile server {item["id"]}')
                )
        self.stdout.write(self.style.SUCCESS(f'Imported {len(items)} tile servers'))

    def import_images(self, items):
        self.stdout.write(f'Importing {len(items)} images...')
        for item in items:
            try:
                staining = None
                if item.get('stainingId'):
                    try:
                        staining = Staining.objects.get(id=item['stainingId'])
                    except Staining.DoesNotExist:
                        pass

                species = None
                if item.get('specieId'):
                    try:
                        species = Species.objects.get(id=item['specieId'])
                    except Species.DoesNotExist:
                        pass

                tile_server = None
                if item.get('tileserverId'):
                    try:
                        tile_server = TileServer.objects.get(id=item['tileserverId'])
                    except TileServer.DoesNotExist:
                        pass

                image, created = Image.objects.update_or_create(
                    id=item['id'],
                    defaults={
                        'title': item['title'],
                        'checksum': item['checksum'],
                        'size': int(item['size']),
                        'file_path': item['filePath'],
                        'thumbnail_small': item.get('thumbnailSmall', ''),
                        'thumbnail_medium': item.get('thumbnailMedium', ''),
                        'thumbnail_large': item.get('thumbnailLarge', ''),
                        'state': item.get('state', 'active'),
                        'imaging_diagnostic': item['imagingDiagnostic'],
                        'staining': staining,
                        'species': species,
                        'tile_server': tile_server,
                        'tags': item.get('tags', []),
                        'deleted_at': None if item.get('deletedAt') is None else item['deletedAt'],
                    }
                )

                # Add organ systems (many-to-many)
                if item.get('organsystemIds'):
                    organ_systems = OrganSystem.objects.filter(id__in=item['organsystemIds'])
                    image.organ_systems.set(organ_systems)

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error importing image {item["id"]}: {e}')
                )
        self.stdout.write(self.style.SUCCESS(f'Imported {len(items)} images'))

    def import_explorations(self, items):
        self.stdout.write(f'Importing {len(items)} explorations...')
        for item in items:
            try:
                image = Image.objects.get(id=item['imageId'])
                institution = Institution.objects.get(id=item['institutionId'])
                
                exploration, created = Exploration.objects.update_or_create(
                    id=item['id'],
                    defaults={
                        'title': item['title'],
                        'is_active': item['isActive'],
                        'image': image,
                        'institution': institution,
                        'annotation_group_count': item.get('annotationGroupCount', 0),
                        'annotation_count': item.get('annotationCount', 0),
                        'is_exam': item['isExam'],
                        'edu_id': item.get('eduId', ''),
                        'tags': item.get('tags', []),
                        'deleted_at': None if item.get('deletedAt') is None else item['deletedAt'],
                        'type': item.get('type', 'exploration'),
                    }
                )

                # Add subjects (many-to-many)
                if item.get('subjectIds'):
                    subjects = Subject.objects.filter(id__in=item['subjectIds'])
                    exploration.subjects.set(subjects)

            except (Image.DoesNotExist, Institution.DoesNotExist) as e:
                self.stdout.write(
                    self.style.WARNING(f'Error importing exploration {item["id"]}: {e}')
                )
        self.stdout.write(self.style.SUCCESS(f'Imported {len(items)} explorations'))

    def import_diagnoses(self, items):
        self.stdout.write(f'Importing {len(items)} diagnoses...')
        for item in items:
            try:
                image = Image.objects.get(id=item['imageId'])
                institution = Institution.objects.get(id=item['institutionId'])
                
                Diagnosis.objects.update_or_create(
                    id=item['id'],
                    defaults={
                        'is_active': item['isActive'],
                        'image': image,
                        'institution': institution,
                        'is_exam': item['isExam'],
                        'deleted_at': None if item.get('deletedAt') is None else item['deletedAt'],
                        'type': item.get('type', 'diagnosis'),
                    }
                )
            except (Image.DoesNotExist, Institution.DoesNotExist) as e:
                self.stdout.write(
                    self.style.WARNING(f'Error importing diagnosis {item["id"]}: {e}')
                )
        self.stdout.write(self.style.SUCCESS(f'Imported {len(items)} diagnoses'))

    def import_structure_searches(self, items):
        self.stdout.write(f'Importing {len(items)} structure searches...')
        for item in items:
            try:
                image = Image.objects.get(id=item['imageId'])
                institution = Institution.objects.get(id=item['institutionId'])
                
                structure_search, created = StructureSearch.objects.update_or_create(
                    id=item['id'],
                    defaults={
                        'title': item['title'],
                        'is_active': item['isActive'],
                        'image': image,
                        'institution': institution,
                        'is_exam': item['isExam'],
                        'annotation_group_count': item.get('annotationGroupCount', 0),
                        'annotation_count': item.get('annotationCount', 0),
                        'tags': item.get('tags', []),
                        'deleted_at': None if item.get('deletedAt') is None else item['deletedAt'],
                        'type': item.get('type', 'structure-search'),
                    }
                )

                # Add subjects (many-to-many)
                if item.get('subjectIds'):
                    subjects = Subject.objects.filter(id__in=item['subjectIds'])
                    structure_search.subjects.set(subjects)

            except (Image.DoesNotExist, Institution.DoesNotExist) as e:
                self.stdout.write(
                    self.style.WARNING(f'Error importing structure search {item["id"]}: {e}')
                )
        self.stdout.write(self.style.SUCCESS(f'Imported {len(items)} structure searches'))

    def import_locales(self, locales_dict):
        self.stdout.write(f'Importing {len(locales_dict)} locales...')
        for key, value in locales_dict.items():
            Locale.objects.update_or_create(
                key=key,
                defaults={'value': value}
            )
        self.stdout.write(self.style.SUCCESS(f'Imported {len(locales_dict)} locales'))