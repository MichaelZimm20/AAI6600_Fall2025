#!/usr/bin/env python3
"""
Group 2 Output Classification Router
Maps 57 subcategories to corresponding processing branches
"""

# =====================================================
# Branch Mapping Definitions for 57 Categories
# =====================================================

# Group 3 Processing: Affordable Care (requires mental health facility recommendations)
GROUP3_CATEGORIES = {
    # Core mental health services
    'Mental health',
    'Mental health support',
    'Counseling',
    'Counseling support',
    
    # Professional medical services
    'Psychiatrist',
    
    # Crisis-related (requires facility recommendations)
    'Crisis counseling',
    'Crisis line',
    'Crisis services',
    
    # Trauma and grief counseling
    'Trauma counseling',
    'Grief counseling',
    
    # Group therapy
    'Group therapy',
    'Emotional regulation group',
    'Skills group',
    
    # Cultural and identity-related counseling
    'LGBTQ+ counseling',
    'Cultural counseling',
    'Cultural adjustment counseling',
    'Accessibility counseling',
    
    # Self-care and wellness
    'Self-care',
    'Self-help',
    'Wellness support',
    'Health',
    
    # Virtual counseling
    'Virtual counseling',
    
    # Other mental health resources
    'Directory of free mental health providers',
    'Specialist',
    'Parenting support',
}

# Group 4 Processing: Local Events (support groups, community activities)
GROUP4_CATEGORIES = {
    # Support groups
    'Support group',
    
    # Peer support
    'Peer support',
    'Peer support organizations',
    'Peer group',
    'Peer mentor',
    
    # LGBTQ+ resources (if in community activity format)
    'LGBTQ+ resource',
}

# Other Categories: Not within scope of Group 3 or 4
OTHER_CATEGORIES = {
    # Academic-related
    'Academic advising',
    'Academic coaching',
    'Advising',
    'Advisor',
    
    # Career-related
    'Career counseling',
    'Career services',
    
    # Campus services
    'Campus health',
    'Campus wellness',
    'Campus case worker',
    'Student services',
    
    # Disability services
    'Disability services',
    'Disability support office',
    
    # Financial aid
    'Financial aid',
    
    # Cultural centers
    'Cultural center',
    'Multicultural center',
    
    # International students
    'International student office',
    
    # Other campus resources
    'Ethics office',
    'STEM mentoring',
    'Mentoring',
    'Online safety resources',
    'Mediation',
    
    # Special services (require specific referral)
    'IPV support services',
    'Military student support',
    'Case management',
    'Case manager',
}


# =====================================================
# Routing Functions
# =====================================================

def route_category(category, confidence=None):
    """
    Determine which branch to route to based on Group 2's classification result
    
    Args:
        category: str, one of the 57 categories identified by Group 2
        confidence: float, confidence level (0-1)
    
    Returns:
        dict: {
            'branch': 'group3' / 'group4' / 'other',
            'message': message for the user,
            'category': original category,
            'confidence': confidence level,
            'action': action to execute
        }
    """
    
    # Normalize category name (remove extra spaces)
    category = category.strip()
    
    # Determine which branch
    if category in GROUP3_CATEGORIES:
        return {
            'branch': 'group3',
            'message': f'Based on your category [{category}], this is within Affordable Care services. Proceeding to Group 3 process.',
            'category': category,
            'confidence': confidence,
            'action': 'proceed_to_group3'
        }
    
    elif category in GROUP4_CATEGORIES:
        return {
            'branch': 'group4',
            'message': f'Based on your category [{category}], this is within Local Events services. Transferring to Group 4 process.',
            'category': category,
            'confidence': confidence,
            'action': 'transfer_to_group4'
        }
    
    elif category in OTHER_CATEGORIES:
        return {
            'branch': 'other',
            'message': f'Based on your category [{category}], this is currently out of scope. Please return to the previous step and try again.',
            'category': category,
            'confidence': confidence,
            'action': 'return_to_previous_step'
        }
    
    else:
        # Unknown category
        return {
            'branch': 'unknown',
            'message': f'Sorry, unable to recognize category [{category}]. Please rephrase your needs.',
            'category': category,
            'confidence': confidence,
            'action': 'ask_for_clarification'
        }


def process_group2_output(group2_result):
    """
    Process complete output from Group 2
    
    Args:
        group2_result: dict, Group 2's output in format:
        {
            'category': 'Mental health',
            'confidence': 0.95,
            'user_input': 'I need affordable therapy'
        }
    
    Returns:
        dict: routing decision result
    """
    
    category = group2_result.get('category', '')
    confidence = group2_result.get('confidence', None)
    
    routing_decision = route_category(category, confidence)
    
    # Add original input information
    if 'user_input' in group2_result:
        routing_decision['original_input'] = group2_result['user_input']
    
    # Warn if confidence is too low
    if confidence and confidence < 0.5:
        routing_decision['warning'] = f'WARNING: Classification confidence is low ({confidence:.2%}), result may be inaccurate'
    
    return routing_decision


def handle_group2_input(group2_output):
    """
    Main entry function for Group 3
    
    This function should be called in Group 3's main program
    
    Args:
        group2_output: Output from Group 2
        {
            'category': 'Mental health',
            'confidence': 0.92,
            'user_input': '...'  # optional
        }
    
    Returns:
        tuple: (is_ours, decision)
        - is_ours: bool, whether this belongs to Group 3 processing
        - decision: dict, detailed routing decision
    """
    
    decision = process_group2_output(group2_output)
    
    # Determine if it belongs to Group 3
    is_ours = (decision['branch'] == 'group3')
    
    return is_ours, decision


# =====================================================
# Helper Functions
# =====================================================

def get_branch_statistics():
    """
    Get statistics on number of categories in each branch
    """
    stats = {
        'Group 3 (Affordable Care)': len(GROUP3_CATEGORIES),
        'Group 4 (Local Events)': len(GROUP4_CATEGORIES),
        'Other (Out of Scope)': len(OTHER_CATEGORIES),
        'Total': len(GROUP3_CATEGORIES) + len(GROUP4_CATEGORIES) + len(OTHER_CATEGORIES)
    }
    return stats


def print_routing_decision(decision):
    """
    Print routing decision (formatted output)
    """
    print("\n" + "="*70)
    print("ROUTING DECISION RESULT")
    print("="*70)
    
    if decision.get('warning'):
        print(f"\n{decision['warning']}\n")
    
    print(f"Input Category: {decision['category']}")
    if decision.get('confidence'):
        print(f"Confidence: {decision['confidence']:.2%}")
    
    print(f"\nRouting Branch: {decision['branch'].upper()}")
    print(f"\n{decision['message']}")
    
    print(f"\nAction to Execute: {decision['action']}")
    
    if decision.get('original_input'):
        print(f"\nOriginal User Input: {decision['original_input']}")
    
    print("="*70 + "\n")


def get_all_group3_categories():
    """
    Get all categories that Group 3 handles
    
    Returns:
        list: sorted list of category names
    """
    return sorted(list(GROUP3_CATEGORIES))


def is_group3_category(category):
    """
    Quick check if a category belongs to Group 3
    
    Args:
        category: str, category name
    
    Returns:
        bool: True if Group 3 should handle this category
    """
    return category.strip() in GROUP3_CATEGORIES


# =====================================================
# Test Code (if running this file directly)
# =====================================================

if __name__ == "__main__":
    
    print("="*70)
    print("GROUP 2 OUTPUT CLASSIFICATION ROUTER - TEST")
    print("="*70)
    
    # Display statistics
    print("\n[CLASSIFICATION STATISTICS]")
    stats = get_branch_statistics()
    for branch, count in stats.items():
        print(f"  {branch}: {count} categories")
    
    # Test cases
    test_cases = [
        {
            'category': 'Mental health',
            'confidence': 0.95,
            'user_input': 'I need affordable therapy for anxiety'
        },
        {
            'category': 'Crisis counseling',
            'confidence': 0.85,
            'user_input': 'I need urgent help'
        },
        {
            'category': 'Cultural adjustment counseling',
            'confidence': 0.93,
            'user_input': "I'm really missing home"
        },
        {
            'category': 'Support group',
            'confidence': 0.80,
            'user_input': 'Are there any support groups?'
        },
        {
            'category': 'Career services',
            'confidence': 0.70,
            'user_input': 'I need help with my career'
        },
        {
            'category': 'Campus health',
            'confidence': 0.73,
            'user_input': 'I want to see a campus doctor'
        }
    ]
    
    print("\n[TEST CASES]\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- Test {i} ---")
        
        is_ours, decision = handle_group2_input(test_case)
        
        print(f"Category: {test_case['category']}")
        print(f"Confidence: {test_case['confidence']:.2%}")
        print(f"→ Route to: {decision['branch']}")
        print(f"→ Group 3 handles: {'Yes ✓' if is_ours else 'No ✗'}")
        print()
    
    # Display all Group 3 categories
    print("\n" + "="*70)
    print("ALL GROUP 3 CATEGORIES (AFFORDABLE CARE)")
    print("="*70)
    
    categories = get_all_group3_categories()
    for i, cat in enumerate(categories, 1):
        print(f"{i:2d}. {cat}")
    
    print(f"\nTotal: {len(categories)} categories")
    print("="*70)
