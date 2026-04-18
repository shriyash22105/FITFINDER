import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:5000"

@pytest.fixture
def tester(base_url):
    from test_api import FitFinderAPITester
    return FitFinderAPITester(base_url)

