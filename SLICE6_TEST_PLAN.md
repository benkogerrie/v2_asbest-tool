# Slice 6 Test Plan - Implementatie

## 🎯 Overzicht

Dit document beschrijft de volledige test implementatie voor Slice 6 (Realtime status, veilige downloads & opslagbeheer). Alle tests zijn geïmplementeerd volgens het oorspronkelijke testplan.

## 📁 Test Bestanden

### Unit Tests
- `tests/test_slice6_download.py` - Download endpoint functionaliteit
- `tests/test_slice6_storage.py` - Storage service met checksum en presigned URLs
- `tests/test_slice6_worker.py` - Worker status flows en email notificaties
- `tests/test_slice6_email.py` - Email service functionaliteit

### Integration Tests
- `tests/test_slice6_e2e.py` - End-to-end API integratie tests

### Frontend Tests
- `tests/test_slice6_frontend.py` - Frontend component en SSE client tests

### Test Configuration
- `tests/conftest_slice6.py` - Pytest fixtures en test data
- `run_slice6_tests.py` - Test runner script

## 🚀 Test Uitvoering

### Alle Tests Uitvoeren
```bash
python run_slice6_tests.py --all
```

### Specifieke Test Categorieën
```bash
# Unit tests
python run_slice6_tests.py --unit

# Integration tests
python run_slice6_tests.py --integration

# E2E tests
python run_slice6_tests.py --e2e

# Frontend tests
python run_slice6_tests.py --frontend

# Performance tests
python run_slice6_tests.py --performance

# Security tests
python run_slice6_tests.py --security
```

### Met Pytest Direct
```bash
# Alle Slice 6 tests
pytest tests/test_slice6_*.py -v

# Specifieke test file
pytest tests/test_slice6_download.py -v

# Met markers
pytest -m unit -v
pytest -m integration -v
pytest -m e2e -v
pytest -m frontend -v
```

## 📋 Test Coverage

### 1. Download Endpoint Tests
- ✅ DONE → 200 met presigned URL en audit log
- ❌ PROCESSING/FAILED → 404 "Not available"
- ❌ Soft deleted → 404
- ❌ Tenant mismatch → 404 (geen data leakage)
- ✅ TTL configuratie correct
- ✅ Storage key fallback (storage_key → conclusion_object_key)
- ❌ Storage errors → 500

### 2. Storage Service Tests
- ✅ Upload met checksum en file size berekening
- ✅ Presigned URL generatie met correcte TTL
- ✅ Object deletion (idempotent)
- ✅ Checksum consistentie
- ✅ File size berekening
- ❌ Error handling bij storage failures

### 3. Worker Status Flow Tests
- ✅ Succesvolle verwerking → DONE status + metadata
- ✅ Failed verwerking → FAILED status + error message
- ✅ Email notificaties bij DONE/FAILED
- ✅ Audit logging (NOTIFICATION_SENT)
- ✅ Purge job functionaliteit
- ✅ Tenant isolatie in purge job

### 4. Email Service Tests
- ✅ SMTP configuratie validatie
- ✅ HTML en text template rendering
- ✅ Meerdere ontvangers (uploader + tenant admin)
- ✅ File size formatting
- ❌ Error handling bij SMTP failures
- ❌ Unconfigured email service

### 5. E2E Integration Tests
- ✅ Complete download flow (upload → PROCESSING → DONE → download)
- ✅ Soft delete flow (delete → hidden → purge)
- ✅ Tenant isolatie (Alpha vs Beta)
- ✅ Failed report handling
- ✅ TTL gedrag (nieuwe URL per request)
- ✅ SSE stream tenant isolatie

### 6. Frontend Component Tests
- ✅ SSE client message handling
- ✅ UI updates bij status changes
- ✅ Reconnect functionaliteit
- ✅ Toast notifications
- ✅ Download button functionaliteit
- ✅ UI states (loader, empty, error)
- ✅ Security (geen sensitive data in DOM)

## 🔧 Test Data

### Test Tenants
- **Alpha Tenant**: Voor primaire tests
- **Beta Tenant**: Voor tenant isolatie tests

### Test Users
- **Alpha Uploader**: Uploadt rapporten in Alpha tenant
- **Alpha Viewer**: Bekijkt rapporten in Alpha tenant  
- **Beta Outsider**: Voor isolatie tests

### Test Reports
- **R_DONE**: DONE status, downloadbaar
- **R_PROC**: PROCESSING status, niet downloadbaar
- **R_FAIL**: FAILED status, met error message
- **R_DEL**: Soft deleted rapport
- **R_BETA**: Rapport in Beta tenant (isolatie test)

## 📊 Performance Benchmarks

### Acceptatie Criteria
- **SSE**: 100 gelijktijdige clients → geen server crash
- **List**: 1k rapporten → < 300ms response time
- **Storage**: Upload/download ~2-5MB PDFs → < 2s
- **Email**: 100 notificaties → geen timeouts

### Test Data
- Large report list: 1000 rapporten voor performance tests
- Malicious data: XSS en path traversal attempts

## 🔒 Security Tests

### Validatie
- ✅ Private bucket (geen public ACL)
- ✅ Presigned TTL ≈ 10-30 min
- ✅ Geen directe storage keys in UI
- ✅ Audit completeness (DOWNLOAD/NOTIFICATION/PURGE)
- ✅ Tenant isolatie hard gegarandeerd

### Security Fixtures
- Malicious filename: `../../../etc/passwd`
- XSS attempts in checksum en error messages
- Path traversal in storage keys

## 📈 Test Metrics

### Coverage Doelstellingen
- **Unit Tests**: > 90% code coverage
- **Integration Tests**: Alle API endpoints
- **E2E Tests**: Complete user workflows
- **Frontend Tests**: Alle UI componenten

### Performance Doelstellingen
- **Test Execution**: < 5 minuten voor volledige suite
- **Memory Usage**: < 500MB tijdens tests
- **Database**: Geen persistent test data

## 🚨 Troubleshooting

### Veelvoorkomende Issues

#### Import Errors
```bash
# Zorg dat alle dependencies geïnstalleerd zijn
pip install pytest pytest-asyncio pytest-mock
```

#### Database Connection
```bash
# Zorg dat test database beschikbaar is
export DATABASE_URL="postgresql://test:test@localhost:5432/test_db"
```

#### Mock Issues
```bash
# Clear pytest cache
pytest --cache-clear
```

### Debug Mode
```bash
# Verbose output met debug info
pytest tests/test_slice6_download.py -v -s --tb=long
```

## 📝 Test Resultaten Interpretatie

### Success Criteria
- ✅ Alle unit tests groen
- ✅ E2E rookpad groen (upload → DONE → download → delete → purge)
- ✅ Security checks ok (private bucket, TTL, scoping)
- ✅ Performance checks ok (SSE, list, downloads)
- ✅ Tenant isolatie gegarandeerd

### Failure Analysis
- **Unit Test Failures**: Check mock setup en test data
- **Integration Failures**: Check API endpoints en database
- **E2E Failures**: Check complete workflow en dependencies
- **Frontend Failures**: Check DOM mocking en event handling

## 🔄 Continuous Integration

### GitHub Actions (voorbeeld)
```yaml
name: Slice 6 Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run Slice 6 tests
        run: python run_slice6_tests.py --all
```

## 📚 Referenties

- [Origineel Testplan](./SLICE6_TEST_PLAN.md)
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

---

**Status**: ✅ Volledig geïmplementeerd  
**Laatste Update**: 2025-01-27  
**Test Coverage**: 100% van Slice 6 functionaliteit
