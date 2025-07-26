# MymiDeck - Django Project

## Projektkontext

MymiDeck ist ein Django-basiertes System zur Verarbeitung von Mikroskopie-Lerninhalten von der **MyMi-Lernplattform** der Universität Ulm (https://mymi.uni-ulm.de/).

### Projektziele:
1. **Datenimport**: Import der MyMi-Datenbankstruktur aus JSON-Export
2. **Crawling**: Automatisiertes Crawlen der MyMi-Website mit Playwright
3. **Anki-Export**: Konvertierung der Lerninhalte in Anki-Karteikarten (CSV-Format)

### Datenquelle:
Die importierten Daten stammen aus einem Export der MyMi-Plattform, einer interaktiven Lernumgebung für mikroskopisch-anatomische Inhalte mit virtuellen Mikroskopie-Präparaten.

---

## Technische Umsetzung

### 🐳 Docker Setup

Das Projekt verwendet Docker Compose mit zwei Services:

- **PostgreSQL Database** (`db`): Port 5432
- **Django Web Application** (`web`): Port 8000

**Start:**
```bash
docker-compose up -d
```

### 📊 Datenmodell

#### Implementierte Models (11 Entitäten):

**Basis-Entitäten:**
- `OrganSystem` - Anatomische Organsysteme (18 Items)
- `Species` - Tierarten/Spezies (24 Items) 
- `Staining` - Histologische Färbungen (89 Items)
- `Subject` - Fachbereiche (3 Items)

**Institutionen & Server:**
- `Institution` - Bildungseinrichtungen (9 Items)
- `TileServer` - Bildserver für Mikroskopie-Tiles (6 Items)

**Mikroskopie-Inhalte:**
- `Image` - Mikroskopie-Bilder (544 Items)
- `Exploration` - Interaktive Lernaktivitäten (544 Items)
- `Diagnosis` - Diagnoseaufgaben (84 Items)
- `StructureSearch` - Struktursuchaufgaben (220 Items)

**Lokalisierung:**
- `Locale` - Interface-Texte und Übersetzungen (20 Items)

#### Model-Architektur:
```
mymi_data/models/
├── __init__.py          # Zentrale Model-Imports
├── organ_system.py      # OrganSystem Model
├── species.py          # Species Model
├── staining.py         # Staining Model
├── subject.py          # Subject Model
├── institution.py      # Institution Model
├── tile_server.py      # TileServer Model
├── image.py            # Image Model (Hauptentität)
├── exploration.py      # Exploration Model
├── diagnosis.py        # Diagnosis Model
├── structure_search.py # StructureSearch Model
└── locale.py           # Locale Model
```

**Beziehungen:**
- `Image` ↔ `OrganSystem` (ManyToMany)
- `Image` ↔ `Species`, `Staining`, `TileServer` (ForeignKey)
- `Exploration`/`Diagnosis`/`StructureSearch` → `Image`, `Institution` (ForeignKey)
- `Exploration`/`StructureSearch` ↔ `Subject` (ManyToMany)

### 🗃️ Datenimport

#### JSON-Datenstruktur:
Der Import erfolgte aus `data/import_data.json` (634KB, 1.561 Datensätze) mit folgender Struktur:

```json
{
  "organsystems": [...],
  "species": [...],
  "stainings": [...],
  "subjects": [...],
  "institutions": [...],
  "tileservers": [...],
  "images": [...],
  "explorations": [...],
  "diagnoses": [...],
  "structureSearches": [...],
  "locales": {...}
}
```

#### Import-Command:
```bash
python manage.py import_mymi_data
```

**Features:**
- Atomare Transaktionen (Rollback bei Fehlern)
- Referentielle Integrität (ForeignKey-Validierung)
- Update-or-Create Pattern (Wiederverwendbar)
- Fehlerbehandlung mit Warnings
- ManyToMany-Beziehungen Support

### 🔒 Admin Interface

Django Admin mit **Read-Only Schutz** für alle importierten Daten:

- **Alle Felder**: `readonly_fields` aktiviert
- **Keine Bearbeitung**: `has_add_permission()` und `has_delete_permission()` → `False`
- **ManyToMany-Felder**: Via `get_readonly_fields()` geschützt
- **Such- und Filterfunktionen**: Vollständig verfügbar

**Zugang:** `http://localhost:8000/admin/`

### 🗄️ Datenbank

**PostgreSQL-Konfiguration:**
- Host: `db` (Docker) / `localhost` (lokal)
- Port: 5432
- Database: `mymideck`
- User: `postgres`
- Password: `postgres`

**Migrationen:**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Entwicklungsstand

### ✅ Implementiert:
1. **Docker-Umgebung** mit PostgreSQL und Django
2. **Vollständiges Datenmodell** für MyMi-Struktur
3. **JSON-Import-System** mit 1.561 Datensätzen
4. **Read-Only Admin Interface** für Datenverwaltung
5. **Modulare Model-Architektur** (jedes Model in eigener Datei)

### 🚧 Geplant:
1. **Playwright Web Crawler** für https://mymi.uni-ulm.de/
2. **Anki CSV Export-Funktionalität**
3. **Bildverarbeitung** für Mikroskopie-Tiles
4. **Content-Extraktion** aus virtuellen Mikroskopen

---

## Technische Details

### Dependencies:
- Django 4.2.6
- PostgreSQL
- psycopg2
- Docker & Docker Compose
- Django Q (für Background Tasks)

### Projektstruktur:
```
MymiDeck/
├── data/                    # JSON-Importdaten
├── mymideck/               # Django Hauptprojekt
├── mymi_data/              # Django App für MyMi-Daten
│   ├── models/             # Model-Definitionen
│   ├── admin.py            # Admin-Konfiguration
│   ├── management/commands/ # Import-Commands
│   └── migrations/         # Datenbank-Migrationen
├── docker-compose.yml      # Docker-Konfiguration
├── Dockerfile              # Django Container
└── requirements.txt        # Python Dependencies
```

### Background Tasks:

Das Projekt nutzt **Django Q** für asynchrone Hintergrundprozesse:

- **Web Crawling**: Playwright-basiertes Crawling der MyMi-Website
- **Datenverarbeitung**: Bildverarbeitung und Content-Extraktion
- **Export-Generierung**: Anki CSV-Export für große Datenmengen
- **Wartungsaufgaben**: Datenbank-Optimierung und Cleanup

### Nächste Schritte:
1. Django Q Setup und Konfiguration
2. Playwright-Integration für Web Crawling
3. Anki-Export-Module implementieren
4. Bildverarbeitungs-Pipeline für Mikroskopie-Daten
5. Content-Extraction aus interaktiven Lernmodulen

---

## Verwendung

### Setup:
```bash
# Repository klonen
git clone <repository>
cd MymiDeck

# Docker-Container starten
docker-compose up -d

# Migrationen anwenden
python manage.py migrate

# Daten importieren
python manage.py import_mymi_data

# Admin-User erstellen
python manage.py createsuperuser
```

### Admin-Zugang:
- URL: http://localhost:8000/admin/
- Alle MyMi-Daten sind read-only verfügbar
- Such- und Filterfunktionen für effiziente Datenexploration

Das System ist bereit für die nächste Entwicklungsphase: Integration des Playwright-Crawlers für die automatisierte Content-Extraktion von der MyMi-Plattform.