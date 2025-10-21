#!/usr/bin/env python3
"""Debug test to see what's being detected"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "integrated"))

from anti_hallucination import NegativeEvidenceDetector

detector = NegativeEvidenceDetector()

test_cases = [
    {'name': 'Luxury Mental Health Spa', 
     'combined_text': 'Premium mental health services, cash only, no insurance accepted'},
    {'name': 'Community Care Center',
     'combined_text': 'Affordable mental health services, accepts Medicaid and Medicare, sliding scale available'}
]

for facility in test_cases:
    result = detector.detect_negative_evidence(facility)
    print(f"\n{facility['name']}:")
    print(f"  Text: {facility['combined_text'][:50]}...")
    print(f"  Strong negative: {result['has_strong_negative']}")
    print(f"  Moderate negative: {result['has_moderate_negative']}")
    print(f"  Found indicators: {result['found_indicators']}")