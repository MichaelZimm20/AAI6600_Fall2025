#!/usr/bin/env python3
"""
Group 2 Output Classification Router
Maps 57 subcategories to corresponding processing branches
Includes Om's Care Level Logic for confidence-based decision making
"""

# =====================================================
# Care Level Definitions (Om's Logic)
# =====================================================

# Urgent categories - always continue even with low confidence
URGENT_CATEGORIES = {
    'Crisis counseling',
    'Crisis line',
    'Crisis services',
    'IPV support services',
    'Trauma counseling',
}

# Moderate categories - continue if confidence >= 30%
MODERATE_CATEGORIES = {
    'Mental health',
    'Mental health support',
    'Counseling',
    'Counseling support',
    'Psychiatrist',
    'Grief counseling',
    'Group therapy',
    'Emotional regulation group',
    'Skills group',
    'LGBTQ+ counseling',
    'Cultural counseling',
    'Cultural adjustment counseling',
    'Accessibility counseling',
    'Wellness support',
    'Health',
    'Virtual counseling',
    'Directory of free mental health providers',
    'Specialist',
    'Parenting support',
    'Case management',
}

# Low priority categories - stop if confidence < 50%
LOW_PRIORITY_CATEGORIES = {
    'Self-care',
    'Self-help',
}


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
    'Case management',
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
        dict: routing decision
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
        group2_result: dict, Group 2's output
    
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
    Main entry function for Group 3 (with Om's Care Level Logic)
    
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
    
    confidence = group2_output.get('confidence', None)
    category = group2_output.get('category', '').strip()
    
    # Om's Care Level Logic: Check urgency level first
    care_level = None
    if category in URGENT_CATEGORIES:
        care_level = 'URGENT'
    elif category in MODERATE_CATEGORIES:
        care_level = 'MODERATE'
    elif category in LOW_PRIORITY_CATEGORIES:
        care_level = 'LOW'
    
    # Low priority + Low confidence = Stop execution ("You're fine")
    if care_level == 'LOW' and confidence and confidence < 0.50:
        decision = {
            'branch': 'no_care_needed',
            'message': f"Based on your input, you're doing well! The assessment suggests {category.lower()}, which you can explore on your own. No immediate professional support needed.",
            'category': category,
            'confidence': confidence,
            'action': 'stop_execution',
            'care_level': care_level
        }
        return False, decision  # Stop - person doesn't need care
    
    # Process normal routing based on category
    decision = process_group2_output(group2_output)
    decision['care_level'] = care_level
    is_ours = (decision['branch'] == 'group3')
    
    # Add confidence-based warnings (but don't stop for Group 3 categories)
    if confidence and confidence < 0.30:
        # Very low confidence - critical warning
        decision['confidence_warning'] = 'CRITICAL'
        decision['warning'] = f'⚠️ CRITICAL: Very low confidence ({confidence:.2%}). Manual review strongly recommended before proceeding.'
        decision['requires_manual_review'] = True
        
        # Override message to show critical warning
        if care_level != 'URGENT':
            decision['message'] += f'\n⚠️⚠️⚠️ CRITICAL WARNING: Confidence only {confidence:.2%}. Consider manual review.'
    
    elif confidence and confidence < 0.50:
        # Low confidence - requires confirmation
        decision['confidence_warning'] = 'LOW'
        decision['requires_confirmation'] = True
        decision['message'] += f' [Low confidence ({confidence:.2%}) - please confirm before proceeding]'
    
    return is_ours, decision


# =====================================================
# Helper Functions
# =====================================================

def get_branch_statistics():
    """Get statistics on number of categories in each branch"""
    stats = {
        'Group 3 (Affordable Care)': len(GROUP3_CATEGORIES),
        'Group 4 (Local Events)': len(GROUP4_CATEGORIES),
        'Other (Out of Scope)': len(OTHER_CATEGORIES),
        'Total': len(GROUP3_CATEGORIES) + len(GROUP4_CATEGORIES) + len(OTHER_CATEGORIES)
    }
    return stats


def print_routing_decision(decision):
    """Print routing decision (formatted output)"""
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
    """Get all categories that Group 3 handles"""
    return sorted(list(GROUP3_CATEGORIES))


def is_group3_category(category):
    """Quick check if a category belongs to Group 3"""
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
            'category': 'Self-care',
            'confidence': 0.40,
            'user_input': 'I want to learn self-care'
        },
        {
            'category': 'Mental health',
            'confidence': 0.25,
            'user_input': 'Feeling a bit stressed'
        },
    ]
    
    print("\n[TEST CASES]\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- Test {i} ---")
        
        is_ours, decision = handle_group2_input(test_case)
        
        print(f"Category: {test_case['category']}")
        print(f"Confidence: {test_case['confidence']:.2%}")
        print(f"→ Route to: {decision['branch']}")
        print(f"→ Group 3 handles: {'Yes ✓' if is_ours else 'No ✗'}")
        if decision.get('care_level'):
            print(f"→ Care Level: {decision['care_level']}")
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
