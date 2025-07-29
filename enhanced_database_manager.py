import json
import os
from datetime import datetime
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt

class FixedEnhancedDatabaseManager:
    def __init__(self):
        self.database_dir = "Database"
        self.risks_file = os.path.join(self.database_dir, "risks_database.json")
        self.chat_file = os.path.join(self.database_dir, "chat_database.json")
        self.counters_file = os.path.join(self.database_dir, "counters.json")
        self.matrix_dir = "Risk Matrix"
        
        # Create directories if they don't exist
        os.makedirs(self.database_dir, exist_ok=True)
        os.makedirs(self.matrix_dir, exist_ok=True)
        
        print("✅ Fixed Enhanced Database Manager initialized")

    def save_all_risks(self, table_widget):
        """Save all risks from the table to JSON database - ENHANCED with error handling"""
        try:
            risks_data = []
            
            print(f"💾 Saving {table_widget.rowCount()} risks to database...")
            
            for row in range(table_widget.rowCount()):
                try:
                    risk_entry = {
                        'date': self.safe_get_cell_text(table_widget, row, 0),
                        'risk_number': self.safe_get_cell_text(table_widget, row, 1),
                        'department': self.safe_get_cell_text(table_widget, row, 2),
                        'device_affected': self.safe_get_cell_text(table_widget, row, 3),
                        'components': self.safe_get_cell_text(table_widget, row, 4),
                        'lifecycle': self.safe_get_cell_text(table_widget, row, 5),
                        'hazard_category': self.safe_get_cell_text(table_widget, row, 6),
                        'hazard_source': self.safe_get_cell_text(table_widget, row, 7),
                        'hazardous_situation': self.get_enhanced_hazardous_situation_data(table_widget, row, 8),
                        'sequence_of_events': self.get_sequence_data(table_widget, row, 9),
                        'harm_influenced': self.safe_get_cell_text(table_widget, row, 10),
                        'harm_description': self.get_enhanced_harm_description_data(table_widget, row, 11),
                        'severity': self.safe_get_cell_text(table_widget, row, 12),
                        'probability': self.safe_get_cell_text(table_widget, row, 13),
                        'rpn': self.safe_get_cell_text(table_widget, row, 14),
                        'risk_control_actions': self.get_control_data(table_widget, row, 15)
                    }
                    risks_data.append(risk_entry)
                except Exception as e:
                    print(f"⚠️ Error saving row {row}: {e}")
                    continue
        
            # Save to JSON file
            with open(self.risks_file, 'w', encoding='utf-8') as f:
                json.dump(risks_data, f, indent=2, ensure_ascii=False)
        
            print(f"✅ Successfully saved {len(risks_data)} risks to database")
            return True
            
        except Exception as e:
            print(f"❌ Error saving risks to database: {e}")
            return False

    def load_all_risks(self, table_widget, numbering_manager=None):
        """Load all risks from JSON database to table with comprehensive error handling"""
        if not os.path.exists(self.risks_file):
            print("📝 No risks database file found")
            return False
        
        try:
            with open(self.risks_file, 'r', encoding='utf-8') as f:
                risks_data = json.load(f)
        
            if not risks_data:
                print("📝 No risks data found in database")
                return False
            
            # Clear existing table
            table_widget.setRowCount(0)
            
            print(f"📊 Loading {len(risks_data)} risks from database...")
            
            loaded_count = 0
            for risk_data in risks_data:
                try:
                    row_position = table_widget.rowCount()
                    table_widget.insertRow(row_position)
                    
                    # Set basic cell data
                    self.safe_set_cell_text(table_widget, row_position, 0, risk_data.get('date', ''))
                    self.safe_set_cell_text(table_widget, row_position, 1, risk_data.get('risk_number', ''))
                    self.safe_set_cell_text(table_widget, row_position, 2, risk_data.get('department', ''))
                    self.safe_set_cell_text(table_widget, row_position, 3, risk_data.get('device_affected', ''))
                    self.safe_set_cell_text(table_widget, row_position, 4, risk_data.get('components', ''))
                    self.safe_set_cell_text(table_widget, row_position, 5, risk_data.get('lifecycle', ''))
                    self.safe_set_cell_text(table_widget, row_position, 6, risk_data.get('hazard_category', ''))
                    self.safe_set_cell_text(table_widget, row_position, 7, risk_data.get('hazard_source', ''))
                    
                    # Create and restore complex widgets
                    component_name = risk_data.get('components', '').split(',')[0].strip()
                    
                    self.create_hazardous_situation_widget(table_widget, row_position, risk_data, 
                                                     numbering_manager, component_name)
                    self.create_sequence_widget(table_widget, row_position, risk_data)
                    
                    self.safe_set_cell_text(table_widget, row_position, 10, risk_data.get('harm_influenced', ''))
                    
                    self.create_harm_description_widget(table_widget, row_position, risk_data, 
                                                  numbering_manager, component_name)
                    
                    self.safe_set_cell_text(table_widget, row_position, 12, risk_data.get('severity', ''))
                    self.safe_set_cell_text(table_widget, row_position, 13, risk_data.get('probability', ''))
                    self.safe_set_cell_text(table_widget, row_position, 14, risk_data.get('rpn', ''))
                    
                    # Create and restore control widget
                    self.create_control_widget(table_widget, row_position, risk_data)
                    
                    table_widget.setRowHeight(row_position, 200)
                    loaded_count += 1
                    
                except Exception as e:
                    print(f"⚠️ Error loading risk {risk_data.get('risk_number', 'unknown')}: {e}")
                    continue
        
            print(f"✅ Successfully loaded {loaded_count} risks from database")
            return True
            
        except Exception as e:
            print(f"❌ Error loading risks from database: {e}")
            return False

    def create_hazardous_situation_widget(self, table_widget, row_position, risk_data, numbering_manager, component_name):
        """Create hazardous situation widget with error handling"""
        try:
            hazardous_data = risk_data.get('hazardous_situation', {})
            
            # Try to import and create the widget
            try:
                from hazardous_situation_widget import HazardousSituationCardWidget
                
                if isinstance(hazardous_data, dict) and hazardous_data.get('situations'):
                    hazardous_widget = HazardousSituationCardWidget(
                        hazardous_data['situations'], 
                        numbering_manager=numbering_manager,
                        component_name=component_name
                    )
                else:
                    hazardous_widget = HazardousSituationCardWidget(
                        numbering_manager=numbering_manager,
                        component_name=component_name
                    )
                
                table_widget.setCellWidget(row_position, 8, hazardous_widget)
                print(f"✅ Created hazardous situation widget for row {row_position}")
                
            except ImportError as e:
                print(f"⚠️ Could not import HazardousSituationCardWidget: {e}")
                self.fallback_to_text_cell(table_widget, row_position, 8, hazardous_data)
            except Exception as e:
                print(f"⚠️ Error creating hazardous situation widget for row {row_position}: {e}")
                self.fallback_to_text_cell(table_widget, row_position, 8, hazardous_data)
                
        except Exception as e:
            print(f"❌ Critical error in hazardous situation widget creation: {e}")
            self.safe_set_cell_text(table_widget, row_position, 8, "")

    def safe_get_cell_text(self, table_widget, row, col):
        """Safely get text from table cell with error handling"""
        try:
            item = table_widget.item(row, col)
            return item.text() if item else ""
        except Exception as e:
            print(f"⚠️ Error getting cell text [{row}, {col}]: {e}")
            return ""

    def safe_set_cell_text(self, table_widget, row, col, text):
        """Safely set text to table cell with error handling"""
        try:
            if text is None:
                text = ""
            table_widget.setItem(row, col, QTableWidgetItem(str(text)))
        except Exception as e:
            print(f"⚠️ Error setting cell text [{row}, {col}]: {e}")
            try:
                # Fallback attempt
                table_widget.setItem(row, col, QTableWidgetItem(""))
            except:
                pass

    def create_sequence_widget(self, table_widget, row_position, risk_data):
        """Create sequence widget with error handling"""
        try:
            sequence_data = risk_data.get('sequence_of_events', {})
            
            try:
                from sequence_widget import SequenceEventWidget
                
                sequence_widget = SequenceEventWidget()
                if isinstance(sequence_data, dict) and sequence_data.get('events'):
                    for event in sequence_data['events']:
                        sequence_widget.add_sequence(event)
                
                table_widget.setCellWidget(row_position, 9, sequence_widget)
                print(f"✅ Created sequence widget for row {row_position}")
                
            except ImportError as e:
                print(f"⚠️ Could not import SequenceEventWidget: {e}")
                self.fallback_to_text_cell(table_widget, row_position, 9, sequence_data)
            except Exception as e:
                print(f"⚠️ Error creating sequence widget for row {row_position}: {e}")
                self.fallback_to_text_cell(table_widget, row_position, 9, sequence_data)
                
        except Exception as e:
            print(f"❌ Critical error in sequence widget creation: {e}")
            self.safe_set_cell_text(table_widget, row_position, 9, "")

    def create_harm_description_widget(self, table_widget, row_position, risk_data, numbering_manager, component_name):
        """Create harm description widget with error handling"""
        try:
            harm_data = risk_data.get('harm_description', {})
            selected_device = risk_data.get('device_affected', '').split(',')[0].strip() if risk_data.get('device_affected') else None
            
            try:
                from harm_description_widget import HarmDescriptionCardWidget
                
                if isinstance(harm_data, dict) and harm_data.get('harms'):
                    harm_widget = HarmDescriptionCardWidget(
                        harm_data['harms'],
                        harm_data.get('rpn_data', {}),
                        selected_device,
                        numbering_manager=numbering_manager,
                        component_name=component_name
                    )
                else:
                    harm_widget = HarmDescriptionCardWidget(
                        [],
                        {},
                        selected_device,
                        numbering_manager=numbering_manager,
                        component_name=component_name
                    )
                
                table_widget.setCellWidget(row_position, 11, harm_widget)
                print(f"✅ Created harm description widget for row {row_position}")
                
            except ImportError as e:
                print(f"⚠️ Could not import HarmDescriptionCardWidget: {e}")
                self.fallback_to_text_cell(table_widget, row_position, 11, harm_data)
            except Exception as e:
                print(f"⚠️ Error creating harm description widget for row {row_position}: {e}")
                self.fallback_to_text_cell(table_widget, row_position, 11, harm_data)
                
        except Exception as e:
            print(f"❌ Critical error in harm description widget creation: {e}")
            self.safe_set_cell_text(table_widget, row_position, 11, "")

    def create_control_widget(self, table_widget, row_position, risk_data):
        """Create control widget with error handling"""
        try:
            control_data = risk_data.get('risk_control_actions', {})
            
            try:
                from ControlAndRequirement import AddControlClass
                
                control_widget = AddControlClass()
                if isinstance(control_data, dict) and control_data.get('controls'):
                    for control in control_data['controls']:
                        control_widget.add_control(control)
                
                table_widget.setCellWidget(row_position, 15, control_widget)
                print(f"✅ Created control widget for row {row_position}")
                
            except ImportError as e:
                print(f"⚠️ Could not import AddControlClass: {e}")
                self.safe_set_cell_text(table_widget, row_position, 15, "")
            except Exception as e:
                print(f"⚠️ Error creating control widget for row {row_position}: {e}")
                self.safe_set_cell_text(table_widget, row_position, 15, "")
                
        except Exception as e:
            print(f"❌ Critical error in control widget creation: {e}")
            self.safe_set_cell_text(table_widget, row_position, 15, "")

    def fallback_to_text_cell(self, table_widget, row, col, data):
        """Fallback to text cell when widget creation fails"""
        try:
            fallback_text = ""
            if isinstance(data, dict):
                fallback_text = data.get('formatted_text', '')
                if not fallback_text and 'situations' in data:
                    fallback_text = "; ".join(data['situations'])
                elif not fallback_text and 'harms' in data:
                    fallback_text = "; ".join(data['harms'])
                elif not fallback_text and 'events' in data:
                    fallback_text = "; ".join(data['events'])
            elif isinstance(data, str):
                fallback_text = data
            
            self.safe_set_cell_text(table_widget, row, col, fallback_text)
            print(f"📝 Used text fallback for cell [{row}, {col}]: {fallback_text[:50]}...")
            
        except Exception as e:
            print(f"❌ Error in fallback for cell [{row}, {col}]: {e}")
            self.safe_set_cell_text(table_widget, row, col, "")

    def sort_table_by_component_number(self, table_widget, numbering_manager):
        """Sort table by component number with improved error handling"""
        if not numbering_manager:
            print("❌ No numbering manager provided for sorting")
            return False
        
        try:
            print("🔄 Starting comprehensive table sort by component number...")
            
            if table_widget.rowCount() == 0:
                print("📝 No rows to sort")
                return True
            
            # Collect all row data with component information
            rows_data = []
            for row in range(table_widget.rowCount()):
                try:
                    component_name = self.safe_get_cell_text(table_widget, row, 4).split(',')[0].strip()
                    risk_number = self.safe_get_cell_text(table_widget, row, 1)
                    component_number = numbering_manager.get_component_number(component_name)
                    
                    row_data = {
                        'row': row,
                        'component_name': component_name,
                        'component_number': component_number or float('inf'),  # Handle None case
                        'risk_number': risk_number,
                        'cells': []
                    }
                    
                    # Store all cell data and widgets
                    for col in range(table_widget.columnCount()):
                        cell_widget = table_widget.cellWidget(row, col)
                        cell_item = table_widget.item(row, col)
                        row_data['cells'].append({
                            'widget': cell_widget,
                            'text': cell_item.text() if cell_item else ''
                        })
                    
                    rows_data.append(row_data)
                    
                except Exception as e:
                    print(f"⚠️ Error collecting row {row} data: {e}")
                    continue
            
            if not rows_data:
                print("❌ No data collected for sorting")
                return False
            
            # Sort rows data
            rows_data.sort(key=lambda x: (x['component_number'], x['risk_number']))
            
            # Clear and rebuild table
            table_widget.setRowCount(0)
            
            # Rebuild table with sorted data
            for row_data in rows_data:
                try:
                    new_row = table_widget.rowCount()
                    table_widget.insertRow(new_row)
                    
                    for col, cell_data in enumerate(row_data['cells']):
                        if cell_data['widget']:
                            table_widget.setCellWidget(new_row, col, cell_data['widget'])
                        else:
                            self.safe_set_cell_text(table_widget, new_row, col, cell_data['text'])
                    
                    table_widget.setRowHeight(new_row, 200)
                    
                except Exception as e:
                    print(f"⚠️ Error restoring row for component {row_data['component_name']}: {e}")
                    continue
        
            print(f"✅ Successfully sorted {len(rows_data)} rows")
            return True
            
        except Exception as e:
            print(f"❌ Critical error sorting table: {e}")
            return False

    def get_database_stats(self):
        """Get statistics about the database with improved error handling"""
        stats = {
            'total_risks': 0,
            'database_size': 0,
            'last_modified': None,
            'departments': {},
            'risk_levels': {'High': 0, 'Medium': 0, 'Low': 0}
        }
        
        if os.path.exists(self.risks_file):
            try:
                # Get file stats
                file_stats = os.stat(self.risks_file)
                stats['database_size'] = file_stats.st_size
                stats['last_modified'] = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                # Load and analyze risks data
                with open(self.risks_file, 'r', encoding='utf-8') as f:
                    risks_data = json.load(f)
                    
                stats['total_risks'] = len(risks_data)
                
                for risk in risks_data:
                    try:
                        # Count by department
                        dept = risk.get('department', 'Unknown')
                        stats['departments'][dept] = stats['departments'].get(dept, 0) + 1
                        
                        # Count by risk level
                        rpn = int(risk.get('rpn', 0))
                        if rpn >= 15:
                            stats['risk_levels']['High'] += 1
                        elif rpn >= 8:
                            stats['risk_levels']['Medium'] += 1
                        else:
                            stats['risk_levels']['Low'] += 1
                    except:
                        continue
            
            except Exception as e:
                print(f"⚠️ Error getting database stats: {e}")
        
        return stats

    # All other database functions with error handling...
    def save_chat_data(self, chat_data):
        """Save chat data to JSON database"""
        try:
            with open(self.chat_file, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving chat data: {e}")
            return False

    def load_chat_data(self):
        """Load chat data from JSON database"""
        if not os.path.exists(self.chat_file):
            return {}
        
        try:
            with open(self.chat_file, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
            return chat_data
        except Exception as e:
            print(f"❌ Error loading chat data: {e}")
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
            
            return sw_counter, elc_counter, mec_counter, us_counter, test_counter
            
        except Exception as e:
            print(f"❌ Error loading counters: {e}")
            return 0, 0, 0, 0, 0

    def backup_database(self):
        """Create a backup of the current database"""
        try:
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
            
            print(f"✅ Created backup of {backup_count} files")
            return backup_count > 0
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False

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
