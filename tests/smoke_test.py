"""
tests/smoke_test.py
A minimal test that verifies imports work.
This keeps CI green without needing the dataset file.
"""

def test_imports():
    import pandas  # noqa: F401
    import numpy   # noqa: F401
    import matplotlib  # noqa: F401
    import seaborn  # noqa: F401
