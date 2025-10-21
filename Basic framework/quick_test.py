#!/usr/bin/env python3
"""
Quick test to verify negative evidence detection is working
"""

import pandas as pd
import sys
from pathlib import Path

# Add paths for imports
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir / "integrated"))

# Import the modules
from facility_scorer import FacilityScorer

# Create test data
test_data = pd.DataFrame([
    {
        'name': 'Luxury Mental Health Spa',
        'org': 'Luxury Mental Health Spa',
        'combined_text': 'Premium mental health services, cash only, no insurance accepted',
        'city': 'New York',
        'state': 'NY'
    },
    {
        'name': 'Community Care Center', 
        'org': 'Community Care Center',
        'combined_text': 'Affordable mental health services, accepts Medicaid and Medicare, sliding scale available',
        'city': 'Chicago',
        'state': 'IL'
    }
])

print("Testing Negative Evidence Detection\n")
print("="*50)

# Initialize scorer
scorer = FacilityScorer()

# Score the facilities
scored_df = scorer.score_facilities(test_data, text_column='combined_text')

# Show results
print("\nResults:")
print("-"*50)
for _, row in scored_df.iterrows():
    print(f"\n{row['name']}")
    print(f"  Score: {row['overall_care_needs_score']:.2f}/10")
    print(f"  Has negative evidence: {row.get('has_negative_evidence', False)}")

print("\n✅ Test complete!")
print("\nIf Luxury spa has lower score than Community center, it's working!")