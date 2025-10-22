#!/usr/bin/env python3
"""
Random Patient Case Generator

Generates test case files with complete user information for testing Group 3's 
facility recommendation functionality.

Output: patient_case.txt (English only, no JSON)
"""

import random
import os
from pathlib import Path

# =====================================================
# Configuration (Relative Paths)
# =====================================================

# Get paths relative to this script
current_file = Path(__file__).resolve()
current_dir = current_file.parent  # result_of_second_group/

OUTPUT_DIR = current_dir
OUTPUT_FILE = 'patient_case.txt'
OUTPUT_PATH = OUTPUT_DIR / OUTPUT_FILE

# =====================================================
# Data: Random Options
# =====================================================

# US States (focus on states with mental health facilities)
STATES = [
    'Connecticut', 'New York', 'Massachusetts', 'California',
    'Texas', 'Florida', 'Illinois', 'Pennsylvania',
    'Ohio', 'Michigan', 'Georgia', 'North Carolina'
]

# Cities by State
CITIES = {
    'Connecticut': ['Hartford', 'New Haven', 'Stamford', 'Bridgeport', 'Waterbury'],
    'New York': ['New York City', 'Buffalo', 'Rochester', 'Albany', 'Syracuse'],
    'Massachusetts': ['Boston', 'Worcester', 'Springfield', 'Cambridge', 'Lowell'],
    'California': ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento', 'Oakland'],
    'Texas': ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth'],
    'Florida': ['Miami', 'Orlando', 'Tampa', 'Jacksonville', 'Fort Lauderdale'],
}

# Insurance Types
INSURANCE_TYPES = ['Medicaid', 'Medicare', 'Private Insurance', 'No Insurance']

# Mental Health Needs
MENTAL_HEALTH_NEEDS = [
    'anxiety',
    'depression',
    'crisis',
    'trauma',
    'PTSD',
    'grief',
    'addiction',
    'eating disorder',
    'bipolar',
    'OCD',
    'panic disorder',
    'social anxiety',
    'general mental health'
]

# Age Groups
AGE_GROUPS = ['18-25', '26-35', '36-50', '51-65', '65+']

# Urgency Levels
URGENCY_LEVELS = ['routine', 'urgent', 'crisis']

# Preferences
PREFERENCES = [
    'in-person only',
    'telehealth preferred',
    'evening/weekend hours',
    'LGBTQ+ affirming',
    'culturally sensitive',
    'Spanish speaking',
    'child-friendly',
    'accepts walk-ins'
]

# Background Story Templates
BACKGROUND_STORIES = [
    "I've been feeling overwhelmed lately and think I need professional help.",
    "I'm struggling with my mental health and looking for affordable options.",
    "I recently moved to the area and need to find a new therapist.",
    "I've been experiencing symptoms that are affecting my daily life.",
    "I'm a student on a tight budget looking for low-cost mental health services.",
    "I need help but don't have much money for expensive therapy.",
    "I'm looking for a therapist who accepts my insurance.",
    "I want to start therapy but not sure where to begin.",
]

# =====================================================
# Generation Functions
# =====================================================

def generate_random_patient_case():
    """
    Generate a random patient case
    
    Returns:
        dict: Complete patient information
    """
    
    # Random state and city
    state = random.choice(STATES)
    city = random.choice(CITIES.get(state, ['Unknown City']))
    
    # Random insurance
    insurance = random.choice(INSURANCE_TYPES)
    
    # Random 1-3 needs
    num_needs = random.randint(1, 3)
    needs = random.sample(MENTAL_HEALTH_NEEDS, num_needs)
    
    # Random urgency
    urgency = random.choice(URGENCY_LEVELS)
    
    # Random age group
    age_group = random.choice(AGE_GROUPS)
    
    # Random preferences (0-2)
    num_prefs = random.randint(0, 2)
    preferences = random.sample(PREFERENCES, num_prefs) if num_prefs > 0 else []
    
    # Random background story
    background = random.choice(BACKGROUND_STORIES)
    
    # Generate case ID
    case_id = f"CASE_{random.randint(1000, 9999)}"
    
    patient_case = {
        'case_id': case_id,
        'location': {
            'city': city,
            'state': state
        },
        'insurance': insurance,
        'needs': needs,
        'urgency': urgency,
        'age_group': age_group,
        'preferences': preferences,
        'background': background
    }
    
    return patient_case


def format_patient_case_txt(case):
    """
    Format as TXT
    
    Args:
        case: Patient case dict
    
    Returns:
        str: Formatted TXT content
    """
    
    lines = []
    
    lines.append("="*70)
    lines.append("PATIENT CASE FILE")
    lines.append("="*70)
    lines.append("")
    
    # Case ID
    lines.append(f"Case ID: {case['case_id']}")
    lines.append("")
    
    # Location
    lines.append("-"*70)
    lines.append("LOCATION INFORMATION")
    lines.append("-"*70)
    lines.append(f"City:  {case['location']['city']}")
    lines.append(f"State: {case['location']['state']}")
    lines.append("")
    
    # Insurance
    lines.append("-"*70)
    lines.append("INSURANCE INFORMATION")
    lines.append("-"*70)
    lines.append(f"Insurance Type: {case['insurance']}")
    lines.append("")
    
    # Needs
    lines.append("-"*70)
    lines.append("MENTAL HEALTH NEEDS")
    lines.append("-"*70)
    for i, need in enumerate(case['needs'], 1):
        lines.append(f"  {i}. {need.title()}")
    lines.append("")
    
    # Urgency
    lines.append("-"*70)
    lines.append("URGENCY LEVEL")
    lines.append("-"*70)
    lines.append(f"Level: {case['urgency'].upper()}")
    
    if case['urgency'] == 'crisis':
        lines.append("WARNING: CRISIS - Requires immediate attention!")
    elif case['urgency'] == 'urgent':
        lines.append("NOTE: URGENT - Should be seen within 1-2 weeks")
    else:
        lines.append("INFO: ROUTINE - Standard appointment scheduling")
    lines.append("")
    
    # Demographics
    lines.append("-"*70)
    lines.append("DEMOGRAPHICS")
    lines.append("-"*70)
    lines.append(f"Age Group: {case['age_group']}")
    lines.append("")
    
    # Preferences
    if case['preferences']:
        lines.append("-"*70)
        lines.append("PREFERENCES")
        lines.append("-"*70)
        for i, pref in enumerate(case['preferences'], 1):
            lines.append(f"  {i}. {pref}")
        lines.append("")
    
    # Background
    lines.append("-"*70)
    lines.append("BACKGROUND / PATIENT STATEMENT")
    lines.append("-"*70)
    lines.append(f'"{case["background"]}"')
    lines.append("")
    
    # Footer
    lines.append("="*70)
    lines.append("END OF CASE FILE")
    lines.append("="*70)
    
    return '\n'.join(lines)


# =====================================================
# File Generation
# =====================================================

def generate_patient_file(output_path=None):
    """
    Generate patient case file
    
    Args:
        output_path: TXT file save path (default: OUTPUT_PATH)
    
    Returns:
        dict: Generated patient case
    """
    
    if output_path is None:
        output_path = OUTPUT_PATH
    
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        print(f"✓ Created directory: {output_dir.name}")
    
    # Delete old file if exists
    if Path(output_path).exists():
        os.remove(output_path)
        print(f"✓ Deleted old file: {Path(output_path).name}")
    
    # Generate random case
    case = generate_random_patient_case()
    
    # Format as TXT
    txt_content = format_patient_case_txt(case)
    
    # Save TXT file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    
    print(f"✓ Generated new file: {Path(output_path).name}")
    print()
    
    # Display case summary
    print("="*70)
    print("Generated Patient Case:")
    print("="*70)
    print(f"Case ID: {case['case_id']}")
    print(f"Location: {case['location']['city']}, {case['location']['state']}")
    print(f"Insurance: {case['insurance']}")
    print(f"Needs: {', '.join(case['needs'])}")
    print(f"Urgency: {case['urgency']}")
    print("="*70 + "\n")
    
    return case


def generate_specific_case(city=None, state=None, insurance=None, needs=None, urgency=None):
    """
    Generate patient case with specified parameters
    """
    
    case = generate_random_patient_case()
    
    # Override specified parameters
    if city:
        case['location']['city'] = city
    if state:
        case['location']['state'] = state
    if insurance:
        case['insurance'] = insurance
    if needs:
        case['needs'] = needs if isinstance(needs, list) else [needs]
    if urgency:
        case['urgency'] = urgency
    
    # Format and save
    txt_content = format_patient_case_txt(case)
    
    # Delete old file
    if OUTPUT_PATH.exists():
        os.remove(OUTPUT_PATH)
    
    # Save new file
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    
    print(f"✓ Generated specified case: {OUTPUT_PATH.name}\n")
    
    return case


# =====================================================
# Preset Case Templates
# =====================================================

def generate_preset_cases():
    """
    Generate preset typical cases
    """
    
    presets = {
        '1': {
            'name': 'Medicaid Patient - Hartford',
            'city': 'Hartford',
            'state': 'Connecticut',
            'insurance': 'Medicaid',
            'needs': ['anxiety', 'depression'],
            'urgency': 'routine'
        },
        '2': {
            'name': 'Crisis Situation - New York',
            'city': 'New York City',
            'state': 'New York',
            'insurance': 'No Insurance',
            'needs': ['crisis'],
            'urgency': 'crisis'
        },
        '3': {
            'name': 'Medicare Patient - Boston',
            'city': 'Boston',
            'state': 'Massachusetts',
            'insurance': 'Medicare',
            'needs': ['grief', 'depression'],
            'urgency': 'urgent'
        },
        '4': {
            'name': 'Child Therapy - Los Angeles',
            'city': 'Los Angeles',
            'state': 'California',
            'insurance': 'Private Insurance',
            'needs': ['anxiety'],
            'urgency': 'routine'
        },
        '5': {
            'name': 'Trauma Treatment - Chicago',
            'city': 'Chicago',
            'state': 'Illinois',
            'insurance': 'Medicaid',
            'needs': ['trauma', 'PTSD'],
            'urgency': 'urgent'
        }
    }
    
    print("\nPreset Cases:")
    for key, preset in presets.items():
        print(f"{key}. {preset['name']}")
    
    choice = input("\nSelect preset case (1-5): ").strip()
    
    if choice in presets:
        preset = presets[choice]
        print(f"\nGenerating case: {preset['name']}\n")
        
        return generate_specific_case(
            city=preset['city'],
            state=preset['state'],
            insurance=preset['insurance'],
            needs=preset['needs'],
            urgency=preset['urgency']
        )
    else:
        print("Invalid selection, generating random case")
        return generate_patient_file()


# =====================================================
# Interactive Case Builder
# =====================================================

def interactive_case_builder():
    """
    Interactive patient case builder
    """
    
    print("\n" + "="*70)
    print("Interactive Case Builder")
    print("="*70 + "\n")
    
    case = {
        'case_id': f"CASE_{random.randint(1000, 9999)}",
        'location': {},
        'insurance': None,
        'needs': [],
        'urgency': 'routine',
        'age_group': '18-25',
        'preferences': [],
        'background': ''
    }
    
    # Collect location
    print("[LOCATION]")
    state = input("State (e.g., Connecticut): ").strip()
    city = input("City (e.g., Hartford): ").strip()
    
    case['location']['state'] = state if state else random.choice(STATES)
    case['location']['city'] = city if city else 'Unknown City'
    
    # Collect insurance
    print("\n[INSURANCE]")
    print("1. Medicaid")
    print("2. Medicare")
    print("3. Private Insurance")
    print("4. No Insurance")
    insurance_choice = input("Select insurance type (1-4): ").strip()
    
    insurance_map = {
        '1': 'Medicaid',
        '2': 'Medicare',
        '3': 'Private Insurance',
        '4': 'No Insurance'
    }
    
    case['insurance'] = insurance_map.get(insurance_choice, 'No Insurance')
    
    # Collect needs
    print("\n[NEEDS]")
    print("Options: anxiety, depression, crisis, trauma, PTSD, addiction, etc.")
    needs_input = input("Enter needs (comma-separated): ").strip()
    
    if needs_input:
        case['needs'] = [n.strip() for n in needs_input.split(',')]
    else:
        case['needs'] = random.sample(MENTAL_HEALTH_NEEDS, random.randint(1, 2))
    
    # Urgency level
    print("\n[URGENCY LEVEL]")
    print("1. Routine")
    print("2. Urgent")
    print("3. Crisis")
    urgency_choice = input("Select urgency level (1-3): ").strip()
    
    urgency_map = {'1': 'routine', '2': 'urgent', '3': 'crisis'}
    case['urgency'] = urgency_map.get(urgency_choice, 'routine')
    
    # Background
    case['background'] = random.choice(BACKGROUND_STORIES)
    
    # Generate file
    txt_content = format_patient_case_txt(case)
    
    # Delete old file
    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)
    
    # Save
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    
    print(f"\n✓ Case generated: {OUTPUT_PATH}\n")
    
    return case


# =====================================================
# Main Program
# =====================================================

if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("Patient Case File Generator")
    print("="*70)
    print(f"\nOutput path: {OUTPUT_PATH}")
    
    print("\nSelect mode:")
    print("1. Generate completely random case")
    print("2. Use preset case template")
    print("3. Interactive case builder")
    print("4. Batch generate multiple cases (for testing)")
    
    choice = input("\nSelect (1-4): ").strip()
    
    if choice == '1':
        # Completely random
        print("\nGenerating random patient case...\n")
        case = generate_patient_file()
        
    elif choice == '2':
        # Preset cases
        case = generate_preset_cases()
        
    elif choice == '3':
        # Interactive
        case = interactive_case_builder()
        
    elif choice == '4':
        # Batch generation
        num = input("\nHow many cases to generate? (1-10): ").strip()
        try:
            num = int(num)
            if 1 <= num <= 10:
                print(f"\nGenerating {num} random cases...\n")
                
                for i in range(num):
                    case_file = OUTPUT_PATH.replace('.txt', f'_{i+1}.txt')
                    
                    # Delete old file
                    if os.path.exists(case_file):
                        os.remove(case_file)
                    
                    # Generate case
                    case = generate_random_patient_case()
                    txt_content = format_patient_case_txt(case)
                    
                    # Save
                    with open(case_file, 'w', encoding='utf-8') as f:
                        f.write(txt_content)
                    
                    print(f"✓ Generated case {i+1}: {case['case_id']} - {case['location']['city']}, {case['location']['state']}")
                
                print(f"\nAll cases saved to: {OUTPUT_DIR}")
            else:
                print("Number out of range")
        except ValueError:
            print("Invalid input")
    
    else:
        print("Invalid selection")
        exit(1)
    
    print("\n" + "="*70)
    print("Complete!")
    print("="*70)
    print("\nYou can now test your Group 3 system:")
    print("  python router_txt_input.py")
    print("\nOr directly load this case to search for facilities.")
    print("="*70 + "\n")
