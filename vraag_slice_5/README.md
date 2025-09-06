# FastAPI Users Authorization Problem - Slice 5

## 📋 OVERZICHT
Deze map bevat alle relevante bestanden en informatie voor het oplossen van een FastAPI Users autorisatie probleem.

## 🚨 PROBLEEM
FastAPI Users dependency injection werkt niet correct. JWT token validatie werkt wel, maar custom dependency functions (`get_current_active_user`, `get_current_system_owner`) geven 401 Unauthorized errors.

## 📁 BESTANDEN

### Probleemstelling
- `PROBLEEMSTELLING.md` - Uitgebreide beschrijving van het probleem
- `README.md` - Deze file

### Relevante Code Bestanden
- `auth.py` - FastAPI Users configuratie
- `dependencies.py` - Custom dependency functions
- `database.py` - Database session configuratie
- `reports.py` - Reports endpoint (failing)
- `tenants.py` - Tenants endpoint (failing)
- `user.py` - User model
- `config.py` - Applicatie configuratie

### Test Scripts
- `test_problem.py` - Script om het probleem te demonstreren

## 🧪 TESTEN
Om het probleem te testen:

```bash
python test_problem.py
```

## 🔍 SYMPTOMEN
- ✅ `/users/me` → 200 OK (FastAPI Users basic functionality)
- ❌ `/reports` → 401 Unauthorized (custom dependency fails)
- ❌ `/tenants` → 401 Unauthorized (custom dependency fails)
- ✅ `/healthz` → 200 OK (no authentication)

## 🎯 VRAAG VOOR CHATGPT/CLAUDE
Hoe kan ik de FastAPI Users dependency injection repareren zodat custom dependency functions correct werken met async database sessions?

## 🔧 GEPROBEERDE OPLOSSINGEN
1. Database session fix (AsyncSession vs Session)
2. FastAPI Users configuratie aanpassing
3. Dependency chain fix

## 📊 TECHNISCHE STACK
- FastAPI
- FastAPI Users
- SQLAlchemy (AsyncSession)
- PostgreSQL
- JWT tokens
- Multi-tenant architectuur

## 🚀 OPLOSSING GEVRAAGD
Een werkende configuratie waarbij:
1. JWT token validatie blijft werken
2. Custom dependency functions correct werken
3. Async database sessions correct worden gebruikt
4. Multi-tenant autorisatie blijft functioneren
