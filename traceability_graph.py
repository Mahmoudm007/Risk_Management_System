from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPolygonF, QCursor
import math

class GraphNode:
    """Represents a moveable node in the traceability graph"""
    def __init__(self, node_id, label, node_type, x=0, y=0, width=200, height=60):
        self.id = node_id
        self.label = label
        self.type = node_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.children = []
        self.parent = None
        self.expanded = True
        self.visible = True
        self.data = {}
        self.level = 0
        self.is_dragging = False
        self.drag_offset = QPointF(0, 0)
        
    def add_child(self, child):
        child.parent = self
        child.level = self.level + 1
        self.children.append(child)
        
    def has_children(self):
        return len(self.children) > 0
        
    def toggle_expanded(self):
        if self.has_children():
            self.expanded = not self.expanded
            self.update_children_visibility()
            
    def update_children_visibility(self):
        """Update visibility of children based on expansion state"""
        for child in self.children:
            child.visible = self.expanded
            if not self.expanded:
                child.expanded = False
                child.update_children_visibility()
                
    def get_rect(self):
        return QRectF(self.x, self.y, self.width, self.height)
        
    def get_center(self):
        return QPointF(self.x + self.width/2, self.y + self.height/2)
        
    def contains_point(self, point):
        return self.get_rect().contains(point)
        
    def move_to(self, x, y):
        """Move node to new position"""
        self.x = x
        self.y = y

class TraceabilityGraphWidget(QWidget):
    """Clean, organized, moveable traceability graph with toggle functionality"""
    
    node_clicked = pyqtSignal(dict)
    
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.parent_window = parent
        self.db_manager = db_manager
        self.nodes = {}  # Dictionary of node_id -> GraphNode
        self.root_node = None
        self.selected_node = None
        self.dragging_node = None
        self.zoom_factor = 0.8
        self.pan_offset = QPointF(0, 0)
        self.last_pan_point = QPointF()
        self.is_panning = False
        self.drag_start_pos = QPointF()
        
        # Layout constants
        self.NODE_WIDTH = 180
        self.NODE_HEIGHT = 60
        self.HORIZONTAL_SPACING = 250
        self.VERTICAL_SPACING = 100
        self.LEVEL_SPACING = 300
        self.MARGIN = 200
        
        self.setMinimumSize(1200, 800)
        self.setMouseTracking(True)
        self.build_hierarchical_graph()
        
    def build_hierarchical_graph(self):
        """Build the specific hierarchical structure requested"""
        if not self.parent_window:
            return
            
        self.nodes.clear()
        
        table_widget = self.parent_window.table_widget
        if not table_widget:
            return
        
        # Create root node - "Risks"
        self.root_node = GraphNode(
            'root',
            'Risks',
            'root',
            self.MARGIN,
            self.MARGIN,
            self.NODE_WIDTH,
            self.NODE_HEIGHT
        )
        self.root_node.data = {'description': 'Main risks container'}
        self.nodes['root'] = self.root_node
        
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
        
        # Create component nodes (Level 1)
        comp_start_y = self.root_node.y + self.root_node.height + self.VERTICAL_SPACING
        for comp_index, (component_name, risk_rows) in enumerate(component_groups.items()):
            comp_x = self.MARGIN + (comp_index * self.HORIZONTAL_SPACING)
            
            comp_node = GraphNode(
                f'comp_{comp_index}',
                f'{component_name}',
                'component',
                comp_x,
                comp_start_y,
                self.NODE_WIDTH,
                self.NODE_HEIGHT
            )
            comp_node.data = {
                'component': component_name,
                'risk_count': len(risk_rows)
            }
            
            self.nodes[comp_node.id] = comp_node
            self.root_node.add_child(comp_node)
            
            # Create sequence of events for each risk in this component
            for risk_index, row in enumerate(risk_rows):
                self.create_sequence_structure(row, comp_node, comp_x, comp_start_y, comp_index, risk_index)
    
    def create_sequence_structure(self, row, parent_comp, base_x, base_y, comp_index, risk_index):
        """Create the complete sequence structure for a risk"""
        table_widget = self.parent_window.table_widget
        
        risk_no = self.get_cell_text(table_widget, row, 1)
        rpn = self.get_cell_text(table_widget, row, 14)
        severity = self.get_cell_text(table_widget, row, 12)
        probability = self.get_cell_text(table_widget, row, 13)
        
        # Sequence of Events node (Level 2)
        seq_y = base_y + self.VERTICAL_SPACING + (risk_index * 400)  # More spacing between sequences
        sequence_node = GraphNode(
            f'seq_{comp_index}_{risk_index}',
            f'Sequence of Events\n({risk_no})',
            'sequence',
            base_x,
            seq_y,
            self.NODE_WIDTH,
            self.NODE_HEIGHT
        )
        sequence_node.data = {
            'risk_no': risk_no,
            'row': row,
            'rpn': rpn
        }
        
        self.nodes[sequence_node.id] = sequence_node
        parent_comp.add_child(sequence_node)
        
        # Create the three main branches (Level 3)
        branch_start_x = base_x + self.LEVEL_SPACING
        
        # 1. Hazardous Situation
        hazard_node = GraphNode(
            f'hazard_{comp_index}_{risk_index}',
            'Hazardous\nSituation',
            'hazardous',
            branch_start_x,
            seq_y - self.VERTICAL_SPACING,
            self.NODE_WIDTH,
            self.NODE_HEIGHT
        )
        hazard_node.data = self.get_hazardous_situations_data(row)
        self.nodes[hazard_node.id] = hazard_node
        sequence_node.add_child(hazard_node)
        
        # 2. Harm Description (with 3 children)
        harm_node = GraphNode(
            f'harm_{comp_index}_{risk_index}',
            'Harm\nDescription',
            'harm',
            branch_start_x,
            seq_y,
            self.NODE_WIDTH,
            self.NODE_HEIGHT
        )
        harm_node.data = self.get_harm_description_data(row)
        self.nodes[harm_node.id] = harm_node
        sequence_node.add_child(harm_node)
        
        # Harm Description children (Level 4)
        harm_children_x = branch_start_x + self.LEVEL_SPACING
        harm_children = [
            {'id': f'severity_{comp_index}_{risk_index}', 'label': f'Severity\n{severity}', 'y_offset': -80, 'data': {'severity': severity}},
            {'id': f'probability_{comp_index}_{risk_index}', 'label': f'Probability\n{probability}', 'y_offset': 0, 'data': {'probability': probability}},
            {'id': f'rpn_{comp_index}_{risk_index}', 'label': f'RPN\n{rpn}', 'y_offset': 80, 'data': {'rpn': rpn}}
        ]
        
        for child_info in harm_children:
            child_node = GraphNode(
                child_info['id'],
                child_info['label'],
                'harm_detail',
                harm_children_x,
                seq_y + child_info['y_offset'],
                self.NODE_WIDTH - 20,
                self.NODE_HEIGHT - 10
            )
            child_node.data = child_info['data']
            child_node.visible = False  # Initially collapsed
            self.nodes[child_node.id] = child_node
            harm_node.add_child(child_node)
        
        # 3. Risk Control (with 3 children)
        control_node = GraphNode(
            f'control_{comp_index}_{risk_index}',
            'Risk\nControl',
            'control',
            branch_start_x,
            seq_y + self.VERTICAL_SPACING,
            self.NODE_WIDTH,
            self.NODE_HEIGHT
        )
        control_node.data = {'row': row}
        self.nodes[control_node.id] = control_node
        sequence_node.add_child(control_node)
        
        # Risk Control children (Level 4)
        control_children_x = branch_start_x + self.LEVEL_SPACING
        control_children = [
            {'id': f'inherent_{comp_index}_{risk_index}', 'label': 'Inherently Safe\nDesign', 'y_offset': -80},
            {'id': f'protective_{comp_index}_{risk_index}', 'label': 'Protective\nMeasure', 'y_offset': 0},
            {'id': f'information_{comp_index}_{risk_index}', 'label': 'Information\nfor Use', 'y_offset': 80}
        ]
        
        for child_info in control_children:
            child_node = GraphNode(
                child_info['id'],
                child_info['label'],
                'control_detail',
                control_children_x,
                seq_y + self.VERTICAL_SPACING + child_info['y_offset'],
                self.NODE_WIDTH - 20,
                self.NODE_HEIGHT - 10
            )
            child_node.visible = False  # Initially collapsed
            self.nodes[child_node.id] = child_node
            control_node.add_child(child_node)
        
        # Initially collapse harm and control nodes
        harm_node.expanded = False
        control_node.expanded = False
        harm_node.update_children_visibility()
        control_node.update_children_visibility()
    
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
        """Paint the organized graph"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor('#f8f9fa'))
        
        # Apply zoom and pan transformations
        painter.scale(self.zoom_factor, self.zoom_factor)
        painter.translate(self.pan_offset)
        
        # Draw connections first
        self.draw_connections(painter)
        
        # Draw nodes
        self.draw_nodes(painter)
    
    def draw_connections(self, painter):
        """Draw clean connections with arrows"""
        pen = QPen(QColor('#2c5f7a'), 2)
        painter.setPen(pen)
        
        for node in self.nodes.values():
            if not node.visible:
                continue
                
            for child in node.children:
                if not child.visible:
                    continue
                    
                # Calculate connection points
                parent_center = node.get_center()
                child_center = child.get_center()
                
                # Determine connection points based on relative positions
                if parent_center.x() < child_center.x():  # Left to right
                    from_point = QPointF(node.x + node.width, parent_center.y())
                    to_point = QPointF(child.x, child_center.y())
                else:  # Top to bottom
                    from_point = QPointF(parent_center.x(), node.y + node.height)
                    to_point = QPointF(child_center.x(), child.y)
                
                # Draw line
                painter.drawLine(from_point, to_point)
                
                # Draw arrow
                self.draw_arrow(painter, from_point, to_point)
    
    def draw_arrow(self, painter, from_point, to_point):
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
    
    def draw_nodes(self, painter):
        """Draw all visible nodes"""
        for node in self.nodes.values():
            if node.visible:
                self.draw_node(painter, node)
    
    def draw_node(self, painter, node):
        """Draw a single node with toggle indicator"""
        rect = node.get_rect()
        
        # Get node color based on type
        color = self.get_node_color(node.type)
        
        # Set style based on selection and dragging
        if node == self.selected_node:
            pen = QPen(QColor('#ff0000'), 3)
            brush = QBrush(color.lighter(120))
        elif node.is_dragging:
            pen = QPen(QColor('#0066cc'), 3)
            brush = QBrush(color.lighter(130))
        else:
            pen = QPen(QColor('#ffffff'), 2)
            brush = QBrush(color)
        
        painter.setPen(pen)
        painter.setBrush(brush)
        
        # Draw rounded rectangle
        painter.drawRoundedRect(rect, 10, 10)
        
        # Draw toggle indicator for nodes with children
        if node.has_children():
            toggle_rect = QRectF(rect.right() - 25, rect.top() + 5, 20, 20)
            painter.setPen(QPen(QColor('white'), 2))
            painter.setBrush(QBrush(QColor('white')))
            painter.drawEllipse(toggle_rect)
            
            # Draw + or - symbol
            painter.setPen(QPen(QColor('black'), 2))
            symbol = '−' if node.expanded else '+'
            font = QFont("Arial", 12, QFont.Bold)
            painter.setFont(font)
            painter.drawText(toggle_rect, Qt.AlignCenter, symbol)
        
        # Draw text
        painter.setPen(QPen(QColor('white')))
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        
        # Handle multi-line text
        lines = node.label.split('\n')
        if len(lines) > 1:
            line_height = painter.fontMetrics().height()
            total_height = line_height * len(lines)
            start_y = rect.center().y() - total_height / 2 + line_height / 2
            
            for i, line in enumerate(lines):
                text_rect = QRectF(rect.x() + 5, start_y + i * line_height - line_height/2, rect.width() - 30, line_height)
                painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, line)
        else:
            text_rect = QRectF(rect.x() + 5, rect.y(), rect.width() - 30, rect.height())
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, node.label)
    
    def get_node_color(self, node_type):
        """Get color based on node type"""
        colors = {
            'root': QColor('#1e3a8a'),           # Dark blue
            'component': QColor('#059669'),       # Green
            'sequence': QColor('#d97706'),        # Orange
            'hazardous': QColor('#dc2626'),       # Red
            'harm': QColor('#7c3aed'),           # Purple
            'control': QColor('#2563eb'),         # Blue
            'harm_detail': QColor('#9333ea'),     # Light purple
            'control_detail': QColor('#1d4ed8')   # Light blue
        }
        return colors.get(node_type, QColor('#6b7280'))
    
    def find_node_at_point(self, point):
        """Find node at given point"""
        adjusted_point = QPointF(
            (point.x() / self.zoom_factor) - self.pan_offset.x(),
            (point.y() / self.zoom_factor) - self.pan_offset.y()
        )
        
        for node in self.nodes.values():
            if node.visible and node.contains_point(adjusted_point):
                return node
        return None
    
    def get_toggle_rect(self, node):
        """Get the toggle button rectangle for a node"""
        rect = node.get_rect()
        return QRectF(rect.right() - 25, rect.top() + 5, 20, 20)
    
    def mousePressEvent(self, event):
        """Handle mouse press for node selection, toggle, and drag start"""
        if event.button() == Qt.LeftButton:
            node = self.find_node_at_point(event.pos())
            if node:
                adjusted_point = QPointF(
                    (event.pos().x() / self.zoom_factor) - self.pan_offset.x(),
                    (event.pos().y() / self.zoom_factor) - self.pan_offset.y()
                )
                
                # Check if click is on toggle area
                if node.has_children():
                    toggle_rect = self.get_toggle_rect(node)
                    if toggle_rect.contains(adjusted_point):
                        # Toggle node
                        node.toggle_expanded()
                        self.update()
                        return
                
                # Start dragging
                self.dragging_node = node
                self.drag_start_pos = adjusted_point
                node.drag_offset = QPointF(adjusted_point.x() - node.x, adjusted_point.y() - node.y)
                node.is_dragging = True
                self.setCursor(QCursor(Qt.ClosedHandCursor))
                
                # Select node
                self.selected_node = node
                node_info = {
                    'id': node.id,
                    'label': node.label,
                    'type': node.type,
                    'data': node.data
                }
                self.node_clicked.emit(node_info)
                self.update()
            else:
                self.selected_node = None
                self.update()
        elif event.button() == Qt.RightButton:
            self.is_panning = True
            self.last_pan_point = event.pos()
            self.setCursor(QCursor(Qt.OpenHandCursor))
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging nodes and panning"""
        if self.dragging_node:
            # Drag node
            adjusted_point = QPointF(
                (event.pos().x() / self.zoom_factor) - self.pan_offset.x(),
                (event.pos().y() / self.zoom_factor) - self.pan_offset.y()
            )
            
            new_x = adjusted_point.x() - self.dragging_node.drag_offset.x()
            new_y = adjusted_point.y() - self.dragging_node.drag_offset.y()
            
            self.dragging_node.move_to(new_x, new_y)
            self.update()
            
        elif self.is_panning:
            # Pan view
            delta = event.pos() - self.last_pan_point
            self.pan_offset += QPointF(delta.x() / self.zoom_factor, delta.y() / self.zoom_factor)
            self.last_pan_point = event.pos()
            self.update()
        else:
            # Update cursor based on what's under mouse
            node = self.find_node_at_point(event.pos())
            if node:
                adjusted_point = QPointF(
                    (event.pos().x() / self.zoom_factor) - self.pan_offset.x(),
                    (event.pos().y() / self.zoom_factor) - self.pan_offset.y()
                )
                
                if node.has_children() and self.get_toggle_rect(node).contains(adjusted_point):
                    self.setCursor(QCursor(Qt.PointingHandCursor))
                else:
                    self.setCursor(QCursor(Qt.OpenHandCursor))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton and self.dragging_node:
            self.dragging_node.is_dragging = False
            self.dragging_node = None
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.update()
        elif event.button() == Qt.RightButton:
            self.is_panning = False
            self.setCursor(QCursor(Qt.ArrowCursor))
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        zoom_in = event.angleDelta().y() > 0
        zoom_factor = 1.1 if zoom_in else 1.0 / 1.1
        
        self.zoom_factor *= zoom_factor
        self.zoom_factor = max(0.3, min(3.0, self.zoom_factor))
        
        self.update()
    
    def reset_view(self):
        """Reset zoom and pan to default"""
        self.zoom_factor = 0.8
        self.pan_offset = QPointF(0, 0)
        self.update()
    
    def expand_all(self):
        """Expand all nodes"""
        for node in self.nodes.values():
            if node.has_children():
                node.expanded = True
                node.update_children_visibility()
        self.update()
    
    def collapse_all(self):
        """Collapse all nodes except root"""
        for node in self.nodes.values():
            if node.has_children() and node != self.root_node:
                node.expanded = False
                node.update_children_visibility()
        self.update()
    
    def refresh_graph(self):
        """Refresh the graph with current data"""
        self.build_hierarchical_graph()
        self.update()


class TraceabilityGraphDialog(QDialog):
    """Dialog containing the traceability graph"""
    
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.parent_window = parent
        self.db_manager = db_manager
        self.setWindowTitle("Risk Traceability Graph")
        self.setGeometry(100, 100, 1400, 900)
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
        self.expand_all_btn = QPushButton("Expand All")
        self.expand_all_btn.clicked.connect(self.expand_all)
        header_layout.addWidget(self.expand_all_btn)
        
        self.collapse_all_btn = QPushButton("Collapse All")
        self.collapse_all_btn.clicked.connect(self.collapse_all)
        header_layout.addWidget(self.collapse_all_btn)
        
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
        instructions = QLabel("Instructions: Left-click and drag to move nodes, Click +/- to expand/collapse, Right-click and drag to pan, Mouse wheel to zoom")
        instructions.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        layout.addWidget(instructions)
    
    def expand_all(self):
        """Expand all nodes"""
        self.graph_widget.expand_all()
    
    def collapse_all(self):
        """Collapse all nodes"""
        self.graph_widget.collapse_all()
    
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
    
    def on_node_clicked(self, node_info):
        """Handle node click"""
        html_content = f"<h3>{node_info.get('label', 'Unknown Node')}</h3>"
        html_content += f"<p><b>Type:</b> {node_info.get('type', 'Unknown')}</p>"
        html_content += f"<p><b>ID:</b> {node_info.get('id', 'Unknown')}</p>"
        
        # Add specific data based on node type
        data = node_info.get('data', {})
        node_type = node_info.get('type', '')
        
        if node_type == 'component':
            html_content += f"<p><b>Component:</b> {data.get('component', 'N/A')}</p>"
            html_content += f"<p><b>Risk Count:</b> {data.get('risk_count', 0)}</p>"
        
        elif node_type == 'sequence':
            html_content += f"<p><b>Risk No:</b> {data.get('risk_no', 'N/A')}</p>"
            html_content += f"<p><b>RPN:</b> {data.get('rpn', 'N/A')}</p>"
        
        elif node_type == 'hazardous':
            situations = data.get('situations', [])
            html_content += f"<p><b>Situations Count:</b> {data.get('count', 0)}</p>"
            if situations:
                html_content += "<p><b>Situations:</b></p><ul>"
                for situation in situations[:3]:  # Show first 3
                    html_content += f"<li>{situation[:100]}{'...' if len(situation) > 100 else ''}</li>"
                if len(situations) > 3:
                    html_content += f"<li>... and {len(situations) - 3} more</li>"
                html_content += "</ul>"
        
        elif node_type == 'harm':
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
        
        elif node_type in ['harm_detail', 'control_detail']:
            for key, value in data.items():
                html_content += f"<p><b>{key.title()}:</b> {value}</p>"
        
        self.details_panel.setHtml(html_content)
