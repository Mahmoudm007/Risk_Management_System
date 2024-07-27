from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout


class Dashboard(QDialog):
    def __init__(self, num_risks, num_approved_risks, num_unapproved_risks, num_reected, parent =None):
        super(Dashboard, self).__init__(parent)
        self.setWindowTitle("Dashboard")
        self.setGeometry(100, 100, 600, 200)

        # Create labels
        self.risks_label = QLabel("Number of Risks:")
        self.risks_count = QLabel(f"{num_risks}")

        self.approved_risks_label = QLabel("Approved Risks:")
        self.approved_risks_count = QLabel(f"{num_approved_risks}")

        self.unapproved_risks_label = QLabel("Unapproved Risks:")
        self.unapproved_risks_count = QLabel(f"{num_unapproved_risks}")

        self.rejected_risks_label = QLabel("Rejected Risks:")
        self.rejected_risks_count = QLabel(f"{num_reected}")


        # Set font sizes
        self.risks_label.setStyleSheet("font-size: 18px;")
        self.risks_count.setStyleSheet("font-size: 28px;")

        self.approved_risks_label.setStyleSheet("font-size: 18px;")
        self.approved_risks_count.setStyleSheet("font-size: 28px;")

        self.unapproved_risks_label.setStyleSheet("font-size: 18px;")
        self.unapproved_risks_count.setStyleSheet("font-size: 28px;")

        self.rejected_risks_label.setStyleSheet("font-size: 18px;")
        self.rejected_risks_count.setStyleSheet("font-size: 28px;")

        # Vertical layouts for each pair
        self.risks_layout = QVBoxLayout()
        self.risks_layout.addWidget(self.risks_label)
        self.risks_layout.addWidget(self.risks_count)

        self.approved_risks_layout = QVBoxLayout()
        self.approved_risks_layout.addWidget(self.approved_risks_label)
        self.approved_risks_layout.addWidget(self.approved_risks_count)

        self.unapproved_risks_layout = QVBoxLayout()
        self.unapproved_risks_layout.addWidget(self.unapproved_risks_label)
        self.unapproved_risks_layout.addWidget(self.unapproved_risks_count)

        # Vertical layouts for each pair
        self.rejected_layout = QVBoxLayout()
        self.rejected_layout.addWidget(self.rejected_risks_label)
        self.rejected_layout.addWidget(self.rejected_risks_count)

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.risks_layout)
        self.main_layout.addLayout(self.approved_risks_layout)
        self.main_layout.addLayout(self.unapproved_risks_layout)
        self.main_layout.addLayout(self.rejected_layout)

        # Set the main layout
        self.setLayout(self.main_layout)

    def update_counts(self, num_risks, num_approved_risks, num_unapproved_risks, num_reected):
        self.risks_count.setText(f"{num_risks}")
        self.approved_risks_count.setText(f"{num_approved_risks}")
        self.unapproved_risks_count.setText(f"{num_unapproved_risks}")
        self.rejected_risks_count.setText(f"{num_reected}")
