# Technical Debt

## 🔴 **CRITICAL: FastAPI Users Custom Dependency 401 Unauthorized Issue**

**Status:** Open  
**Priority:** High  
**Created:** 2025-09-06  
**Last Updated:** 2025-09-06  

### **Problem Description**

FastAPI Users custom dependency functions geven 401 Unauthorized errors, ondanks correcte configuratie en UUID fixes.

**Symptoms:**
- ✅ JWT login werkt perfect (`/auth/jwt/login` → 200 OK)
- ✅ `/users/me` endpoint werkt perfect (FastAPI Users default)
- ❌ Custom endpoints met custom dependencies geven 401 Unauthorized
- ❌ Zelfs system owner krijgt 401 op `/tenants` endpoint

**Affected Endpoints:**
- `/reports` → 401 Unauthorized (custom dependency: `get_current_active_user`)
- `/tenants` → 401 Unauthorized (custom dependency: `get_current_system_owner`)
- Alle andere custom endpoints met custom dependencies

### **Root Cause Analysis**

**ChatGPT's Analysis:**
Het probleem is dat `current_user()` in custom endpoints buiten de juiste FastAPI Users context draait. FastAPI Users heeft zijn eigen authenticator/transport die correct verankerd moet zijn in de dependency boom.

**Technical Details:**
- FastAPI Users versie: 12.1.3
- FastAPI versie: 0.104.1
- User model: `SQLAlchemyBaseUserTableUUID` (UUID ID)
- Database: PostgreSQL met AsyncSession

### **Attempted Solutions**

#### ✅ **Solution 1: UUID Fix (Implemented)**
- `UserManager[User, uuid.UUID]` in plaats van `str`
- `FastAPIUsers[User, uuid.UUID]` in plaats van `str`
- `parse_id()` converteert string naar `uuid.UUID`
- `active=True` parameter toegevoegd

**Result:** UUID fix was correct, maar probleem blijft bestaan.

#### ❌ **Solution 2: Security/Authenticator (Failed)**
- `Security(authenticator.current_user(...))` implementatie
- `Authenticator` import en configuratie
- **Result:** Werkte niet in deze FastAPI/FastAPI Users versies

#### ❌ **Solution 3: JWT Decode Workaround (Failed)**
- Handmatige JWT token decodering
- User ID extractie uit JWT payload
- Database user loading
- **Result:** Gaf "Missing or invalid authorization header" errors

#### ❌ **Solution 4: Claude's Direct Reference (Failed)**
- Directe referentie naar `fastapi_users.current_user(active=True)`
- Module-level variabele: `current_user = fastapi_users.current_user(active=True)`
- Alle dependencies gebruiken `Depends(current_user)`
- **Result:** Nog steeds 401 Unauthorized errors

### **Current State**

**Working:**
- JWT authentication en token validatie
- FastAPI Users default endpoints (`/users/me`)
- Database connectie en user management
- UUID type consistency

**Not Working:**
- Custom dependency functions (`get_current_active_user`, `get_current_system_owner`)
- Custom API endpoints (`/reports`, `/tenants`)
- Role-based authorization in custom endpoints

### **Impact**

**High Impact:**
- Slice 5 backend functionaliteit is geïmplementeerd maar niet toegankelijk
- Reports API endpoints werken niet
- Tenants API endpoints werken niet
- Multi-tenant authorization werkt niet

**Business Impact:**
- Gebruikers kunnen geen reports uploaden/bekijken
- Tenant management werkt niet
- System owner functionaliteit werkt niet

### **Proposed Solutions**

#### **Option 1: FastAPI Users Version Upgrade**
- Upgrade naar nieuwere FastAPI Users versie
- Mogelijk compatibiliteitsproblemen met huidige setup
- **Risk:** Breaking changes

#### **Option 2: Custom Authentication Implementation**
- Implementeer eigen JWT authentication systeem
- Vervang FastAPI Users custom dependencies
- **Risk:** Veel werk, verlies van FastAPI Users functionaliteit

#### **Option 3: FastAPI Users Configuration Fix**
- Onderzoek diepere FastAPI Users configuratie issues
- Mogelijk missing schemas of incorrect router registration
- **Risk:** Onbekend, mogelijk complex

#### **Option 4: Alternative Library**
- Overweeg alternatieve authentication library
- **Risk:** Major refactoring

### **Recommendations**

1. **Short Term:** Onderzoek FastAPI Users versie upgrade mogelijkheden
2. **Medium Term:** Implementeer custom authentication als fallback
3. **Long Term:** Evalueer alternatieve authentication libraries

### **AI Analysis Results**

**ChatGPT's Analysis:** Type mismatch tussen User model (UUID) en FastAPI Users configuratie (str) - UUID fix geïmplementeerd maar probleem blijft bestaan.

**Claude's Analysis:** Het probleem was dat we FastAPI Users dependencies probeerden te "wrappen" in plaats van ze direct te gebruiken - directe referentie oplossing geïmplementeerd maar probleem blijft bestaan.

**Conclusion:** Alle AI-gesuggereerde oplossingen hebben gefaald. Het probleem is dieper dan verwacht en vereist mogelijk een fundamenteel andere aanpak.

### **Files Affected**

- `app/auth/auth.py` - FastAPI Users configuratie
- `app/auth/dependencies.py` - Custom dependency functions
- `app/api/reports.py` - Reports endpoints
- `app/api/tenants.py` - Tenants endpoints
- `app/api/analyses.py` - Analyses endpoints
- `app/api/findings.py` - Findings endpoints

### **Testing**

**Test Scripts Created:**
- `test_authenticator_fix.py` - Test Security/Authenticator oplossing
- `test_jwt_workaround_fix.py` - Test JWT decode workaround
- `test_deployment_status.py` - Test deployment status
- `test_import_issue.py` - Test import issues

**Test Results:**
- Alle test scripts bevestigen het probleem
- Geen van de geprobeerde oplossingen werkt
- Probleem is reproduceerbaar en consistent

### **Next Steps**

1. **Research:** Onderzoek FastAPI Users versie upgrade
2. **Investigate:** Diepere configuratie issues
3. **Implement:** Fallback authentication systeem
4. **Test:** Uitgebreide testing van nieuwe oplossing

---

**Note:** Dit is een kritieke technical debt die de core functionaliteit van de applicatie blokkeert. Prioriteit moet hoog zijn voor oplossing.
