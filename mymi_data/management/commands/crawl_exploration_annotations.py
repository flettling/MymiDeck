import os
import asyncio
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from playwright.async_api import async_playwright


class Command(BaseCommand):
    help = "Crawl exploration annotations from MyMi platform using Playwright"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--visible',
            action='store_true',
            help='Run browser in visible mode (default: headless for Docker)',
        )
        parser.add_argument(
            '--cookies',
            type=str,
            help='JWT token for authentication (if not provided, will prompt)',
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='media/screenshots',
            help='Directory to save screenshots (default: media/screenshots)',
        )
    
    def handle(self, *args, **options):
        asyncio.run(self.async_handle(options))
    
    async def async_handle(self, options):
        # Test URL für Exploration
        test_url = "https://mymi.uni-ulm.de/microscope/exploration/m3WiwXyV"
        
        # JWT Token handling
        jwt_token = options.get('cookies')
        if not jwt_token:
            jwt_token = self.get_jwt_token()
        
        # Screenshot directory setup
        screenshot_dir = Path(options['output_dir'])
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        self.stdout.write(f"🔬 Starting exploration annotation crawler...")
        self.stdout.write(f"📸 Screenshots will be saved to: {screenshot_dir}")
        self.stdout.write(f"🌐 Test URL: {test_url}")
        
        async with async_playwright() as p:
            # Browser setup - Default headless im Docker Container  
            is_headless = not options.get('visible', False)  # Umgekehrte Logik
            browser = await p.chromium.launch(
                headless=is_headless,
                slow_mo=1000 if not is_headless else 0,  # Langsamer wenn sichtbar
                args=[
                    '--disable-web-security',  # CORS deaktivieren
                    '--disable-features=VizDisplayCompositor',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            context = await browser.new_context(
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
                    'Cache-Control': 'no-cache'
                },
                # User Agent setzen um wie ein echter Browser zu wirken
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # JWT Cookie für alle MyMi-Domains setzen
            cookie_domains = [
                'mymi.uni-ulm.de',
                '.uni-ulm.de',  # Wildcard für alle Subdomains
            ]
            
            for domain in cookie_domains:
                await context.add_cookies([{
                    'name': 'mymi_jwt',
                    'value': jwt_token,
                    'domain': domain,
                    'path': '/',
                    'secure': True,
                    'httpOnly': False,
                }])
                self.stdout.write(f"🍪 JWT Cookie set for domain: {domain}")
            
            page = await context.new_page()
            
            # Network monitoring aktivieren
            await self.setup_network_monitoring(page)
            
            # Request Interception für Tile-Server Auth
            await self.setup_request_interception(page, jwt_token)
            
            try:
                self.stdout.write(f"🚀 Navigating to: {test_url}")
                await page.goto(test_url, wait_until='networkidle')
                
                # Überprüfen ob authentifiziert
                if await self.check_authentication(page):
                    self.stdout.write("✅ Authentication successful")
                    
                    # Debug der Seite
                    await self.debug_page_state(page)
                    
                    # Warten auf Content-Loading
                    await self.trigger_content_loading(page)
                    
                    # Nach Interaktion nochmal debuggen
                    await self.debug_page_state(page)
                    
                    # Screenshot machen
                    screenshot_path = screenshot_dir / "exploration_test.png"
                    await page.screenshot(path=str(screenshot_path), full_page=True)
                    self.stdout.write(f"📸 Screenshot saved: {screenshot_path}")
                    
                    # Kurz warten für Beobachtung (nur im sichtbaren Modus)
                    if not is_headless:
                        self.stdout.write("⏳ Waiting 5 seconds for observation...")
                        await page.wait_for_timeout(5000)
                    
                else:
                    self.stdout.write("❌ Authentication failed - please check JWT token")
                    
            except Exception as e:
                self.stdout.write(f"❌ Error during crawling: {e}")
                
            finally:
                await browser.close()
    
    def get_jwt_token(self):
        """Interaktive JWT-Token Eingabe"""
        self.stdout.write("\n🔐 MyMi JWT Token Required")
        self.stdout.write("1. Go to https://mymi.uni-ulm.de/ and login")  
        self.stdout.write("2. Press F12 → Application → Cookies → mymi_jwt")
        self.stdout.write("3. Copy the JWT token value and paste below:")
        
        jwt_token = input("JWT Token: ").strip()
        
        if not jwt_token:
            raise ValueError("JWT token is required for authentication")
            
        return jwt_token
    
    async def check_authentication(self, page):
        """Überprüft ob die Authentifizierung erfolgreich war"""
        try:
            # Warten auf ein Element das nur bei erfolgreicher Auth existiert
            # z.B. Microscope viewer oder spezifische UI-Elemente
            await page.wait_for_selector('.microscope-viewer', timeout=10000)
            return True
        except:
            # Falls Login-Form oder Redirect zur Login-Seite
            current_url = page.url
            if 'login' in current_url.lower() or 'auth' in current_url.lower():
                return False
            # Andere Checks können hier hinzugefügt werden
            return True
    
    async def wait_for_content_loaded(self, page):
        """Wartet auf vollständiges Laden der wichtigsten Bilder"""
        try:
            self.stdout.write("🔍 Analyzing page structure...")
            
            # Initial info
            page_info = await page.evaluate("""
                () => {
                    const imgs = document.querySelectorAll('img');
                    return {
                        imgCount: imgs.length,
                        loadedImgs: Array.from(imgs).filter(img => img.complete && img.naturalWidth > 0).length
                    };
                }
            """)
            
            self.stdout.write(f"📊 Images: {page_info['loadedImgs']}/{page_info['imgCount']} loaded")
            
            # Warten bis deutlich mehr Bilder geladen sind
            max_wait_time = 30000  # 30 Sekunden maximum
            check_interval = 2000   # Alle 2 Sekunden prüfen
            start_time = 0
            
            while start_time < max_wait_time:
                current_info = await page.evaluate("""
                    () => {
                        const imgs = document.querySelectorAll('img');
                        const loaded = Array.from(imgs).filter(img => img.complete && img.naturalWidth > 0).length;
                        return {
                            total: imgs.length,
                            loaded: loaded,
                            percentage: Math.round((loaded / imgs.length) * 100)
                        };
                    }
                """)
                
                self.stdout.write(f"⏳ Loading progress: {current_info['loaded']}/{current_info['total']} ({current_info['percentage']}%)")
                
                # Stoppen wenn mindestens 80% der Bilder geladen sind
                if current_info['percentage'] >= 80:
                    self.stdout.write("✅ Sufficient images loaded (80%+)")
                    break
                
                # Oder wenn sich 5 Sekunden nichts mehr tut
                if start_time > 0:
                    prev_loaded = getattr(self, '_prev_loaded', 0)
                    if current_info['loaded'] == prev_loaded and start_time > 10000:
                        self.stdout.write("✅ No more images loading, proceeding...")
                        break
                
                self._prev_loaded = current_info['loaded']
                await page.wait_for_timeout(check_interval)
                start_time += check_interval
            
            # Finaler Check
            final_info = await page.evaluate("""
                () => {
                    const imgs = document.querySelectorAll('img');
                    return Array.from(imgs).filter(img => img.complete && img.naturalWidth > 0).length;
                }
            """)
            
            self.stdout.write(f"✅ Final: {final_info} images loaded")
            
        except Exception as e:
            self.stdout.write(f"⚠️  Loading check failed: {e}")
            await page.wait_for_timeout(5000)
    
    async def setup_request_interception(self, page, jwt_token):
        """Fügt JWT-Token zu Tile-Server Requests hinzu"""
        async def handle_route(route):
            request = route.request
            
            # Nur Tile-Server Requests modifizieren
            if 'tl-ul' in request.url or '.mymi.uni-ulm.de' in request.url:
                # Bestehende Headers kopieren
                headers = dict(request.headers)
                
                # JWT als Cookie und Authorization Header hinzufügen
                if 'cookie' in headers:
                    if 'mymi_jwt' not in headers['cookie']:
                        headers['cookie'] += f'; mymi_jwt={jwt_token}'
                else:
                    headers['cookie'] = f'mymi_jwt={jwt_token}'
                
                # Auch als Authorization Header (falls erwartet)
                headers['authorization'] = f'Bearer {jwt_token}'
                
                self.stdout.write(f"🔒 Adding auth to: {request.url}")
                
                # Request mit modifizierten Headers weiterleiten
                await route.continue_(headers=headers)
            else:
                # Normale Requests unverändert weiterleiten
                await route.continue_()
        
        # Route handler aktivieren
        await page.route('**/*', handle_route)
    
    async def trigger_content_loading(self, page):
        """Einfaches Warten auf Content-Loading"""
        try:
            # Einfach warten bis die Annotationen geladen sind
            self.stdout.write("⏳ Waiting for annotations to load...")
            await page.wait_for_timeout(5000)  # 5 Sekunden warten
            
        except Exception as e:
            self.stdout.write(f"⚠️  Content loading failed: {e}")
            await page.wait_for_timeout(3000)
    
    async def setup_network_monitoring(self, page):
        """Überwacht Netzwerk-Requests und JavaScript-Errors"""
        self.requests = []
        self.js_errors = []
        
        # Request monitoring
        async def handle_request(request):
            try:
                self.requests.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': dict(request.headers)
                })
            except Exception as e:
                self.stdout.write(f"⚠️  Request monitoring error: {e}")
        
        # Response monitoring  
        async def handle_response(response):
            if 'api' in response.url or 'ajax' in response.url or response.url.endswith('.json') or 'mymi.tl' in response.url:
                try:
                    status = response.status
                    content_type = response.headers.get('content-type', '')
                    method = response.request.method if response.request else 'GET'
                    self.stdout.write(f"🌐 API Response: {method} {response.url} -> {status} ({content_type})")
                    
                    if status >= 400:
                        self.stdout.write(f"❌ Failed API Request: {response.url} -> {status}")
                    elif status == 0:
                        self.stdout.write(f"❌ CORS/Network Error: {response.url}")
                        
                except Exception as e:
                    self.stdout.write(f"⚠️  Response handling error: {e}")
        
        # Console/JS error monitoring
        async def handle_console(msg):
            if msg.type in ['error', 'warning']:
                self.js_errors.append({
                    'type': msg.type,
                    'text': msg.text,
                    'location': msg.location
                })
                self.stdout.write(f"🚨 JS {msg.type.upper()}: {msg.text}")
        
        # Event listeners aktivieren
        page.on('request', handle_request)
        page.on('response', handle_response) 
        page.on('console', handle_console)
        
        # JavaScript execution test
        js_enabled = await page.evaluate("typeof window !== 'undefined' && typeof document !== 'undefined'")
        self.stdout.write(f"🔧 JavaScript enabled: {js_enabled}")
    
    async def debug_page_state(self, page):
        """Detailliertes Debugging der Seite"""
        try:
            self.stdout.write("\n🔍 DEBUGGING PAGE STATE...")
            
            # 1. JavaScript Console Errors
            if self.js_errors:
                self.stdout.write(f"❌ Found {len(self.js_errors)} JavaScript errors:")
                for error in self.js_errors[-3:]:  # Letzte 3
                    self.stdout.write(f"   - {error['type']}: {error['text']}")
            
            # 2. Network Requests Analysis
            api_requests = [r for r in self.requests[-20:] if 'api' in r['url'] or 'ajax' in r['url'] or '.json' in r['url']]
            self.stdout.write(f"🌐 API Requests made: {len(api_requests)}")
            for req in api_requests[-5:]:  # Letzte 5
                self.stdout.write(f"   - {req['method']} {req['url']}")
            
            # 3. Annotations Box Status
            annotations_info = await page.evaluate("""
                () => {
                    const annotationsBox = document.querySelector('[class*="annotation"], .sidebar, .panel');
                    if (annotationsBox) {
                        return {
                            text: annotationsBox.textContent.trim(),
                            html: annotationsBox.innerHTML.substring(0, 200),
                            classList: Array.from(annotationsBox.classList)
                        };
                    }
                    return null;
                }
            """)
            
            if annotations_info:
                self.stdout.write(f"📋 Annotations box content: {annotations_info['text'][:100]}")
            else:
                self.stdout.write("📋 No annotations box found")
            
            # 4. AJAX/Fetch Status Check
            ajax_status = await page.evaluate("""
                () => {
                    // Check if jQuery is loaded and working
                    const hasJQuery = typeof $ !== 'undefined';
                    const hasFetch = typeof fetch !== 'undefined';
                    
                    // Check for common loading indicators
                    const loadingElements = document.querySelectorAll('[class*="loading"], [class*="spinner"], .fa-spinner');
                    
                    return {
                        hasJQuery: hasJQuery,
                        hasFetch: hasFetch,
                        loadingElements: loadingElements.length,
                        currentUrl: window.location.href,
                        cookiesCount: document.cookie.split(';').length
                    };
                }
            """)
            
            self.stdout.write(f"⚙️  AJAX Status: jQuery={ajax_status['hasJQuery']}, Fetch={ajax_status['hasFetch']}")
            self.stdout.write(f"⌛ Loading elements: {ajax_status['loadingElements']}")
            self.stdout.write(f"🍪 Cookies: {ajax_status['cookiesCount']}")
            
        except Exception as e:
            self.stdout.write(f"⚠️  Debug failed: {e}")