from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPolygonF
import math

class TraceabilityGraphWidget(QWidget):
    """Clean, organized traceability graph matching the reference design"""
    
    node_clicked = pyqtSignal(dict)
    
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.parent_window = parent
        self.db_manager = db_manager
        self.nodes = []
        self.connections = []
        self.selected_node = None
        self.zoom_factor = 1.0
        self.pan_offset = QPointF(0, 0)
        self.last_pan_point = QPointF()
        self.is_panning = False
        
        # Layout constants for clean organization
        self.NODE_WIDTH = 200
        self.NODE_HEIGHT = 50
        self.HORIZONTAL_SPACING = 250
        self.VERTICAL_SPACING = 80
        self.COMPONENT_SPACING = 400
        
        self.setMinimumSize(1000, 700)
        self.setMouseTracking(True)
        self.build_clean_graph()
        
    def build_clean_graph(self):
        """Build a clean, organized graph structure"""
        if not self.parent_window:
            return
            
        self.nodes.clear()
        self.connections.clear()
        
        table_widget = self.parent_window.table_widget
        if not table_widget:
            return
        
        # Root node - centered at top
        root_node = {
            'id': 'root',
            'label': 'Risks',
            'type': 'root',
            'pos': QPointF(400, 50),
            'size': QPointF(self.NODE_WIDTH, self.NODE_HEIGHT),
            'color': QColor('#1e5f74'),
            'data': {}
        }
        self.nodes.append(root_node)
        
        # Group risks by component
        component_groups = {}
        for row in range(table_widget.rowCount()):
            components = self.get_cell_text(table_widget, row, 4)
            if not components:
                components = "Unassigned"
                
            for component in components.split(','):
                component = component.strip()
                if component not in component_groups:
                    component_groups[component] = []
                component_groups[component].append(row)
        
        # Calculate layout positions
        num_components = len(component_groups)
        start_x = 100
        
        for comp_index, (component_name, risk_rows) in enumerate(component_groups.items()):
            component_x = start_x + (comp_index * 600)  # Spread components horizontally
            
            # Component node
            comp_node = {
                'id': f'comp_{comp_index}',
                'label': f'Component {comp_index + 1}\n{component_name}',
                'type': 'component',
                'pos': QPointF(component_x, 150),
                'size': QPointF(self.NODE_WIDTH, self.NODE_HEIGHT),
                'color': QColor('#1e5f74'),
                'data': {'component': component_name, 'risk_count': len(risk_rows)}
            }
            self.nodes.append(comp_node)
            self.connections.append(('root', comp_node['id']))
            
            # Create sequence nodes for each risk
            for risk_index, row in enumerate(risk_rows):
                sequence_y = 250 + (risk_index * self.COMPONENT_SPACING)
                self.create_clean_risk_sequence(row, comp_node['id'], component_x, sequence_y, comp_index, risk_index)
    
    def create_clean_risk_sequence(self, row, parent_comp_id, base_x, base_y, comp_index, risk_index):
        """Create a clean risk sequence following the reference design"""
        table_widget = self.parent_window.table_widget
        
        risk_no = self.get_cell_text(table_widget, row, 1)
        rpn = self.get_cell_text(table_widget, row, 14)
        severity = self.get_cell_text(table_widget, row, 12)
        probability = self.get_cell_text(table_widget, row, 13)
        
        # Sequence of Event node
        sequence_node = {
            'id': f'seq_{comp_index}_{risk_index}',
            'label': f'Sequence of Event {risk_index + 1}',
            'type': 'sequence',
            'pos': QPointF(base_x, base_y),
            'size': QPointF(self.NODE_WIDTH, self.NODE_HEIGHT),
            'color': QColor('#1e5f74'),
            'data': {'risk_no': risk_no, 'row': row}
        }
        self.nodes.append(sequence_node)
        self.connections.append((parent_comp_id, sequence_node['id']))
        
        # Three main branches from sequence
        branch_x = base_x + self.HORIZONTAL_SPACING
        
        # 1. Hazardous Situations
        hazardous_node = {
            'id': f'hazard_{comp_index}_{risk_index}',
            'label': 'Hazardous situations',
            'type': 'hazardous',
            'pos': QPointF(branch_x, base_y - self.VERTICAL_SPACING),
            'size': QPointF(self.NODE_WIDTH, self.NODE_HEIGHT),
            'color': QColor('#1e5f74'),
            'data': self.get_hazardous_situations_data(row)
        }
        self.nodes.append(hazardous_node)
        self.connections.append((sequence_node['id'], hazardous_node['id']))
        
        # 2. Harm Description
        harm_node = {
            'id': f'harm_{comp_index}_{risk_index}',
            'label': 'Harm description',
            'type': 'harm',
            'pos': QPointF(branch_x, base_y),
            'size': QPointF(self.NODE_WIDTH, self.NODE_HEIGHT),
            'color': QColor('#1e5f74'),
            'data': self.get_harm_description_data(row)
        }
        self.nodes.append(harm_node)
        self.connections.append((sequence_node['id'], harm_node['id']))
        
        # Harm description sub-branches
        harm_branch_x = branch_x + self.HORIZONTAL_SPACING
        harm_branches = [
            {'id': f'severity_{comp_index}_{risk_index}', 'label': 'Severity', 'y_offset': -40, 'data': {'severity': severity}},
            {'id': f'probability_{comp_index}_{risk_index}', 'label': 'Probability', 'y_offset': 0, 'data': {'probability': probability}},
            {'id': f'rpn_{comp_index}_{risk_index}', 'label': 'RPN', 'y_offset': 40, 'data': {'rpn': rpn}}
        ]
        
        for branch in harm_branches:
            branch_node = {
                'id': branch['id'],
                'label': branch['label'],
                'type': 'detail',
                'pos': QPointF(harm_branch_x, base_y + branch['y_offset']),
                'size': QPointF(self.NODE_WIDTH, self.NODE_HEIGHT),
                'color': QColor('#1e5f74'),
                'data': branch['data']
            }
            self.nodes.append(branch_node)
            self.connections.append((harm_node['id'], branch_node['id']))
        
        # 3. Risk Control
        control_node = {
            'id': f'control_{comp_index}_{risk_index}',
            'label': 'Risk Control',
            'type': 'control',
            'pos': QPointF(branch_x, base_y + self.VERTICAL_SPACING),
            'size': QPointF(self.NODE_WIDTH, self.NODE_HEIGHT),
            'color': QColor('#1e5f74'),
            'data': {'row': row}
        }
        self.nodes.append(control_node)
        self.connections.append((sequence_node['id'], control_node['id']))
        
        # Risk control sub-branches
        control_branch_x = branch_x + self.HORIZONTAL_SPACING
        control_branches = [
            {'id': f'inherent_{comp_index}_{risk_index}', 'label': 'Inherently safe design', 'y_offset': -40},
            {'id': f'protective_{comp_index}_{risk_index}', 'label': 'Protective measure', 'y_offset': 0},
            {'id': f'information_{comp_index}_{risk_index}', 'label': 'Information for Safety', 'y_offset': 40}
        ]
        
        for branch in control_branches:
            branch_node = {
                'id': branch['id'],
                'label': branch['label'],
                'type': 'control_detail',
                'pos': QPointF(control_branch_x, base_y + self.VERTICAL_SPACING + branch['y_offset']),
                'size': QPointF(self.NODE_WIDTH, self.NODE_HEIGHT),
                'color': QColor('#1e5f74'),
                'data': {}
            }
            self.nodes.append(branch_node)
            self.connections.append((control_node['id'], branch_node['id']))
    
    def get_hazardous_situations_data(self, row):
        """Get hazardous situations data from the table"""
        table_widget = self.parent_window.table_widget
        hazardous_widget = table_widget.cellWidget(row, 8)
        
        if hazardous_widget and hasattr(hazardous_widget, 'get_situations_list'):
            situations = hazardous_widget.get_situations_list()
            return {'situations': situations, 'count': len(situations)}
        
        return {'situations': [], 'count': 0}
    
    def get_harm_description_data(self, row):
        """Get harm description data from the table"""
        table_widget = self.parent_window.table_widget
        harm_widget = table_widget.cellWidget(row, 11)
        
        data = {'harms': [], 'count': 0, 'rpn_data': {}}
        
        if harm_widget and hasattr(harm_widget, 'get_harms_list'):
            harms = harm_widget.get_harms_list()
            data['harms'] = harms
            data['count'] = len(harms)
            
            if hasattr(harm_widget, 'get_rpn_data'):
                data['rpn_data'] = harm_widget.get_rpn_data()
        
        return data
    
    def get_cell_text(self, table_widget, row, col):
        """Safely get text from table cell"""
        item = table_widget.item(row, col)
        return item.text() if item else ""
    
    def paintEvent(self, event):
        """Paint the clean graph"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor('#f8f9fa'))
        
        # Apply zoom and pan transformations
        painter.scale(self.zoom_factor, self.zoom_factor)
        painter.translate(self.pan_offset)
        
        # Draw connections first
        self.draw_clean_connections(painter)
        
        # Draw nodes
        self.draw_clean_nodes(painter)
    
    def draw_clean_connections(self, painter):
        """Draw clean connections with proper arrows"""
        pen = QPen(QColor('#2c5f7a'), 2)
        painter.setPen(pen)
        
        for from_id, to_id in self.connections:
            from_node = self.find_node(from_id)
            to_node = self.find_node(to_id)
            
            if from_node and to_node:
                # Calculate clean connection points
                from_center = QPointF(
                    from_node['pos'].x() + from_node['size'].x() / 2,
                    from_node['pos'].y() + from_node['size'].y() / 2
                )
                to_center = QPointF(
                    to_node['pos'].x() + to_node['size'].x() / 2,
                    to_node['pos'].y() + to_node['size'].y() / 2
                )
                
                # Determine connection points based on relative positions
                if from_center.x() < to_center.x():  # Left to right
                    from_point = QPointF(from_node['pos'].x() + from_node['size'].x(), from_center.y())
                    to_point = QPointF(to_node['pos'].x(), to_center.y())
                else:  # Right to left or vertical
                    from_point = QPointF(from_center.x(), from_node['pos'].y() + from_node['size'].y())
                    to_point = QPointF(to_center.x(), to_node['pos'].y())
                
                # Draw straight line
                painter.drawLine(from_point, to_point)
                
                # Draw arrow
                self.draw_clean_arrow(painter, from_point, to_point)
    
    def draw_clean_arrow(self, painter, from_point, to_point):
        """Draw a clean arrow"""
        # Calculate direction
        dx = to_point.x() - from_point.x()
        dy = to_point.y() - from_point.y()
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
        
        # Normalize
        dx /= length
        dy /= length
        
        # Arrow dimensions
        arrow_length = 12
        arrow_width = 6
        
        # Calculate arrow points
        arrow_tip = to_point
        arrow_base1 = QPointF(
            to_point.x() - arrow_length * dx + arrow_width * dy,
            to_point.y() - arrow_length * dy - arrow_width * dx
        )
        arrow_base2 = QPointF(
            to_point.x() - arrow_length * dx - arrow_width * dy,
            to_point.y() - arrow_length * dy + arrow_width * dx
        )
        
        # Draw filled arrow
        arrow_polygon = QPolygonF([arrow_tip, arrow_base1, arrow_base2])
        painter.setBrush(QBrush(QColor('#2c5f7a')))
        painter.drawPolygon(arrow_polygon)
    
    def draw_clean_nodes(self, painter):
        """Draw clean, uniform nodes"""
        for node in self.nodes:
            self.draw_clean_node(painter, node)
    
    def draw_clean_node(self, painter, node):
        """Draw a single clean node"""
        rect = QRectF(node['pos'], node['size'])
        
        # Set style based on selection
        if node == self.selected_node:
            pen = QPen(QColor('#000000'), 3)
            brush = QBrush(node['color'].lighter(110))
        else:
            pen = QPen(QColor('#ffffff'), 2)
            brush = QBrush(node['color'])
        
        painter.setPen(pen)
        painter.setBrush(brush)
        
        # Draw rounded rectangle
        painter.drawRoundedRect(rect, 10, 10)
        
        # Draw text
        painter.setPen(QPen(QColor('white')))
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        
        # Handle multi-line text
        lines = node['label'].split('\n')
        if len(lines) > 1:
            line_height = painter.fontMetrics().height()
            total_height = line_height * len(lines)
            start_y = rect.center().y() - total_height / 2 + line_height / 2
            
            for i, line in enumerate(lines):
                text_rect = QRectF(rect.x(), start_y + i * line_height - line_height/2, rect.width(), line_height)
                painter.drawText(text_rect, Qt.AlignCenter, line)
        else:
            painter.drawText(rect, Qt.AlignCenter, node['label'])
    
    def find_node(self, node_id):
        """Find node by ID"""
        for node in self.nodes:
            if node['id'] == node_id:
                return node
        return None
    
    def find_node_at_point(self, point):
        """Find node at given point"""
        adjusted_point = QPointF(
            (point.x() / self.zoom_factor) - self.pan_offset.x(),
            (point.y() / self.zoom_factor) - self.pan_offset.y()
        )
        
        for node in self.nodes:
            rect = QRectF(node['pos'], node['size'])
            if rect.contains(adjusted_point):
                return node
        return None
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            node = self.find_node_at_point(event.pos())
            if node:
                self.selected_node = node
                self.node_clicked.emit(node)
                self.update()
            else:
                self.selected_node = None
                self.update()
        elif event.button() == Qt.RightButton:
            self.is_panning = True
            self.last_pan_point = event.pos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if self.is_panning:
            delta = event.pos() - self.last_pan_point
            self.pan_offset += QPointF(delta.x() / self.zoom_factor, delta.y() / self.zoom_factor)
            self.last_pan_point = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.RightButton:
            self.is_panning = False
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        zoom_in = event.angleDelta().y() > 0
        zoom_factor = 1.1 if zoom_in else 1.0 / 1.1
        
        self.zoom_factor *= zoom_factor
        self.zoom_factor = max(0.3, min(2.0, self.zoom_factor))
        
        self.update()
    
    def reset_view(self):
        """Reset zoom and pan to default"""
        self.zoom_factor = 0.8  # Start slightly zoomed out for better overview
        self.pan_offset = QPointF(0, 0)
        self.update()
    
    def refresh_graph(self):
        """Refresh the graph with current data"""
        self.build_clean_graph()
        self.update()


class TraceabilityGraphDialog(QDialog):
    """Dialog containing the traceability graph"""
    
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.parent_window = parent
        self.db_manager = db_manager
        self.setWindowTitle("Risk Traceability Graph")
        self.setGeometry(100, 100, 1200, 800)
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Risk Traceability Graph")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Control buttons
        self.zoom_in_btn = QPushButton("🔍+")
        self.zoom_in_btn.setToolTip("Zoom In")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        header_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("🔍-")
        self.zoom_out_btn.setToolTip("Zoom Out")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        header_layout.addWidget(self.zoom_out_btn)
        
        self.reset_view_btn = QPushButton("🔄")
        self.reset_view_btn.setToolTip("Reset View")
        self.reset_view_btn.clicked.connect(self.reset_view)
        header_layout.addWidget(self.reset_view_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_graph)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Graph widget
        self.graph_widget = TraceabilityGraphWidget(self.parent_window, self.db_manager)
        self.graph_widget.node_clicked.connect(self.on_node_clicked)
        content_layout.addWidget(self.graph_widget, 3)
        
        # Details panel
        self.details_panel = QTextEdit()
        self.details_panel.setMaximumWidth(300)
        self.details_panel.setReadOnly(True)
        self.details_panel.setHtml("<h3>Node Details</h3><p>Click on a node to see details</p>")
        content_layout.addWidget(self.details_panel, 1)
        
        layout.addLayout(content_layout)
        
        # Instructions
        instructions = QLabel("Instructions: Left-click to select nodes, Right-click and drag to pan, Mouse wheel to zoom")
        instructions.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        layout.addWidget(instructions)
    
    def zoom_in(self):
        """Zoom in the graph"""
        self.graph_widget.zoom_factor *= 1.1
        self.graph_widget.zoom_factor = min(3.0, self.graph_widget.zoom_factor)
        self.graph_widget.update()
    
    def zoom_out(self):
        """Zoom out the graph"""
        self.graph_widget.zoom_factor /= 1.1
        self.graph_widget.zoom_factor = max(0.1, self.graph_widget.zoom_factor)
        self.graph_widget.update()
    
    def reset_view(self):
        """Reset the view"""
        self.graph_widget.reset_view()
    
    def refresh_graph(self):
        """Refresh the graph"""
        self.graph_widget.refresh_graph()
    
    def on_node_clicked(self, node_data):
        """Handle node click"""
        html_content = f"<h3>{node_data['label']}</h3>"
        html_content += f"<p><b>Type:</b> {node_data['type']}</p>"
        
        # Add specific data based on node type
        data = node_data.get('data', {})
        
        if node_data['type'] == 'component':
            html_content += f"<p><b>Component:</b> {data.get('component', 'N/A')}</p>"
            html_content += f"<p><b>Risk Count:</b> {data.get('risk_count', 0)}</p>"
        
        elif node_data['type'] == 'hazardous':
            situations = data.get('situations', [])
            html_content += f"<p><b>Situations Count:</b> {data.get('count', 0)}</p>"
            if situations:
                html_content += "<p><b>Situations:</b></p><ul>"
                for situation in situations[:3]:  # Show first 3
                    html_content += f"<li>{situation[:100]}{'...' if len(situation) > 100 else ''}</li>"
                if len(situations) > 3:
                    html_content += f"<li>... and {len(situations) - 3} more</li>"
                html_content += "</ul>"
        
        elif node_data['type'] == 'harm':
            harms = data.get('harms', [])
            rpn_data = data.get('rpn_data', {})
            html_content += f"<p><b>Harm Count:</b> {data.get('count', 0)}</p>"
            if harms:
                html_content += "<p><b>Harm Descriptions:</b></p><ul>"
                for harm in harms[:3]:  # Show first 3
                    html_content += f"<li>{harm[:100]}{'...' if len(harm) > 100 else ''}</li>"
                    if harm in rpn_data:
                        rpn_info = rpn_data[harm]
                        html_content += f"<small>S:{rpn_info.get('severity', '?')} P:{rpn_info.get('probability', '?')} RPN:{rpn_info.get('rpn', '?')}</small>"
                if len(harms) > 3:
                    html_content += f"<li>... and {len(harms) - 3} more</li>"
                html_content += "</ul>"
        
        elif node_data['type'] == 'detail':
            for key, value in data.items():
                html_content += f"<p><b>{key.title()}:</b> {value}</p>"
        
        self.details_panel.setHtml(html_content)
