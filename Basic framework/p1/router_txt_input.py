#!/usr/bin/env python3
"""
Group 3 TXT Version - Solution 2: Read Single Scenario from TXT File

Reads TXT files provided by Group 2, extracts classification results and processes.

Default file path: ../result_of_second_group/test.txt (relative to this file)
"""

import re
import os
import sys
import subprocess
import json
from pathlib import Path

# Add relative path for group2_router
current_file = Path(__file__).resolve()
current_dir = current_file.parent  # p1/
root_dir = current_dir.parent  # Basic framework/

# Import group2_router from same directory (p1/)
from group2_router import handle_group2_input

# =====================================================
# Configuration (Relative Paths)
# =====================================================

# Default paths relative to Basic framework root
DEFAULT_INPUT_FILE = root_dir / "result_of_second_group" / "test.txt"
OUTPUT_DIR = root_dir / "result_of_second_group"
GROUP3_SCRIPT = root_dir / "p2" / "Group3_script_base_version.py"

# =====================================================
# TXT File Parser
# =====================================================

def parse_group2_txt(filepath):
    """
    Parse Group 2's TXT output file, extract classification results
    """
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {
        'category': None,
        'confidence': None,
        'user_input': None,
        'scenario_name': None
    }
    
    # Extract scenario name
    scenario_match = re.search(r'SCENARIO \d+:\s*-?\s*([A-Z\s\-]+?)(?:Student:|User:|\n)', content)
    if scenario_match:
        result['scenario_name'] = scenario_match.group(1).strip()
    
    # Extract user input
    user_input_match = re.search(r'(?:Student|User):\s*(.+?)(?=\n|─)', content, re.DOTALL)
    if user_input_match:
        result['user_input'] = user_input_match.group(1).strip()[:200]
    
    # Extract recommended category
    category_match = re.search(r'🎯\s*Recommended:\s*(.+?)(?:\n|$)', content)
    if not category_match:
        category_match = re.search(r'Recommended:\s*(.+?)(?:\n|$)', content)
    
    if category_match:
        result['category'] = category_match.group(1).strip()
    else:
        raise ValueError("Cannot find 'Recommended' category in file")
    
    # Extract confidence
    confidence_match = re.search(r'(?:📊\s*)?Confidence:\s*([\d.]+)%', content)
    if confidence_match:
        result['confidence'] = float(confidence_match.group(1)) / 100
    else:
        result['confidence'] = 0.5
    
    return result


# =====================================================
# Information Collection Functions
# =====================================================

def collect_location():
    """Collect location information"""
    print("[LOCATION INFORMATION]")
    print("Please enter your location")
    print("Format: City, State  OR  State only")
    print("Example: Hartford, CT  OR  Connecticut")
    
    location_input = input("\nYour location: ").strip()
    
    if not location_input:
        print("⚠️  No location provided, will search all areas")
        return {}
    
    if ',' in location_input:
        parts = [p.strip() for p in location_input.split(',')]
        return {'city': parts[0], 'state': parts[1] if len(parts) > 1 else ''}
    else:
        return {'state': location_input}


def collect_insurance():
    """Collect insurance information"""
    print("\n[INSURANCE INFORMATION]")
    print("Do you have health insurance?")
    print("1. Medicaid (Medical Assistance)")
    print("2. Medicare (Federal Health Insurance)")
    print("3. Private Insurance")
    print("4. No Insurance")
    
    choice = input("\nSelect (1-4): ").strip()
    
    insurance_map = {
        '1': 'Medicaid',
        '2': 'Medicare',
        '3': 'Private Insurance',
        '4': 'No Insurance'
    }
    
    insurance = insurance_map.get(choice, 'Unknown')
    print(f"✓ Selected: {insurance}")
    
    return insurance


def collect_needs():
    """Collect special needs (fixed version - correctly handles phrases)"""
    print("\n[SPECIAL NEEDS] (Optional)")
    print("Please select your needs (separate multiple with commas):")
    print("  - Anxiety")
    print("  - Depression")
    print("  - Crisis (crisis intervention)")
    print("  - Trauma (trauma treatment)")
    print("  - Addiction (addiction treatment)")
    print("  - Child/Teen (child/adolescent therapy)")
    print("  - Grief (grief counseling)")
    print("  - General Mental Health")
    print("\nOr press Enter to skip")
    
    needs_input = input("\nSpecial needs: ").strip()
    
    if not needs_input:
        return []
    
    # Split by comma first (preserve phrases)
    raw_needs = [n.strip() for n in needs_input.split(',')]
    
    # Normalize keywords
    normalized_needs = []
    
    for need in raw_needs:
        if not need:
            continue
        
        need_lower = need.lower()
        
        # Multi-word phrase matching (priority)
        if 'general' in need_lower and 'mental' in need_lower:
            normalized_needs.append('general_mental_health')
        elif 'mental' in need_lower and 'health' in need_lower:
            normalized_needs.append('mental_health')
        
        # Single word keyword matching
        elif 'anxiety' in need_lower or 'anxious' in need_lower:
            normalized_needs.append('anxiety')
        elif 'depression' in need_lower or 'depressed' in need_lower:
            normalized_needs.append('depression')
        elif 'crisis' in need_lower or 'emergency' in need_lower or 'urgent' in need_lower:
            normalized_needs.append('crisis')
        elif 'trauma' in need_lower or 'ptsd' in need_lower:
            normalized_needs.append('trauma')
        elif 'addiction' in need_lower or 'substance' in need_lower or 'drug' in need_lower:
            normalized_needs.append('addiction')
        elif 'child' in need_lower or 'teen' in need_lower or 'adolescent' in need_lower:
            normalized_needs.append('child')
        elif 'grief' in need_lower or 'loss' in need_lower or 'bereavement' in need_lower:
            normalized_needs.append('grief')
        else:
            # Keep original input (replace spaces with underscores)
            normalized_needs.append(need_lower.replace(' ', '_'))
    
    # Remove duplicates while preserving order
    normalized_needs = list(dict.fromkeys(normalized_needs))
    
    if normalized_needs:
        print(f"✓ Recognized needs: {', '.join(normalized_needs)}")
    
    return normalized_needs


# =====================================================
# Call Actual Group 3 Script
# =====================================================

def call_group3_script(location, insurance, needs):
    """Call actual Group 3 processing script"""
    
    # Check if script exists
    if not GROUP3_SCRIPT.exists():
        print(f"⚠️  Group 3 script not created yet: {GROUP3_SCRIPT}")
        print("Using mock data instead...\n")
        return simulate_facility_search(location, insurance, needs)
    
    try:
        # Prepare input data
        input_data = {
            'location': location,
            'insurance': insurance,
            'needs': needs
        }
        
        # Save to temporary file
        temp_input = OUTPUT_DIR / 'temp_input.json'
        with open(temp_input, 'w', encoding='utf-8') as f:
            json.dump(input_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Prepared input data: {temp_input}")
        print(f"✓ Calling script: {GROUP3_SCRIPT}")
        print("  (Waiting for processing...)\n")
        
        # Call script
        result = subprocess.run(
            ['python', str(GROUP3_SCRIPT), '--input', str(temp_input)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Check execution result
        if result.returncode != 0:
            print(f"✗ Script execution failed:")
            print(result.stderr)
            print("\nUsing mock data instead...\n")
            return simulate_facility_search(location, insurance, needs)
        
        # Read output file
        output_file = OUTPUT_DIR / 'group3_output.json'
        
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                facilities = json.load(f)
            
            print(f"✓ Successfully retrieved {len(facilities)} facilities from Group 3 script\n")
            return facilities
        else:
            print("⚠️  Output file not found, using mock data\n")
            return simulate_facility_search(location, insurance, needs)
    
    except Exception as e:
        print(f"✗ Error calling script: {e}")
        print("Using mock data instead...\n")
        return simulate_facility_search(location, insurance, needs)


def simulate_facility_search(location, insurance, needs):
    """Simulate facility search (Fallback)"""
    
    print("📝 Note: Currently using mock data")
    print("   In production, this would call Group3_script_base_version.py\n")
    
    city = location.get('city', 'Hartford')
    state = location.get('state', 'CT')
    
    mock_facilities = [
        {
            'name': '[MOCK] Community Mental Health Center',
            'address': '123 Main Street',
            'city': city,
            'state': state,
            'zip': '06103',
            'phone': '(860) 123-4567',
            'score': 8.5,
            'affordability_score': 9.2,
            'crisis_care_score': 7.5,
            'accessibility_score': 8.0,
            'specialization_score': 6.5,
            'community_integration_score': 8.0,
            'accepts_insurance': [insurance]
        },
        {
            'name': '[MOCK] City Counseling Services',
            'address': '456 Elm Avenue',
            'city': city,
            'state': state,
            'zip': '06105',
            'phone': '(860) 234-5678',
            'score': 7.8,
            'affordability_score': 8.5,
            'crisis_care_score': 6.0,
            'accessibility_score': 8.5,
            'specialization_score': 7.0,
            'community_integration_score': 7.5,
            'accepts_insurance': [insurance, 'Private Insurance']
        },
        {
            'name': '[MOCK] Affordable Therapy Clinic',
            'address': '789 Oak Road',
            'city': city,
            'state': state,
            'zip': '06106',
            'phone': '(860) 345-6789',
            'score': 8.1,
            'affordability_score': 9.5,
            'crisis_care_score': 5.5,
            'accessibility_score': 7.0,
            'specialization_score': 6.0,
            'community_integration_score': 7.8,
            'accepts_insurance': ['Medicaid', 'Medicare']
        }
    ]
    
    return mock_facilities[:5]


# =====================================================
# Main Processing Function
# =====================================================

def handle_group3_from_txt(input_file=None):
    """Group 3 main processing function - TXT file version"""
    
    if input_file is None:
        input_file = DEFAULT_INPUT_FILE
    
    print("\n" + "="*70)
    print("GROUP 3: AFFORDABLE MENTAL HEALTH FACILITY FINDER (TXT Version)")
    print("="*70 + "\n")
    
    # Step 1: Parse TXT
    print(f"Reading Group 2's output file...")
    print(f"File path: {input_file}\n")
    
    try:
        group2_output = parse_group2_txt(input_file)
        print("✓ Successfully parsed TXT file\n")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        return {'status': 'error', 'message': 'Input file not found'}
    except ValueError as e:
        print(f"✗ Error: {e}")
        return {'status': 'error', 'message': 'Cannot parse TXT file'}
    
    # Display parsed information
    print("Group 2's classification result:")
    if group2_output.get('scenario_name'):
        print(f"  Scenario: {group2_output['scenario_name']}")
    print(f"  Category: {group2_output['category']}")
    print(f"  Confidence: {group2_output['confidence']:.2%}")
    if group2_output.get('user_input'):
        print(f"  User input: {group2_output['user_input'][:60]}...")
    print()
    
    # Step 2: Router decision
    is_ours, decision = handle_group2_input(group2_output)
    
    print(decision['message'])
    print()
    
    # Step 3: Determine if we process
    if not is_ours:
        print(f"→ This category is handled by {decision['branch']}")
        return {
            'status': 'not_handled',
            'branch': decision['branch'],
            'category': group2_output['category'],
            'message': decision['message']
        }
    
    # Step 4: Collect information
    print("Starting to collect necessary information...\n")
    
    location = collect_location()
    insurance = collect_insurance()
    needs = collect_needs()
    
    # Step 5: Call Group 3 script
    print("\n" + "-"*70)
    print("Calling Group 3's facility search script...")
    print("-"*70 + "\n")
    
    facilities = call_group3_script(location, insurance, needs)
    
    # Step 6: Display results
    if not facilities:
        print("Sorry, no facilities found matching your criteria.")
        return {'status': 'no_results'}
    
    display_results(facilities, location, insurance)
    
    return {
        'status': 'success',
        'facilities_count': len(facilities),
        'facilities': facilities[:3],
        'category': group2_output['category'],
        'confidence': group2_output['confidence'],
        'scenario': group2_output.get('scenario_name')
    }


# =====================================================
# Results Display
# =====================================================

def display_results(facilities, location, insurance):
    """Display search results"""
    
    print("="*70)
    print(f"FOUND {len(facilities)} MATCHING FACILITIES")
    print("="*70 + "\n")
    
    location_str = location.get('city', location.get('state', 'your area'))
    
    print(f"📍 Location: {location_str}")
    print(f"💳 Insurance: {insurance}")
    print()
    
    for i, fac in enumerate(facilities, 1):
        print(f"{'─'*70}")
        print(f"{i}. {fac['name']} ⭐ Overall Score: {fac['score']}/10")
        print(f"{'─'*70}")
        
        print(f"📍 Address: {fac['address']}, {fac['city']}, {fac['state']} {fac['zip']}")
        print(f"📞 Phone: {fac['phone']}")
        print(f"💰 Affordability: {fac['affordability_score']}/10")
        print(f"🚨 Crisis Care: {fac['crisis_care_score']}/10")
        print(f"🚶 Accessibility: {fac['accessibility_score']}/10")
        
        if 'specialization_score' in fac:
            print(f"🏥 Specialization: {fac['specialization_score']}/10")
        if 'community_integration_score' in fac:
            print(f"🏘️  Community Integration: {fac['community_integration_score']}/10")
        
        print(f"💳 Accepted Insurance: {', '.join(fac['accepts_insurance'])}")
        print()
    
    print("="*70)
    print("💙 Seeking help is a sign of strength. Take care!")
    print("="*70)


# =====================================================
# Test Functions
# =====================================================

def test_parser():
    """Test TXT parser"""
    
    print("\n" + "="*70)
    print("Test TXT Parser")
    print("="*70 + "\n")
    
    print(f"Parsing file: {DEFAULT_INPUT_FILE}\n")
    
    try:
        result = parse_group2_txt(DEFAULT_INPUT_FILE)
        
        print("✓ Parse successful!\n")
        print("Extracted information:")
        print(f"  Scenario name: {result['scenario_name']}")
        print(f"  Category: {result['category']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        if result['user_input']:
            print(f"  User input: {result['user_input'][:80]}...")
        
        return result
        
    except Exception as e:
        print(f"✗ Parse failed: {e}")
        return None


def test_router_only():
    """Test Router decision only"""
    
    print("\n" + "="*70)
    print("Test Router Decision")
    print("="*70 + "\n")
    
    try:
        group2_output = parse_group2_txt(DEFAULT_INPUT_FILE)
        
        print("Parse result:")
        print(f"  Category: {group2_output['category']}")
        print(f"  Confidence: {group2_output['confidence']:.2%}\n")
        
        is_ours, decision = handle_group2_input(group2_output)
        
        print("="*70)
        print("Router Decision Result:")
        print("="*70)
        print(decision['message'])
        print()
        print(f"Branch: {decision['branch']}")
        print(f"Group 3 handles: {'Yes ✓' if is_ours else 'No ✗'}")
        print(f"Action: {decision['action']}")
        
        if is_ours:
            print("\n→ Next step: Group 3 will collect user info and search facilities")
        elif decision['branch'] == 'group4':
            print("\n→ Next step: Transfer to Group 4 processing")
        else:
            print("\n→ Next step: Return to previous step and retry")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")


# =====================================================
# Main Program
# =====================================================

if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("GROUP 3 TXT VERSION - Read Single Scenario")
    print("="*70)
    print(f"\nInput file: {DEFAULT_INPUT_FILE}")
    
    print("\nSelect mode:")
    print("1. Test TXT parser (parse only, no processing)")
    print("2. Test Router decision (parse + route decision)")
    print("3. Complete workflow (parse + route + collect + search)")
    
    choice = input("\nSelect (1/2/3): ").strip()
    
    if choice == '1':
        test_parser()
    
    elif choice == '2':
        test_router_only()
    
    elif choice == '3':
        print("\n" + "="*70)
        print("Starting complete workflow")
        print("="*70)
        
        result = handle_group3_from_txt(DEFAULT_INPUT_FILE)
        
        print("\n" + "="*70)
        print("Final processing result:")
        print("="*70)
        print(f"Status: {result['status']}")
        if result.get('facilities_count'):
            print(f"Facilities found: {result['facilities_count']}")
        if result.get('category'):
            print(f"Category processed: {result['category']}")
        if result.get('confidence'):
            print(f"Confidence: {result['confidence']:.2%}")
        print("="*70)
    
    else:
        print("Invalid selection")
