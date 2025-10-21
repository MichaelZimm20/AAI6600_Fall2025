#!/usr/bin/env python3
"""
Facility Scoring Module - Integrated from script.py and cleaned_program.py

Functions:
1. Load facility data (Google Maps / NPI / Other sources)
2. Score using Cosine Similarity + Targeted Questions
3. Five-dimensional evaluation (affordability, crisis_care, accessibility, specialization, community_integration)
4. Output scoring results (0-10 scale)

Note: This module has NO imports from other project modules to avoid circular dependencies.
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')
from anti_hallucination import NegativeEvidenceDetector

# NO OTHER PROJECT IMPORTS - Keep this module independent!


class FacilityScorer:
    """Facility Scorer - Integrated Scoring System"""
    
    # ==============================
    # Targeted Questions (Five Dimensions)
    # ==============================
    TARGETED_QUESTIONS = {
        'affordability': """Does this mental health facility accept Medicaid, Medicare, or offer sliding scale fees, free services, or low-cost counseling? Is it a community mental health center, public health facility, county health department, or federally qualified health center (FQHC)?""",
        
        'crisis_care': """Does this facility provide crisis intervention services, emergency mental health care, crisis hotline, suicide prevention, 24/7 urgent psychiatric services, or walk-in crisis support?""",
        
        'accessibility': """Is this facility easily accessible with walk-in services, multiple locations, convenient hours (evening/weekend), telehealth options, or community-based outreach? Does it have low barriers to entry?""",
        
        'specialization': """Does this facility specialize in specific mental health services such as child psychology, family therapy, trauma treatment, PTSD care, addiction/substance abuse treatment, eating disorders, or veteran mental health services?""",
        
        'community_integration': """Is this facility integrated with the community, serving as a neighborhood mental health center, community behavioral health organization, public health department, or nonprofit organization focused on underserved populations?"""
    }
    
    # Mental Health Taxonomy Codes (NPI)
    MENTAL_HEALTH_TAXONOMY_CODES = [
        '101Y',  # Counselor
        '103T',  # Psychologist
        '104',   # Social Worker
        '106',   # Marriage & Family Therapist
        '261Q',  # Mental Health Clinic/Center
        '273R',  # Psychiatric Hospital
        '2084',  # Psychiatry & Neurology
        '163W',  # Psychiatric Nurse
    ]
    
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initialize scorer
        
        Args:
            model_name: Sentence Transformer model name
        """
        print("Loading facility scorer...")
        
        try:
            self.model = SentenceTransformer(model_name)
            print("✓ Semantic model loaded successfully")
        except Exception as e:
            print(f"✗ Model loading failed: {e}")
            raise
        
        # NEW: Initialize negative evidence detector
        self.negative_detector = NegativeEvidenceDetector()
        
        # Pre-compute question embeddings
        print("Pre-computing question embeddings...")
        self.question_embeddings = {}
        for key, question in self.TARGETED_QUESTIONS.items():
            self.question_embeddings[key] = self.model.encode(
                question.strip(), 
                convert_to_tensor=False, 
                show_progress_bar=False
            )
        print("✓ Scorer initialization complete\n")
    
    def create_clean_text(self, row):
        """
        Create clean text for semantic analysis
        Does not include pre-added keywords
        """
        parts = [
            str(row.get('facility_name', row.get('name', ''))),
            str(row.get('address', row.get('street', ''))),
            str(row.get('city', '')),
            str(row.get('state', ''))
        ]
        
        clean_parts = [
            p.lower() for p in parts 
            if p and str(p).strip() and str(p) != 'nan'
        ]
        
        return ' '.join(clean_parts)
    
    def calculate_cosine_similarity(self, text, question_embedding):
        """
        Calculate cosine similarity between text and question
        
        Args:
            text: Facility description text
            question_embedding: Question embedding vector
        
        Returns:
            Similarity score (0-1)
        """
        if pd.isna(text) or not str(text).strip():
            return 0.0
        
        try:
            text_embedding = self.model.encode(
                str(text), 
                convert_to_tensor=False, 
                show_progress_bar=False
            )
            
            similarity = np.dot(question_embedding, text_embedding) / (
                np.linalg.norm(question_embedding) * np.linalg.norm(text_embedding) + 1e-8
            )
            
            return float(similarity)
        except:
            return 0.0
    
    def similarity_to_score(self, similarity):
        """
        Convert similarity (0-1) to score (0-10)
        
        Mapping rules:
        [0.00, 0.20) → [0, 2)
        [0.20, 0.30) → [2, 4)
        [0.30, 0.40) → [4, 6)
        [0.40, 0.50) → [6, 8)
        [0.50, 1.00] → [8, 10]
        """
        similarity = max(0.0, similarity)
        
        if similarity < 0.20:
            score = similarity / 0.20 * 2
        elif similarity < 0.30:
            score = 2 + (similarity - 0.20) / 0.10 * 2
        elif similarity < 0.40:
            score = 4 + (similarity - 0.30) / 0.10 * 2
        elif similarity < 0.50:
            score = 6 + (similarity - 0.40) / 0.10 * 2
        else:
            score = 8 + (similarity - 0.50) / 0.50 * 2
        
        return max(0.0, min(10.0, score))
    
    def score_facilities(self, df, text_column='clean_text'):
        """
        Score facility dataframe
        
        Args:
            df: Facility dataframe
            text_column: Text column name for scoring
        
        Returns:
            Scored dataframe
        """
        print(f"\nScoring {len(df)} facilities...")
        
        # 1. Generate clean_text if not present
        if text_column not in df.columns:
            print("   Generating clean_text...")
            df[text_column] = df.apply(self.create_clean_text, axis=1)
        
        # 2. Calculate similarity for each dimension
        print("   Calculating multi-dimensional similarities...")
        
        for key in self.TARGETED_QUESTIONS.keys():
            df[f'{key}_similarity'] = 0.0
        
        for idx in tqdm(range(len(df)), desc="   Similarity calculation"):
            clean_text = str(df.iloc[idx][text_column])
            
            for key, question_emb in self.question_embeddings.items():
                similarity = self.calculate_cosine_similarity(clean_text, question_emb)
                df.at[df.index[idx], f'{key}_similarity'] = similarity
        
        # 3. Convert to 0-10 scores
        print("   Converting to Care Needs scores...")
        
        score_cols = []
        for key in self.TARGETED_QUESTIONS.keys():
            sim_col = f'{key}_similarity'
            score_col = f'{key}_score'
            score_cols.append(score_col)
            
            df[score_col] = df[sim_col].apply(self.similarity_to_score)
        
        # 4. Calculate overall score
        df['overall_care_needs_score'] = df[score_cols].mean(axis=1)
        
        
        # ===== NEW STEP 5: CHECK FOR NEGATIVE EVIDENCE =====
        print("   Checking for negative evidence (cash-only, luxury services)...")
    
        negative_count = 0
        df['has_negative_evidence'] = False
    
        for idx in range(len(df)):
            row_dict = df.iloc[idx].to_dict()
        
            # Check for negative evidence
            negative_result = self.negative_detector.detect_negative_evidence(row_dict)
        
            if negative_result['has_strong_negative'] or negative_result['has_moderate_negative']:
                # Adjust the overall score
                original_score = df.at[df.index[idx], 'overall_care_needs_score']
                adjusted_score = self.negative_detector.adjust_score_for_negative_evidence(
                original_score, negative_result
            )
            
                # Update the score
                df.at[df.index[idx], 'overall_care_needs_score'] = adjusted_score
                df.at[df.index[idx], 'has_negative_evidence'] = True
                negative_count += 1
    
        if negative_count > 0:
            print(f"   ⚠️  Adjusted {negative_count} facilities with negative evidence")
        # ===== END OF NEW STEP 5 =====
        
        print("✓ Scoring complete\n")
        
        return df
    
    def get_score_statistics(self, df):
        """
        Get scoring statistics
        
        Returns:
            Statistics dictionary
        """
        stats = {}
        
        dimension_names = list(self.TARGETED_QUESTIONS.keys())
        
        for dim_name in dimension_names:
            score_col = f'{dim_name}_score'
            
            if score_col in df.columns:
                stats[dim_name] = {
                    'mean': df[score_col].mean(),
                    'median': df[score_col].median(),
                    'std': df[score_col].std(),
                    'min': df[score_col].min(),
                    'max': df[score_col].max(),
                    'high_count': (df[score_col] >= 7).sum(),
                    'high_percentage': (df[score_col] >= 7).sum() / len(df) * 100
                }
        
        # Overall statistics
        if 'overall_care_needs_score' in df.columns:
            stats['overall'] = {
                'mean': df['overall_care_needs_score'].mean(),
                'median': df['overall_care_needs_score'].median(),
                'std': df['overall_care_needs_score'].std(),
                'min': df['overall_care_needs_score'].min(),
                'max': df['overall_care_needs_score'].max()
            }
        
        return stats
    
    def print_statistics(self, df):
        """Print scoring statistics"""
        
        stats = self.get_score_statistics(df)
        
        print("\n" + "="*70)
        print("SCORING STATISTICS")
        print("="*70 + "\n")
        
        dimension_names = list(self.TARGETED_QUESTIONS.keys())
        
        for dim_name in dimension_names:
            if dim_name in stats:
                s = stats[dim_name]
                print(f"{dim_name:25s}: Avg {s['mean']:.2f}/10, "
                      f"High {s['high_count']} ({s['high_percentage']:.1f}%)")
        
        if 'overall' in stats:
            s = stats['overall']
            print(f"\n{'Overall Score':25s}: Avg {s['mean']:.2f}/10 "
                  f"(Range: {s['min']:.2f} - {s['max']:.2f})")
        
        print("\n" + "="*70 + "\n")
    
    def filter_by_needs(self, df, needs_list):
        """
        Filter facilities by specific needs (improved version)
        
        Args:
            df: Facility dataframe
            needs_list: List of needs, e.g., ['crisis', 'anxiety', 'child']
        
        Returns:
            Filtered dataframe
        """
        if not needs_list:
            return df
        
        # Needs to dimension mapping
        needs_mapping = {
            'crisis': 'crisis_care_score',
            'emergency': 'crisis_care_score',
            'urgent': 'crisis_care_score',
            
            'child': 'specialization_score',
            'teen': 'specialization_score',
            'adolescent': 'specialization_score',
            
            'trauma': 'specialization_score',
            'ptsd': 'specialization_score',
            
            'addiction': 'specialization_score',
            'substance': 'specialization_score',
            
            'affordable': 'affordability_score',
            'low-cost': 'affordability_score',
            'medicaid': 'affordability_score',
            
            # General needs don't filter
            'anxiety': None,
            'depression': None,
            'general_mental_health': None,
        }
        
        # Collect relevant scoring dimensions
        relevant_dimensions = []
        for need in needs_list:
            dim = needs_mapping.get(need.lower())
            if dim and dim not in relevant_dimensions:
                relevant_dimensions.append(dim)
        
        if not relevant_dimensions:
            # If all general needs (anxiety, depression, etc.), don't filter
            return df
        
        # Strategy: Calculate needs relevance score
        df = df.copy()
        
        # Calculate weighted score (emphasize user's focus dimensions)
        weights = {dim: 0 for dim in ['affordability_score', 'crisis_care_score', 
                                       'accessibility_score', 'specialization_score', 
                                       'community_integration_score']}
        
        # User's focus dimensions get higher weight
        for dim in relevant_dimensions:
            weights[dim] = 0.5  # Focus dimensions 50% weight
        
        # Other dimensions split remaining weight
        remaining_weight = 1.0 - sum(weights.values())
        n_other = len([w for w in weights.values() if w == 0])
        if n_other > 0:
            for dim in weights:
                if weights[dim] == 0:
                    weights[dim] = remaining_weight / n_other
        
        # Calculate needs relevance score
        df['needs_relevance_score'] = 0.0
        for dim, weight in weights.items():
            if dim in df.columns:
                df['needs_relevance_score'] += df[dim] * weight
        
        # Filter: Keep facilities with needs dimension ≥ 6.5 (raised threshold)
        for dim in relevant_dimensions:
            if dim in df.columns:
                df = df[df[dim] >= 6.5]  # Raised from 5.0 to 6.5
        
        # Sort by needs relevance score (not overall score)
        df = df.sort_values('needs_relevance_score', ascending=False)
        
        return df
    
    def get_top_facilities(self, df, n=10, city=None, state=None, needs=None):
        """
        Get top N facilities
        
        Args:
            df: Facility dataframe
            n: Number to return
            city: City filter
            state: State filter
            needs: Special needs list
        
        Returns:
            Top N facilities
        """
        filtered_df = df.copy()
        
        # Geographic filtering
        if state:
            filtered_df = filtered_df[
                filtered_df['state'].str.upper() == state.upper()
            ]
        
        if city:
            filtered_df = filtered_df[
                filtered_df['city'].str.contains(city, case=False, na=False)
            ]
        
        # Needs filtering
        if needs:
            filtered_df = self.filter_by_needs(filtered_df, needs)
        
        # Sort by overall score
        if 'overall_care_needs_score' in filtered_df.columns:
            filtered_df = filtered_df.sort_values(
                'overall_care_needs_score', 
                ascending=False
            )
        
        return filtered_df.head(n)


# ==============================
# Convenience Functions
# ==============================

def score_csv_file(input_csv, output_csv=None):
    """
    Score facilities in CSV file
    
    Args:
        input_csv: Input CSV file path
        output_csv: Output CSV file path (optional)
    
    Returns:
        Scored DataFrame
    """
    print(f"\nReading file: {input_csv}")
    
    df = pd.read_csv(input_csv, dtype=str)
    print(f"✓ Read {len(df)} records\n")
    
    # Create scorer
    scorer = FacilityScorer()
    
    # Score
    df_scored = scorer.score_facilities(df)
    
    # Statistics
    scorer.print_statistics(df_scored)
    
    # Save
    if output_csv:
        df_scored.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"Result saved: {output_csv}\n")
    
    return df_scored


def quick_search(scored_csv, city=None, state=None, needs=None, top_n=5):
    """
    Quick search in scored facilities
    
    Args:
        scored_csv: Scored CSV file
        city: City
        state: State
        needs: Needs list
        top_n: Number to return
    
    Returns:
        Top N facilities
    """
    print(f"\nSearching facilities...")
    
    df = pd.read_csv(scored_csv)
    
    scorer = FacilityScorer()
    results = scorer.get_top_facilities(
        df, 
        n=top_n, 
        city=city, 
        state=state, 
        needs=needs
    )
    
    print(f"✓ Found {len(results)} facilities\n")
    
    return results


# ==============================
# Testing
# ==============================

if __name__ == "__main__":
    
    print("="*70)
    print("Facility Scoring Module - Test")
    print("="*70)
    
    # Use relative paths
    from pathlib import Path
    current_dir = Path(__file__).parent
    
    # Example: Score facilities_final.csv (relative to Basic framework root)
    data_dir = current_dir.parent / "Group3_dataset"
    input_file = data_dir / "facilities_final.csv"
    output_file = data_dir / "facilities_scored.csv"
    
    print("\n[TEST 1] Scoring facilities")
    print("-"*70)
    
    try:
        df_scored = score_csv_file(str(input_file), str(output_file))
        
        # Display Top 5
        print("\n[TOP 5 FACILITIES]")
        print("-"*70)
        
        top_5 = df_scored.nlargest(5, 'overall_care_needs_score')
        
        for i, (_, row) in enumerate(top_5.iterrows(), 1):
            # Handle different possible column names
            facility_name = row.get('facility_name', row.get('name', 'Unknown'))
            
            print(f"\n{i}. {facility_name}")
            print(f"   Overall Score: {row['overall_care_needs_score']:.2f}/10")
            print(f"   Location: {row['city']}, {row['state']}")
            print(f"   Affordability: {row['affordability_score']:.2f}/10")
        
    except FileNotFoundError:
        print(f"WARNING: File not found: {input_file}")
        print("\nExpected structure:")
        print("  Basic framework/")
        print("  ├── Group3_dataset/")
        print("  │   └── facilities_final.csv")
        print("  └── integrated/")
        print("      └── facility_scorer.py")
    
    print("\n" + "="*70)
    print("✓ Test complete")
