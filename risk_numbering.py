class RiskNumberGenerator:
    """Generate structured risk numbers with descriptive formatting"""
    
    def __init__(self):
        self.department_codes = {
            "Software Department": "SW",
            "Electrical Department": "ELC", 
            "Mechanical Department": "MEC",
            "Usability Team": "US",
            "Testing Team": "TEST"
        }
        
        # Track IDs for each component
        self.sequence_id_counter = {}
        self.situation_id_counter = {}
        self.harm_id_counter = {}
    
    def get_or_create_sequence_id(self, sequence_text):
        """Get existing ID or create new one for sequence"""
        if sequence_text not in self.sequence_id_counter:
            self.sequence_id_counter[sequence_text] = len(self.sequence_id_counter) + 1
        return self.sequence_id_counter[sequence_text]
    
    def get_or_create_situation_id(self, situation_text):
        """Get existing ID or create new one for hazardous situation"""
        if situation_text not in self.situation_id_counter:
            self.situation_id_counter[situation_text] = len(self.situation_id_counter) + 1
        return self.situation_id_counter[situation_text]
    
    def get_or_create_harm_id(self, harm_text):
        """Get existing ID or create new one for harm description"""
        if harm_text not in self.harm_id_counter:
            self.harm_id_counter[harm_text] = len(self.harm_id_counter) + 1
        return self.harm_id_counter[harm_text]
    
    def generate_risk_number(self, department, component, sequence_text, situation_text, harm_text):
        """Generate structured risk number"""
        dept_code = self.department_codes.get(department, "UNK")
        component_code = component.upper().replace(" ", "_")[:10]  # Limit length
        
        sequence_id = self.get_or_create_sequence_id(sequence_text)
        situation_id = self.get_or_create_situation_id(situation_text)
        harm_id = self.get_or_create_harm_id(harm_text)
        
        return f"RSK_{dept_code}_{component_code}_{sequence_id}_{situation_id}_{harm_id}"