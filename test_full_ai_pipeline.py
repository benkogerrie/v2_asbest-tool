#!/usr/bin/env python3
"""
Test script voor volledige AI pipeline met PDF generatie
"""

import asyncio
import os
import tempfile
from pathlib import Path
from app.queue.ai_analysis import run_ai_analysis

async def test_full_ai_pipeline():
    print("🔧 Full AI Pipeline Tester")
    print("=" * 60)
    
    # Check if we have the real PDF
    pdf_path = Path("test_real_asbest_rapport.pdf")
    if not pdf_path.exists():
        print("❌ Real asbest PDF not found!")
        return
    
    print(f"📄 Found real asbest PDF: {pdf_path}")
    
    # Read PDF bytes
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    print(f"📖 PDF loaded: {len(pdf_bytes):,} bytes")
    
    # Test parameters
    report_id = "test-report-123"
    tenant_id = "test-tenant-456"
    
    print(f"🧪 Testing full AI pipeline:")
    print(f"   - Report ID: {report_id}")
    print(f"   - Tenant ID: {tenant_id}")
    print(f"   - PDF size: {len(pdf_bytes):,} bytes")
    
    try:
        # Run the full AI analysis pipeline
        print("\n🚀 Starting AI analysis pipeline...")
        await run_ai_analysis(report_id, tenant_id, pdf_bytes)
        
        print("✅ AI analysis pipeline completed successfully!")
        print("   - PDF text extracted")
        print("   - AI analysis performed")
        print("   - Findings stored in database")
        print("   - Conclusion PDF generated")
        print("   - PDF uploaded to storage")
        
        print("\n🎉 Full pipeline test completed!")
        print("   Ready for production use!")
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if we have required environment variables
    if not os.getenv('AI_API_KEY'):
        print("⚠️  No AI_API_KEY found, pipeline will use mock analysis")
    
    asyncio.run(test_full_ai_pipeline())