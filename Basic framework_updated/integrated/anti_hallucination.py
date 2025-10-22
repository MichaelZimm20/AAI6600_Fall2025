#!/usr/bin/env python3
"""
Anti-Hallucination Validation Module

This module prevents unreliable or fabricated facility recommendations by:
1. Validating scoring reliability based on semantic similarity
2. Flagging low-confidence results with clear warnings
3. Adding data source traceability for transparency
4. Providing comprehensive warning reports and disclaimers

Usage:
    from anti_hallucination import AntiHallucinationValidator
    
    validator = AntiHallucinationValidator()
    validated = validator.validate_results(facilities)
    print(validator.generate_warning_report(validated))

Requirements:
    - pandas
    - numpy
    
Note: This module works independently and has no absolute path dependencies.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class AntiHallucinationValidator:
    """Anti-Hallucination Validator"""
    
    # Confidence thresholds
    CONFIDENCE_THRESHOLDS = {
        'high': 0.70,      # High confidence: similarity > 0.70
        'medium': 0.50,    # Medium confidence: 0.50-0.70
        'low': 0.30        # Low confidence: < 0.50
    }
    
    # Score reasonability thresholds
    SCORE_THRESHOLDS = {
        'suspiciously_high': 9.5,  # Suspiciously high score
        'suspiciously_low': 2.0    # Suspiciously low score
    }
    
    def __init__(self):
        """Initialize validator"""
        self.validation_warnings = []
    
    def validate_facility(self, facility: Dict) -> Dict:
        """
        Validate reliability of a single facility
        
        Args:
            facility: facility dictionary
        
        Returns:
            facility dictionary with added validation information
        """
        
        validation = {
            'confidence_level': 'unknown',
            'warnings': [],
            'data_source': facility.get('source', 'unknown'),
            'reliability_score': 0.0
        }
        
        # 1. Check score confidence
        confidence = self._check_score_confidence(facility)
        validation['confidence_level'] = confidence
        
        # 2. Check data completeness
        completeness = self._check_data_completeness(facility)
        if completeness < 0.5:
            validation['warnings'].append(
                f"Incomplete data ({completeness*100:.0f}%)"
            )
        
        # 3. Check score anomalies
        score_anomalies = self._check_score_anomalies(facility)
        validation['warnings'].extend(score_anomalies)
        
        # 4. Calculate reliability score
        validation['reliability_score'] = self._calculate_reliability(
            facility, confidence, completeness
        )
        
        # Add to facility information
        facility['validation'] = validation
        
        return facility
    
    def _check_score_confidence(self, facility: Dict) -> str:
        """
        Check score confidence
        Based on original similarity scores (if available)
        """
        
        # Try to get original similarities
        similarities = []
        for dim in ['affordability', 'crisis_care', 'accessibility', 
                    'specialization', 'community_integration']:
            sim_key = f'{dim}_similarity'
            if sim_key in facility:
                similarities.append(facility[sim_key])
        
        if not similarities:
            # If no similarity data, estimate based on score range
            score = facility.get('score', 0)
            if score >= 8.5:
                return 'high'
            elif score >= 7.0:
                return 'medium'
            else:
                return 'low'
        
        avg_similarity = np.mean(similarities)
        
        if avg_similarity >= self.CONFIDENCE_THRESHOLDS['high']:
            return 'high'
        elif avg_similarity >= self.CONFIDENCE_THRESHOLDS['medium']:
            return 'medium'
        else:
            return 'low'
    
    def _check_data_completeness(self, facility: Dict) -> float:
        """
        Check data completeness
        
        Returns:
            completeness score (0-1)
        """
        
        required_fields = ['name', 'city', 'state']
        optional_fields = ['address', 'phone', 'zip']
        
        complete_required = sum(
            1 for field in required_fields 
            if facility.get(field) and str(facility[field]).strip() 
            and str(facility[field]).lower() != 'nan'
        )
        
        complete_optional = 0
        for field in optional_fields:
            value = facility.get(field, '')
            # Check if valid value (not empty, nan, or "not available")
            if (value and str(value).strip() 
                and str(value).lower() not in ['nan', 'address not available', 
                                                 'phone not available', '']):
                complete_optional += 1
        
        # Required fields weight 80%, optional fields weight 20%
        completeness = (
            (complete_required / len(required_fields)) * 0.8 +
            (complete_optional / len(optional_fields)) * 0.2
        )
        
        return completeness
    
    def _check_score_anomalies(self, facility: Dict) -> List[str]:
        """
        Check score anomalies
        
        Returns:
            list of warning messages
        """
        
        warnings = []
        
        overall_score = facility.get('score', 0)
        
        # Check suspiciously high scores
        if overall_score >= self.SCORE_THRESHOLDS['suspiciously_high']:
            warnings.append(
                f"Abnormally high score ({overall_score:.1f}/10), manual verification recommended"
            )
        
        # Check suspiciously low scores
        if overall_score <= self.SCORE_THRESHOLDS['suspiciously_low']:
            warnings.append(
                f"Abnormally low score ({overall_score:.1f}/10), may not match criteria"
            )
        
        # Check consistency across five dimensions
        dimension_scores = []
        for dim in ['affordability_score', 'crisis_care_score', 
                    'accessibility_score', 'specialization_score', 
                    'community_integration_score']:
            if dim in facility:
                dimension_scores.append(facility[dim])
        
        if dimension_scores:
            std_dev = np.std(dimension_scores)
            if std_dev > 2.0:
                warnings.append(
                    f"High score variance (std dev={std_dev:.1f}), may be unreliable"
                )
        
        return warnings
    
    def _calculate_reliability(self, facility: Dict, 
                               confidence: str, 
                               completeness: float) -> float:
        """
        Calculate reliability score
        
        Returns:
            reliability score (0-100)
        """
        
        # Confidence weights
        confidence_weights = {
            'high': 1.0,
            'medium': 0.7,
            'low': 0.4,
            'unknown': 0.3
        }
        
        confidence_score = confidence_weights.get(confidence, 0.3)
        
        # Comprehensive reliability
        reliability = (
            confidence_score * 0.6 +    # Confidence weight 60%
            completeness * 0.3 +         # Completeness weight 30%
            0.1                          # Base score 10%
        ) * 100
        
        return min(100, max(0, reliability))
    
    def validate_results(self, facilities: List[Dict]) -> List[Dict]:
        """
        Validate all results
        
        Args:
            facilities: list of facilities
        
        Returns:
            validated facility list (with warnings)
        """
        
        validated = []
        
        for facility in facilities:
            validated_facility = self.validate_facility(facility)
            validated.append(validated_facility)
        
        return validated
    
    def generate_warning_report(self, facilities: List[Dict]) -> str:
        """
        Generate warning report
        
        Returns:
            warning report text
        """
        
        report_lines = []
        
        report_lines.append("="*70)
        report_lines.append("WARNING: VALIDATION REPORT")
        report_lines.append("="*70)
        
        total = len(facilities)
        high_confidence = sum(
            1 for f in facilities 
            if f.get('validation', {}).get('confidence_level') == 'high'
        )
        medium_confidence = sum(
            1 for f in facilities 
            if f.get('validation', {}).get('confidence_level') == 'medium'
        )
        low_confidence = sum(
            1 for f in facilities 
            if f.get('validation', {}).get('confidence_level') == 'low'
        )
        
        report_lines.append(f"\nTotal Facilities: {total}")
        report_lines.append(f"High Confidence: {high_confidence} ({high_confidence/total*100:.0f}%)")
        report_lines.append(f"Medium Confidence: {medium_confidence} ({medium_confidence/total*100:.0f}%)")
        report_lines.append(f"Low Confidence: {low_confidence} ({low_confidence/total*100:.0f}%)")
        
        # Display specific warnings
        facilities_with_warnings = [
            f for f in facilities 
            if f.get('validation', {}).get('warnings')
        ]
        
        if facilities_with_warnings:
            report_lines.append(f"\nWARNING: {len(facilities_with_warnings)} facilities have warnings:")
            for i, facility in enumerate(facilities_with_warnings, 1):
                report_lines.append(f"\n{i}. {facility['name']}")
                for warning in facility['validation']['warnings']:
                    report_lines.append(f"   - {warning}")
        else:
            report_lines.append("\n✓ All facilities passed validation")
        
        report_lines.append("\n" + "="*70)
        
        return "\n".join(report_lines)
    
    def add_disclaimer(self, facilities: List[Dict]) -> str:
        """
        Generate disclaimer
        
        Returns:
            disclaimer text
        """
        
        avg_reliability = np.mean([
            f.get('validation', {}).get('reliability_score', 0)
            for f in facilities
        ])
        
        disclaimer = []
        
        disclaimer.append("\nIMPORTANT NOTICE:")
        disclaimer.append("-"*70)
        
        if avg_reliability >= 70:
            disclaimer.append("✓ Results based on multi-source evaluation, high reliability")
        elif avg_reliability >= 50:
            disclaimer.append("WARNING: Results based on limited data, phone verification recommended")
        else:
            disclaimer.append("CAUTION: Low confidence results, manual verification strongly recommended")
        
        disclaimer.append("")
        disclaimer.append("DISCLAIMER: This system provides reference information only,")
        disclaimer.append("            not medical advice. Actual services, costs, and")
        disclaimer.append("            availability should be confirmed directly with facilities.")
        disclaimer.append("")
        disclaimer.append(f"Average Reliability: {avg_reliability:.0f}/100")
        disclaimer.append("-"*70)
        
        return "\n".join(disclaimer)


# =====================================================
# Integration Functions for Main System
# =====================================================

def validate_and_display_with_warnings(facilities: List[Dict]):
    """
    Validate and display results (with warnings)
    
    Usage: Call this function in your main workflow
    """
    
    if not facilities:
        print("ERROR: No facilities found")
        return
    
    # Create validator
    validator = AntiHallucinationValidator()
    
    # Validate all facilities
    validated_facilities = validator.validate_results(facilities)
    
    # Display results (with validation information)
    print("\n" + "="*70)
    print(f"FOUND {len(validated_facilities)} FACILITIES")
    print("="*70)
    
    for i, facility in enumerate(validated_facilities, 1):
        validation = facility.get('validation', {})
        
        # Reliability indicator
        reliability = validation.get('reliability_score', 0)
        if reliability >= 70:
            reliability_icon = "🟢"  # Green
        elif reliability >= 50:
            reliability_icon = "🟡"  # Yellow
        else:
            reliability_icon = "🔴"  # Red
        
        print(f"\n{i}. {facility['name']} {reliability_icon}")
        print(f"   Score: {facility['score']:.1f}/10")
        print(f"   Reliability: {reliability:.0f}/100")
        
        # Display warnings
        warnings = validation.get('warnings', [])
        if warnings:
            print(f"   WARNING:")
            for warning in warnings:
                print(f"      - {warning}")
        
        print(f"   Location: {facility['city']}, {facility['state']}")
        print(f"   Phone: {facility['phone']}")
        print(f"   Data Source: {validation.get('data_source', 'unknown')}")
    
    # Display warning report
    print(validator.generate_warning_report(validated_facilities))
    
    # Display disclaimer
    print(validator.add_disclaimer(validated_facilities))


def get_high_confidence_facilities(facilities: List[Dict]) -> List[Dict]:
    """
    Filter for high-confidence facilities only
    
    Args:
        facilities: list of facilities
    
    Returns:
        list of high-confidence facilities
    """
    
    validator = AntiHallucinationValidator()
    validated = validator.validate_results(facilities)
    
    high_confidence = [
        f for f in validated
        if f.get('validation', {}).get('confidence_level') == 'high'
    ]
    
    return high_confidence


def add_validation_badges(facilities: List[Dict]) -> List[Dict]:
    """
    Add validation badges to facilities for display
    
    Args:
        facilities: list of facilities
    
    Returns:
        facilities with badge information added
    """
    
    validator = AntiHallucinationValidator()
    validated = validator.validate_results(facilities)
    
    for facility in validated:
        validation = facility.get('validation', {})
        reliability = validation.get('reliability_score', 0)
        confidence = validation.get('confidence_level', 'unknown')
        
        # Create badge text
        badges = []
        
        if reliability >= 70:
            badges.append("VERIFIED")
        
        if confidence == 'high':
            badges.append("HIGH CONFIDENCE")
        
        if not validation.get('warnings'):
            badges.append("NO WARNINGS")
        
        facility['badges'] = badges
    
    return validated


# =====================================================
# Testing
# =====================================================

if __name__ == "__main__":
    
    # Test data
    test_facilities = [
        {
            'name': 'Test Facility 1 - High Quality',
            'city': 'Hartford',
            'state': 'CT',
            'address': '123 Main St',
            'phone': '(860) 123-4567',
            'score': 8.5,
            'affordability_score': 9.0,
            'crisis_care_score': 8.0,
            'accessibility_score': 8.5,
            'specialization_score': 8.0,
            'community_integration_score': 9.0,
            'affordability_similarity': 0.75,
            'source': 'Google Maps'
        },
        {
            'name': 'Test Facility 2 - Incomplete Data',
            'city': 'New Haven',
            'state': 'CT',
            'address': '',  # Missing address
            'phone': '',    # Missing phone
            'score': 6.5,
            'affordability_score': 7.0,
            'crisis_care_score': 5.0,
            'accessibility_score': 6.0,
            'specialization_score': 7.0,
            'community_integration_score': 7.5,
            'affordability_similarity': 0.45,  # Low similarity
            'source': 'SAMHSA'
        },
        {
            'name': 'Test Facility 3 - Suspicious Score',
            'city': 'Bridgeport',
            'state': 'CT',
            'address': '789 Oak Ave',
            'phone': '(203) 987-6543',
            'score': 9.8,  # Suspiciously high
            'affordability_score': 9.9,
            'crisis_care_score': 9.8,
            'accessibility_score': 9.7,
            'specialization_score': 9.9,
            'community_integration_score': 9.8,
            'affordability_similarity': 0.85,
            'source': 'NPI'
        }
    ]
    
    print("="*70)
    print("ANTI-HALLUCINATION VALIDATION MODULE - TEST")
    print("="*70)
    
    # Test main validation function
    validate_and_display_with_warnings(test_facilities)
    
    # Test filtering
    print("\n\n" + "="*70)
    print("TEST: High-Confidence Filter")
    print("="*70)
    
    high_conf = get_high_confidence_facilities(test_facilities)
    print(f"\nFound {len(high_conf)} high-confidence facilities:")
    for f in high_conf:
        print(f"  - {f['name']}")
    
    # Test badges
    print("\n\n" + "="*70)
    print("TEST: Validation Badges")
    print("="*70)
    
    with_badges = add_validation_badges(test_facilities)
    for f in with_badges:
        badges = f.get('badges', [])
        badge_str = " | ".join(badges) if badges else "No badges"
        print(f"\n{f['name']}")
        print(f"  Badges: {badge_str}")
