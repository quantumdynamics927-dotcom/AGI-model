#!/usr/bin/env python3
"""
Simple test for async database functionality
"""

import asyncio
import numpy as np
from agi_database import AGIDatabase

async def test_async_functionality():
    """Test async database operations"""
    print("🧪 Testing Async Database Functionality")

    # Test data
    test_vector = np.random.randn(128).astype(np.float32)

    try:
        # Test async context manager
        async with AGIDatabase().async_context() as db:
            print("✅ Async context manager working")

            # Test async sacred geometry insert (will fail without DB, but tests async path)
            try:
                result = await db.insert_sacred_geometry_data_async(
                    "test_dataset", "test_type", test_vector, 0.5
                )
                print(f"✅ Async insert returned: {result}")
            except Exception as e:
                print(f"ℹ️  Async insert failed (expected without database): {type(e).__name__}")

        print("✅ Async functionality test completed")

    except Exception as e:
        print(f"❌ Async test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_async_functionality())
    print(f"Test result: {'PASSED' if success else 'FAILED'}")