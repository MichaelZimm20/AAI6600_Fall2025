#!/usr/bin/env python3
"""
Random Test File Generator for Group 2 Output

Generates a test.txt file in the same format as Group 2's output.
Deletes old file and creates new one with random category and confidence.
"""

import random
import os
import sys
from pathlib import Path

# =====================================================
# Configuration (Relative Paths)
# =====================================================

# Get paths relative to this script
current_file = Path(__file__).resolve()
current_dir = current_file.parent  # result_of_second_group/
root_dir = current_dir.parent  # Basic framework/

OUTPUT_DIR = current_dir
OUTPUT_FILE = 'test.txt'
OUTPUT_PATH = OUTPUT_DIR / OUTPUT_FILE

# =====================================================
# All 57 Categories
# =====================================================

ALL_CATEGORIES = [
    # Group 3 categories (27)
    'Mental health', 'Mental health support', 'Counseling', 'Counseling support',
    'Psychiatrist', 'Crisis counseling', 'Crisis line', 'Crisis services',
    'Trauma counseling', 'Grief counseling', 'Group therapy', 'Emotional regulation group',
    'Skills group', 'LGBTQ+ counseling', 'Cultural counseling', 'Cultural adjustment counseling',
    'Accessibility counseling', 'Self-care', 'Self-help', 'Wellness support', 'Health',
    'Virtual counseling', 'Directory of free mental health providers', 'Specialist',
    'Parenting support', 'Case management',
    
    # Group 4 categories (6)
    'Support group', 'Peer support', 'Peer support organizations', 'Peer group',
    'Peer mentor', 'LGBTQ+ resource',
    
    # Other categories (24)
    'Academic advising', 'Academic coaching', 'Advising', 'Advisor',
    'Career counseling', 'Career services', 'Campus health', 'Campus wellness',
    'Campus case worker', 'Student services', 'Disability services', 'Disability support office',
    'Financial aid', 'Cultural center', 'Multicultural center', 'International student office',
    'Ethics office', 'STEM mentoring', 'Mentoring', 'Online safety resources', 'Mediation',
    'IPV support services', 'Military student support', 'Case manager',
]

# Sample user inputs
SAMPLE_INPUTS = {
    'Mental health': "I need affordable therapy for my mental health",
    'Crisis counseling': "I'm having a crisis and need urgent help",
    'Trauma counseling': "I need help dealing with past trauma",
    'Support group': "Are there any support groups in my area?",
    'Career services': "I need help with career planning",
    'Self-care': "I want to learn more about self-care techniques",
    'Self-help': "Looking for self-help resources",
}

SCENARIO_NAMES = [
    'ANXIETY', 'DEPRESSION', 'CRISIS', 'HOMESICKNESS', 'STRESS',
    'TRAUMA', 'GRIEF', 'CAREER_ANXIETY', 'CULTURAL_ADJUSTMENT',
    'SOCIAL_ISOLATION', 'BURNOUT', 'RELATIONSHIP_ISSUES'
]

# Import categories from router
try:
    p1_dir = root_dir / "p1"
    if str(p1_dir) not in sys.path:
        sys.path.insert(0, str(p1_dir))
    from group2_router import GROUP3_CATEGORIES, GROUP4_CATEGORIES, OTHER_CATEGORIES
    print("✓ Imported categories from group2_router.py\n")
except ImportError:
    print("⚠️  Using local category definitions\n")
    GROUP3_CATEGORIES = set([c for c in ALL_CATEGORIES[:27]])
    GROUP4_CATEGORIES = set([c for c in ALL_CATEGORIES[27:33]])
    OTHER_CATEGORIES = set([c for c in ALL_CATEGORIES[33:]])

# =====================================================
# Generator Functions
# =====================================================

def generate_random_scenario():
    """Generate a random test scenario"""
    category = random.choice(ALL_CATEGORIES)
    
    if category in ['Mental health', 'Crisis counseling', 'Counseling']:
        confidence = random.uniform(0.75, 0.98)
    else:
        confidence = random.uniform(0.50, 0.90)
    
    scenario_name = random.choice(SCENARIO_NAMES)
    user_input = SAMPLE_INPUTS.get(category, f"Student: I need help with {category.lower()}")
    top_3 = generate_top_3(category, confidence)
    
    if confidence >= 0.80:
        confidence_level = "🟢 High confidence"
    elif confidence >= 0.50:
        confidence_level = "🟡 Medium confidence"
    else:
        confidence_level = "🔴 Low confidence - consider manual review"
    
    return {
        'scenario_name': scenario_name,
        'category': category,
        'confidence': confidence,
        'user_input': user_input,
        'top_3': top_3,
        'confidence_level': confidence_level
    }

def generate_top_3(primary_category, primary_confidence):
    """Generate top 3 recommendations"""
    other_categories = [c for c in ALL_CATEGORIES if c != primary_category]
    alternatives = random.sample(other_categories, min(2, len(other_categories)))
    
    remaining = 1.0 - primary_confidence
    conf_2 = remaining * random.uniform(0.3, 0.7)
    conf_3 = remaining - conf_2
    
    return [
        {'category': primary_category, 'confidence': primary_confidence},
        {'category': alternatives[0], 'confidence': conf_2},
        {'category': alternatives[1] if len(alternatives) > 1 else 'Campus wellness', 'confidence': conf_3}
    ]

def format_confidence_bar(confidence):
    """Generate visual confidence bar"""
    bar_length = int(confidence * 20)
    return '█' * bar_length

def generate_txt_content(scenario):
    """Generate complete TXT file content"""
    lines = [
        "─" * 70,
        f"Sample #1: SCENARIO 1:  - {scenario['scenario_name']} {scenario['user_input'][:50]}...",
        "─" * 70,
        f"🎯 Recommended: {scenario['category']}",
        f"📊 Confidence: {scenario['confidence']*100:.2f}%",
        "📋 Top 3 recommendations:"
    ]
    
    for i, rec in enumerate(scenario['top_3'], 1):
        bar = format_confidence_bar(rec['confidence'])
        lines.append(f"   {i}. {rec['category']:<40} {rec['confidence']*100:>5.2f}% {bar}")
    
    lines.extend(["", f"   {scenario['confidence_level']}"])
    return '\n'.join(lines)

def generate_test_file(output_path=None, category=None, confidence=None):
    """Generate test.txt file"""
    if output_path is None:
        output_path = OUTPUT_PATH
    
    output_dir = Path(output_path).parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    if Path(output_path).exists():
        os.remove(output_path)
        print(f"✓ Deleted old file: {Path(output_path).name}")
    
    scenario = generate_random_scenario()
    
    if category:
        scenario['category'] = category
        scenario['top_3'][0]['category'] = category
    if confidence:
        scenario['confidence'] = confidence
        scenario['top_3'][0]['confidence'] = confidence
        # Update confidence level
        if confidence >= 0.80:
            scenario['confidence_level'] = "🟢 High confidence"
        elif confidence >= 0.50:
            scenario['confidence_level'] = "🟡 Medium confidence"
        else:
            scenario['confidence_level'] = "🔴 Low confidence - consider manual review"
    
    content = generate_txt_content(scenario)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Generated: {Path(output_path).name}")
    print(f"\n{'='*70}")
    print(f"Scenario: {scenario['scenario_name']}")
    print(f"Category: {scenario['category']}")
    print(f"Confidence: {scenario['confidence']:.2%}")
    print(f"{'='*70}\n")
    
    return scenario

# =====================================================
# Main Program
# =====================================================

if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("RANDOM TEST FILE GENERATOR FOR GROUP 2 OUTPUT")
    print("="*70)
    print(f"Output: {OUTPUT_FILE} (in {OUTPUT_DIR.name}/)\n")
    
    print("="*70)
    print("BASIC MODES:")
    print("  1. Random scenario")
    print("  2. Group 4 category")
    print("  3. Other category")
    print("  4. Interactive (custom category + confidence)")
    print()
    print("SYSTEMATIC TESTING (Om's Care Level Logic):")
    print("  5. URGENT + HIGH confidence (>80%)")
    print("  6. URGENT + MEDIUM confidence (50-79%)")
    print("  7. URGENT + LOW confidence (<30%)")
    print()
    print("  8. MODERATE + HIGH confidence (>80%)")
    print("  9. MODERATE + MEDIUM confidence (50-79%)")
    print(" 10. MODERATE + LOW confidence (<30%)")
    print()
    print(" 11. LOW priority + HIGH confidence (>80%)")
    print(" 12. LOW priority + MEDIUM confidence (50-79%)")
    print(" 13. LOW priority + LOW confidence (<50%) [SHOULD STOP]")
    print("="*70)
    
    choice = input("\nSelect (1-13): ").strip()
    
    if choice == '1':
        print("\n[Random]")
        generate_test_file()
    elif choice == '2':
        print("\n[Group 4]")
        cats = ['Support group', 'Peer support']
        generate_test_file(category=random.choice(cats))
    elif choice == '3':
        print("\n[Other]")
        cats = ['Career services', 'Campus health', 'Academic advising']
        generate_test_file(category=random.choice(cats))
    elif choice == '4':
        print("\n[Interactive]")
        cat = input("Category: ").strip()
        conf = float(input("Confidence (0-1): ").strip())
        generate_test_file(category=cat, confidence=conf)
    
    # URGENT tests
    elif choice == '5':
        print("\n[URGENT + HIGH]")
        generate_test_file(category='Crisis counseling', confidence=random.uniform(0.80, 0.98))
        print("✅ Expected: No warnings")
    elif choice == '6':
        print("\n[URGENT + MEDIUM]")
        generate_test_file(category='Crisis counseling', confidence=random.uniform(0.50, 0.79))
        print("✅ Expected: No warnings (urgent overrides)")
    elif choice == '7':
        print("\n[URGENT + LOW]")
        generate_test_file(category='Crisis counseling', confidence=random.uniform(0.10, 0.29))
        print("⚠️ Expected: CRITICAL warning BUT continue")
    
    # MODERATE tests
    elif choice == '8':
        print("\n[MODERATE + HIGH]")
        generate_test_file(category='Mental health', confidence=random.uniform(0.80, 0.98))
        print("✅ Expected: No warnings")
    elif choice == '9':
        print("\n[MODERATE + MEDIUM]")
        generate_test_file(category='Mental health', confidence=random.uniform(0.50, 0.79))
        print("✅ Expected: No warnings")
    elif choice == '10':
        print("\n[MODERATE + LOW]")
        generate_test_file(category='Mental health', confidence=random.uniform(0.10, 0.29))
        print("⚠️⚠️⚠️ Expected: CRITICAL warning BUT continue")
    
    # LOW priority tests
    elif choice == '11':
        print("\n[LOW + HIGH]")
        generate_test_file(category='Self-care', confidence=random.uniform(0.80, 0.98))
        print("✅ Expected: Continue (high confidence overrides)")
    elif choice == '12':
        print("\n[LOW + MEDIUM]")
        generate_test_file(category='Self-help', confidence=random.uniform(0.50, 0.79))
        print("✅ Expected: Continue")
    elif choice == '13':
        print("\n[LOW + LOW] - STOP TEST")
        generate_test_file(category='Self-care', confidence=random.uniform(0.10, 0.49))
        print("❌ Expected: STOP - 'You're doing well!'")
        print("   is_ours = FALSE")
    
    else:
        print("Invalid selection")
        exit(1)
    
    print("\n" + "="*70)
    print("FILE GENERATED!")
    print("="*70)
    print("Run: python main_workflow.py")
    print("="*70 + "\n")
