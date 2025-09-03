# Railway Deployment Checklist

## **🚨 Kritieke Environment Variables**

### **1. Database (PostgreSQL)**
```bash
DATABASE_URL=postgresql://username:password@host:port/database
```
- **Format**: Moet `postgresql://` zijn (niet `postgres://`)
- **Railway**: Automatisch ingesteld bij PostgreSQL service
- **Check**: Health endpoint moet "database: healthy" tonen

### **2. Redis**
```bash
REDIS_URL=redis://:password@host:port/0
```
- **Format**: Moet exact dit formaat hebben
- **Railway**: Moet handmatig worden ingesteld
- **Check**: Health endpoint moet "redis: healthy" tonen

### **3. JWT Secret**
```bash
JWT_SECRET=your-super-secret-key-here
```
- **Railway**: Moet handmatig worden ingesteld
- **Check**: API moet starten zonder JWT errors

## **🔧 Service Configuratie**

### **API Service**
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/healthz`
- **Dependencies**: Database + Redis

### **Worker Service**
- **Start Command**: `python -m worker.run`
- **Config File**: `railway-worker.json`
- **Dependencies**: Database + Redis

## **📊 Health Check Interpretatie**

### **Gezonde Status**
```json
{
  "status": "healthy",
  "message": "API is running",
  "timestamp": "2024-01-27T10:30:00Z",
  "checks": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### **Degraded Status (Database of Redis down)**
```json
{
  "status": "degraded",
  "message": "API is running",
  "timestamp": "2024-01-27T10:30:00Z",
  "checks": {
    "database": "healthy",
    "redis": "unhealthy: Redis connection failed"
  }
}
```

## **🚨 Troubleshooting Stappen**

### **Health Check Fails (503/500)**
1. **Controleer Environment Variables** in Railway dashboard
2. **Controleer Service Logs** voor specifieke error messages
3. **Controleer Service Dependencies** (Database + Redis moeten draaien)

### **Database Connection Fails**
1. **Controleer DATABASE_URL** format
2. **Controleer PostgreSQL service** status
3. **Controleer database credentials**

### **Redis Connection Fails**
1. **Controleer REDIS_URL** format
2. **Controleer Redis service** status
3. **Controleer Redis credentials**

### **API Start Fails**
1. **Controleer alle environment variables**
2. **Controleer service logs** voor import errors
3. **Controleer Python dependencies**

## **✅ Deployment Volgorde**

1. **Database Service** (PostgreSQL)
2. **Redis Service** (Redis plugin of externe provider)
3. **API Service** (met alle environment variables)
4. **Worker Service** (met alle environment variables)

## **🔍 Log Analysis**

### **Succesvolle Start**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **Database Error**
```
ERROR:    Database connection failed: connection refused
ERROR:    Health check failed: database unhealthy
```

### **Redis Error**
```
ERROR:    Redis connection failed: connection refused
ERROR:    Health check failed: redis unhealthy
```

## **📞 Support**

Als alle bovenstaande stappen zijn gevolgd en het probleem blijft bestaan:
1. **Controleer Railway status page**
2. **Controleer service logs** voor specifieke errors
3. **Controleer network connectivity** tussen services
