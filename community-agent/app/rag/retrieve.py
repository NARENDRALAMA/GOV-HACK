"""
RAG (Retrieval-Augmented Generation) System for Government Data

This module provides intelligent retrieval of government service information,
demographics, and requirements to power the agentic AI assistant.
"""

import csv
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
from datetime import datetime

class GovernmentDataRetriever:
    """Intelligent retriever for government datasets and information"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "data"
        self.service_locations = None
        self.abs_profiles = None
        self.howto_content = None
        self._load_datasets()
    
    def _load_datasets(self):
        """Load all government datasets into memory"""
        try:
            # Load service locations
            service_path = self.data_dir / "nsw_bdm_service_locations.csv"
            if service_path.exists():
                self.service_locations = pd.read_csv(service_path)
                print(f"✅ Loaded {len(self.service_locations)} service locations")
            
            # Load ABS demographics
            abs_path = self.data_dir / "abs_sa2_profile.csv"
            if abs_path.exists():
                self.abs_profiles = pd.read_csv(abs_path)
                print(f"✅ Loaded {len(self.abs_profiles)} ABS profiles")
            
            # Load how-to guides
            howto_path = self.data_dir / "birth_registration_howto.md"
            if howto_path.exists():
                with open(howto_path, 'r', encoding='utf-8') as f:
                    self.howto_content = f.read()
                print(f"✅ Loaded how-to guide ({len(self.howto_content)} characters)")
                
        except Exception as e:
            print(f"⚠️ Error loading datasets: {e}")
    
    def search_services(self, query: str, postcode: str = None) -> List[Dict]:
        """
        Find nearest service locations based on query and postcode
        
        Args:
            query: Service type (e.g., "birth registration", "medicare")
            postcode: Target postcode for proximity search
            
        Returns:
            List of service locations with distance ranking
        """
        if self.service_locations is None:
            return []
        
        # Filter by service type
        query_lower = query.lower()
        if "birth" in query_lower or "registration" in query_lower:
            service_type = "birth_registration"
        elif "medicare" in query_lower:
            service_type = "medicare_enrolment"
        else:
            service_type = None
        
        # Filter services
        if service_type:
            services = self.service_locations[
                self.service_locations['service_type'] == service_type
            ].copy()
        else:
            services = self.service_locations.copy()
        
        if len(services) == 0:
            return []
        
        # Add distance calculation if postcode provided
        if postcode:
            services['distance'] = services['postcode'].apply(
                lambda x: self._calculate_postcode_distance(str(x), str(postcode))
            )
            services = services.sort_values('distance')
        
        # Convert to list of dicts
        results = []
        for _, row in services.head(5).iterrows():  # Top 5 results
            service_info = {
                'name': row['name'],
                'address': f"{row['address']}, {row['suburb']} {row['postcode']}",
                'phone': row['phone'],
                'url': row['url'],
                'operating_hours': row['operating_hours'],
                'distance': row.get('distance', None)
            }
            results.append(service_info)
        
        return results
    
    def load_howto(self, topic: str) -> Dict:
        """
        Load relevant how-to information with source citations
        
        Args:
            topic: Topic to search for (e.g., "birth registration", "timeframe")
            
        Returns:
            Dictionary with content and source information
        """
        if self.howto_content is None:
            return {
                'content': 'How-to guide not available',
                'source_url': 'https://www.bdm.nsw.gov.au',
                'citations': []
            }
        
        # Extract relevant sections based on topic
        topic_lower = topic.lower()
        relevant_sections = []
        citations = []
        
        # Split content into sections
        sections = self.howto_content.split('## ')
        
        for section in sections:
            if topic_lower in section.lower():
                # Extract section title and content
                lines = section.strip().split('\n')
                if lines:
                    title = lines[0].strip()
                    content = '\n'.join(lines[1:]).strip()
                    relevant_sections.append(f"## {title}\n{content}")
        
        # Extract URLs as citations
        url_pattern = r'https?://[^\s\)]+'
        urls = re.findall(url_pattern, self.howto_content)
        citations = list(set(urls))
        
        return {
            'content': '\n\n'.join(relevant_sections) if relevant_sections else self.howto_content,
            'source_url': 'https://www.bdm.nsw.gov.au/Pages/births/birth-registration.aspx',
            'citations': citations,
            'topic': topic
        }
    
    def load_abs_profile(self, postcode: str) -> Dict:
        """
        Load ABS demographic profile for a postcode
        
        Args:
            postcode: Target postcode
            
        Returns:
            Dictionary with demographic information
        """
        if self.abs_profiles is None:
            return {}
        
        # Find exact postcode match
        profile = self.abs_profiles[
            self.abs_profiles['postcode'] == int(postcode)
        ]
        
        if len(profile) == 0:
            return {}
        
        row = profile.iloc[0]
        
        return {
            'postcode': str(row['postcode']),
            'suburb': row['suburb'],
            'state': row['state'],
            'lang_non_english_pct': float(row['lang_non_english_pct']),
            'median_age': int(row['median_age']),
            'median_income': int(row['median_income']),
            'population': int(row['population']),
            'indigenous_pct': float(row['indigenous_pct']),
            'disability_pct': float(row['disability_pct'])
        }
    
    def get_inclusivity_adjustments(self, postcode: str) -> Dict:
        """
        Get inclusivity adjustments based on demographic data
        
        Args:
            postcode: Target postcode
            
        Returns:
            Dictionary with inclusivity recommendations
        """
        profile = self.load_abs_profile(postcode)
        if not profile:
            return {}
        
        adjustments = {
            'postcode': postcode,
            'language_support': False,
            'accessibility_preferences': [],
            'communication_preferences': []
        }
        
        # Language support (if >40% non-English speaking)
        if profile.get('lang_non_english_pct', 0) > 40:
            adjustments['language_support'] = True
            adjustments['communication_preferences'].append('multilingual_support')
        
        # Age-based preferences (if median age >60)
        if profile.get('median_age', 0) > 60:
            adjustments['communication_preferences'].extend(['voice_updates', 'sms_updates'])
        
        # Disability considerations
        if profile.get('disability_pct', 0) > 10:
            adjustments['accessibility_preferences'].extend(['screen_reader', 'high_contrast', 'large_text'])
        
        # Indigenous community considerations
        if profile.get('indigenous_pct', 0) > 5:
            adjustments['accessibility_preferences'].append('cultural_sensitivity')
        
        return adjustments
    
    def _calculate_postcode_distance(self, postcode1: str, postcode2: str) -> int:
        """
        Calculate approximate distance between postcodes
        This is a simplified calculation - in production, use proper geocoding
        """
        try:
            p1, p2 = int(postcode1), int(postcode2)
            return abs(p1 - p2)
        except ValueError:
            return 9999  # High distance for invalid postcodes
    
    def search_knowledge_base(self, query: str) -> List[Dict]:
        """
        Search across all knowledge sources for relevant information
        
        Args:
            query: Search query
            
        Returns:
            List of relevant information snippets
        """
        results = []
        
        # Search how-to content
        if self.howto_content:
            howto_result = self.load_howto(query)
            if howto_result['content'] != 'How-to guide not available':
                results.append({
                    'type': 'howto',
                    'content': howto_result['content'][:200] + '...',
                    'source': howto_result['source_url'],
                    'relevance': 'high'
                })
        
        # Search service locations
        if self.service_locations is not None:
            service_results = self.search_services(query)
            for service in service_results[:2]:  # Top 2 services
                results.append({
                    'type': 'service_location',
                    'content': f"{service['name']} - {service['address']}",
                    'source': service['url'],
                    'relevance': 'medium'
                })
        
        return results

# Global instance
retriever = GovernmentDataRetriever()

# Convenience functions
def search_services(query: str, postcode: str = None) -> List[Dict]:
    """Find nearest service locations"""
    return retriever.search_services(query, postcode)

def load_howto(topic: str) -> Dict:
    """Load relevant how-to information"""
    return retriever.load_howto(topic)

def load_abs_profile(postcode: str) -> Dict:
    """Load ABS demographic profile"""
    return retriever.load_abs_profile(postcode)

def get_inclusivity_adjustments(postcode: str) -> Dict:
    """Get inclusivity adjustments based on demographics"""
    return retriever.get_inclusivity_adjustments(postcode)

def search_knowledge_base(query: str) -> List[Dict]:
    """Search across all knowledge sources"""
    return retriever.search_knowledge_base(query)
