#!/usr/bin/env python3
"""
Simple test script to verify RFP extraction system functionality.
This tests the core components without requiring full service setup.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)

    try:
        import sqlalchemy
        print("✓ SQLAlchemy imported")
    except ImportError as e:
        print(f"✗ SQLAlchemy import failed: {e}")
        return False

    try:
        import fitz
        print("✓ PyMuPDF imported")
    except ImportError as e:
        print(f"✗ PyMuPDF import failed: {e}")
        return False

    try:
        from database import engine, Base, get_db_session
        print("✓ Database module imported")
    except ImportError as e:
        print(f"✗ Database import failed: {e}")
        return False

    try:
        from models import Document, Requirement, TextChunk
        print("✓ Models imported")
    except ImportError as e:
        print(f"✗ Models import failed: {e}")
        return False

    try:
        from document_processor import DocumentProcessor
        print("✓ Document processor imported")
    except ImportError as e:
        print(f"✗ Document processor import failed: {e}")
        return False

    print("\n✅ All imports successful\n")
    return True

def test_database():
    """Test database initialization"""
    print("=" * 60)
    print("TEST 2: Database Initialization")
    print("=" * 60)

    try:
        from database import engine, Base, get_db_session
        from models import Document, Requirement, TextChunk

        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created")

        # Test connection
        with get_db_session() as session:
            result = session.execute(sqlalchemy.text("SELECT 1")).scalar()
            if result == 1:
                print("✓ Database connection verified")
            else:
                print("✗ Database connection test failed")
                return False

        # Check tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = ['documents', 'text_chunks', 'requirements', 'processing_jobs']
        for table in expected_tables:
            if table in tables:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' missing")
                return False

        print("\n✅ Database initialized successfully\n")
        return True

    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_processing():
    """Test document processing with sample content"""
    print("=" * 60)
    print("TEST 3: Document Processing")
    print("=" * 60)

    try:
        import uuid
        import asyncio
        from datetime import datetime
        from database import get_db_session
        from models import Document, ProcessingStatus, ProcessingJob
        from document_processor import DocumentProcessor

        # Create sample RFP content
        sample_rfp = """
        Section C: Performance Work Statement

        1. INTRODUCTION
        The contractor shall provide IT Support Services as described herein.

        2. TECHNICAL REQUIREMENTS
        2.1 System Performance
        The system shall process user requests within 2 seconds response time.
        The contractor shall maintain 99.9% uptime availability.

        2.2 Security Requirements
        The contractor shall comply with NIST 800-171 security standards.
        All data shall be encrypted at rest and in transit.

        3. DELIVERABLES
        The contractor shall deliver monthly status reports.
        The contractor shall provide technical documentation.

        Section L: Proposal Instructions

        Offerors shall submit proposals in three volumes:
        - Volume 1: Technical Approach
        - Volume 2: Management Approach
        - Volume 3: Price Proposal

        Section M: Evaluation Criteria

        Proposals will be evaluated on:
        1. Technical Approach (40 points)
        2. Past Performance (30 points)
        3. Price (30 points)
        """

        # Save to test file
        test_file = Path("test_rfp_sample.txt")
        test_file.write_text(sample_rfp)
        print(f"✓ Created test file: {test_file}")

        # Create document record
        doc_id = uuid.uuid4()
        job_id = uuid.uuid4()

        with get_db_session() as session:
            document = Document(
                id=doc_id,
                original_filename="test_rfp_sample.txt",
                file_path=str(test_file),
                file_type="txt",
                file_size=len(sample_rfp),
                status=ProcessingStatus.PENDING,
                uploaded_at=datetime.utcnow()
            )
            session.add(document)

            job = ProcessingJob(
                id=job_id,
                document_id=doc_id,
                job_type="extraction",
                status="pending"
            )
            session.add(job)
            session.commit()
            print(f"✓ Created document record: {doc_id}")
            print(f"✓ Created processing job: {job_id}")

        # Process document
        processor = DocumentProcessor()

        # For testing, we'll manually extract and chunk
        print("\n📄 Processing document...")

        # Test text extraction
        text = test_file.read_text()
        if len(text) > 0:
            print(f"✓ Extracted {len(text)} characters")
        else:
            print("✗ No text extracted")
            return False

        # Test chunking
        chunks = asyncio.run(processor._intelligent_chunking(text, document))
        print(f"✓ Created {len(chunks)} text chunks")

        if len(chunks) > 0:
            print(f"\nSample chunk:")
            print(f"  Section: {chunks[0].get('section', 'N/A')}")
            print(f"  Text: {chunks[0]['text'][:100]}...")

        # Test requirement detection
        requirement_count = 0
        for chunk in chunks:
            if processor._is_requirement_text(chunk['text']):
                requirement_count += 1

        print(f"✓ Detected {requirement_count} potential requirements")

        # Test classification
        if requirement_count > 0:
            sample_req = next(c for c in chunks if processor._is_requirement_text(c['text']))
            classification = asyncio.run(processor._classify_requirement(sample_req['text']))
            print(f"✓ Sample classification: {classification}")

        # Clean up
        test_file.unlink()
        print(f"✓ Cleaned up test file")

        print("\n✅ Document processing test successful\n")
        return True

    except Exception as e:
        print(f"✗ Document processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test that FastAPI can initialize"""
    print("=" * 60)
    print("TEST 4: API Initialization")
    print("=" * 60)

    try:
        from main import app
        print("✓ FastAPI app imported")

        # Check routes exist
        routes = [route.path for route in app.routes]
        expected_routes = ['/health', '/documents/upload', '/requirements/review_queue']

        for route in expected_routes:
            if route in routes:
                print(f"✓ Route '{route}' exists")
            else:
                print(f"✗ Route '{route}' missing")
                return False

        print("\n✅ API initialization successful\n")
        return True

    except Exception as e:
        print(f"✗ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RFP EXTRACTION PLATFORM - SYSTEM TEST")
    print("=" * 60 + "\n")

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Database", test_database()))
    results.append(("Document Processing", test_document_processing()))
    results.append(("API Initialization", test_api_endpoints()))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! System is ready for use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
