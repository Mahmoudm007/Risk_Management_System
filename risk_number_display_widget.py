from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from risk_numbering import RiskNumberGenerator

class RiskNumberDisplayWidget(QWidget):
    """Widget to display structured risk numbers with sub-labels"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.risk_numbers = []
        self.risk_generator = RiskNumberGenerator()
        self.setupUI()
    
    def setupUI(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(2)
        
        # Primary risk number (larger, bold)
        self.primary_label = QLabel("")
        self.primary_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.primary_label.setStyleSheet("""
            color: #2c5aa0;
            background-color: #e8f4f8;
            border: 1px solid #2c5aa0;
            border-radius: 3px;
            padding: 3px;
        """)
        self.main_layout.addWidget(self.primary_label)
        
        # Scroll area for sub-risk numbers
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(100)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.sub_container = QWidget()
        self.sub_layout = QVBoxLayout(self.sub_container)
        self.sub_layout.setContentsMargins(2, 2, 2, 2)
        self.sub_layout.setSpacing(1)
        
        self.scroll_area.setWidget(self.sub_container)
        self.main_layout.addWidget(self.scroll_area)
    
    def update_risk_numbers(self, department, component, sequences, situations, harms):
        """Generate and display risk numbers for all combinations"""
        self.risk_numbers = []
        
        if not sequences or not situations or not harms:
            self.primary_label.setText("No risk combinations")
            self.clear_sub_numbers()
            return
        
        # Generate risk numbers for all combinations
        primary_risk = None
        for seq_idx, sequence in enumerate(sequences):
            for sit_idx, situation in enumerate(situations):
                for harm_idx, harm in enumerate(harms):
                    risk_number = self.risk_generator.generate_risk_number(
                        department, component, sequence, situation, harm['description']
                    )
                    
                    risk_data = {
                        'number': risk_number,
                        'sequence': sequence,
                        'situation': situation,
                        'harm': harm['description'],
                        'severity': harm['severity'],
                        'probability': harm['probability'],
                        'rpn': harm['rpn']
                    }
                    
                    self.risk_numbers.append(risk_data)
                    
                    # First combination becomes primary
                    if primary_risk is None:
                        primary_risk = risk_number
        
        # Display primary risk number
        if primary_risk:
            self.primary_label.setText(primary_risk)
        
        # Display sub-risk numbers
        self.update_sub_numbers()
    
    def update_sub_numbers(self):
        """Update the display of sub-risk numbers"""
        # Clear existing sub-widgets
        for i in reversed(range(self.sub_layout.count())):
            child = self.sub_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add sub-risk numbers (skip the first one as it's the primary)
        for i, risk_data in enumerate(self.risk_numbers[1:], 1):
            sub_widget = self.create_sub_risk_widget(risk_data, i)
            self.sub_layout.addWidget(sub_widget)
    
    def create_sub_risk_widget(self, risk_data, index):
        """Create a widget for a sub-risk number"""
        container = QFrame()
        container.setFrameStyle(QFrame.Box)
        container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px;
                margin: 1px;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(3, 3, 3, 3)
        
        # Sub-risk number
        risk_label = QLabel(f"└ {risk_data['number']}")
        risk_label.setFont(QFont("Arial", 8))
        risk_label.setStyleSheet("color: #6c757d; background: transparent; border: none;")
        layout.addWidget(risk_label, 1)
        
        # RPN indicator
        rpn_label = QLabel(risk_data['rpn'])
        rpn_color = {"High": "red", "Medium": "yellow", "Low": "green"}.get(risk_data['rpn'], "lightgray")
        rpn_label.setStyleSheet(f"""
            background-color: {rpn_color};
            color: black;
            border: 1px solid black;
            border-radius: 2px;
            padding: 1px 3px;
            font-size: 7px;
            font-weight: bold;
        """)
        rpn_label.setMaximumWidth(40)
        layout.addWidget(rpn_label)
        
        return container
    
    def clear_sub_numbers(self):
        """Clear all sub-risk number displays"""
        for i in reversed(range(self.sub_layout.count())):
            child = self.sub_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
    
    def get_all_risk_numbers(self):
        """Get all generated risk numbers"""
        return self.risk_numbers.copy()
    
    def get_primary_risk_number(self):
        """Get the primary risk number"""
        return self.risk_numbers[0]['number'] if self.risk_numbers else ""