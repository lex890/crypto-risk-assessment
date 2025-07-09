import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app.search_screen import format_large_number, get_search_terms

@pytest.mark.parametrize(
    "raw, expected",
    [
        # --- nominal happy‑paths -----------------------------------------
        ("2500000000000", "2T"),           # ≥ 1 000 000 000 000  ➜ T
        ("3500000000",     "3B"),          # ≥ 1 000 000 000     ➜ B
        ("4200000",        "4M"),          # ≥ 1 000 000         ➜ M
        ("7500",           "7K"),          # ≥ 1 000             ➜ K
        ("999",            "999"),         # < 1 000             ➜ unchanged int str
        # --- formatting quirks -------------------------------------------
        ("1,234,567",      "1M"),          # commas should be ignored
        (1234.56,          "1K"),          # non‑string numeric
        # --- edge / error handling ---------------------------------------
        ("notanumber",     "notanumber"),  # invalid → returned verbatim
        (None,             None),          # AttributeError path
        (-123,             "-123"),        # negative values preserved
    ],
)

def test_format_large_number(raw, expected):
    assert format_large_number(raw) == expected

def test_get_search_terms():
    #expects for list of dicts
    sample_data = [
        {'#': '1', 'Name': 'Bitcoin', 'Symbol': 'BTC'},
        {'#': '2', 'Name': 'Ethereum', 'Symbol': 'ETH'},
    ]
    result = get_search_terms(sample_data)

    # Check exact terms returned
    expected_terms = ['1', 'Bitcoin', 'BTC', '2', 'Ethereum', 'ETH']
    assert result == expected_terms

    # Optional: check length
    assert len(result) == 6

    # Optional: check for presence
    assert 'Bitcoin' in result
    assert 'ETH' in result