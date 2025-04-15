import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QTabWidget, QProgressBar, QScrollArea,
                            QGraphicsDropShadowEffect, QSplitter, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, QMargins
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush, QPainter, QRadialGradient

from ahp_func import compute_alternative_score, normalize_and_calculate_weights

class CustomTableWidget(QTableWidget):
    """Enhanced table widget with better visual presentation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                gridline-color: #F0F0F0;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #F0F0F0;
            }
            QTableWidget::item:selected {
                background-color: #B2DFDB;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #26A69A;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: 0px;
                border-radius: 0px;
            }
        """)

class CardWidget(QWidget):
    """Custom card widget with shadow effect"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        
        # Create shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(2, 3)
        self.setGraphicsEffect(shadow)
        
        # Create layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layout)
        
        # Add title if provided
        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Roboto", 16, QFont.Bold))
            title_label.setStyleSheet("color: #26A69A;")
            self.layout.addWidget(title_label)
            
            # Add separator line
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setStyleSheet("background-color: #E0E0E0; min-height: 1px; margin: 10px 0px;")
            self.layout.addWidget(separator)
        
        self.setStyleSheet("""
            #card {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #F0F0F0;
            }
        """)
    
    def addWidget(self, widget):
        self.layout.addWidget(widget)
        
    def addLayout(self, layout):
        self.layout.addLayout(layout)

class PhoneAHPWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Phone Selector - AHP Analysis")
        self.setGeometry(100, 100, 1200, 900)
        self.alternatives = ["iPhone 12", "Itel A56", "Tecno Camon 12", "Infinix Hot 10", 
                             "Huawei P30", "Google Pixel 7", "Xiaomi Redmi Note 10", 
                             "Samsung Galaxy S22", "Motorola Razr+", "iPhone XR", 
                             "Samsung Galaxy Note 10"]
        self.criteria = ["Memory", "Storage", "CPU Frequency", "Price", "Brand"]
        self.n_alts = len(self.alternatives)
        self.n_crits = len(self.criteria)
        self.init_ui()

    def init_ui(self):
        """Set up the enhanced modern GUI."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_widget.setLayout(main_layout)

        # Styling - More modern look
        self.setStyleSheet("""
            QMainWindow { 
                background-color: #F5F7FA; 
            }
            QLabel { 
                color: #263238; 
                font-family: 'Roboto', 'Segoe UI', Arial; 
            }
            QLineEdit { 
                background-color: white; 
                border: 1px solid #CFD8DC; 
                border-radius: 8px; 
                padding: 12px; 
                font-size: 14px; 
            }
            QLineEdit:focus { 
                border: 2px solid #26A69A; 
            }
            QLineEdit[valid="true"] { 
                border: 2px solid #4CAF50; 
            }
            QLineEdit[valid="false"] { 
                border: 2px solid #F44336; 
            }
            QPushButton { 
                background-color: #26A69A; 
                color: white; 
                padding: 12px 24px; 
                border-radius: 8px; 
                font-size: 14px; 
                font-weight: bold; 
                border: none;
            }
            QPushButton:hover { 
                background-color: #2BBBAD; 
            }
            QPushButton:pressed { 
                background-color: #00897B; 
            }
            QTabWidget::pane { 
                border: none;
                background: transparent; 
                border-radius: 8px; 
            }
            QTabWidget::tab-bar { 
                alignment: center; 
            }
            QTabWidget QTabBar::tab { 
                background: #E0E0E0; 
                border-radius: 8px; 
                padding: 12px 24px; 
                margin: 5px 3px; 
                font-size: 14px; 
                font-weight: bold;
                color: #546E7A;
            }
            QTabWidget QTabBar::tab:selected { 
                background: #26A69A; 
                color: white; 
            }
            QTabWidget QTabBar::tab:hover:!selected { 
                background: #BDBDBD; 
            }
            QProgressBar { 
                border: none; 
                border-radius: 8px; 
                text-align: center; 
                font-size: 12px; 
                background-color: #E0E0E0;
                font-weight: bold;
                height: 20px;
            }
            QProgressBar::chunk { 
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #26A69A, stop:1 #4CAF50);
                border-radius: 8px; 
            }
        """)

        # Application Header
        header_card = CardWidget()
        header_layout = QHBoxLayout()
        header = QLabel("Smart Phone Selector - AHP Analysis")
        header.setFont(QFont("Roboto", 24, QFont.Bold))
        header.setStyleSheet("color: #26A69A;")
        header.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(header)
        header_card.addLayout(header_layout)
        main_layout.addWidget(header_card)

        # Description Card
        desc_card = CardWidget()
        desc_label = QLabel(
            "This tool helps you select the best smartphone based on your criteria "
            "preferences using the Analytic Hierarchy Process (AHP) method. Adjust "
            "the criteria importance on the Criteria Preferences tab, then click Calculate."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont("Roboto", 12))
        desc_label.setStyleSheet("color: #546E7A;")
        desc_card.addWidget(desc_label)
        main_layout.addWidget(desc_card)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Roboto", 14))
        main_layout.addWidget(self.tabs)

        # Tab 1: Alternatives & Criteria
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        tab1.setLayout(tab1_layout)

        tab1_card = CardWidget("Phones & Criteria")
        
        # Instructions
        instructions = QLabel("Enter phones and criteria, separated by commas.")
        instructions.setStyleSheet("color: #546E7A; font-style: italic;")
        tab1_card.addWidget(instructions)
        
        # Grid layout for inputs
        input_grid = QGridLayout()
        input_grid.setSpacing(15)
        
        # Alternatives section
        alt_label = QLabel("Phones:")
        alt_label.setFont(QFont("Roboto", 14))
        alt_label.setToolTip("Enter phone names separated by commas")
        input_grid.addWidget(alt_label, 0, 0)
        
        self.alt_input = QLineEdit("iPhone 12,Itel A56,Tecno Camon 12,Infinix Hot 10,Huawei P30,Google Pixel 7,Xiaomi Redmi Note 10,Samsung Galaxy S22,Motorola Razr+,iPhone XR,Samsung Galaxy Note 10")
        self.alt_input.setProperty("valid", True)
        self.alt_input.textChanged.connect(self.validate_inputs)
        self.alt_input.setPlaceholderText("Phone models separated by commas...")
        input_grid.addWidget(self.alt_input, 0, 1)

        # Criteria section
        crit_label = QLabel("Criteria:")
        crit_label.setFont(QFont("Roboto", 14))
        crit_label.setToolTip("Enter criteria like Memory, Storage, Brand")
        input_grid.addWidget(crit_label, 1, 0)
        
        self.crit_input = QLineEdit("Memory,Storage,CPU Frequency,Price,Brand")
        self.crit_input.setProperty("valid", True)
        self.crit_input.textChanged.connect(self.validate_inputs)
        self.crit_input.setPlaceholderText("Criteria separated by commas...")
        input_grid.addWidget(self.crit_input, 1, 1)
        
        tab1_card.addLayout(input_grid)
        tab1_layout.addWidget(tab1_card)
        tab1_layout.addStretch()
        self.tabs.addTab(tab1, "Phones & Criteria")

        # Tab 2: Criteria Matrix
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        tab2.setLayout(tab2_layout)

        tab2_card = CardWidget("Criteria Comparisons")
        
        crit_matrix_label = QLabel(
            "Compare the importance of each criterion (row) against each other criterion (column).\n"
            "Use the following scale: 1=equal, 3=moderately prefer, 5=strongly prefer, 7=very strongly prefer, 9=extremely prefer"
        )
        crit_matrix_label.setWordWrap(True)
        crit_matrix_label.setFont(QFont("Roboto", 12))
        crit_matrix_label.setToolTip("Compare importance of criteria (e.g., Price vs. Brand)")
        crit_matrix_label.setStyleSheet("color: #546E7A; margin-bottom: 10px;")
        tab2_card.addWidget(crit_matrix_label)
        
        # Importance scale legend
        scale_box = QWidget()
        scale_layout = QHBoxLayout()
        scale_layout.setSpacing(10)
        
        scale_items = [
            ("1: Equal", "#E0E0E0"),
            ("3: Moderate", "#B2DFDB"),
            ("5: Strong", "#80CBC4"),
            ("7: Very Strong", "#4DB6AC"),
            ("9: Extreme", "#26A69A")
        ]
        
        for text, color in scale_items:
            item = QWidget()
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)
            
            color_box = QLabel()
            color_box.setFixedSize(20, 20)
            color_box.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
            
            label = QLabel(text)
            label.setFont(QFont("Roboto", 10))
            
            item_layout.addWidget(color_box)
            item_layout.addWidget(label)
            item.setLayout(item_layout)
            
            scale_layout.addWidget(item)
        
        scale_box.setLayout(scale_layout)
        tab2_card.addWidget(scale_box)
        
        # Criteria matrix table
        self.crit_matrix_table = CustomTableWidget()
        self.crit_matrix_table.setRowCount(5)
        self.crit_matrix_table.setColumnCount(5)
        criteria = ["Memory", "Storage", "CPU Frequency", "Price", "Brand"]
        self.crit_matrix_table.setHorizontalHeaderLabels(criteria)
        self.crit_matrix_table.setVerticalHeaderLabels(criteria)
        
        crit_matrix_data = [
            [1, 5, 3, 3, 7],
            [0.2, 1, 0.333, 0.333, 5],
            [0.333, 3, 1, 1, 5],
            [0.333, 3, 1, 1, 5],
            [0.143, 0.2, 0.2, 0.2, 1]
        ]
        
        # Fill the table with values and set color coding
        for i in range(5):
            for j in range(5):
                value = round(crit_matrix_data[i][j], 3)
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.crit_matrix_table.setItem(i, j, item)
                
                # Color coding based on value intensity
                if i == j:  # Diagonal is always 1
                    item.setBackground(QColor("#E0E0E0"))
                elif value >= 7:
                    item.setBackground(QColor("#26A69A"))
                    # item.setForeground(QColor("white"))
                elif value >= 5:
                    item.setBackground(QColor("#4DB6AC"))
                elif value >= 3:
                    item.setBackground(QColor("#80CBC4"))
                elif value > 1:
                    item.setBackground(QColor("#B2DFDB"))
                else:
                    # Values less than 1 (inverse preferences)
                    intensity = max(0.2, min(1.0, value * 0.8))
                    item.setBackground(QColor(f"rgba(224, 224, 224, {intensity})"))
                
        # Adjust the table size
        table_height = self.crit_matrix_table.verticalHeader().length() + 60
        self.crit_matrix_table.setMinimumHeight(table_height)
        self.crit_matrix_table.setMaximumHeight(table_height)
        
        tab2_card.addWidget(self.crit_matrix_table)
        tab2_layout.addWidget(tab2_card)
        tab2_layout.addStretch()
        self.tabs.addTab(tab2, "Criteria Preferences")

        # Tab 3: Results (Specifications, Weights, Conclusion)
        self.tab3 = QWidget()
        tab3_scroll = QScrollArea()
        tab3_scroll.setWidgetResizable(True)
        tab3_container = QWidget()
        self.tab3_layout = QVBoxLayout()
        tab3_container.setLayout(self.tab3_layout)
        tab3_scroll.setWidget(tab3_container)

        # Specifications Table
        specs_card = CardWidget("Phone Specifications")
        
        # Description of specifications
        specs_desc = QLabel("These are the technical specifications for each phone that will be evaluated.")
        specs_desc.setStyleSheet("color: #546E7A; font-style: italic; margin-bottom: 10px;")
        specs_card.addWidget(specs_desc)
        
        self.specs_table = CustomTableWidget()
        self.specs_table.setRowCount(11)
        self.specs_table.setColumnCount(6)
        self.specs_table.setHorizontalHeaderLabels(["Phone", "Memory (GB)", "Storage (GB)", "CPU Frequency (GHz)", "Price (USD)", "Brand Score"])
        
        memory_specs = [8, 2, 3, 3, 4, 12, 4, 12, 4, 6, 6]  # GB
        storage_specs = [256, 64, 64, 64, 128, 256, 128, 512, 128, 128, 256]  # GB
        cpu_specs = [3.0, 1.5, 1.8, 1.8, 2.0, 3.0, 2.0, 3.2, 2.0, 2.5, 2.8]  # GHz
        price_specs = [800, 150, 200, 200, 300, 700, 300, 1000, 400, 600, 900]  # USD
        brand_scores = [8, 1, 2, 2, 7, 8, 5, 10, 5, 7, 9]  # Provided
        
        for i in range(11):
            # Phone name - emphasize
            name_item = QTableWidgetItem(self.alternatives[i])
            name_item.setFont(QFont("Roboto", 10, QFont.Bold))
            self.specs_table.setItem(i, 0, name_item)
            
            # Specs - highlight special values
            specs_data = [
                (memory_specs[i], 1, max(memory_specs)),
                (storage_specs[i], 2, max(storage_specs)),
                (cpu_specs[i], 3, max(cpu_specs)),
                (price_specs[i], 4, min(price_specs)),  # For price, lower is better
                (brand_scores[i], 5, max(brand_scores))
            ]
            
            for value, col, benchmark in specs_data:
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Highlight cells with exceptional values
                is_best = False
                if col == 4:  # Price - lower is better
                    is_best = value == benchmark
                    intensity = 1 - (value - benchmark) / (max(price_specs) - benchmark + 1)
                else:  # Other specs - higher is better
                    is_best = value == benchmark
                    intensity = value / (benchmark + 0.1)
                
                # Set background color based on how good the value is
                if is_best:
                    item.setBackground(QColor("#B2DFDB"))
                elif intensity > 0.8:
                    item.setBackground(QColor("#E0F2F1"))
                
                self.specs_table.setItem(i, col, item)
        
        specs_card.addWidget(self.specs_table)
        self.tab3_layout.addWidget(specs_card)

        specs = [["Alternatives"] + self.criteria]
        for index, alt in enumerate(self.alternatives):
            specs.append([alt, memory_specs[index], storage_specs[index], cpu_specs[index], price_specs[index], brand_scores[index]])

        # Results Table (Weights and Conclusion)
        self.results_card = CardWidget("Analysis Results")
        self.results_card.setVisible(False)
        
        # Description for results
        results_desc = QLabel(
            "Based on your criteria preferences, here are the weighted scores for each phone. "
            "Higher scores indicate better match with your preferences."
        )
        results_desc.setWordWrap(True)
        results_desc.setStyleSheet("color: #546E7A; font-style: italic; margin-bottom: 10px;")
        self.results_card.addWidget(results_desc)
        
        # Criteria weights section
        self.weights_box = QWidget()
        weights_layout = QHBoxLayout()
        weights_layout.setSpacing(15)
        self.weights_box.setLayout(weights_layout)
        self.weights_box.setVisible(False)
        self.weights_labels = []
        
        for criterion in self.criteria:
            weight_widget = QWidget()
            weight_layout = QVBoxLayout()
            weight_layout.setAlignment(Qt.AlignCenter)
            
            name = QLabel(criterion)
            name.setAlignment(Qt.AlignCenter)
            name.setFont(QFont("Roboto", 10, QFont.Bold))
            
            value = QLabel("0.00")
            value.setAlignment(Qt.AlignCenter)
            value.setFont(QFont("Roboto", 12))
            value.setStyleSheet("color: #26A69A; font-weight: bold;")
            
            weight_layout.addWidget(name)
            weight_layout.addWidget(value)
            weight_widget.setLayout(weight_layout)
            
            weights_layout.addWidget(weight_widget)
            self.weights_labels.append(value)
            
        self.results_card.addWidget(self.weights_box)
        
        # Results table
        self.results_table = CustomTableWidget()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels(["Phone", "Memory", "Storage", "CPU Frequency", "Price", "Brand", "Total Score"])
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_card.addWidget(self.results_table)
        
        # Visualization of top phones
        self.visualization_widget = QWidget()
        viz_layout = QVBoxLayout()
        self.visualization_widget.setLayout(viz_layout)
        self.visualization_widget.setVisible(False)
        
        # Top 3 phones visualization
        self.top_phones_box = QWidget()
        top_layout = QHBoxLayout()
        self.top_phones_box.setLayout(top_layout)
        
        # Create placeholders for top 3 phones
        self.top_positions = []
        positions = [
            ("1st Place", "#4CAF50", 18, 14),
            ("2nd Place", "#26A69A", 16, 12),
            ("3rd Place", "#80CBC4", 14, 11)
        ]
        
        for title, color, size1, size2 in positions:
            pos_widget = QWidget()
            pos_layout = QVBoxLayout()
            pos_layout.setAlignment(Qt.AlignCenter)
            
            rank = QLabel(title)
            rank.setAlignment(Qt.AlignCenter)
            rank.setFont(QFont("Roboto", 12, QFont.Bold))
            rank.setStyleSheet(f"color: {color};")
            
            name = QLabel("TBD")
            name.setAlignment(Qt.AlignCenter)
            name.setFont(QFont("Roboto", size1, QFont.Bold))
            name.setStyleSheet(f"color: {color};")
            
            score = QLabel("0.00")
            score.setAlignment(Qt.AlignCenter)
            score.setFont(QFont("Roboto", size2))
            
            pos_layout.addWidget(rank)
            pos_layout.addWidget(name)
            pos_layout.addWidget(score)
            pos_widget.setLayout(pos_layout)
            
            top_layout.addWidget(pos_widget)
            self.top_positions.append((name, score))
        
        viz_layout.addWidget(self.top_phones_box)
        self.results_card.addWidget(self.visualization_widget)
        
        # Conclusion
        self.conclusion_frame = QFrame()
        self.conclusion_frame.setFrameShape(QFrame.StyledPanel)
        self.conclusion_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #4CAF50;
                border-radius: 8px;
                background-color: #E8F5E9;
                padding: 10px;
                margin-top: 15px;
            }
        """)
        conclusion_layout = QVBoxLayout()
        
        conclusion_header = QLabel("Recommendation")
        conclusion_header.setFont(QFont("Roboto", 14, QFont.Bold))
        conclusion_header.setAlignment(Qt.AlignCenter)
        conclusion_header.setStyleSheet("color: #2E7D32;")
        
        self.conclusion_text = QLabel()
        self.conclusion_text.setWordWrap(True)
        self.conclusion_text.setFont(QFont("Roboto", 12))
        self.conclusion_text.setAlignment(Qt.AlignCenter)
        self.conclusion_text.setStyleSheet("color: #1B5E20;")
        
        conclusion_layout.addWidget(conclusion_header)
        conclusion_layout.addWidget(self.conclusion_text)
        self.conclusion_frame.setLayout(conclusion_layout)
        self.conclusion_frame.setVisible(False)
        
        self.results_card.addWidget(self.conclusion_frame)
        self.tab3_layout.addWidget(self.results_card)
        
        self.tab3_layout.addStretch()
        self.tabs.addTab(tab3_scroll, "Results")

        # Button Section
        btn_card = CardWidget()
        btn_layout = QHBoxLayout()
        
        compute_btn = QPushButton("Calculate")
        compute_btn.setIcon(self.style().standardIcon(self.style().SP_DialogApplyButton))
        compute_btn.setIconSize(QSize(20, 20))
        compute_btn.clicked.connect(self.compute_ahp)
        compute_btn.setMinimumHeight(50)
        compute_btn.setCursor(Qt.PointingHandCursor)
        
        reset_btn = QPushButton("Reset")
        reset_btn.setIcon(self.style().standardIcon(self.style().SP_DialogResetButton))
        reset_btn.setIconSize(QSize(20, 20))
        reset_btn.clicked.connect(self.reset_inputs)
        reset_btn.setMinimumHeight(50)
        reset_btn.setStyleSheet("background-color: #BDBDBD;")
        reset_btn.setCursor(Qt.PointingHandCursor)
        
        btn_layout.addWidget(compute_btn)
        btn_layout.addWidget(reset_btn)
        btn_card.addLayout(btn_layout)
        main_layout.addWidget(btn_card)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(10)
        self.progress_bar.setMaximumHeight(10)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Add stretch to push everything up
        main_layout.addStretch()

        # Animation for results
        self.animation = QPropertyAnimation(self.results_card, b"maximumHeight")
        self.animation.setDuration(600)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def validate_inputs(self):
        """Validate inputs in real-time."""
        sender = self.sender()
        try:
            if sender == self.alt_input:
                alts = [x.strip() for x in self.alt_input.text().split(",") if x.strip()]
                sender.setProperty("valid", len(alts) >= 2)
            elif sender == self.crit_input:
                crits = [x.strip() for x in self.crit_input.text().split(",") if x.strip()]
                sender.setProperty("valid", len(crits) >= 2)
            sender.style().unpolish(sender)
            sender.style().polish(sender)
        except:
            sender.setProperty("valid", False)
            sender.style().unpolish(sender)
            sender.style().polish(sender)

    def get_table_data(self, table):
        """Extract data from QTableWidget."""
        rows, cols = table.rowCount(), table.columnCount()
        data = np.zeros((rows, cols))
        for i in range(rows):
            for j in range(cols):
                item = table.item(i, j)
                try:
                    data[i, j] = float(item.text()) if item else 1
                except:
                    raise ValueError(f"Invalid value at row {i+1}, col {j+1}")
        return data

    def get_specs_data(self):
        """Extract specs from specs_table (including headers)."""
        specs = []
        # Include headers as the first row
        headers = ["Phone"] + self.criteria
        specs.append(headers)
        # Extract data rows
        for i in range(self.specs_table.rowCount()):
            row = []
            for j in range(self.specs_table.columnCount()):
                item = self.specs_table.item(i, j)
                try:
                    value = item.text() if item else "0"
                    # For non-Phone columns, convert to float
                    if j > 0:
                        value = float(value)
                    row.append(value)
                except:
                    raise ValueError(f"Invalid spec value at row {i+1}, col {j+1}")
            specs.append(row)
        return specs

    def compute_ahp(self):
        """Run AHP and display results using compute_alternative_score."""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            QTimer.singleShot(100, lambda: self.progress_bar.setValue(30))
            QTimer.singleShot(200, lambda: self.progress_bar.setValue(50))

            alternatives = [x.strip() for x in self.alt_input.text().split(",") if x.strip()]
            criteria = [x.strip() for x in self.crit_input.text().split(",") if x.strip()]
            n_alts, n_crits = len(alternatives), len(criteria)

            if n_alts != self.n_alts or n_crits != self.n_crits:
                raise ValueError("Number of phones and criteria must match defaults for this version")

            criteria_matrix = self.get_table_data(self.crit_matrix_table)
            if criteria_matrix.shape != (n_crits, n_crits):
                raise ValueError(f"Criteria matrix must be {n_crits}x{n_crits}")

            # Get specs from the specs_table (including headers)
            specs = self.get_specs_data()
            if len(specs) <= 1 or len(specs[1]) - 1 != n_crits:
                raise ValueError(f"Specs table must have {n_alts} rows and {n_crits} columns (excluding Phone column)")

            # Calculate criteria weights for display
            weights = normalize_and_calculate_weights(criteria_matrix)
            
            QTimer.singleShot(300, lambda: self.progress_bar.setValue(70))

            # Compute scores using the function
            alternatives_scores, totals, message = compute_alternative_score(specs, criteria_matrix)
            if totals is None:
                self.progress_bar.setVisible(False)
                QMessageBox.critical(self, "Error", message)
                return

            QTimer.singleShot(400, lambda: self.progress_bar.setValue(90))

            # Ensure results_card is visible before showing results
            self.results_card.setVisible(True)
            QTimer.singleShot(500, lambda: self.progress_bar.setValue(100))
            QTimer.singleShot(600, lambda: self.show_results(alternatives, criteria, alternatives_scores, totals, weights))

        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Error", f"Computation failed: {str(e)}")

    def show_results(self, alternatives, criteria, alternatives_scores, totals, weights):
        """Display enhanced results with animations and visualizations."""
        try:
            # Prepare the weights display
            for i, label in enumerate(self.weights_labels):
                weight_value = weights[i]
                label.setText(f"{weight_value:.4f}")
                # Adjust color intensity based on weight importance
                intensity = int(weight_value * 255 / max(weights))
                label.setStyleSheet(f"color: rgb(38, {100 + intensity//2}, {154 + intensity//3}); font-weight: bold;")
            
            self.weights_box.setVisible(True)
            
            # Prepare the results table
            self.results_table.setRowCount(len(alternatives))
            self.results_table.setColumnCount(1 + len(criteria) + 1)
            self.results_table.setHorizontalHeaderLabels(["Phone"] + criteria + ["Total Score"])

            # Sort alternatives by totals (descending)
            sorted_indices = np.argsort(totals)[::-1]
            
            # Maximum value for each criterion for normalization in visualization
            max_criterion_values = []
            for j in range(len(criteria)):
                max_val = max([alternatives_scores[i][j] for i in range(len(alternatives))])
                max_criterion_values.append(max_val if max_val > 0 else 1)
                
            # Fill table with enhanced visuals
            for row, idx in enumerate(sorted_indices):
                # Phone name with rank indicator
                phone_item = QTableWidgetItem(f"{alternatives[idx]}")
                if row < 3:  # Top 3 get special treatment
                    rank_colors = ["#4CAF50", "#26A69A", "#80CBC4"]
                    phone_item.setFont(QFont("Roboto", 10, QFont.Bold))
                    phone_item.setForeground(QColor(rank_colors[row]))
                self.results_table.setItem(row, 0, phone_item)
                
                # Individual criterion scores with visual intensity
                for col, score in enumerate(alternatives_scores[idx], 1):
                    item = QTableWidgetItem(f"{score:.4f}")
                    item.setTextAlignment(Qt.AlignCenter)
                    
                    # Visual intensity based on normalized score
                    norm_score = score / max_criterion_values[col-1] if max_criterion_values[col-1] > 0 else 0
                    
                    # Create gradient colors based on score importance
                    if norm_score > 0.8:
                        item.setBackground(QColor("#C8E6C9"))  # Strong green
                    elif norm_score > 0.6:
                        item.setBackground(QColor("#DCEDC8"))  # Medium green
                    elif norm_score > 0.4:
                        item.setBackground(QColor("#F1F8E9"))  # Light green
                    
                    self.results_table.setItem(row, col, item)
                
                # Total score with proper visual highlighting
                total_item = QTableWidgetItem(f"{totals[idx]:.4f}")
                total_item.setTextAlignment(Qt.AlignCenter)
                total_item.setFont(QFont("Roboto", 10, QFont.Bold))
                
                # Highlight based on ranking
                if row == 0:  # Best option
                    total_item.setBackground(QColor("#4CAF50"))
                    # total_item.setForeground(QColor("white"))
                elif row == 1:  # Second best
                    total_item.setBackground(QColor("#81C784"))
                    # total_item.setForeground(QColor("white"))
                elif row == 2:  # Third best
                    total_item.setBackground(QColor("#A5D6A7"))
                    
                self.results_table.setItem(row, len(criteria) + 1, total_item)
            
            # Show visualization of top 3 phones
            for i in range(min(3, len(sorted_indices))):
                idx = sorted_indices[i]
                name_label, score_label = self.top_positions[i]
                name_label.setText(alternatives[idx])
                score_label.setText(f"Score: {totals[idx]:.4f}")
            
            self.visualization_widget.setVisible(True)
            
            # Show conclusion
            ideal_phone = alternatives[sorted_indices[0]]
            second_phone = alternatives[sorted_indices[1]]
            ideal_score = totals[sorted_indices[0]]
            second_score = totals[sorted_indices[1]]
            
            # Calculate percentage difference between top phones
            percentage_diff = ((ideal_score - second_score) / second_score) * 100 if second_score > 0 else 0
            
            conclusion_text = (
                f"Based on your criteria preferences, the <b>{ideal_phone}</b> is the optimal choice "
                f"with an overall score of <b>{ideal_score:.4f}</b>. "
            )
            
            if percentage_diff > 15:
                conclusion_text += f"It significantly outperforms the {second_phone} by {percentage_diff:.1f}%."
            elif percentage_diff > 5:
                conclusion_text += f"It outperforms the {second_phone} by {percentage_diff:.1f}%."
            else:
                conclusion_text += f"It slightly edges out the {second_phone} (difference: {percentage_diff:.1f}%)."
            
            self.conclusion_text.setText(conclusion_text)
            self.conclusion_frame.setVisible(True)
            
            # Animate results appearance
            self.results_card.setMaximumHeight(0)
            self.animation.setStartValue(0)
            self.animation.setEndValue(1000)  # Large enough to show all content
            self.animation.start()
            
            self.progress_bar.setVisible(False)
            self.tabs.setCurrentIndex(2)  # Switch to results tab

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display results: {str(e)}")

    def reset_inputs(self):
        """Reset all inputs and results."""
        # Reset alternatives and criteria
        self.alt_input.setText("iPhone 12,Itel A56,Tecno Camon 12,Infinix Hot 10,Huawei P30,Google Pixel 7,Xiaomi Redmi Note 10,Samsung Galaxy S22,Motorola Razr+,iPhone XR,Samsung Galaxy Note 10")
        self.crit_input.setText("Memory,Storage,CPU Frequency,Price,Brand")
        
        # Reset criteria matrix
        self.crit_matrix_table.setRowCount(5)
        self.crit_matrix_table.setColumnCount(5)
        criteria = ["Memory", "Storage", "CPU Frequency", "Price", "Brand"]
        self.crit_matrix_table.setHorizontalHeaderLabels(criteria)
        self.crit_matrix_table.setVerticalHeaderLabels(criteria)
        crit_matrix_data = [
            [1, 5, 3, 3, 7],
            [0.2, 1, 0.333, 0.333, 5],
            [0.333, 3, 1, 1, 5],
            [0.333, 3, 1, 1, 5],
            [0.143, 0.2, 0.2, 0.2, 1]
        ]
        
        for i in range(5):
            for j in range(5):
                value = round(crit_matrix_data[i][j], 3)
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.crit_matrix_table.setItem(i, j, item)
                
                # Color coding based on value intensity
                if i == j:  # Diagonal is always 1
                    item.setBackground(QColor("#E0E0E0"))
                elif value >= 7:
                    item.setBackground(QColor("#26A69A"))
                    item.setForeground(QColor("white"))
                elif value >= 5:
                    item.setBackground(QColor("#4DB6AC"))
                elif value >= 3:
                    item.setBackground(QColor("#80CBC4"))
                elif value > 1:
                    item.setBackground(QColor("#B2DFDB"))
                else:
                    # Values less than 1 (inverse preferences)
                    intensity = max(0.2, min(1.0, value * 0.8))
                    item.setBackground(QColor(f"rgba(224, 224, 224, {intensity})"))

        # Reset specs table
        memory_specs = [8, 2, 3, 3, 4, 12, 4, 12, 4, 6, 6]
        storage_specs = [256, 64, 64, 64, 128, 256, 128, 512, 128, 128, 256]
        cpu_specs = [3.0, 1.5, 1.8, 1.8, 2.0, 3.0, 2.0, 3.2, 2.0, 2.5, 2.8]
        price_specs = [800, 150, 200, 200, 300, 700, 300, 1000, 400, 600, 900]
        brand_scores = [8, 1, 2, 2, 7, 8, 5, 10, 5, 7, 9]
        
        for i in range(11):
            # Phone name
            name_item = QTableWidgetItem(self.alternatives[i])
            name_item.setFont(QFont("Roboto", 10, QFont.Bold))
            self.specs_table.setItem(i, 0, name_item)
            
            # Specs with highlighting
            specs_data = [
                (memory_specs[i], 1, max(memory_specs)),
                (storage_specs[i], 2, max(storage_specs)),
                (cpu_specs[i], 3, max(cpu_specs)),
                (price_specs[i], 4, min(price_specs)),  # For price, lower is better
                (brand_scores[i], 5, max(brand_scores))
            ]
            
            for value, col, benchmark in specs_data:
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Reset cell background
                is_best = False
                if col == 4:  # Price - lower is better
                    is_best = value == benchmark
                    intensity = 1 - (value - benchmark) / (max(price_specs) - benchmark + 1)
                else:  # Other specs - higher is better
                    is_best = value == benchmark
                    intensity = value / (benchmark + 0.1)
                
                # Set background color based on how good the value is
                if is_best:
                    item.setBackground(QColor("#B2DFDB"))
                elif intensity > 0.8:
                    item.setBackground(QColor("#E0F2F1"))
                
                self.specs_table.setItem(i, col, item)

        # Reset results
        self.results_table.setRowCount(0)
        self.weights_box.setVisible(False)
        self.visualization_widget.setVisible(False)
        self.conclusion_frame.setVisible(False)
        self.results_card.setVisible(False)
        self.progress_bar.setVisible(False)
        
        # Reset top positions
        for name_label, score_label in self.top_positions:
            name_label.setText("TBD")
            score_label.setText("0.00")
        
        # Switch to first tab
        self.tabs.setCurrentIndex(0)
        
        QMessageBox.information(self, "Reset Complete", "All inputs and results have been reset to default values.")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Roboto", 12))
    window = PhoneAHPWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()