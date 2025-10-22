#!/usr/bin/env python3
"""
Group 3 Main Workflow

Process:
1. TXT Input (router_txt_input.py) → Parse + Route
2. Info Collection (router_txt_input.py) → Location, Insurance, Needs
3. Facility Scoring (facility_scorer.py) → Load scored data or score in real-time
4. Search Matching (facility_scorer.py) → Filter by user info
5. Results Display (router_txt_input.py) → Formatted output
"""

import sys
import os
from pathlib import Path

# Add relative paths
current_file = Path(__file__).resolve()
current_dir = current_file.parent  # integrated/
root_dir = current_dir.parent  # Basic framework/

# Add p1 folder to path
p1_dir = root_dir / "p1"
if str(p1_dir) not in sys.path:
    sys.path.insert(0, str(p1_dir))

# Import modules
from group2_router import handle_group2_input
from router_txt_input import (
    parse_group2_txt,
    collect_location,
    collect_insurance,
    collect_needs,
    display_results
)

# Import scoring module
from facility_scorer import FacilityScorer, score_csv_file

import pandas as pd


class Group3MainWorkflow:
    """Group 3 Main Workflow"""
    
    def __init__(self, data_dir=None):
        """
        Initialize workflow
        
        Args:
            data_dir: Data directory path
        """
        print("\n" + "="*70)
        print("🚀 Group 3 Main Workflow Initialization")
        print("="*70 + "\n")
        
        # Data directory
        if data_dir is None:
            self.data_dir = root_dir / "Group3_dataset"
        else:
            self.data_dir = Path(data_dir)
        
        # Facility data
        self.facilities_df = None
        self.scorer = None
        
        # Try to load pre-scored data
        self._try_load_scored_facilities()
        
        print("✅ Initialization complete\n")
    
    def _try_load_scored_facilities(self):
        """Try to load and merge all datasets"""
        
        print("📂 Loading all datasets...")
        
        all_dataframes = []
        needs_scoring = []  # Data that needs scoring
        
        # Define all possible data files
        data_files = [
            # Priority: Look for scored data first
            ("care_needs_scores.csv", "Google Maps"),
            ("facilities_scored.csv", "Google Maps"),
            ("all_facilities_scored.csv", "Multiple Sources"),
            
            # Raw data (needs scoring)
            ("facilities_final.csv", "Google Maps"),
            ("locations_affordable_normalized.csv", "HRSA/EHB"),
            ("locations_affordable_plpfile.csv", "NPI Registry"),
            ("Placesaffordablehealth_cleaned.csv", "Google Places"),
            ("SAMHSA_cleaned .csv", "SAMHSA"),
            ("nsumhss_affordability_min(Janet).csv", "NSUMHSS Survey"),
            
            # Other possible locations
            (r"..\w5 6600\final_complete_analysis\GoogleMap_results\care_needs_scores.csv", "Google Maps Analysis"),
            (r"..\w5 6600\final_complete_analysis\NPI_results\care_needs_scores.csv", "NPI Analysis"),
        ]
        
        scored_count = 0
        unscored_count = 0
        
        for filename, source_label in data_files:
            file_path = self.data_dir / filename
            
            # Handle relative paths
            if not file_path.exists() and ".." in filename:
                file_path = Path(filename)
            
            if not file_path.exists():
                continue
            
            try:
                print(f"   📄 {file_path.name}...", end=" ")
                df = pd.read_csv(file_path, encoding='utf-8-sig', low_memory=False, on_bad_lines='skip')
                
                # Standardize column names
                df = self._standardize_columns(df)
                
                # Add source label
                if 'source' not in df.columns:
                    df['source'] = source_label
                
                # Check if already scored
                has_scores = 'overall_care_needs_score' in df.columns
                
                if has_scores:
                    print(f"✓ Scored {len(df)} records")
                    all_dataframes.append(df)
                    scored_count += 1
                else:
                    print(f"⚠ Unscored {len(df)} records, will score later")
                    needs_scoring.append((file_path.name, df))
                    unscored_count += 1
                
            except Exception as e:
                print(f"✗ Failed: {e}")
                continue
        
        # If no scored data but have unscored data
        if not all_dataframes and needs_scoring:
            print(f"\n⚠️  No scored data found, but have {unscored_count} unscored datasets")
            print(f"Starting scoring now (this may take a few minutes)...\n")
            
            # Initialize scorer
            if self.scorer is None:
                self.scorer = FacilityScorer()
            
            # Score each unscored dataset
            for filename, df in needs_scoring:
                print(f"🔄 Scoring: {filename} ({len(df)} records)...")
                try:
                    df_scored = self.scorer.score_facilities(df)
                    all_dataframes.append(df_scored)
                except Exception as e:
                    print(f"   ❌ Scoring failed: {e}")
                    continue
        
        # If no scored data and scoring failed
        if not all_dataframes:
            print("\n   ⚠️  No usable datasets found, will use mock data\n")
            self.facilities_df = None
            return
        
        # Merge all dataframes
        print(f"\n🔄 Merging {len(all_dataframes)} datasets...")
        self.facilities_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Deduplicate
        original_count = len(self.facilities_df)
        self.facilities_df = self._deduplicate_facilities(self.facilities_df)
        dedup_count = original_count - len(self.facilities_df)
        
        if dedup_count > 0:
            print(f"   Deduplication: {original_count} → {len(self.facilities_df)} records (removed {dedup_count} duplicates)")
        
        print(f"\n✅ Final dataset: {len(self.facilities_df)} facilities")
        
        # Save merged scored results (if new data was scored)
        if needs_scoring and len(needs_scoring) > 0:
            output_path = self.data_dir / "all_facilities_scored.csv"
            self.facilities_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"💾 Merged scored results saved: all_facilities_scored.csv (in Group3_dataset/)")
        
        # Display state distribution
        if 'state' in self.facilities_df.columns:
            state_counts = self.facilities_df['state'].value_counts().head(10)
            print(f"\n📊 Top 10 States:")
            for state, count in state_counts.items():
                if state and str(state).strip():
                    print(f"   {state}: {count} facilities")
        
        print()
    
    def _standardize_columns(self, df):
        """Standardize column names"""
        
        # Column name mapping
        column_mapping = {
            # Name fields
            'facility_name': 'name',
            'org': 'name',
            'name1': 'name',
            'Provider Organization Name (Legal Business Name)': 'name',
            
            # Address fields
            'address': 'street',
            'street1': 'street',
            'Provider First Line Business Practice Location Address': 'street',
            
            # City fields
            'city': 'city',
            'city/town': 'city',
            'Provider Business Practice Location Address City Name': 'city',
            
            # State fields
            'state': 'state',
            'Provider Business Practice Location Address State Name': 'state',
            
            # ZIP fields
            'zip': 'zipcode',
            'Provider Business Practice Location Address Postal Code': 'zipcode',
            
            # Phone fields
            'phone': 'phone',
            'Provider Business Practice Location Address Telephone Number': 'phone',
        }
        
        # Rename existing columns
        rename_dict = {}
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns and new_name not in df.columns:
                rename_dict[old_name] = new_name
        
        if rename_dict:
            df = df.rename(columns=rename_dict)
        
        # Ensure necessary fields exist
        for col in ['name', 'street', 'city', 'state', 'zipcode']:
            if col not in df.columns:
                df[col] = ''
        
        return df
    
    def _deduplicate_facilities(self, df):
        """Deduplicate facilities (improved - based on name+city+state+zip)"""
        
        # Normalize phone numbers (remove formatting)
        def normalize_phone(phone):
            if pd.isna(phone) or not phone:
                return ''
            # Keep only digits
            return ''.join(filter(str.isdigit, str(phone)))
        
        df['_phone_normalized'] = df['phone'].apply(normalize_phone) if 'phone' in df.columns else ''
        
        # Create deduplication keys (multiple strategies)
        # Strategy 1: Name+City+State+ZIP
        df['_dedup_key_1'] = (
            df['name'].fillna('').astype(str).str.lower().str.strip() + '|' +
            df['city'].fillna('').astype(str).str.lower().str.strip() + '|' +
            df['state'].fillna('').astype(str).str.upper().str.strip() + '|' +
            df['zipcode'].fillna('').astype(str).str[:5]  # Only first 5 digits of ZIP
        )
        
        # Strategy 2: Name+Phone (if available)
        df['_dedup_key_2'] = (
            df['name'].fillna('').astype(str).str.lower().str.strip() + '|' +
            df['_phone_normalized']
        )
        
        # First deduplicate by strategy 1
        df = df.drop_duplicates(subset='_dedup_key_1', keep='first')
        
        # Then deduplicate by strategy 2 (only for records with phone)
        mask_has_phone = df['_phone_normalized'].str.len() >= 10
        df_with_phone = df[mask_has_phone]
        df_without_phone = df[~mask_has_phone]
        
        if len(df_with_phone) > 0:
            df_with_phone = df_with_phone.drop_duplicates(subset='_dedup_key_2', keep='first')
        
        # Merge back
        df = pd.concat([df_with_phone, df_without_phone], ignore_index=True)
        
        # Remove temporary columns
        df = df.drop(columns=['_dedup_key_1', '_dedup_key_2', '_phone_normalized'])
        
        return df
    
    def _deduplicate_search_results(self, df):
        """
        Deduplicate search results (keep highest scoring)
        
        For final deduplication of search results, ensure no duplicates in Top N
        """
        
        # Create simple dedup key based on name+city+zip
        df['_search_dedup_key'] = (
            df['name'].fillna('').astype(str).str.lower().str.strip() + '|' +
            df['city'].fillna('').astype(str).str.lower().str.strip() + '|' +
            df['zipcode'].fillna('').astype(str).str[:5]
        )
        
        # Keep highest scoring in each group
        df = df.sort_values('overall_care_needs_score', ascending=False)
        df = df.drop_duplicates(subset='_search_dedup_key', keep='first')
        
        # Remove temporary column
        df = df.drop(columns=['_search_dedup_key'])
        
        return df
    
    def process_txt_input(self, txt_file):
        """
        Process TXT input (complete workflow)
        
        Args:
            txt_file: Group 2's TXT output file path
        
        Returns:
            Processing result dictionary
        """
        
        print("\n" + "="*70)
        print("📋 Starting Group 2 Output Processing")
        print("="*70 + "\n")
        
        # ====================
        # Step 1: Parse TXT file
        # ====================
        print("【Step 1】Parse TXT File")
        print("-"*70)
        
        try:
            group2_output = parse_group2_txt(txt_file)
            
            print(f"✅ Parse successful")
            print(f"   Category: {group2_output['category']}")
            print(f"   Confidence: {group2_output['confidence']:.2%}")
            if group2_output.get('user_input'):
                print(f"   User input: {group2_output['user_input'][:60]}...")
            print()
            
        except Exception as e:
            print(f"❌ Parse failed: {e}")
            return {'status': 'error', 'message': str(e)}
        
        # ====================
        # Step 2: Router decision
        # ====================
        print("\n【Step 2】Router Decision")
        print("-"*70)
        
        is_ours, decision = handle_group2_input(group2_output)
        
        print(f"Route result: {decision['branch']}")
        print(f"{decision['message']}")
        print()
        
        if not is_ours:
            return {
                'status': 'not_handled',
                'branch': decision['branch'],
                'message': decision['message'],
                'category': group2_output['category']
            }
        
        # ====================
        # Step 3: Collect user information
        # ====================
        print("\n【Step 3】Collect User Information")
        print("-"*70 + "\n")
        
        location = collect_location()
        insurance = collect_insurance()
        #needs = collect_needs()
        
        user_info = {
            'location': location,
            'insurance': insurance,
           # 'needs': needs
        }
        
        # ====================
        # Step 4: Search facilities
        # ====================
        print("\n【Step 4】Search Matching Facilities")
        print("-"*70 + "\n")
        
        facilities = self._search_facilities(user_info)
        
        if not facilities:
            print("❌ No matching facilities found")
            return {
                'status': 'no_results',
                'message': 'No matching facilities found, try expanding search criteria'
            }
        
        # ====================
        # Step 5: Validate and display results
        # ====================
        print("\n【Step 5】Validate and Display Results")
        print("-"*70 + "\n")
        
        # Add anti-hallucination validation
        try:
            from anti_hallucination import AntiHallucinationValidator
            
            validator = AntiHallucinationValidator()
            validated_facilities = validator.validate_results(facilities)
            
            # Display validation report
            print(validator.generate_warning_report(validated_facilities))
            print()
            
            # Display results
            display_results(validated_facilities, location, insurance)
            
            # Display disclaimer
            print(validator.add_disclaimer(validated_facilities))
            
        except ImportError:
            # If no anti-hallucination module, still display results with basic warning
            print("⚠️  Note: Some facility information may be incomplete, phone verification recommended\n")
            display_results(facilities, location, insurance)
            print("\n📋 Important: This system provides reference information only, verify details directly with facilities")
        except Exception as e:
            print(f"⚠️  Validation module error: {e}")
            print("   Continuing with results display...\n")
            display_results(facilities, location, insurance)
        
        # ====================
        # Return results
        # ====================
        return {
            'status': 'success',
            'facilities': facilities,
            'user_info': user_info,
            'category': group2_output['category'],
            'confidence': group2_output['confidence']
        }
    
    def _search_facilities(self, user_info):
        """
        Search facilities (improved - smarter state matching)
        
        Args:
            user_info: {
                'location': {'city': ..., 'state': ...},
                'insurance': str,
                'needs': [...]
            }
        
        Returns:
            Facility list
        """
        
        if self.facilities_df is None or len(self.facilities_df) == 0:
            print("⚠️  Using mock data")
            return self._get_mock_facilities(user_info)
        
        # Copy dataframe
        df = self.facilities_df.copy()
        
        # Extract filter criteria
        location = user_info.get('location', {})
        city = location.get('city', '')
        state_input = location.get('state', '')
        needs = user_info.get('needs', [])
        insurance = user_info.get('insurance', '')
        
        print(f"   Search criteria:")
        if city:
            print(f"      City: {city}")
        if state_input:
            print(f"      State: {state_input}")
        if needs:
            print(f"      Needs: {', '.join(needs)}")
        print(f"      Insurance: {insurance}")
        print()
        
        # State name mapping (support full name and abbreviation)
        STATE_MAPPING = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
            'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
            'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
            'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
            'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
            'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
            'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
            'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
            'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
            'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
            'wisconsin': 'WI', 'wyoming': 'WY'
        }
        
        # Filter: State
        if state_input:
            original_count = len(df)
            
            # Normalize user input
            state_normalized = state_input.strip().lower()
            
            # If full name, convert to abbreviation
            if state_normalized in STATE_MAPPING:
                state_code = STATE_MAPPING[state_normalized]
            else:
                state_code = state_input.strip().upper()
            
            # Try multiple matching methods
            df_filtered = df[
                (df['state'].str.strip().str.upper() == state_code) |
                (df['state'].str.strip().str.lower() == state_normalized) |
                (df['state'].str.strip().str.upper() == state_input.strip().upper())
            ]
            
            if len(df_filtered) > 0:
                df = df_filtered
                print(f"   Filter by state: {original_count} → {len(df)} records")
            else:
                # If exact match fails, try contains match
                df_filtered = df[df['state'].str.contains(state_input, case=False, na=False)]
                if len(df_filtered) > 0:
                    df = df_filtered
                    print(f"   Filter by state (fuzzy): {original_count} → {len(df)} records")
                else:
                    print(f"   ⚠️  State filter failed: {original_count} → 0 records")
                    print(f"   Hint: Sample state values in data: {df['state'].value_counts().head(5).index.tolist()}")
        
        # Filter: City
        if city and len(df) > 0:
            original_count = len(df)
            city_col = 'city' if 'city' in df.columns else 'city/town'
            df = df[df[city_col].str.contains(city, case=False, na=False)]
            print(f"   Filter by city: {original_count} → {len(df)} records")
        
        # Filter: Special needs
        if needs and len(df) > 0:
            original_count = len(df)
            
            # Ensure scorer is initialized
            if self.scorer is None:
                from facility_scorer import FacilityScorer
                self.scorer = FacilityScorer()
            
            df = self.scorer.filter_by_needs(df, needs)
            print(f"   Filter by needs: {original_count} → {len(df)} records")
        
        # If filtered to empty and have state, relax criteria (state only, ignore needs)
        if len(df) == 0 and state_input:
            print(f"\n   ⚠️  No matches found, relaxing criteria (state only, ignore needs)")
            df = self.facilities_df.copy()
            
            # Re-filter by state
            state_normalized = state_input.strip().lower()
            if state_normalized in STATE_MAPPING:
                state_code = STATE_MAPPING[state_normalized]
            else:
                state_code = state_input.strip().upper()
            
            df = df[
                (df['state'].str.strip().str.upper() == state_code) |
                (df['state'].str.strip().str.lower() == state_normalized)
            ]
            
            print(f"   Expanded search: {len(df)} records")
        
        # Sort
        if len(df) > 0 and 'overall_care_needs_score' in df.columns:
            df = df.sort_values('overall_care_needs_score', ascending=False)
        
        # Deduplicate search results (based on name+city+zip)
        if len(df) > 0:
            df = self._deduplicate_search_results(df)
        
        print(f"\n   ✅ Found {len(df)} facilities, returning Top 5\n")
        
        # Convert to dictionary list
        facilities = []
        for _, row in df.head(5).iterrows():
            facilities.append(self._row_to_facility_dict(row, insurance))
        
        return facilities
    
    def _row_to_facility_dict(self, row, insurance):
        """Convert DataFrame row to facility dictionary (fixed - preserve similarity data)"""
        
        # Unified field names and handle nan
        def get_field(row, *field_names):
            """Get non-empty value from multiple possible field names"""
            for field in field_names:
                value = row.get(field, '')
                if pd.notna(value) and str(value).strip() and str(value).lower() != 'nan':
                    return str(value).strip()
            return ''
        
        name = get_field(row, 'facility_name', 'name', 'org')
        if not name:
            name = 'Unknown Facility'
        
        street = get_field(row, 'address', 'street', 'street1')
        city = get_field(row, 'city', 'city/town')
        state = get_field(row, 'state')
        zipcode = get_field(row, 'zip', 'zipcode')
        phone = get_field(row, 'phone')
        
        facility_dict = {
            'name': name,
            'address': street if street else 'Address not available',
            'city': city,
            'state': state,
            'zip': zipcode,
            'phone': phone if phone else 'Phone not available',
            'score': float(row.get('overall_care_needs_score', 7.5)),
            'affordability_score': float(row.get('affordability_score', 8.0)),
            'crisis_care_score': float(row.get('crisis_care_score', 6.5)),
            'accessibility_score': float(row.get('accessibility_score', 7.0)),
            'specialization_score': float(row.get('specialization_score', 6.5)),
            'community_integration_score': float(row.get('community_integration_score', 7.0)),
            'accepts_insurance': [insurance],
            'source': row.get('source', 'unknown')
        }
        
        # Add original similarity data (for confidence assessment)
        for dim in ['affordability', 'crisis_care', 'accessibility', 
                    'specialization', 'community_integration']:
            sim_key = f'{dim}_similarity'
            if sim_key in row:
                facility_dict[sim_key] = float(row.get(sim_key, 0))
        
        return facility_dict
    
    def _get_mock_facilities(self, user_info):
        """Get mock facilities (Fallback)"""
        
        location = user_info.get('location', {})
        city = location.get('city', 'Hartford')
        state = location.get('state', 'CT')
        insurance = user_info.get('insurance', 'Medicaid')
        
        return [
            {
                'name': '[MOCK] Community Mental Health Center',
                'address': '123 Main Street',
                'city': city,
                'state': state,
                'zip': '06103',
                'phone': '(860) 123-4567',
                'score': 8.2,
                'affordability_score': 9.0,
                'crisis_care_score': 7.5,
                'accessibility_score': 8.0,
                'specialization_score': 7.0,
                'community_integration_score': 8.5,
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
                'specialization_score': 7.5,
                'community_integration_score': 7.5,
                'accepts_insurance': [insurance, 'Private Insurance']
            }
        ]
    
    def process_interactive(self):
        """Interactive mode (manual input, no TXT file needed)"""
        
        print("\n" + "="*70)
        print("📋 Interactive Mode - Manual Input")
        print("="*70 + "\n")
        
        # Simulate Group 2 output
        print("【Simulate Group 2 Output】")
        category = input("Category (e.g., Mental health): ").strip() or "Mental health"
        confidence = float(input("Confidence (0-1, e.g., 0.92): ").strip() or "0.92")
        user_input = input("User input (e.g., I need affordable therapy): ").strip() or "I need affordable therapy"
        
        group2_output = {
            'category': category,
            'confidence': confidence,
            'user_input': user_input
        }
        
        # Router decision
        is_ours, decision = handle_group2_input(group2_output)
        
        print(f"\nRoute result: {decision['message']}\n")
        
        if not is_ours:
            return
        
        # Collect information
        location = collect_location()
        insurance = collect_insurance()
        #needs = collect_needs()
        
        user_info = {
            'location': location,
            'insurance': insurance,
            #'needs': needs
        }
        
        # Search
        facilities = self._search_facilities(user_info)
        
        # Display
        if facilities:
            display_results(facilities, location, insurance)
        else:
            print("❌ No matching facilities found")


# ==============================
# Main Program
# ==============================

def main():
    """Main program"""
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     Group 3: Affordable Mental Health Facility Locator          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize workflow
    workflow = Group3MainWorkflow()
    
    # Select mode
    print("="*70)
    print("Select Mode:")
    print("="*70)
    print()
    print("1. 📄 TXT Input Mode (Read Group 2's TXT output file)")
    print("2. ⌨️  Interactive Mode (Manual input of all information)")
    print("3. ❌ Exit")
    print()
    
    choice = input("Select (1-3): ").strip()
    
    if choice == '1':
        # TXT input mode
        default_txt = root_dir / "result_of_second_group" / "test.txt"
        
        print(f"\nDefault TXT file: test.txt (in result_of_second_group/)")
        use_default = input("Use default path? (y/n): ").strip().lower()
        
        if use_default == 'y':
            txt_file = str(default_txt)
        else:
            txt_file = input("Enter TXT file path: ").strip()
        
        # Process
        result = workflow.process_txt_input(txt_file)
        
        # Display final status
        print("\n" + "="*70)
        print("Processing Result:")
        print("="*70)
        print(f"Status: {result['status']}")
        if result.get('facilities'):
            print(f"Facilities found: {len(result['facilities'])}")
        print("="*70 + "\n")
    
    elif choice == '2':
        # Interactive mode
        workflow.process_interactive()
    
    elif choice == '3':
        print("\n👋 Goodbye!")
        return
    
    else:
        print("\n❌ Invalid selection")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 User interrupted, exiting")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
