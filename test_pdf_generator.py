#!/usr/bin/env python3
"""
Test script voor PDF generator met Art.22 analyse resultaten
"""

import os
import json
from pathlib import Path
from app.services.pdf_generator import generate_conclusion_pdf

def test_pdf_generator():
    print("🔧 PDF Generator Tester")
    print("=" * 50)
    
    # Create output directory
    os.makedirs("out", exist_ok=True)
    
    # Sample report metadata
    report_meta = {
        "Opdrachtgever": "Roessen & Roessen",
        "Projectnummer": "252.948",
        "Objectlocatie": "Dedemsvaartweg 1086, 2545BG te 's-Gravenhage",
        "Rapportdatum": "2025-01-18",
        "Versie": "1.0",
        "Opsteller": "Van Santen Advies B.V."
    }
    
    # Sample BAG data
    bag_data = {
        "Adres": "Dedemsvaartweg 1086",
        "Plaats": "'s-Gravenhage",
        "Postcode": "2545BG",
        "BAG Pand-ID": "0123456789012345",
        "BAG VBO-ID": "0987654321098765",
        "Bouwjaar": "1981",
        "Oppervlakte (m²)": "245",
        "Gebruiksdoel": "Wonen",
        "Status": "In gebruik"
    }
    
    # Sample AI analysis results (based on our Art.22 test)
    ai_analysis = {
        "report_summary": "Asbestinventarisatierapport voor Dedemsvaartweg 1086, 's-Gravenhage. Rapport bevat systematische inventarisatie van asbesthoudende materialen met bijbehorende risicobeoordeling.",
        "score": 85.0,
        "findings": [
            {
                "code": "A22.META",
                "title": "Titelblad & metadata",
                "category": "FORMAL",
                "severity": "HIGH",
                "status": "PASS",
                "page": 1,
                "evidence_snippet": "Rapport bevat alle vereiste metadata: titel, opdrachtgever, projectnummer, adres, datum",
                "suggested_fix": None
            },
            {
                "code": "A22.SCOPE",
                "title": "Reikwijdte / onderzoeksomvang",
                "category": "FORMAL",
                "severity": "HIGH",
                "status": "PASS",
                "page": 2,
                "evidence_snippet": "Duidelijke scope beschrijving van onderzoeksomvang en grenzen",
                "suggested_fix": None
            },
            {
                "code": "A22.METHOD",
                "title": "Methodiek & uitvoering",
                "category": "CONTENT",
                "severity": "MEDIUM",
                "status": "FAIL",
                "page": 3,
                "evidence_snippet": "Methodiek beschrijving is onvolledig, ontbreken details over inspectieniveau",
                "suggested_fix": "Voeg gedetailleerde beschrijving toe van toegepaste inventarisatiemethode"
            },
            {
                "code": "A22.ID_FINDINGS",
                "title": "Identificatie asbest(bron)nen",
                "category": "CONTENT",
                "severity": "CRITICAL",
                "status": "PASS",
                "page": 5,
                "evidence_snippet": "Overzicht van asbesthoudende materialen per locatie met beschrijvingen",
                "suggested_fix": None
            },
            {
                "code": "A22.SAMPLES_LAB",
                "title": "Monsters & analyseresultaten",
                "category": "CONTENT",
                "severity": "CRITICAL",
                "status": "FAIL",
                "page": 8,
                "evidence_snippet": "Labrapporten ontbreken, geen verwijzing naar bijlagen met analyseresultaten",
                "suggested_fix": "Voeg labrapporten toe als bijlage en verwijs ernaar in hoofdtekst"
            },
            {
                "code": "A22.RECOMMENDATIONS",
                "title": "Aanbevelingen vervolgstappen",
                "category": "RISK",
                "severity": "MEDIUM",
                "status": "PASS",
                "page": 12,
                "evidence_snippet": "Concrete aanbevelingen voor vervolgacties per gevonden materiaal",
                "suggested_fix": None
            }
        ]
    }
    
    print("📋 Test data prepared:")
    print(f"   - Report metadata: {len(report_meta)} items")
    print(f"   - BAG data: {len(bag_data)} items")
    print(f"   - AI analysis: {ai_analysis['score']}/100 score, {len(ai_analysis['findings'])} findings")
    
    # Generate PDF
    output_path = "out/qa_conclusie_test.pdf"
    print(f"\n🔨 Generating PDF: {output_path}")
    
    try:
        result_path = generate_conclusion_pdf(
            output_path=output_path,
            report_meta=report_meta,
            ai_analysis=ai_analysis,
            bag_data=bag_data,
            streetview_path=None  # No street view for this test
        )
        
        print(f"✅ PDF generated successfully!")
        print(f"   Path: {result_path}")
        
        # Check if file exists and get size
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        print(f"\n📄 PDF Preview:")
        print(f"   - Title: QA-Conclusierapport Asbestinventarisatie")
        print(f"   - Article 22 compliance reference")
        print(f"   - Report metadata table")
        print(f"   - BAG viewer data table")
        print(f"   - Final score: {ai_analysis['score']}/100")
        print(f"   - Findings table with {len(ai_analysis['findings'])} items")
        print(f"   - AI analysis summary section")
        print(f"   - QA methodology section")
        
        print(f"\n🎉 PDF generator test completed successfully!")
        print(f"   Ready for integration with AI analysis pipeline!")
        
        return result_path
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_pdf_generator()
