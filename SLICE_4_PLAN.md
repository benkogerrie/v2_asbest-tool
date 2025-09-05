# Slice 4 - Verwerkingspipeline Stappenplan

**Doel:** Implementeer queue + worker + dummy AI + PDF generatie  
**Startpunt:** Slice 3 checkpoint (`slice-3-complete` tag)  
**Eindpunt:** Upload → Queue → Worker → AI analyse → PDF → Download

## 🎯 Overzicht Slice 4

**Wat we bouwen:**
1. **Worker deployment** - Aparte Railway service voor background processing
2. **Queue integratie** - Koppel upload aan RQ queue
3. **Dummy AI analyse** - Simuleer AI verwerking (score + bevindingen)
4. **PDF generatie** - Maak conclusie PDF aan
5. **Status updates** - Update rapport status tijdens verwerking
6. **Download endpoints** - Source + conclusion downloads

---

## 📋 Stappenplan (Testbaar per stap)

### **Stap 1: Worker Setup & Deployment** ⏱️ 30 min
**Doel:** Zet worker op Railway als aparte service

**Wat we doen:**
- [ ] Check bestaande worker code (`worker/run.py`)
- [ ] Test worker lokaal
- [ ] Deploy worker op Railway als aparte service
- [ ] Test worker verbinding met Redis

**Test criteria:**
- [ ] Worker start zonder errors
- [ ] Worker kan verbinden met Redis
- [ ] Worker wacht op jobs

**Exit criteria:** ✅ Worker draait stabiel op Railway

---

### **Stap 2: Queue Integration** ⏱️ 45 min
**Doel:** Koppel file upload aan queue systeem

**Wat we doen:**
- [ ] Check bestaande queue setup (`app/queue/`)
- [ ] Voeg job enqueue toe aan upload endpoint
- [ ] Test job creation in database
- [ ] Test job wordt opgepikt door worker

**Test criteria:**
- [ ] Upload endpoint maakt job aan
- [ ] Job verschijnt in database
- [ ] Worker pikt job op
- [ ] Job status wordt geüpdatet

**Exit criteria:** ✅ Upload → Queue → Worker flow werkt

---

### **Stap 3: Dummy AI Analyse** ⏱️ 30 min
**Doel:** Implementeer dummy AI die score + bevindingen genereert

**Wat we doen:**
- [ ] Maak dummy AI service (`app/services/ai_dummy.py`)
- [ ] Genereer deterministische score (85-95)
- [ ] Genereer 2-3 dummy bevindingen
- [ ] Test AI service in worker

**Test criteria:**
- [ ] AI service genereert consistente output
- [ ] Score is tussen 85-95
- [ ] Bevindingen hebben severity levels
- [ ] Output wordt opgeslagen in database

**Exit criteria:** ✅ Dummy AI analyse werkt en genereert realistische data

---

### **Stap 4: PDF Generatie** ⏱️ 45 min
**Doel:** Maak conclusie PDF met AI analyse resultaten

**Wat we doen:**
- [ ] Installeer ReportLab dependency
- [ ] Maak PDF generator service (`app/services/pdf_generator.py`)
- [ ] Genereer PDF met score, bevindingen, aanbevelingen
- [ ] Upload PDF naar storage (S3-compatible)

**Test criteria:**
- [ ] PDF wordt gegenereerd zonder errors
- [ ] PDF bevat score en bevindingen
- [ ] PDF wordt opgeslagen in storage
- [ ] PDF is downloadbaar

**Exit criteria:** ✅ PDF generatie werkt en wordt opgeslagen

---

### **Stap 5: Status Updates** ⏱️ 30 min
**Doel:** Update rapport status tijdens verwerking

**Wat we doen:**
- [ ] Update Report model status tijdens verwerking
- [ ] Log status changes in audit log
- [ ] Test status flow: PROCESSING → DONE/FAILED
- [ ] Handle error scenarios

**Test criteria:**
- [ ] Status wordt geüpdatet naar PROCESSING
- [ ] Status wordt geüpdatet naar DONE bij succes
- [ ] Status wordt geüpdatet naar FAILED bij errors
- [ ] Audit logs worden bijgehouden

**Exit criteria:** ✅ Status updates werken correct

---

### **Stap 6: Download Endpoints** ⏱️ 30 min
**Doel:** Voeg download endpoints toe voor source + conclusion

**Wat we doen:**
- [ ] Implementeer GET `/reports/{id}/source` endpoint
- [ ] Implementeer GET `/reports/{id}/conclusion` endpoint
- [ ] Test download van origineel bestand
- [ ] Test download van conclusie PDF

**Test criteria:**
- [ ] Source download werkt voor geüploade bestanden
- [ ] Conclusion download werkt voor verwerkte rapporten
- [ ] Downloads hebben juiste content-type
- [ ] RBAC werkt voor downloads

**Exit criteria:** ✅ Download endpoints werken correct

---

### **Stap 7: End-to-End Test** ⏱️ 30 min
**Doel:** Test complete flow van upload tot download

**Wat we doen:**
- [ ] Upload test bestand via API
- [ ] Controleer job wordt aangemaakt
- [ ] Wacht tot verwerking compleet is
- [ ] Download conclusie PDF
- [ ] Test error scenarios

**Test criteria:**
- [ ] Complete flow werkt zonder errors
- [ ] PDF bevat verwachte content
- [ ] Status updates zijn correct
- [ ] Error handling werkt

**Exit criteria:** ✅ Complete verwerkingspipeline werkt end-to-end

---

## 🔄 Rollback Plan

**Als iets misgaat:**
```bash
# Terug naar Slice 3 checkpoint
git checkout slice-3-complete
git reset --hard slice-3-complete
```

## 📊 Success Metrics

**Slice 4 is compleet wanneer:**
- [ ] Upload → Queue → Worker → AI → PDF → Download flow werkt
- [ ] Status updates zijn real-time zichtbaar
- [ ] PDF generatie werkt consistent
- [ ] Error handling is robuust
- [ ] Performance is acceptabel (< 30s voor dummy AI)

## 🚀 Volgende Stappen (Slice 5)

Na Slice 4 kunnen we:
- Echte AI/RAG integratie
- Geavanceerde PDF templates
- Performance optimalisatie
- Monitoring en alerting

---

**Totaal geschatte tijd:** 4-5 uur  
**Testbaar per stap:** ✅ Ja  
**Rollback mogelijk:** ✅ Ja (Slice 3 checkpoint)
