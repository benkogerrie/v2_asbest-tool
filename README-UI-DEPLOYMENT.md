# 🚀 Vercel UI Deployment Guide

## 📁 **Aanbevolen Mapstructuur**

```
/
├── ui/
│   ├── tenant-admin/
│   │   └── index.html      (Tenant Admin UI)
│   ├── user/
│   │   └── index.html      (User UI)
│   ├── system-owner/
│   │   └── index.html      (System Owner UI)
│   └── vercel.json         (Routing configuratie)
└── README-UI-DEPLOYMENT.md
```

## 🎯 **Stap 1: Vercel Project Aanmaken**

1. Ga naar [vercel.com](https://vercel.com) en log in
2. Klik op **"New Project"**
3. **Import Git Repository** (je GitHub repo)
4. **Framework Preset:** Laat leeg of kies "Other"
5. **Project Name:** `asbest-tool-ui`
6. **Root Directory:** `ui` (belangrijk!)
7. **Build Command:** Laat leeg
8. **Output Directory:** Laat leeg
9. **Install Command:** Laat leeg
10. Klik **"Deploy"**

## 🔧 **Stap 2: Bestanden Voorbereiden**

### **Maak de UI map aan:**
```bash
mkdir ui
mkdir ui/tenant-admin
mkdir ui/user
mkdir ui/system-owner
```

### **Plaats de bestanden:**
- `index.html` → `ui/tenant-admin/index.html` (Tenant Admin)
- `user.html` → `ui/user/index.html` (User)
- `system-owner.html` → `ui/system-owner/index.html` (System Owner)

### **vercel.json configuratie:**
```json
{
  "routes": [
    {
      "src": "/",
      "dest": "/tenant-admin/index.html"
    },
    {
      "src": "/tenant-admin",
      "dest": "/tenant-admin/index.html"
    },
    {
      "src": "/user",
      "dest": "/user/index.html"
    },
    {
      "src": "/system-owner",
      "dest": "/system-owner/index.html"
    }
  ]
}
```

## 🌐 **Stap 3: Deployen**

1. **Commit en push** je wijzigingen naar GitHub
2. Vercel detecteert automatisch de wijzigingen
3. **Automatic deployment** start
4. Wacht tot deployment klaar is (groene checkmark)

## 📝 **Stap 4: URLs Noteren**

Na deployment krijg je deze URLs:
- **Tenant Admin:** `https://asbest-tool-ui.vercel.app/` of `https://asbest-tool-ui.vercel.app/tenant-admin`
- **User:** `https://asbest-tool-ui.vercel.app/user`
- **System Owner:** `https://asbest-tool-ui.vercel.app/system-owner`

**⚠️ Noteer deze URLs!** Je hebt ze nodig voor de Railway CORS configuratie.

## 🔍 **Stap 5: Testen**

1. **Open elke URL** in je browser
2. **Controleer** of de UI's laden
3. **Test** de API health check (zie console voor errors)
4. **Noteer** eventuele CORS errors (normaal in deze fase)

## 🎯 **Volgende Stap: Railway API**

Zodra je Vercel URLs hebt, gaan we:
1. Railway project aanmaken
2. PostgreSQL database toevoegen
3. API deployen
4. CORS configureren met je Vercel URLs

---

**💡 Tip:** Nu zijn alle UI's consistent georganiseerd in submappen! Dit maakt het ook makkelijker om later nieuwe UI's toe te voegen.
