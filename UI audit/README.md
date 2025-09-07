# UI Audit - API/UI Mismatch Analysis

## Probleemstelling

De UI heeft meerdere functionaliteiten die niet correct werken door mismatches tussen:
1. **API Response Structure** - Wat de backend API retourneert
2. **UI Data Handling** - Hoe de frontend de data verwerkt
3. **Field Name Mismatches** - Verschillende veldnamen tussen API en UI

## Bekende Problemen

### 1. Reports Loading (OPGELOST)
- **Probleem**: UI verwachtte direct array, API retourneerde `{items: [...], page: 1, ...}`
- **Oplossing**: `loadReports()` functies aangepast om `data.items` te gebruiken

### 2. User Management (NIET WERKEND)
- **Probleem**: Gebruikers aanpassen en opslaan werkt niet
- **Mogelijke oorzaken**:
  - API endpoint mismatch
  - Request body structure mismatch
  - Response handling mismatch
  - Field name mismatches

### 3. Tenant Management (ONBEKEND)
- **Status**: Moet gecontroleerd worden
- **Mogelijke problemen**: Zelfde als user management

## Bestanden voor Analyse

### Frontend (UI)
- `tenant-admin.html` - Tenant Admin interface
- `system-owner.html` - System Owner interface  
- `user.html` - Regular User interface

### Backend (API)
- `users.py` - User management API endpoints
- `tenants.py` - Tenant management API endpoints
- `reports.py` - Report management API endpoints
- `auth.py` - Authentication API endpoints

### Data Models & Schemas
- `user.py` - User model en schemas
- `tenant.py` - Tenant model en schemas
- `report.py` - Report model en schemas

## Audit Doelstellingen

1. **API Endpoint Mapping**: Controleer of alle UI API calls naar juiste endpoints gaan
2. **Request Body Structure**: Verificeer of UI requests de juiste data structuur hebben
3. **Response Handling**: Controleer of UI correct omgaat met API responses
4. **Field Name Consistency**: Identificeer alle field name mismatches
5. **Error Handling**: Controleer of errors correct worden afgehandeld

## Specifieke Vragen voor Claude

1. **User Management**: Waarom werkt het aanpassen en opslaan van gebruikers niet?
2. **API Response Structure**: Zijn er meer endpoints die `{items: [...]}` structuur gebruiken?
3. **Field Mappings**: Welke veldnamen zijn inconsistent tussen API en UI?
4. **Request Format**: Zijn alle POST/PUT requests correct geformatteerd?
5. **Error Handling**: Worden API errors correct getoond aan de gebruiker?

## Test Scenario's

1. **User Create**: Maak nieuwe user aan via UI
2. **User Edit**: Bewerk bestaande user via UI
3. **User Delete**: Verwijder user via UI
4. **Tenant Create**: Maak nieuwe tenant aan via UI
5. **Tenant Edit**: Bewerk bestaande tenant via UI
6. **Report Upload**: Upload rapport via UI
7. **Report List**: Bekijk rapporten lijst
8. **Report Detail**: Bekijk rapport details

## Verwachte Output

Een gedetailleerde analyse met:
- Lijst van alle gevonden mismatches
- Concrete fixes voor elk probleem
- Code voorbeelden van correcte implementatie
- Prioriteit van fixes (kritiek/hoog/medium/laag)
