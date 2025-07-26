import os
import requests
from django.core.management.base import BaseCommand
from mymi_data.models import Image


class Command(BaseCommand):
    help = 'Crawl thumbnails from MyMi platform (simple version with manual cookie setup)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='media/thumbnails',
            help='Output directory for thumbnails (default: media/thumbnails)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of images to process (for testing)'
        )
        parser.add_argument(
            '--cookies',
            type=str,
            help='Session cookies as string (optional - will prompt if not provided)',
            required=False
        )

    def download_thumbnails(self, session, image_obj, output_dir):
        """Download all thumbnails for a single image"""
        # Use the calculated thumbnail URLs from the model
        thumbnail_urls = [
            ('large', image_obj.thumbnail_large_url),
            ('medium', image_obj.thumbnail_medium_url),
            ('small', image_obj.thumbnail_small_url)
        ]
        
        # Filter out None values
        thumbnail_urls = [(size, url) for size, url in thumbnail_urls if url]
        
        if not thumbnail_urls:
            self.stdout.write(f"⚠️  No thumbnail URLs found for image {image_obj.id}")
            return 0
        
        self.stdout.write(f"🔍 Found {len(thumbnail_urls)} thumbnail URLs for {image_obj.id}")
        
        downloaded_count = 0
        
        for size, thumbnail_url in thumbnail_urls:
            try:
                self.stdout.write(f"📥 Downloading {size}: {thumbnail_url}")
                response = session.get(thumbnail_url, timeout=30)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    # If we get HTML instead of image, it's probably a login/error page
                    if 'text/html' in content_type:
                        self.stdout.write(f"⚠️  Got HTML response for {size} - check authentication")
                        continue
                        
                    if 'image' in content_type or thumbnail_url.endswith(('.jpg', '.jpeg', '.png')):
                        # Extract filename from URL (e.g., 53lN9wqU33OC20fO.jpg from /assets/thumbnails/53lN9wqU33OC20fO.jpg)
                        filename = thumbnail_url.split('/')[-1]
                        filepath = os.path.join(output_dir, filename)
                        
                        # Save thumbnail
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        self.stdout.write(f"✅ Downloaded {size}: {filename}")
                        downloaded_count += 1
                    else:
                        self.stdout.write(f"⚠️  Invalid content type for {size}: {content_type}")
                else:
                    self.stdout.write(f"❌ HTTP {response.status_code} for {size} thumbnail")
                        
            except Exception as e:
                self.stdout.write(f"⚠️  Failed {size} thumbnail: {str(e)}")
                continue
        
        if downloaded_count == 0:
            self.stdout.write(f"❌ No thumbnails downloaded for image {image_obj.id}")
        else:
            self.stdout.write(f"🎉 Downloaded {downloaded_count}/{len(thumbnail_urls)} thumbnails for {image_obj.id}")
        
        return downloaded_count

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        limit = options.get('limit')
        cookies_string = options.get('cookies')
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        self.stdout.write(self.style.SUCCESS(f"🚀 Starting thumbnail crawler..."))
        self.stdout.write(f"📁 Output directory: {output_dir}")
        if limit:
            self.stdout.write(f"🔢 Processing limit: {limit} images")
        
        # Get JWT token
        if not cookies_string:
            self.stdout.write("\n🔐 MyMi JWT Token Required")
            self.stdout.write("1. Go to https://mymi.uni-ulm.de/ and login")
            self.stdout.write("2. Press F12 → Application → Cookies → mymi_jwt")
            self.stdout.write("3. Copy the JWT token value and paste below:")
            jwt_token = input("\nJWT Token: ").strip()
            cookies_string = f"mymi_jwt={jwt_token}"
        
        # Parse cookies
        cookies = {}
        for cookie in cookies_string.split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                cookies[key] = value
        
        self.stdout.write(f"🍪 Using {len(cookies)} cookies for authentication")
        
        # Create authenticated session
        session = requests.Session()
        session.cookies.update(cookies)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Get images to process
        images_query = Image.objects.all()
        if limit:
            images_query = images_query[:limit]
        
        images = list(images_query)
        total_images = len(images)
        
        self.stdout.write(f"🎯 Found {total_images} images to process")
        
        total_downloaded = 0
        total_failed = 0
        
        for i, image_obj in enumerate(images, 1):
            self.stdout.write(f"📸 Processing {i}/{total_images}: {image_obj.title}")
            
            downloaded_count = self.download_thumbnails(session, image_obj, output_dir)
            if downloaded_count > 0:
                total_downloaded += downloaded_count
            else:
                total_failed += 1
            
            # Rate limiting between images
            import time
            time.sleep(0.5)
        
        self.stdout.write(self.style.SUCCESS(
            f"🎉 Download complete! Downloaded: {total_downloaded} thumbnails, Failed images: {total_failed}"
        ))