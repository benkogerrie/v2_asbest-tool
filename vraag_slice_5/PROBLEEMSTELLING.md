# FastAPI Users Authorization Problem - Slice 5 (UPDATED - NARROWED SCOPE)

## 🚨 PROBLEEM
FastAPI Users custom dependency functions geven 401 Unauthorized errors, ondanks correcte configuratie en UUID fixes. Het probleem is dat `current_user()` in custom endpoints buiten de juiste FastAPI Users context draait.

## 📋 SYMPTOMEN (BIG UPDATE - PROBLEEM IS VEEL KLEINER!)
- **JWT token validatie werkt:** `/users/me` endpoint retourneert 200 OK
- **Reports endpoints werken:** `POST /reports/` en `GET /reports/` retourneren 200 OK
- **Tenants endpoints falen:** `GET /tenants/` retourneert 401 Unauthorized
- **Users bestaan in database:** Login werkt correct, users zijn actief en geverifieerd
- **Database connectie werkt:** Health endpoints en basic functionaliteit werken
- **System owner faalt alleen op tenants:** System owner krijgt 401 op `/tenants` endpoint

## 🔍 TECHNISCHE DETAILS

### Werkende Endpoints:
- `GET /users/me` → 200 OK (FastAPI Users basic functionality)
- `GET /healthz` → 200 OK
- `POST /auth/jwt/login` → 200 OK
- `POST /reports/` → 201 OK (gebruikt `get_current_admin_or_system_owner`)
- `GET /reports/` → 200 OK (gebruikt `get_current_active_user`)

### Failing Endpoints:
- `GET /tenants/` → 401 Unauthorized (gebruikt `get_current_system_owner`)
- `POST /tenants/` → 401 Unauthorized (gebruikt `get_current_system_owner`)
- `GET /tenants/{id}` → 401 Unauthorized (gebruikt `get_current_system_owner`)
- `PUT /tenants/{id}` → 401 Unauthorized (gebruikt `get_current_system_owner`)
- `DELETE /tenants/{id}` → 401 Unauthorized (gebruikt `get_current_system_owner`)
- `GET /tenants/my` → 401 Unauthorized (gebruikt `get_current_tenant_user`)

### Test User Details:
```json
{
  "id": "7a5bb229-1960-42d6-bda5-0fb5d8958e4f",
  "email": "admin@bedrijfy.nl",
  "role": "ADMIN",
  "tenant_id": "4a548704-0dfa-4649-bce3-c39a014dd577",
  "is_active": true,
  "is_verified": true
}
```

## 🏗️ ARCHITECTUUR
- **FastAPI** met **FastAPI Users** voor authenticatie
- **SQLAlchemy** met **AsyncSession** voor database
- **PostgreSQL** database
- **JWT** tokens voor authenticatie
- **Multi-tenant** architectuur

## 🔧 GEPROBEERDE OPLOSSINGEN

### ✅ **Oplossing 1: UUID Fix (Geïmplementeerd)**
- `UserManager[User, uuid.UUID]` in plaats van `str`
- `FastAPIUsers[User, uuid.UUID]` in plaats van `str`
- `parse_id()` converteert string naar `uuid.UUID`
- `active=True` parameter toegevoegd
- **Resultaat:** UUID fix was correct, maar probleem blijft bestaan

### ❌ **Oplossing 2: Security/Authenticator (Gefaald)**
- `Security(authenticator.current_user(...))` implementatie
- `Authenticator` import en configuratie
- **Resultaat:** Werkte niet in FastAPI 0.104.1 / FastAPI Users 12.1.3

### ❌ **Oplossing 3: JWT Decode Workaround (Gefaald)**
- Handmatige JWT token decodering
- User ID extractie uit JWT payload
- Database user loading
- **Resultaat:** Gaf "Missing or invalid authorization header" errors

### ❌ **Oplossing 4: Database Session Fix (Gefaald)**
- AsyncSession vs Session inconsistentie opgelost
- **Resultaat:** Probleem bleef bestaan

### ❌ **Oplossing 5: Dependency Chain Fix (Gefaald)**
- `get_current_active_user` direct FastAPI Users dependency laten gebruiken
- **Resultaat:** Probleem bleef bestaan

## 📁 RELEVANTE BESTANDEN
- `app/auth/auth.py` - FastAPI Users configuratie
- `app/auth/dependencies.py` - Custom dependency functions
- `app/database.py` - Database session configuratie
- `app/api/reports.py` - Reports endpoint (failing)
- `app/api/tenants.py` - Tenants endpoint (failing)
- `app/models/user.py` - User model
- `app/config.py` - Applicatie configuratie

## 🎯 VRAAG (UPDATED - NARROWED SCOPE)
Hoe kan ik de FastAPI Users custom dependency probleem oplossen voor specifiek de `/tenants` endpoints? Het probleem is dat `get_current_system_owner` en `get_current_tenant_user` dependencies 401 Unauthorized geven, terwijl `get_current_active_user` en `get_current_admin_or_system_owner` wel werken. Alle geprobeerde oplossingen hebben gefaald.

## 🔍 ROOT CAUSE (ChatGPT's Analyse)
Het probleem is dat `current_user()` in custom endpoints buiten de juiste FastAPI Users context draait. FastAPI Users heeft zijn eigen authenticator/transport die correct verankerd moet zijn in de dependency boom. In v12.1.x is current_user() een security dependency die leunt op de interne Authenticator + gekozen AuthenticationBackend.

## 📊 TEST RESULTATEN (UPDATED)
```
✅ /users/me: 200 - FastAPI Users basic functionality works
✅ /reports: 200 - get_current_active_user works
✅ POST /reports: 201 - get_current_admin_or_system_owner works
❌ /tenants: 401 - get_current_system_owner fails
❌ /tenants/my: 401 - get_current_tenant_user fails
✅ /healthz: 200 - No authentication required
```

## 🚀 OPLOSSING GEVRAAGD (UPDATED)
Een werkende configuratie waarbij:
1. JWT token validatie blijft werken
2. `get_current_system_owner` en `get_current_tenant_user` dependencies correct werken
3. Async database sessions correct worden gebruikt
4. Multi-tenant autorisatie blijft functioneren
5. Bestaande werkende dependencies (`get_current_active_user`, `get_current_admin_or_system_owner`) blijven werken

## 📋 VERSIE INFORMATIE
- **FastAPI:** 0.104.1
- **FastAPI Users:** 12.1.3
- **SQLAlchemy:** 2.0.23
- **Python:** 3.11+

## 🔍 TECHNICAL DEBT
Dit probleem is gedocumenteerd als CRITICAL technical debt in `TECHNICAL_DEBT.md` omdat het de tenants management functionaliteit blokkeert. De core functionaliteit (reports) werkt wel.

## 🎯 SPECIFIEKE VRAAG VOOR CHATGPT/CLAUDE
Waarom werken `get_current_active_user` en `get_current_admin_or_system_owner` wel, maar `get_current_system_owner` en `get_current_tenant_user` niet? Alle dependencies gebruiken dezelfde `fastapi_users.current_user(active=True)` call. Wat is het verschil in implementatie dat dit veroorzaakt?
