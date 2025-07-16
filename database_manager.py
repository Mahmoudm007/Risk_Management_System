import json
import os
from datetime import datetime
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget
from sequence_widget import SequenceEventWidget
from ControlAndRequirement import AddControlClass

class DatabaseManager:
    def __init__(self):
        self.database_dir = "Database"
        self.risks_file = os.path.join(self.database_dir, "risks_database.json")
        self.chat_file = os.path.join(self.database_dir, "chat_database.json")
        self.counters_file = os.path.join(self.database_dir, "counters.json")
        self.matrix_dir = "Risk Matrix"
        
        # Create directories if they don't exist
        os.makedirs(self.database_dir, exist_ok=True)
        os.makedirs(self.matrix_dir, exist_ok=True)

    def save_all_risks(self, table_widget):
        """Save all risks from the table to JSON database"""
        risks_data = []
        
        for row in range(table_widget.rowCount()):
            risk_data = {
                'row_id': row,
                'date': self.get_cell_text(table_widget, row, 0),
                'risk_no': self.get_cell_text(table_widget, row, 1),
                'department': self.get_cell_text(table_widget, row, 2),
                'device_affected': self.get_cell_text(table_widget, row, 3),
                'components': self.get_cell_text(table_widget, row, 4),
                'lifecycle': self.get_cell_text(table_widget, row, 5),
                'hazard_category': self.get_cell_text(table_widget, row, 6),
                'hazard_source': self.get_cell_text(table_widget, row, 7),
                'hazardous_situation': self.get_cell_text(table_widget, row, 8),
                'sequence_of_events': self.get_sequence_data(table_widget, row, 9),
                'harm_influenced': self.get_cell_text(table_widget, row, 10),
                'harm_description': self.get_cell_text(table_widget, row, 11),
                'severity': self.get_cell_text(table_widget, row, 12),
                'probability': self.get_cell_text(table_widget, row, 13),
                'rpn': self.get_cell_text(table_widget, row, 14),
                'risk_control_actions': self.get_control_data(table_widget, row, 15),
                'approved_by': self.get_cell_text(table_widget, row, 16),
                'created_timestamp': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat()
            }
            risks_data.append(risk_data)
        
        # Save to JSON file
        try:
            with open(self.risks_file, 'w', encoding='utf-8') as f:
                json.dump(risks_data, f, indent=2, ensure_ascii=False)
            # print(f"✅ Saved {len(risks_data)} risks to database")
            return True
        except Exception as e:
            # print(f"❌ Error saving risks: {e}")
            return False

    def load_all_risks(self, table_widget):
        """Load all risks from JSON database to table"""
        if not os.path.exists(self.risks_file):
            # print("📝 No existing risks database found")
            return False
        
        try:
            with open(self.risks_file, 'r', encoding='utf-8') as f:
                risks_data = json.load(f)
            
            # Clear existing table
            table_widget.setRowCount(0)
            
            # Load each risk
            for risk_data in risks_data:
                row_position = table_widget.rowCount()
                table_widget.insertRow(row_position)
                
                # Set basic cell data
                self.set_cell_text(table_widget, row_position, 0, risk_data.get('date', ''))
                self.set_cell_text(table_widget, row_position, 1, risk_data.get('risk_no', ''))
                self.set_cell_text(table_widget, row_position, 2, risk_data.get('department', ''))
                self.set_cell_text(table_widget, row_position, 3, risk_data.get('device_affected', ''))
                self.set_cell_text(table_widget, row_position, 4, risk_data.get('components', ''))
                self.set_cell_text(table_widget, row_position, 5, risk_data.get('lifecycle', ''))
                self.set_cell_text(table_widget, row_position, 6, risk_data.get('hazard_category', ''))
                self.set_cell_text(table_widget, row_position, 7, risk_data.get('hazard_source', ''))
                self.set_cell_text(table_widget, row_position, 8, risk_data.get('hazardous_situation', ''))
                
                # Set sequence widget
                sequence_data = risk_data.get('sequence_of_events', {})
                if sequence_data and sequence_data.get('events'):
                    sequence_widget = SequenceEventWidget()
                    sequence_widget.set_sequence(sequence_data['events'])
                    table_widget.setCellWidget(row_position, 9, sequence_widget)
                else:
                    # Create empty sequence widget
                    sequence_widget = SequenceEventWidget()
                    table_widget.setCellWidget(row_position, 9, sequence_widget)
                
                self.set_cell_text(table_widget, row_position, 10, risk_data.get('harm_influenced', ''))
                self.set_cell_text(table_widget, row_position, 11, risk_data.get('harm_description', ''))
                self.set_cell_text(table_widget, row_position, 12, risk_data.get('severity', ''))
                self.set_cell_text(table_widget, row_position, 13, risk_data.get('probability', ''))
                self.set_cell_text(table_widget, row_position, 14, risk_data.get('rpn', ''))
                
                # Set control widget
                control_data = risk_data.get('risk_control_actions', {})
                control_widget = AddControlClass()
                if control_data and control_data.get('controls'):
                    self.restore_control_widget(control_widget, control_data['controls'])
                table_widget.setCellWidget(row_position, 15, control_widget)
                
                self.set_cell_text(table_widget, row_position, 16, risk_data.get('approved_by', ''))
                
                # Set row height
                table_widget.setRowHeight(row_position, 180)
            
            # print(f"✅ Loaded {len(risks_data)} risks from database")
            return True
            
        except Exception as e:
            # print(f"❌ Error loading risks: {e}")
            return False

    def save_chat_data(self, chat_data):
        """Save chat data to JSON database"""
        try:
            with open(self.chat_file, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
            # print("✅ Chat data saved to database")
            return True
        except Exception as e:
            # print(f"❌ Error saving chat data: {e}")
            return False

    def load_chat_data(self):
        """Load chat data from JSON database"""
        if not os.path.exists(self.chat_file):
            return {}
        
        try:
            with open(self.chat_file, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
            # print("✅ Chat data loaded from database")
            return chat_data
        except Exception as e:
            # print(f"❌ Error loading chat data: {e}")
            return {}

    def save_counters(self, sw_counter, elc_counter, mec_counter, us_counter, test_counter):
        """Save department counters to database"""
        counters_data = {
            'sw_counter': sw_counter,
            'elc_counter': elc_counter,
            'mec_counter': mec_counter,
            'us_counter': us_counter,
            'test_counter': test_counter,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(self.counters_file, 'w', encoding='utf-8') as f:
                json.dump(counters_data, f, indent=2)
            # print("✅ Counters saved to database")
            return True
        except Exception as e:
            print(f"❌ Error saving counters: {e}")
            return False

    def load_counters(self):
        """Load department counters from database"""
        if not os.path.exists(self.counters_file):
            return 0, 0, 0, 0, 0
        
        try:
            with open(self.counters_file, 'r', encoding='utf-8') as f:
                counters_data = json.load(f)
            
            sw_counter = counters_data.get('sw_counter', 0)
            elc_counter = counters_data.get('elc_counter', 0)
            mec_counter = counters_data.get('mec_counter', 0)
            us_counter = counters_data.get('us_counter', 0)
            test_counter = counters_data.get('test_counter', 0)
            
            # print("✅ Counters loaded from database")
            return sw_counter, elc_counter, mec_counter, us_counter, test_counter
            
        except Exception as e:
            print(f"❌ Error loading counters: {e}")
            return 0, 0, 0, 0, 0

    def get_cell_text(self, table_widget, row, col):
        """Get text from table cell"""
        item = table_widget.item(row, col)
        return item.text() if item else ""

    def set_cell_text(self, table_widget, row, col, text):
        """Set text to table cell"""
        table_widget.setItem(row, col, QTableWidgetItem(str(text)))

    def get_sequence_data(self, table_widget, row, col):
        """Get sequence data from sequence widget"""
        widget = table_widget.cellWidget(row, col)
        if isinstance(widget, SequenceEventWidget):
            return {
                'events': widget.get_sequence_list(),
                'formatted_text': widget.get_sequence_text()
            }
        return {}

    def get_control_data(self, table_widget, row, col):
        """Get control data from control widget"""
        widget = table_widget.cellWidget(row, col)
        if isinstance(widget, AddControlClass):
            controls = []
            root = widget.tree.invisibleRootItem()
            for i in range(root.childCount()):
                item = root.child(i)
                control_data = {
                    'text': item.text(0),
                    'type': item.text(1),
                    'children': []
                }
                
                # Get children
                for j in range(item.childCount()):
                    child = item.child(j)
                    control_data['children'].append({
                        'text': child.text(0),
                        'type': child.text(1)
                    })
                
                controls.append(control_data)
            
            return {'controls': controls}
        return {}

    def restore_control_widget(self, control_widget, controls_data):
        """Restore control widget from saved data"""
        from PyQt5.QtWidgets import QTreeWidgetItem
        
        for control_data in controls_data:
            # Create parent item
            parent_item = QTreeWidgetItem([control_data['text'], control_data['type']])
            control_widget.tree.addTopLevelItem(parent_item)
            
            # Add children
            for child_data in control_data.get('children', []):
                child_item = QTreeWidgetItem([child_data['text'], child_data['type']])
                parent_item.addChild(child_item)
            
            parent_item.setExpanded(True)

    def backup_database(self):
        """Create a backup of the current database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(self.database_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        files_to_backup = [
            (self.risks_file, f"risks_backup_{timestamp}.json"),
            (self.chat_file, f"chat_backup_{timestamp}.json"),
            (self.counters_file, f"counters_backup_{timestamp}.json")
        ]
        
        backup_count = 0
        for source_file, backup_name in files_to_backup:
            if os.path.exists(source_file):
                try:
                    backup_path = os.path.join(backup_dir, backup_name)
                    with open(source_file, 'r', encoding='utf-8') as src:
                        with open(backup_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                    backup_count += 1
                except Exception as e:
                    print(f"❌ Error backing up {source_file}: {e}")
        
        # print(f"✅ Created backup of {backup_count} database files")
        return backup_count > 0

    def get_database_stats(self):
        """Get statistics about the database"""
        stats = {
            'total_risks': 0,
            'database_size': 0,
            'last_modified': None,
            'departments': {},
            'risk_levels': {'High': 0, 'Medium': 0, 'Low': 0}
        }
        
        if os.path.exists(self.risks_file):
            try:
                # Get file size
                stats['database_size'] = os.path.getsize(self.risks_file)
                stats['last_modified'] = datetime.fromtimestamp(
                    os.path.getmtime(self.risks_file)
                ).isoformat()
                
                # Load and analyze data
                with open(self.risks_file, 'r', encoding='utf-8') as f:
                    risks_data = json.load(f)
                
                stats['total_risks'] = len(risks_data)
                
                # Count by department and risk level
                for risk in risks_data:
                    dept = risk.get('department', 'Unknown')
                    stats['departments'][dept] = stats['departments'].get(dept, 0) + 1
                    
                    rpn = risk.get('rpn', '')
                    if rpn in stats['risk_levels']:
                        stats['risk_levels'][rpn] += 1
                        
            except Exception as e:
                print(f"❌ Error getting database stats: {e}")
        
        return stats
