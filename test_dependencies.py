#!/usr/bin/env python3
"""
Test script to check if new dependencies are available.
"""
import sys

def test_imports():
    """Test if new dependencies can be imported."""
    print("🔍 TESTING NEW DEPENDENCIES")
    print("=" * 40)
    
    # Test PyMuPDF
    try:
        import fitz
        print(f"✅ PyMuPDF: {fitz.__version__}")
    except ImportError as e:
        print(f"❌ PyMuPDF: {e}")
    
    # Test ReportLab
    try:
        import reportlab
        print(f"✅ ReportLab: {reportlab.Version}")
    except ImportError as e:
        print(f"❌ ReportLab: {e}")
    
    # Test new models
    try:
        from app.models.analysis import Analysis
        from app.models.finding import Finding
        print("✅ New models: Analysis, Finding")
    except ImportError as e:
        print(f"❌ New models: {e}")
    
    # Test new services
    try:
        from app.services.analyzer.rules import analyze_text_to_result
        from app.services.pdf.conclusion_reportlab import build_conclusion_pdf
        print("✅ New services: Analyzer, PDF generator")
    except ImportError as e:
        print(f"❌ New services: {e}")
    
    # Test worker job
    try:
        from app.queue.jobs import process_report
        print("✅ Worker job: process_report")
    except ImportError as e:
        print(f"❌ Worker job: {e}")

def test_worker_functionality():
    """Test if worker functionality works."""
    print("\n🔧 TESTING WORKER FUNCTIONALITY")
    print("=" * 40)
    
    try:
        from app.services.analyzer.rules import run_rules_v1
        from app.services.analyzer.scoring import compute_score
        
        # Test with dummy text
        test_text = "This is a test document with project information and some findings."
        findings = run_rules_v1(test_text)
        score = compute_score([f.dict() for f in findings])
        
        print(f"✅ Rules engine: {len(findings)} findings, score {score}")
        
        for finding in findings[:3]:  # Show first 3
            print(f"   - {finding.rule_id}: {finding.severity}")
            
    except Exception as e:
        print(f"❌ Worker functionality: {e}")

def main():
    """Main function."""
    test_imports()
    test_worker_functionality()
    
    print("\n📊 DEPENDENCY TEST SUMMARY")
    print("=" * 40)
    print("If all tests pass, the worker should be able to process reports.")
    print("If any fail, that's likely the cause of the 500 errors.")

if __name__ == "__main__":
    main()
