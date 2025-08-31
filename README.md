# Asbest Tool API

Een FastAPI-gebaseerde API voor het uploaden en analyseren van asbest rapporten.

## Features

- **Slice 1**: Basis authenticatie en autorisatie
- **Slice 2**: File upload functionaliteit
- **Slice 3**: Rapportenlijst en rapportdetail API
- **Slice 4**: Verwerkingspipeline (Queue + Worker, dummy AI + PDF generatie) ✅

## API Endpoints

### Authenticatie

Alle endpoints vereisen JWT authenticatie via Bearer token.

### File Upload (Slice 2)

#### POST /reports/

Upload een rapport bestand.

**Voorbeelden:**

```bash
# Upload als regular user (eigen tenant)
curl -X POST "http://localhost:8000/reports/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@rapport.pdf"

# Upload als SYSTEM_OWNER naar specifieke tenant
curl -X POST "http://localhost:8000/reports/?tenant_id=550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@rapport.pdf"
```

**Response:**
```json
{
  "id": "794301cb-ed5d-4bd9-bdb2-8a5e93bfb6c8",
  "filename": "rapport.pdf",
  "status": "PROCESSING",
  "finding_count": 0,
  "score": null,
  "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
  "uploaded_by": "550e8400-e29b-41d4-a716-446655440000",
  "uploaded_at": "2025-01-27T10:30:00Z",
  "source_object_key": "tenants/550e8400-e29b-41d4-a716-446655440001/reports/794301cb-ed5d-4bd9-bdb2-8a5e93bfb6c8/source/rapport.pdf",
  "conclusion_object_key": null
}
```

### Rapportenlijst (Slice 3)

#### GET /reports/

Haal een lijst van rapporten op met filtering, sortering en paginatie.

**Query Parameters:**
- `page` (int, default=1): Pagina nummer
- `page_size` (int, default=20, max=100): Items per pagina
- `status` (optional): Filter op status (PROCESSING, DONE, FAILED, DELETED_SOFT)
- `tenant_id` (optional, SYSTEM_OWNER only): Filter op tenant ID
- `q` (optional): Zoeken in bestandsnaam (case-insensitive)
- `sort` (optional): Sortering (uploaded_at_desc, uploaded_at_asc, filename_asc, filename_desc)

**Voorbeelden:**

```bash
# Basis lijst voor USER/ADMIN (eigen tenant)
curl -X GET "http://localhost:8000/reports/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Met paginatie
curl -X GET "http://localhost:8000/reports/?page=2&page_size=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Met status filter
curl -X GET "http://localhost:8000/reports/?status=DONE" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Met zoeken
curl -X GET "http://localhost:8000/reports/?q=project" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Met sortering
curl -X GET "http://localhost:8000/reports/?sort=filename_asc" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# SYSTEM_OWNER: alle rapporten
curl -X GET "http://localhost:8000/reports/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# SYSTEM_OWNER: filter op tenant
curl -X GET "http://localhost:8000/reports/?tenant_id=550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "items": [
    {
      "id": "794301cb-ed5d-4bd9-bdb2-8a5e93bfb6c8",
      "filename": "project-123_Kade-12-Amsterdam.pdf",
      "status": "DONE",
      "finding_count": 2,
      "score": 89,
      "uploaded_at": "2025-01-27T10:30:00Z",
      "tenant_name": "Bedrijf Y"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 42
}
```

### Rapport Detail (Slice 3)

#### GET /reports/{id}

Haal gedetailleerde informatie op over een specifiek rapport.

**Voorbeelden:**

```bash
# Basis detail opvragen
curl -X GET "http://localhost:8000/reports/794301cb-ed5d-4bd9-bdb2-8a5e93bfb6c8" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "id": "794301cb-ed5d-4bd9-bdb2-8a5e93bfb6c8",
  "filename": "project-123_Kade-12-Amsterdam.pdf",
  "summary": "Rapport is grotendeels compleet; aanvulling nodig voor maatregel 2A (dummy).",
  "findings": [
    {
      "code": "R001",
      "severity": "MAJOR",
      "title": "Projectadres onvolledig",
      "detail_text": "Postcode ontbreekt (dummy)"
    },
    {
      "code": "R012",
      "severity": "CRITICAL", 
      "title": "Maatregelen onduidelijk",
      "detail_text": "2A niet uitgewerkt (dummy)"
    }
  ],
  "uploaded_at": "2025-01-27T10:30:00Z",
  "uploaded_by_name": "S. Jansen",
  "tenant_name": "Bedrijf Y",
  "status": "DONE",
  "finding_count": 2,
  "score": 89
}
```

### Download Endpoints (Slice 4)

#### GET /reports/{id}/source

Download het originele bronbestand.

#### GET /reports/{id}/conclusion

Download de conclusie PDF (alleen beschikbaar na verwerking).

**Voorbeelden:**

```bash
# Download bronbestand
curl -X GET "http://localhost:8000/reports/794301cb-ed5d-4bd9-bdb2-8a5e93bfb6c8/source" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  --output rapport.pdf

# Download conclusie PDF
curl -X GET "http://localhost:8000/reports/794301cb-ed5d-4bd9-bdb2-8a5e93bfb6c8/conclusion" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  --output conclusie.pdf
```

## RBAC (Role-Based Access Control)

### USER/ADMIN
- Kan alleen rapporten van eigen tenant zien
- Kan geen soft-deleted rapporten zien
- Kan geen tenant_id filter gebruiken

### SYSTEM_OWNER
- Kan alle rapporten zien (inclusief soft-deleted)
- Kan optioneel filteren op tenant_id
- Ziet tenant_name in responses

## Status Codes

- `200`: Success
- `201`: Created (upload)
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden (RBAC violation)
- `404`: Not Found
- `413`: File Too Large
- `415`: Unsupported Media Type
- `422`: Validation Error
- `500`: Internal Server Error

## Setup

### Lokaal Development

1. Installeer dependencies:
```bash
pip install -r requirements.txt
```

2. Configureer environment variables:
```bash
cp env.sample .env
# Vul de benodigde waarden in
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start alle services met Docker Compose:
```bash
docker-compose up
```

Dit start:
- API server (port 8000)
- PostgreSQL database (port 5432)
- Redis (port 6379)
- MinIO storage (port 9000)
- Worker service voor verwerking

### Railway Deployment

Voor Railway deployment:

1. Voeg een aparte worker service toe met dezelfde environment variables als de API
2. Worker service command: `python -m worker.run`
3. Zorg dat Redis service beschikbaar is

### Worker Monitoring

De worker verwerkt automatisch geüploade rapporten:

- Status: PROCESSING → DONE/FAILED
- Genereert dummy AI analyse (score: 89, 2 bevindingen)
- Maakt conclusie PDF aan
- Audit logs: PROCESS_START, PROCESS_DONE, PROCESS_FAIL

## Testing

Run de tests:
```bash
pytest tests/ -v
```

## Volgende Slices

- **Slice 5**: Echte AI/RAG integratie
- **Slice 6**: UI integratie
