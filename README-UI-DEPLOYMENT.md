# 🚀 Asbest Tool UI Deployment naar Vercel

## 📋 Overzicht

Deze repository bevat 3 verschillende UI's voor de Asbest Tool:
- **User UI** (`user.html`) - Voor reguliere gebruikers
- **Tenant Admin UI** (`index.html`) - Voor tenant administrators  
- **System Owner UI** (`system-owner.html`) - Voor systeembeheerders

## 🎯 Deployment Stappenplan

### Stap 1: Vercel Project Aanmaken

1. Ga naar [vercel.com](https://vercel.com)
2. Log in met je GitHub account
3. Klik "New Project"
4. Importeer deze repository

### Stap 2: UI's Deployen

#### Optie A: Alle UI's in één project (Aanbevolen)

1. **Maak een nieuwe directory structuur:**
```bash
mkdir asbest-tool-ui
cd asbest-tool-ui
```

2. **Kopieer de UI bestanden:**
```bash
# User UI
cp user.html user/index.html

# Tenant Admin UI (hoofdinterface)
cp index.html index.html

# System Owner UI
cp system-owner.html system-owner/index.html
```

3. **Maak een vercel.json configuratie:**
```json
{
  "routes": [
    { "src": "/user", "dest": "/user/index.html" },
    { "src": "/system-owner", "dest": "/system-owner/index.html" },
    { "src": "/", "dest": "/index.html" }
  ]
}
```

#### Optie B: Aparte projecten per UI

1. **User UI Project:**
   - Upload `user.html` als `index.html`
   - Project naam: `asbest-tool-user`

2. **Tenant Admin UI Project:**
   - Upload `index.html` 
   - Project naam: `asbest-tool-admin`

3. **System Owner UI Project:**
   - Upload `system-owner.html` als `index.html`
   - Project naam: `asbest-tool-system-owner`

### Stap 3: API URL Configuratie

**BELANGRIJK:** Pas de API URL aan in alle UI bestanden:

```javascript
// In alle 3 UI bestanden, vervang deze regel:
const API_BASE_URL = 'https://asbest-tool-staging-production.up.railway.app';

// Met jouw echte Railway URL:
const API_BASE_URL = 'https://jouw-railway-project.up.railway.app';
```

### Stap 4: CORS Configuratie in Railway

Ga naar je Railway API project en voeg deze CORS origins toe:

```bash
# Voor Optie A (één project):
CORS_ORIGINS=https://jouw-vercel-project.vercel.app,http://localhost:5173

# Voor Optie B (drie projecten):
CORS_ORIGINS=https://asbest-tool-user.vercel.app,https://asbest-tool-admin.vercel.app,https://asbest-tool-system-owner.vercel.app,http://localhost:5173
```

## 🔗 URL Structuur

### Optie A (Één project):
- **User UI:** `https://jouw-project.vercel.app/user`
- **Tenant Admin UI:** `https://jouw-project.vercel.app/`
- **System Owner UI:** `https://jouw-project.vercel.app/system-owner`

### Optie B (Drie projecten):
- **User UI:** `https://asbest-tool-user.vercel.app`
- **Tenant Admin UI:** `https://asbest-tool-admin.vercel.app`
- **System Owner UI:** `https://asbest-tool-system-owner.vercel.app`

## ✅ Test Checklist

Na deployment, test het volgende:

### 1. API Health Check
- Open browser console op elke UI
- Controleer of je deze log ziet: `API Health: {status: "healthy", database: "connected"}`

### 2. CORS Test
- Open elke UI in de browser
- Controleer of er geen CORS errors in de console staan

### 3. Functionaliteit Test
- **User UI:** Test rapporten upload en bekijken
- **Tenant Admin UI:** Test admin functies en gebruiker beheer
- **System Owner UI:** Test tenant overzicht en systeem beheer

## 🚨 Veelvoorkomende Problemen

### CORS Error
**Symptoom:** `Access to fetch at '...' from origin '...' has been blocked by CORS policy`

**Oplossing:**
1. Controleer of de exacte Vercel URL in `CORS_ORIGINS` staat
2. Geen trailing slash toevoegen
3. Railway service opnieuw deployen na CORS wijziging

### API Connection Failed
**Symptoom:** `API Health Check Failed` in console

**Oplossing:**
1. Controleer of de `API_BASE_URL` correct is ingesteld
2. Controleer of je Railway API draait
3. Test de API URL direct: `curl https://jouw-api.up.railway.app/healthz`

### 404 Not Found
**Symptoom:** UI laadt niet of geeft 404

**Oplossing:**
1. Controleer of de bestanden correct zijn geüpload naar Vercel
2. Controleer de `vercel.json` configuratie (voor Optie A)
3. Controleer of de bestandsnamen correct zijn

## 🔧 Development Tips

### Lokale Testen
Voor lokale ontwikkeling, start een simpele HTTP server:

```bash
# Python 3
python -m http.server 8000

# Node.js
npx serve .

# Dan open: http://localhost:8000
```

### API URL Wisselen
Voor snelle API URL wijzigingen, gebruik browser localStorage:

```javascript
// In browser console:
localStorage.setItem('API_BASE_URL', 'https://nieuwe-api-url.com');
location.reload();
```

## 📞 Support

Als je problemen ondervindt:

1. **Controleer de browser console** voor error messages
2. **Test de API direct** met curl of Postman
3. **Controleer Railway logs** voor API problemen
4. **Controleer Vercel deployment logs** voor UI problemen

## 🎉 Succes!

Na het voltooien van deze stappen heb je:
- ✅ 3 werkende UI's gedeployed op Vercel
- ✅ API integratie geconfigureerd
- ✅ CORS correct ingesteld
- ✅ Alle rollen (User, Admin, System Owner) beschikbaar

Je Asbest Tool is nu volledig in de cloud! 🚀
