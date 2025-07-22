import json
import os
from datetime import datetime

class RiskNumberingManager:
    """Manages the comprehensive risk numbering system - UPDATED VERSION"""
    
    def __init__(self):
        self.numbering_file = "Database/risk_numbering.json"
        self.component_numbers = {}  # component_name -> number
        self.sequence_counters = {}  # component_name -> current_sequence_count
        self.hazardous_situation_counts = {}  # component_name -> current_count
        self.harm_description_counts = {}  # component_name -> current_count
        self.next_component_number = 1
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(self.numbering_file), exist_ok=True)
        
        # Load existing numbering data
        self.load_numbering_data()
    
    def load_numbering_data(self):
        """Load numbering data from file"""
        try:
            if os.path.exists(self.numbering_file):
                with open(self.numbering_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.component_numbers = data.get('component_numbers', {})
                self.sequence_counters = data.get('sequence_counters', {})
                self.hazardous_situation_counts = data.get('hazardous_situation_counts', {})
                self.harm_description_counts = data.get('harm_description_counts', {})
                self.next_component_number = data.get('next_component_number', 1)
                
                print(f"✅ Loaded numbering data: {len(self.component_numbers)} components tracked")
            else:
                print("📝 No existing numbering data found, starting fresh")
                
        except Exception as e:
            print(f"❌ Error loading numbering data: {e}")
            # Initialize with defaults
            self.component_numbers = {}
            self.sequence_counters = {}
            self.hazardous_situation_counts = {}
            self.harm_description_counts = {}
            self.next_component_number = 1
    
    def save_numbering_data(self):
        """Save numbering data to file"""
        try:
            data = {
                'component_numbers': self.component_numbers,
                'sequence_counters': self.sequence_counters,
                'hazardous_situation_counts': self.hazardous_situation_counts,
                'harm_description_counts': self.harm_description_counts,
                'next_component_number': self.next_component_number,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.numbering_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved numbering data: {len(self.component_numbers)} components")
            return True
            
        except Exception as e:
            print(f"❌ Error saving numbering data: {e}")
            return False
    
    def get_component_number_for_preview(self, component_name):
        """Get component number for preview WITHOUT assigning a new number"""
        if not component_name or component_name.strip() == "":
            return "000"
        
        component_name = component_name.strip()
        
        # If component already has a number, return it
        if component_name in self.component_numbers:
            return f"{self.component_numbers[component_name]:03d}"
        
        # For preview, return what the NEXT number would be
        return f"{self.next_component_number:03d}"
    
    def assign_component_number(self, component_name):
        """Actually assign a number to a component (only when risk is added)"""
        if not component_name or component_name.strip() == "":
            return "000"
        
        component_name = component_name.strip()
        
        # Only assign if not already assigned
        if component_name not in self.component_numbers:
            self.component_numbers[component_name] = self.next_component_number
            self.next_component_number += 1
            self.save_numbering_data()
            print(f"🔢 Assigned number {self.component_numbers[component_name]:03d} to component: {component_name}")
        
        return f"{self.component_numbers[component_name]:03d}"
    
    def get_component_number(self, component_name):
        """Get existing component number (returns 000 if not assigned)"""
        if not component_name or component_name.strip() == "":
            return "000"
        
        component_name = component_name.strip()
        
        if component_name in self.component_numbers:
            return f"{self.component_numbers[component_name]:03d}"
        else:
            return "000"  # Not assigned yet
    
    def increment_sequence_counter(self, component_name):
        """Increment sequence counter for a component"""
        if not component_name or component_name.strip() == "":
            return 1
        
        component_name = component_name.strip()
        
        # Ensure component has a number assigned first
        self.assign_component_number(component_name)
        
        if component_name not in self.sequence_counters:
            self.sequence_counters[component_name] = 0
        
        self.sequence_counters[component_name] += 1
        self.save_numbering_data()
        print(f"🔄 Incremented sequence counter for {component_name}: {self.sequence_counters[component_name]}")
        return self.sequence_counters[component_name]
    
    def get_current_sequence_count(self, component_name):
        """Get current sequence count for a component"""
        if not component_name or component_name.strip() == "":
            return 0
        
        component_name = component_name.strip()
        return self.sequence_counters.get(component_name, 0)
    
    def update_hazardous_situation_count(self, component_name, count):
        """Update hazardous situation count for a component"""
        if not component_name or component_name.strip() == "":
            return
        
        component_name = component_name.strip()
        self.hazardous_situation_counts[component_name] = count
        self.save_numbering_data()
    
    def update_harm_description_count(self, component_name, count):
        """Update harm description count for a component"""
        if not component_name or component_name.strip() == "":
            return
        
        component_name = component_name.strip()
        self.harm_description_counts[component_name] = count
        self.save_numbering_data()
    
    def get_hazardous_situation_count(self, component_name):
        """Get hazardous situation count for a component"""
        if not component_name or component_name.strip() == "":
            return 1
        
        component_name = component_name.strip()
        return max(1, self.hazardous_situation_counts.get(component_name, 0))
    
    def get_harm_description_count(self, component_name):
        """Get harm description count for a component"""
        if not component_name or component_name.strip() == "":
            return 1
        
        component_name = component_name.strip()
        return max(1, self.harm_description_counts.get(component_name, 0))
    
    def generate_risk_number_preview(self, department, component_name, sequence_count=None, 
                                   hazardous_count=None, harm_count=None):
        """Generate risk number for PREVIEW only (doesn't assign component number)"""
        # Department prefix mapping
        dept_prefixes = {
            "Software Department": "SW",
            "Electrical Department": "ELC", 
            "Mechanical Department": "MEC",
            "Usability Team": "US",
            "Testing Team": "TEST"
        }
        
        dept_prefix = dept_prefixes.get(department, "UNK")
        component_num = self.get_component_number_for_preview(component_name)
        
        # Use provided counts or defaults for preview
        if sequence_count is None:
            sequence_count = 1
        if hazardous_count is None:
            hazardous_count = 1
        if harm_count is None:
            harm_count = 1
        
        # Ensure minimum values
        sequence_count = max(1, sequence_count)
        hazardous_count = max(1, hazardous_count)
        harm_count = max(1, harm_count)
        
        risk_number = f"{dept_prefix}-RSK-{component_num}-{sequence_count:02d}-{hazardous_count:02d}-{harm_count:02d}"
        return risk_number
    
    def generate_risk_number(self, department, component_name, sequence_count=None, 
                           hazardous_count=None, harm_count=None):
        """Generate complete risk number (assigns component number if needed)"""
        # Department prefix mapping
        dept_prefixes = {
            "Software Department": "SW",
            "Electrical Department": "ELC", 
            "Mechanical Department": "MEC",
            "Usability Team": "US",
            "Testing Team": "TEST"
        }
        
        dept_prefix = dept_prefixes.get(department, "UNK")
        component_num = self.assign_component_number(component_name)  # This assigns if needed
        
        # Use provided counts or get current counts
        if sequence_count is None:
            sequence_count = self.get_current_sequence_count(component_name)
        if hazardous_count is None:
            hazardous_count = self.get_hazardous_situation_count(component_name)
        if harm_count is None:
            harm_count = self.get_harm_description_count(component_name)
        
        # Ensure minimum values
        sequence_count = max(1, sequence_count)
        hazardous_count = max(1, hazardous_count)
        harm_count = max(1, harm_count)
        
        risk_number = f"{dept_prefix}-RSK-{component_num}-{sequence_count:02d}-{hazardous_count:02d}-{harm_count:02d}"
        print(f"🏷️ Generated risk number: {risk_number}")
        return risk_number
    
    def get_component_list_sorted(self):
        """Get list of components sorted by their numbers"""
        if not self.component_numbers:
            return []
        
        # Sort by component number
        sorted_components = sorted(self.component_numbers.items(), key=lambda x: x[1])
        return [comp[0] for comp in sorted_components]
    
    def get_component_stats(self):
        """Get statistics about components"""
        stats = {
            'total_components': len(self.component_numbers),
            'next_number': self.next_component_number,
            'components_with_risks': len([c for c in self.sequence_counters.values() if c > 0])
        }
        return stats
    
    def get_risks_for_component(self, component_name):
        """Get risk count information for a component"""
        return {
            'component_number': self.component_numbers.get(component_name, 0),
            'total_risks': self.sequence_counters.get(component_name, 0),
            'hazardous_situations': self.hazardous_situation_counts.get(component_name, 0),
            'harm_descriptions': self.harm_description_counts.get(component_name, 0)
        }
