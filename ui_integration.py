# Add this to your setupUI method or create the buttons programmatically

def create_tree_buttons(self):
    """Create tree view buttons"""
    # Tree bar button
    self.tree_bar_btn = QPushButton("🌳 Tree Bar")
    self.tree_bar_btn.setToolTip("Open hierarchical tree view of risks and components")
    self.tree_bar_btn.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)
    
    # Tree view graph button
    self.tree_view_graph_btn = QPushButton("📊 Tree View Graph")
    self.tree_view_graph_btn.setToolTip("Open interactive traceability graph")
    self.tree_view_graph_btn.setStyleSheet("""
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
    """)
    
    # Add buttons to your layout (adjust according to your UI structure)
    # For example, if you have a toolbar or button panel:
    # self.toolbar_layout.addWidget(self.tree_bar_btn)
    # self.toolbar_layout.addWidget(self.tree_view_graph_btn)
