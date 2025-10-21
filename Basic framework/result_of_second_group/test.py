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
    'Mental health',
    'Mental health support',
    'Counseling',
    'Counseling support',
    'Psychiatrist',
    'Crisis counseling',
    'Crisis line',
    'Crisis services',
    'Trauma counseling',
    'Grief counseling',
    'Group therapy',
    'Emotional regulation group',
    'Skills group',
    'LGBTQ+ counseling',
    'Cultural counseling',
    'Cultural adjustment counseling',
    'Accessibility counseling',
    'Self-care',
    'Self-help',
    'Wellness support',
    'Health',
    'Virtual counseling',
    'Directory of free mental health providers',
    'Specialist',
    'Parenting support',
    'Case management',
    
    # Group 4 categories (6)
    'Support group',
    'Peer support',
    'Peer support organizations',
    'Peer group',
    'Peer mentor',
    'LGBTQ+ resource',
    
    # Other categories (24)
    'Academic advising',
    'Academic coaching',
    'Advising',
    'Advisor',
    'Career counseling',
    'Career services',
    'Campus health',
    'Campus wellness',
    'Campus case worker',
    'Student services',
    'Disability services',
    'Disability support office',
    'Financial aid',
    'Cultural center',
    'Multicultural center',
    'International student office',
    'Ethics office',
    'STEM mentoring',
    'Mentoring',
    'Online safety resources',
    'Mediation',
    'IPV support services',
    'Military student support',
    'Case manager',
]

# Sample user inputs for different scenarios
SAMPLE_INPUTS = {
    'Mental health': "I need affordable therapy for my mental health",
    'Crisis counseling': "I'm having a crisis and need urgent help",
    'Trauma counseling': "I need help dealing with past trauma",
    'Support group': "Are there any support groups in my area?",
    'Career services': "I need help with career planning",
    'Campus health': "I want to visit the campus health center",
    'Cultural adjustment counseling': "I'm having trouble adjusting to a new culture",
    'LGBTQ+ counseling': "I need LGBTQ-affirming therapy",
    'Grief counseling': "I'm struggling with grief and loss",
    'Anxiety counseling': "I have severe anxiety and panic attacks",
}

SCENARIO_NAMES = [
    'ANXIETY', 'DEPRESSION', 'CRISIS', 'HOMESICKNESS', 'STRESS',
    'TRAUMA', 'GRIEF', 'CAREER_ANXIETY', 'CULTURAL_ADJUSTMENT',
    'SOCIAL_ISOLATION', 'BURNOUT', 'RELATIONSHIP_ISSUES'
]

# =====================================================
# Generator Functions
# =====================================================

def generate_random_scenario():
    """
    Generate a random test scenario
    
    Returns:
        dict: {
            'scenario_name': 'ANXIETY',
            'category': 'Mental health',
            'confidence': 0.92,
            'user_input': 'I need therapy...',
            'top_3': [...]
        }
    """
    
    # Random category
    category = random.choice(ALL_CATEGORIES)
    
    # Random confidence (higher for Group 3 categories)
    if category in ['Mental health', 'Crisis counseling', 'Counseling']:
        confidence = random.uniform(0.75, 0.98)
    else:
        confidence = random.uniform(0.50, 0.90)
    
    # Random scenario name
    scenario_name = random.choice(SCENARIO_NAMES)
    
    # Get or generate user input
    user_input = SAMPLE_INPUTS.get(category, f"Student: I need help with {category.lower()}")
    
    # Generate top 3 recommendations
    top_3 = generate_top_3(category, confidence)
    
    # Confidence level indicator
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
    """
    Generate top 3 recommendations with decreasing confidence
    """
    
    # Select 2 other random categories as alternatives
    other_categories = [c for c in ALL_CATEGORIES if c != primary_category]
    alternatives = random.sample(other_categories, min(2, len(other_categories)))
    
    # Calculate alternative confidences
    remaining = 1.0 - primary_confidence
    conf_2 = remaining * random.uniform(0.3, 0.7)
    conf_3 = remaining - conf_2
    
    top_3 = [
        {'category': primary_category, 'confidence': primary_confidence},
        {'category': alternatives[0], 'confidence': conf_2},
        {'category': alternatives[1] if len(alternatives) > 1 else 'Campus wellness', 
         'confidence': conf_3}
    ]
    
    return top_3


def format_confidence_bar(confidence):
    """
    Generate a visual confidence bar
    """
    bar_length = int(confidence * 20)  # Max 20 characters
    return '█' * bar_length


def generate_txt_content(scenario):
    """
    Generate the complete TXT file content
    
    Parameters:
        scenario: dict from generate_random_scenario()
    
    Returns:
        str: formatted TXT content
    """
    
    lines = []
    
    # Header line
    lines.append("─" * 70)
    
    # Scenario header
    lines.append(f"Sample #1: SCENARIO 1:  - {scenario['scenario_name']} {scenario['user_input'][:50]}...")
    
    # Separator
    lines.append("─" * 70)
    
    # Recommended category
    lines.append(f"🎯 Recommended: {scenario['category']}")
    
    # Confidence
    lines.append(f"📊 Confidence: {scenario['confidence']*100:.2f}%")
    
    # Top 3 recommendations
    lines.append("📋 Top 3 recommendations:")
    
    for i, rec in enumerate(scenario['top_3'], 1):
        bar = format_confidence_bar(rec['confidence'])
        lines.append(f"   {i}. {rec['category']:<40} {rec['confidence']*100:>5.2f}% {bar}")
    
    # Blank line
    lines.append("")
    
    # Confidence level indicator
    lines.append(f"   {scenario['confidence_level']}")
    
    return '\n'.join(lines)


# =====================================================
# Main Function
# =====================================================

def generate_test_file(output_path=None, category=None, confidence=None):
    """
    Generate a random test.txt file
    
    Parameters:
        output_path: where to save the file (default: OUTPUT_PATH)
        category: if specified, use this category instead of random
        confidence: if specified, use this confidence instead of random
    
    Returns:
        dict: the generated scenario
    """
    
    if output_path is None:
        output_path = OUTPUT_PATH
    
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        print(f"✓ Created directory: {output_dir}")
    
    # Delete old file if exists
    if Path(output_path).exists():
        os.remove(output_path)
        print(f"✓ Deleted old file: {Path(output_path).name}")
    
    # Generate random scenario
    scenario = generate_random_scenario()
    
    # Override if specified
    if category:
        scenario['category'] = category
        scenario['top_3'][0]['category'] = category
    
    if confidence:
        scenario['confidence'] = confidence
        scenario['top_3'][0]['confidence'] = confidence
    
    # Generate content
    content = generate_txt_content(scenario)
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Generated new file: {Path(output_path).name}\n")
    
    # Display what was generated
    print("="*70)
    print("GENERATED SCENARIO:")
    print("="*70)
    print(f"Scenario: {scenario['scenario_name']}")
    print(f"Category: {scenario['category']}")
    print(f"Confidence: {scenario['confidence']:.2%}")
    print(f"User input: {scenario['user_input'][:60]}...")
    print("="*70 + "\n")
    
    return scenario


def generate_specific_category(category_name):
    """
    Generate test file with a specific category
    """
    
    if category_name not in ALL_CATEGORIES:
        print(f"⚠️  Warning: '{category_name}' not in the 57 categories list")
        print("Proceeding anyway...\n")
    
    return generate_test_file(category=category_name)


def interactive_mode():
    """
    Interactive mode to select what to generate
    """
    
    print("\n" + "="*70)
    print("INTERACTIVE TEST FILE GENERATOR")
    print("="*70)
    
    print("\nOptions:")
    print("1. Generate completely random scenario")
    print("2. Choose specific category from Group 3 (27 categories)")
    print("3. Choose specific category from Group 4 (6 categories)")
    print("4. Choose specific category from Other (24 categories)")
    print("5. Enter custom category")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == '1':
        # Completely random
        generate_test_file()
    
    elif choice == '2':
        # Group 3 category
        print("\nGroup 3 categories:")
        group3_list = sorted(list(GROUP3_CATEGORIES))
        for i, cat in enumerate(group3_list, 1):
            print(f"{i:2d}. {cat}")
        
        cat_choice = input(f"\nSelect category (1-{len(group3_list)}): ").strip()
        try:
            idx = int(cat_choice) - 1
            if 0 <= idx < len(group3_list):
                generate_test_file(category=group3_list[idx])
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
    
    elif choice == '3':
        # Group 4 category
        print("\nGroup 4 categories:")
        group4_list = sorted(list(GROUP4_CATEGORIES))
        for i, cat in enumerate(group4_list, 1):
            print(f"{i}. {cat}")
        
        cat_choice = input(f"\nSelect category (1-{len(group4_list)}): ").strip()
        try:
            idx = int(cat_choice) - 1
            if 0 <= idx < len(group4_list):
                generate_test_file(category=group4_list[idx])
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
    
    elif choice == '4':
        # Other category
        print("\nOther categories:")
        other_list = sorted(list(OTHER_CATEGORIES))
        for i, cat in enumerate(other_list[:10], 1):  # Show first 10
            print(f"{i:2d}. {cat}")
        print("... (24 total)")
        
        cat_choice = input(f"\nEnter category number or name: ").strip()
        
        try:
            if cat_choice.isdigit():
                idx = int(cat_choice) - 1
                if 0 <= idx < len(other_list):
                    generate_test_file(category=other_list[idx])
                else:
                    print("Invalid selection")
            else:
                generate_test_file(category=cat_choice)
        except:
            print("Invalid input")
    
    elif choice == '5':
        # Custom category
        custom = input("\nEnter custom category name: ").strip()
        generate_test_file(category=custom)
    
    else:
        print("Invalid selection")


# =====================================================
# Quick Test Presets
# =====================================================

def generate_group3_test():
    """Generate a test file with Group 3 category"""
    categories = ['Mental health', 'Crisis counseling', 'Trauma counseling']
    return generate_test_file(category=random.choice(categories))


def generate_group4_test():
    """Generate a test file with Group 4 category"""
    categories = ['Support group', 'Peer support']
    return generate_test_file(category=random.choice(categories))


def generate_other_test():
    """Generate a test file with Other category"""
    categories = ['Career services', 'Campus health', 'Academic advising']
    return generate_test_file(category=random.choice(categories))


# =====================================================
# Import GROUP3/4/OTHER from router if needed
# =====================================================

# If group2_router.py exists, import from there
try:
    # Add p1 folder to path
    p1_dir = root_dir / "p1"
    if str(p1_dir) not in sys.path:
        sys.path.insert(0, str(p1_dir))
    
    from group2_router import GROUP3_CATEGORIES, GROUP4_CATEGORIES, OTHER_CATEGORIES
    print("✓ Imported categories from group2_router.py")
except ImportError:
    print("⚠️  Could not import from group2_router.py, using local definitions")
    
    GROUP3_CATEGORIES = {
        'Mental health', 'Mental health support', 'Counseling',
        'Counseling support', 'Psychiatrist', 'Crisis counseling',
        'Crisis line', 'Crisis services', 'Trauma counseling',
        'Grief counseling', 'Group therapy', 'Emotional regulation group',
        'Skills group', 'LGBTQ+ counseling', 'Cultural counseling',
        'Cultural adjustment counseling', 'Accessibility counseling',
        'Self-care', 'Self-help', 'Wellness support', 'Health',
        'Virtual counseling', 'Directory of free mental health providers',
        'Specialist', 'Parenting support', 'Case management'
    }
    
    GROUP4_CATEGORIES = {
        'Support group', 'Peer support', 'Peer support organizations',
        'Peer group', 'Peer mentor', 'LGBTQ+ resource'
    }
    
    OTHER_CATEGORIES = {
        'Academic advising', 'Academic coaching', 'Advising', 'Advisor',
        'Career counseling', 'Career services', 'Campus health',
        'Campus wellness', 'Campus case worker', 'Student services',
        'Disability services', 'Disability support office', 'Financial aid',
        'Cultural center', 'Multicultural center', 'International student office',
        'Ethics office', 'STEM mentoring', 'Mentoring', 'Online safety resources',
        'Mediation', 'IPV support services', 'Military student support',
        'Case manager'
    }


# =====================================================
# Main Program
# =====================================================

if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("RANDOM TEST FILE GENERATOR FOR GROUP 2 OUTPUT")
    print("="*70)
    print(f"\nOutput location: {OUTPUT_FILE} (in {OUTPUT_DIR.name}/)")
    
    print("\nSelect mode:")
    print("1. Generate completely random scenario")
    print("2. Generate Group 3 category (Mental health, Crisis, etc.)")
    print("3. Generate Group 4 category (Support group, Peer support)")
    print("4. Generate Other category (Career, Campus, etc.)")
    print("5. Interactive mode (choose specific category)")
    
    choice = input("\nSelect (1-5): ").strip()
    
    if choice == '1':
        # Completely random
        print("\nGenerating random scenario...\n")
        generate_test_file()
    
    elif choice == '2':
        # Group 3 category
        print("\nGenerating Group 3 category scenario...\n")
        generate_group3_test()
    
    elif choice == '3':
        # Group 4 category
        print("\nGenerating Group 4 category scenario...\n")
        generate_group4_test()
    
    elif choice == '4':
        # Other category
        print("\nGenerating Other category scenario...\n")
        generate_other_test()
    
    elif choice == '5':
        # Interactive
        interactive_mode()
    
    else:
        print("Invalid selection")
        exit(1)
    
    print("\n" + "="*70)
    print("FILE GENERATED SUCCESSFULLY!")
    print("="*70)
    print(f"\nYou can now run:")
    print(f"  python main_workflow.py")
    print(f"\nto process this test file.")
    print("="*70 + "\n")
