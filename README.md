# V2 Asbest Tool API

Een moderne FastAPI-gebaseerde applicatie voor asbest management met multi-tenant architectuur en role-based access control.

## 🚀 **Features**

- **FastAPI** - Moderne, snelle web framework
- **FastAPI Users** - JWT authenticatie en user management
- **PostgreSQL** - Async database met SQLAlchemy ORM
- **Alembic** - Database migraties
- **Multi-tenant architectuur** - Isolatie tussen verschillende bedrijven
- **Role-based access control** - SYSTEM_OWNER, ADMIN, USER rollen
- **Object Storage** - S3/MinIO compatibele bestandsopslag
- **File Upload** - PDF/DOCX upload met validatie en RBAC
- **Audit Logging** - Volledige audit trail voor alle acties
- **Docker Compose** - Eenvoudige deployment met MinIO
- **Comprehensive testing** - pytest met httpx

## 🏗️ **Architectuur**

### **Multi-tenant Model**
- **Tenants**: Bedrijven/organisaties met eigen data isolatie
- **Users**: Gebruikers gekoppeld aan tenants (behalve system owner)
- **Roles**: Hiërarchische toegangscontrole

### **Database Schema**
```sql
-- Tenants tabel
tenants (
  id UUID PRIMARY KEY,
  name VARCHAR NOT NULL,
  kvk VARCHAR NOT NULL,
  contact_email VARCHAR NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
)

-- Users tabel
users (
  id UUID PRIMARY KEY,
  tenant_id UUID REFERENCES tenants(id),
  email VARCHAR(320) UNIQUE NOT NULL,
  first_name VARCHAR NOT NULL,
  last_name VARCHAR NOT NULL,
  role ENUM('USER', 'ADMIN', 'SYSTEM_OWNER') NOT NULL,
  hashed_password VARCHAR(1024) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  is_superuser BOOLEAN DEFAULT FALSE,
  is_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
)
```

## 🛠️ **Installatie**

### **Prerequisites**
- Python 3.11+
- Docker & Docker Compose
- Git

### **Lokale Setup**

1. **Clone de repository**
```bash
git clone https://github.com/benkogerrie/v2_asbest-tool.git
cd v2_asbest-tool
```

2. **Installeer dependencies**
```bash
pip install -r requirements.txt
# Of met Poetry:
poetry install
```

3. **Start de database**
```bash
docker-compose up -d db
```

4. **Run database migraties**
```bash
python -m alembic upgrade head
```

5. **Seed de database**
```bash
python -m scripts.seed
```

6. **Start de applicatie**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Docker Setup**

```bash
# Start alle services (API, DB, MinIO, Adminer)
docker-compose up -d

# Bekijk logs
docker-compose logs -f api
```

### **MinIO Console**
- **URL**: http://localhost:9001
- **Username**: `minioadmin`
- **Password**: `minioadmin`
- **Bucket**: `asbesttool-dev` (wordt automatisch aangemaakt)

## 📚 **API Documentatie**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 **Authenticatie**

### **Test Accounts**
Na het uitvoeren van de seed script zijn de volgende accounts beschikbaar:

- **System Owner**
  - Email: `system@asbest-tool.nl`
  - Wachtwoord: `SystemOwner123!`
  - Rechten: Volledige toegang tot alle tenants en users

- **Tenant Admin**
  - Email: `admin@bedrijfy.nl`
  - Wachtwoord: `Admin123!`
  - Rechten: Alleen toegang tot eigen tenant

### **JWT Token Gebruik**
```bash
# Login
curl -X POST "http://localhost:8000/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=system@asbest-tool.nl&password=SystemOwner123!"

# Gebruik token
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### **File Upload Voorbeelden**
```bash
# Upload als tenant admin (eigen tenant)
curl -X POST "http://localhost:8000/reports/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@report.pdf"

# Upload als system owner (specificeer tenant_id)
curl -X POST "http://localhost:8000/reports/?tenant_id=TENANT_UUID" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@report.docx"

# List reports
curl -X GET "http://localhost:8000/reports/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🧪 **Testing**

```bash
# Run alle tests
python -m pytest

# Run tests met coverage
python -m pytest --cov=app

# Run specifieke test
python -m pytest tests/test_auth.py::TestAuth::test_login_works -v
```

## 📁 **Project Structuur**

```
v2_asbest-tool/
├── alembic/                 # Database migraties
├── app/
│   ├── api/                # API endpoints
│   ├── auth/               # Authenticatie configuratie
│   ├── models/             # Database modellen
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic services
│   ├── config.py           # Configuratie
│   ├── database.py         # Database setup
│   ├── exceptions.py       # Custom exceptions
│   └── main.py             # FastAPI applicatie
├── scripts/
│   └── seed.py             # Database seeding
├── tests/                  # Unit tests
├── docker-compose.yml      # Docker services
├── Dockerfile              # API container
├── pyproject.toml          # Poetry configuratie
└── README.md               # Deze file
```

## 🔧 **Configuratie**

### **Environment Variables**
Maak een `.env` bestand aan:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/asbest_tool

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME=Asbest Tool API
DEBUG=false
```

## 🚀 **Deployment**

### **Production**
```bash
# Build en start
docker-compose -f docker-compose.prod.yml up -d

# Migraties
docker-compose exec api python -m alembic upgrade head

# Seed data
docker-compose exec api python -m scripts.seed
```

## 📊 **Health Check**

```bash
curl http://localhost:8000/healthz
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🤝 **Bijdragen**

1. Fork de repository
2. Maak een feature branch (`git checkout -b feature/amazing-feature`)
3. Commit je wijzigingen (`git commit -m 'Add amazing feature'`)
4. Push naar de branch (`git push origin feature/amazing-feature`)
5. Open een Pull Request

## 📄 **Licentie**

Dit project is gelicenseerd onder de MIT License - zie het [LICENSE](LICENSE) bestand voor details.

## 👥 **Auteurs**

- **Ben Kogerrie** - *Initial work* - [benkogerrie](https://github.com/benkogerrie)

## 🙏 **Acknowledgments**

- FastAPI voor het geweldige framework
- FastAPI Users voor de authenticatie functionaliteit
- SQLAlchemy voor de ORM
- Alembic voor database migraties
