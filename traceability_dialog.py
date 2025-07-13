from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from collections import defaultdict
from PyQt5.QtWidgets import (QPushButton, QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox,
                             QAbstractItemView, QMenu, QDialog, QHBoxLayout, QScrollArea, QTreeWidget, QTreeWidgetItem,
                             QCheckBox, QGroupBox, QMessageBox, QFileDialog)


class TraceabilityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Traceability Network Generator")
        self.setGeometry(200, 200, 600, 700)
        self.parent_window = parent
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Generate Traceability Network")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px; color: #2c3e50;")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel("Create a traceability network showing relationships between different risk attributes.")
        desc_label.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-bottom: 20px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Root Selection
        root_group = QGroupBox("Select Root Type")
        root_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        root_layout = QVBoxLayout(root_group)

        self.root_combo = QComboBox()
        self.root_combo.addItems([
            "Risk Level", "Department", "Device", "Component", 
            "Life Cycle", "Severity", "Probability"
        ])
        root_layout.addWidget(self.root_combo)

        layout.addWidget(root_group)

        # Child Selection
        child_group = QGroupBox("Select Child Type")
        child_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        child_layout = QVBoxLayout(child_group)

        self.child_combo = QComboBox()
        self.child_combo.addItems([
            "Risk Level", "Department", "Device", "Component", 
            "Life Cycle", "Severity", "Probability"
        ])
        child_layout.addWidget(self.child_combo)

        layout.addWidget(child_group)

        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        self.include_risk_numbers = QCheckBox("Include Risk Numbers")
        self.include_risk_numbers.setChecked(True)
        options_layout.addWidget(self.include_risk_numbers)

        self.show_counts = QCheckBox("Show Child Counts")
        self.show_counts.setChecked(True)
        options_layout.addWidget(self.show_counts)

        layout.addWidget(options_group)

        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_label = QLabel("Select root and child types to see preview...")
        self.preview_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        preview_layout.addWidget(self.preview_label)

        layout.addWidget(preview_group)

        # Connect signals for preview
        self.root_combo.currentTextChanged.connect(self.update_preview)
        self.child_combo.currentTextChanged.connect(self.update_preview)

        # Buttons
        button_layout = QHBoxLayout()

        generate_button = QPushButton("Generate PDF")
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        generate_button.clicked.connect(self.generate_traceability_pdf)
        button_layout.addWidget(generate_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # Initial preview
        self.update_preview()

    def update_preview(self):
        """Update the preview text based on current selections"""
        root_type = self.root_combo.currentText()
        child_type = self.child_combo.currentText()
        
        if root_type == child_type:
            self.preview_label.setText("⚠️ Root and Child types should be different for meaningful traceability.")
            self.preview_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        else:
            preview_text = f"Will generate networks with:\n"
            preview_text += f"• Root: {root_type}\n"
            preview_text += f"• Children: {child_type}\n"
            preview_text += f"• Each {root_type} will show connected {child_type}s with Risk Numbers"
            
            self.preview_label.setText(preview_text)
            self.preview_label.setStyleSheet("color: #27ae60; font-weight: normal;")

    def get_column_index(self, field_type):
        """Get the column index for a given field type"""
        column_mapping = {
            "Risk Level": 14,  # RPN column
            "Department": 2,
            "Device": 3,
            "Component": 4,
            "Life Cycle": 5,
            "Severity": 12,
            "Probability": 13
        }
        return column_mapping.get(field_type, 0)

    def extract_data_for_traceability(self):
        """Extract data from the table for traceability analysis"""
        root_type = self.root_combo.currentText()
        child_type = self.child_combo.currentText()
        
        root_col = self.get_column_index(root_type)
        child_col = self.get_column_index(child_type)
        risk_no_col = 1  # Risk No. column
        
        data = defaultdict(list)
        table = self.parent_window.table_widget
        
        for row in range(table.rowCount()):
            # Get root value
            root_item = table.item(row, root_col)
            root_value = root_item.text().strip() if root_item else "Unknown"
            
            # Get child value
            child_item = table.item(row, child_col)
            child_value = child_item.text().strip() if child_item else "Unknown"
            
            # Get risk number
            risk_no_item = table.item(row, risk_no_col)
            risk_no = risk_no_item.text().strip() if risk_no_item else "Unknown"
            
            # Handle multiple values (comma-separated)
            if child_type in ["Device", "Component"]:
                child_values = [v.strip() for v in child_value.split(',') if v.strip()]
            else:
                child_values = [child_value] if child_value else []
            
            for child_val in child_values:
                if child_val and child_val != "Unknown":
                    data[root_value].append({
                        'child': child_val,
                        'risk_no': risk_no
                    })
        
        return data

    def create_network_diagram(self, root_name, children_data, ax):
        """Create a network diagram for a single root and its children"""
        ax.clear()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        # Root node position
        root_x, root_y = 2, 4
        root_width, root_height = 2, 0.8
        
        # Draw root node
        root_rect = patches.FancyBboxPatch(
            (root_x - root_width/2, root_y - root_height/2),
            root_width, root_height,
            boxstyle="round,pad=0.1",
            facecolor='#3498db',
            edgecolor='#2980b9',
            linewidth=2
        )
        ax.add_patch(root_rect)
        
        # Root text
        ax.text(root_x, root_y, root_name, ha='center', va='center', 
                fontsize=12, fontweight='bold', color='white')
        
        # Children nodes
        if not children_data:
            ax.text(5, 4, "No data available", ha='center', va='center', 
                   fontsize=10, style='italic', color='gray')
            return
        
        num_children = len(children_data)
        if num_children == 0:
            return
            
        # Calculate positions for children
        child_x = 6.5
        if num_children == 1:
            child_positions = [4]
        else:
            child_positions = np.linspace(1, 7, num_children)
        
        child_width, child_height = 2.5, 0.6
        
        for i, (child_name, risk_numbers) in enumerate(children_data.items()):
            child_y = child_positions[i]
            
            # Draw child node
            child_rect = patches.FancyBboxPatch(
                (child_x - child_width/2, child_y - child_height/2),
                child_width, child_height,
                boxstyle="round,pad=0.05",
                facecolor='#e74c3c',
                edgecolor='#c0392b',
                linewidth=1
            )
            ax.add_patch(child_rect)
            
            # Child text
            if self.include_risk_numbers.isChecked() and risk_numbers:
                risk_text = ", ".join(risk_numbers[:3])  # Show first 3 risk numbers
                if len(risk_numbers) > 3:
                    risk_text += f" (+{len(risk_numbers)-3})"
                child_text = f"{child_name}\n[{risk_text}]"
            else:
                child_text = child_name
                
            if self.show_counts.isChecked():
                child_text += f"\n({len(risk_numbers)} risks)"
            
            ax.text(child_x, child_y, child_text, ha='center', va='center', 
                   fontsize=9, color='white', fontweight='bold')
            
            # Draw connection line
            ax.plot([root_x + root_width/2, child_x - child_width/2], 
                   [root_y, child_y], 'k-', linewidth=2, alpha=0.7)
            
            # Add arrow
            ax.annotate('', xy=(child_x - child_width/2, child_y), 
                       xytext=(root_x + root_width/2, root_y),
                       arrowprops=dict(arrowstyle='->', lw=2, color='black', alpha=0.7))

    def generate_traceability_pdf(self):
        """Generate the traceability PDF"""
        root_type = self.root_combo.currentText()
        child_type = self.child_combo.currentText()
        
        if root_type == child_type:
            QMessageBox.warning(self, "Invalid Selection", 
                              "Root and Child types must be different!")
            return
        
        # Extract data
        data = self.extract_data_for_traceability()
        
        if not data:
            QMessageBox.information(self, "No Data", 
                                  "No data available for the selected criteria.")
            return
        
        # Get save location
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Traceability Network", 
            f"Traceability_{root_type}_to_{child_type}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not filename:
            return
        
        try:
            with PdfPages(filename) as pdf:
                for root_value, children_list in data.items():
                    if not children_list:
                        continue
                    
                    # Group children by name and collect risk numbers
                    children_grouped = defaultdict(list)
                    for item in children_list:
                        children_grouped[item['child']].append(item['risk_no'])
                    
                    # Create figure
                    fig, ax = plt.subplots(figsize=(12, 8))
                    fig.suptitle(f'Traceability Network: {root_type} → {child_type}', 
                               fontsize=16, fontweight='bold')
                    
                    # Create the network diagram
                    self.create_network_diagram(root_value, children_grouped, ax)
                    
                    # Add metadata
                    metadata_text = f"Root: {root_value} | Children: {len(children_grouped)} | "
                    metadata_text += f"Total Risks: {len(children_list)}"
                    fig.text(0.5, 0.02, metadata_text, ha='center', fontsize=10, 
                           style='italic', color='gray')
                    
                    plt.tight_layout()
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close(fig)
            
            QMessageBox.information(self, "Success", 
                                  f"Traceability network saved to:\n{filename}")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Failed to generate PDF:\n{str(e)}")

    def closeEvent(self, event):
        """Handle dialog close event"""
        event.accept()
