from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette
import json
import os

class TreeSidebar(QWidget):
    """Tree sidebar widget for displaying hierarchical risk structure"""
    
    def __init__(self, parent=None, db_manager=None, numbering_manager=None):
        super().__init__(parent)
        self.parent_window = parent
        self.db_manager = db_manager
        self.numbering_manager = numbering_manager
        self.setFixedWidth(400)
        self.setupUI()
        self.refresh_tree()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_tree)
        self.refresh_timer.start(300000)  # Refresh every 5 seconds
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Risk Tree View")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setMaximumSize(25, 25)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.close_btn.clicked.connect(self.hide)
        header_layout.addWidget(self.close_btn)
        
        layout.addLayout(header_layout)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search risks, components...")
        self.search_box.textChanged.connect(self.filter_tree)
        layout.addWidget(self.search_box)
        
        # Tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Risk Hierarchy")
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Set tree style
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTreeWidget::item {
                padding: 3px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
            QTreeWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        
        layout.addWidget(self.tree_widget)
        
        # Statistics panel
        self.stats_label = QLabel("Statistics will appear here")
        self.stats_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.stats_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.expand_all_btn = QPushButton("Expand All")
        self.expand_all_btn.clicked.connect(self.tree_widget.expandAll)
        button_layout.addWidget(self.expand_all_btn)
        
        self.collapse_all_btn = QPushButton("Collapse All")
        self.collapse_all_btn.clicked.connect(self.tree_widget.collapseAll)
        button_layout.addWidget(self.collapse_all_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_tree)
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
        self.setGeometry(0, 0, 1900, 500)  # Set initial size and position
        self.setMinimumSize(900, 700)
        
    def refresh_tree(self):
        """Refresh the tree with current data from the main table"""
        if not self.parent_window:
            return
            
        self.tree_widget.clear()
        
        # Get data from main table
        table_widget = self.parent_window.table_widget
        if not table_widget:
            return
            
        # Create root node
        root_item = QTreeWidgetItem(self.tree_widget)
        root_item.setText(0, "🎯 All Risks")
        root_item.setFont(0, QFont("Arial", 12, QFont.Bold))
        root_item.setExpanded(True)
        
        # Group risks by component
        component_groups = {}
        risk_stats = {'total': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for row in range(table_widget.rowCount()):
            # Get risk data
            risk_no = self.get_cell_text(table_widget, row, 1)
            department = self.get_cell_text(table_widget, row, 2)
            components = self.get_cell_text(table_widget, row, 4)
            rpn = self.get_cell_text(table_widget, row, 14)
            
            if not components:
                components = "Unassigned"
                
            # Update statistics
            risk_stats['total'] += 1
            if rpn.upper() == 'HIGH':
                risk_stats['high'] += 1
            elif rpn.upper() == 'MEDIUM':
                risk_stats['medium'] += 1
            elif rpn.upper() == 'LOW':
                risk_stats['low'] += 1
            
            # Group by component
            for component in components.split(','):
                component = component.strip()
                if component not in component_groups:
                    component_groups[component] = []
                component_groups[component].append({
                    'row': row,
                    'risk_no': risk_no,
                    'department': department,
                    'rpn': rpn
                })
        
        # Create component nodes
        for component_name, risks in component_groups.items():
            component_item = QTreeWidgetItem(root_item)
            component_item.setText(0, f"🔧 {component_name} ({len(risks)} risks)")
            component_item.setFont(0, QFont("Arial", 10, QFont.Bold))
            component_item.setData(0, Qt.UserRole, {'type': 'component', 'name': component_name})
            
            # Add risks under component
            for risk_data in risks:
                risk_item = QTreeWidgetItem(component_item)
                risk_item.setText(0, f"📋 {risk_data['risk_no']} - {risk_data['department']}")
                risk_item.setData(0, Qt.UserRole, {
                    'type': 'risk', 
                    'row': risk_data['row'],
                    'risk_no': risk_data['risk_no']
                })
                
                # Set color based on RPN
                if risk_data['rpn'].upper() == 'HIGH':
                    risk_item.setBackground(0, risk_item.background(0).color().lighter(180))
                    risk_item.setForeground(0, risk_item.foreground(0).color().darker(150))
                
                # Add risk details
                self.add_risk_details(risk_item, risk_data['row'])
        
        # Update statistics
        self.update_statistics(risk_stats)
        
        # Expand root by default
        root_item.setExpanded(True)
        
    def add_risk_details(self, parent_item, row):
        """Add detailed risk information as child nodes"""
        table_widget = self.parent_window.table_widget
        
        # Hazardous Situations
        hazardous_widget = table_widget.cellWidget(row, 8)
        if hazardous_widget and hasattr(hazardous_widget, 'get_situations_list'):
            situations = hazardous_widget.get_situations_list()
            if situations:
                hazardous_item = QTreeWidgetItem(parent_item)
                hazardous_item.setText(0, f"⚠️ Hazardous Situations ({len(situations)})")
                hazardous_item.setFont(0, QFont("Arial", 9, QFont.Bold))
                
                for i, situation in enumerate(situations):
                    situation_item = QTreeWidgetItem(hazardous_item)
                    situation_item.setText(0, f"S{i+1}: {situation[:50]}{'...' if len(situation) > 50 else ''}")
                    situation_item.setToolTip(0, situation)
        
        # Harm Descriptions
        harm_widget = table_widget.cellWidget(row, 11)
        if harm_widget and hasattr(harm_widget, 'get_harms_list'):
            harms = harm_widget.get_harms_list()
            rpn_data = harm_widget.get_rpn_data() if hasattr(harm_widget, 'get_rpn_data') else {}
            
            if harms:
                harm_item = QTreeWidgetItem(parent_item)
                harm_item.setText(0, f"💔 Harm Descriptions ({len(harms)})")
                harm_item.setFont(0, QFont("Arial", 9, QFont.Bold))
                
                for i, harm in enumerate(harms):
                    harm_detail_item = QTreeWidgetItem(harm_item)
                    harm_text = f"H{i+1}: {harm[:50]}{'...' if len(harm) > 50 else ''}"
                    
                    # Add RPN info if available
                    if harm in rpn_data:
                        rpn_info = rpn_data[harm]
                        harm_text += f" [S:{rpn_info.get('severity', '?')} P:{rpn_info.get('probability', '?')} RPN:{rpn_info.get('rpn', '?')}]"
                    
                    harm_detail_item.setText(0, harm_text)
                    harm_detail_item.setToolTip(0, harm)
        
        # Risk Controls
        control_widget = table_widget.cellWidget(row, 15)
        if control_widget:
            control_item = QTreeWidgetItem(parent_item)
            control_item.setText(0, "🛡️ Risk Controls")
            control_item.setFont(0, QFont("Arial", 9, QFont.Bold))
            
            # Add placeholder for controls (you can expand this based on your control widget structure)
            control_detail = QTreeWidgetItem(control_item)
            control_detail.setText(0, "Control measures defined")
        
        # Sequence of Events
        sequence_widget = table_widget.cellWidget(row, 9)
        if sequence_widget and hasattr(sequence_widget, 'get_sequence_list'):
            sequences = sequence_widget.get_sequence_list()
            if sequences:
                sequence_item = QTreeWidgetItem(parent_item)
                sequence_item.setText(0, f"🔄 Sequence of Events ({len(sequences)})")
                sequence_item.setFont(0, QFont("Arial", 9, QFont.Bold))
                
                for i, sequence in enumerate(sequences):
                    seq_item = QTreeWidgetItem(sequence_item)
                    seq_item.setText(0, f"E{i+1}: {sequence[:50]}{'...' if len(sequence) > 50 else ''}")
                    seq_item.setToolTip(0, sequence)
    
    def get_cell_text(self, table_widget, row, col):
        """Safely get text from table cell"""
        item = table_widget.item(row, col)
        return item.text() if item else ""
    
    def update_statistics(self, stats):
        """Update the statistics panel"""
        stats_text = f"""
        📊 Risk Statistics:
        Total Risks: {stats['total']}
        🔴 High Risk: {stats['high']}
        🟡 Medium Risk: {stats['medium']}
        🟢 Low Risk: {stats['low']}
        """
        self.stats_label.setText(stats_text)
    
    def filter_tree(self, text):
        """Filter tree items based on search text"""
        def hide_item_recursive(item, hide):
            item.setHidden(hide)
            for i in range(item.childCount()):
                hide_item_recursive(item.child(i), hide)
        
        def search_item_recursive(item, search_text):
            # Check if current item matches
            item_matches = search_text.lower() in item.text(0).lower()
            
            # Check children
            child_matches = False
            for i in range(item.childCount()):
                if search_item_recursive(item.child(i), search_text):
                    child_matches = True
            
            # Show item if it or any child matches
            should_show = item_matches or child_matches
            item.setHidden(not should_show)
            
            return should_show
        
        if not text.strip():
            # Show all items if search is empty
            for i in range(self.tree_widget.topLevelItemCount()):
                hide_item_recursive(self.tree_widget.topLevelItem(i), False)
        else:
            # Filter items
            for i in range(self.tree_widget.topLevelItemCount()):
                search_item_recursive(self.tree_widget.topLevelItem(i), text)
    
    def on_item_clicked(self, item, column):
        """Handle item click"""
        data = item.data(0, Qt.UserRole)
        if data and data.get('type') == 'risk':
            # Highlight corresponding row in main table
            row = data.get('row')
            if row is not None and self.parent_window:
                self.parent_window.table_widget.selectRow(row)
                self.parent_window.table_widget.scrollToItem(
                    self.parent_window.table_widget.item(row, 0)
                )
    
    def on_item_double_clicked(self, item, column):
        """Handle item double click"""
        data = item.data(0, Qt.UserRole)
        if data and data.get('type') == 'risk':
            # Open risk details or edit dialog
            row = data.get('row')
            if row is not None and self.parent_window:
                # You can add custom logic here, like opening an edit dialog
                QMessageBox.information(self, "Risk Details", 
                                      f"Double-clicked on risk: {data.get('risk_no')}\n"
                                      f"Row: {row}")
