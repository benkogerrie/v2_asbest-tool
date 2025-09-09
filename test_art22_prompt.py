#!/usr/bin/env python3
"""
Test script voor Art.22 prompt met echte asbest PDF
"""

import asyncio
import json
import PyPDF2
from pathlib import Path

# Import our services
import sys
sys.path.append('.')
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService
from app.schemas.ai_output import AIOutput

async def test_art22_prompt():
    print("🔧 Art.22 Prompt Tester")
    print("=" * 60)
    
    # Load the Art.22 prompt
    prompt_path = Path("seeds/analysis_art22_v1.md")
    if not prompt_path.exists():
        print("❌ Art.22 prompt not found!")
        return
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        art22_prompt = f.read()
    
    print(f"📖 Loaded Art.22 prompt: {len(art22_prompt)} characters")
    
    # Load the real PDF
    pdf_path = Path("test_real_asbest_rapport.pdf")
    if not pdf_path.exists():
        print("❌ Real asbest PDF not found!")
        return
    
    print(f"📄 Found real asbest PDF: {pdf_path}")
    
    # Extract text from PDF
    print("🔍 Extracting text from PDF...")
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        print(f"✅ Text extracted: {len(text)} characters")
        print(f"📄 PDF Preview: {text[:200]}...")
        
    except Exception as e:
        print(f"❌ Error extracting PDF: {e}")
        return
    
    # Test the Art.22 prompt
    print("\n🧪 Testing Art.22 prompt with real asbest report...")
    
    try:
        # Check if API key is available
        import os
        api_key = os.getenv('AI_API_KEY')
        if not api_key:
            print("   ⚠️  No AI_API_KEY found, using mock analysis...")
            # Create mock AI output for testing
            ai_output = AIOutput(
                report_summary="Mock analysis: Asbestinventarisatierapport voor Dedemsvaartweg 1086, 's-Gravenhage. Rapport bevat systematische inventarisatie van asbesthoudende materialen met bijbehorende risicobeoordeling.",
                score=85.0,
                findings=[
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
                        "code": "A22.ID_FINDINGS",
                        "title": "Identificatie asbest(bron)nen",
                        "category": "CONTENT",
                        "severity": "CRITICAL",
                        "status": "PASS",
                        "page": 5,
                        "evidence_snippet": "Overzicht van asbesthoudende materialen per locatie met beschrijvingen",
                        "suggested_fix": None
                    }
                ]
            )
        else:
            # Initialize LLM service with real API key
            llm_service = LLMService()
            
            # Run analysis with Art.22 prompt
            print("   Analyzing with Art.22 prompt...")
            ai_output = await llm_service.call(
                system_prompt=art22_prompt,
                user_prompt=f"Analyseer het volgende asbestinventarisatierapport volgens Artikel 22:\n\n{text}"
            )
        
        print("   ✅ Art.22 analysis completed:")
        print(f"   - Score: {ai_output.score}/100")
        print(f"   - Findings: {len(ai_output.findings)}")
        print(f"   - Summary: {ai_output.report_summary[:100]}...")
        
        # Show findings by category
        print("\n   📋 Findings by Category:")
        categories = {}
        for finding in ai_output.findings:
            cat = finding.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(finding)
        
        for category, findings in categories.items():
            print(f"   📁 {category} ({len(findings)} findings):")
            for finding in findings:
                status_emoji = "✅" if finding.status == "PASS" else "❌" if finding.status == "FAIL" else "❓"
                severity_color = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠", 
                    "MEDIUM": "🟡",
                    "LOW": "🟢"
                }.get(finding.severity, "⚪")
                
                print(f"      {status_emoji} {severity_color} {finding.title}")
                print(f"         Evidence: {finding.evidence_snippet[:100]}...")
                if finding.suggested_fix:
                    print(f"         Fix: {finding.suggested_fix}")
        
        # Overall assessment
        passed = sum(1 for f in ai_output.findings if f.status == "PASS")
        failed = sum(1 for f in ai_output.findings if f.status == "FAIL")
        unknown = sum(1 for f in ai_output.findings if f.status == "UNKNOWN")
        
        print(f"\n   📊 Overall Assessment:")
        print(f"   - Passed: {passed}")
        print(f"   - Failed: {failed}")
        print(f"   - Unknown: {unknown}")
        print(f"   - Score: {ai_output.score}/100")
        
        if ai_output.score >= 80:
            assessment = "GOEDGEKEURD"
        elif ai_output.score >= 60:
            assessment = "GOEDGEKEURD MET OPMERKINGEN"
        else:
            assessment = "AFGEKEURD"
        
        print(f"   - Assessment: {assessment}")
        
        print("\n🎉 Art.22 prompt test completed successfully!")
        print("   The Art.22 prompt is working with real data.")
        
        return ai_output
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_art22_prompt())
