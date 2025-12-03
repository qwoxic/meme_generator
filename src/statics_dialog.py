from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class StatisticsDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Статистика мемов")
        self.setStyleSheet("""
            QDialog {
                background-color: #1A1A2E;
                color: white;
                font-family: Arial;
            }
            QLabel {
                color: #E6E6FA;
                font-size: 12px;
                padding: 3px;
            }
            QTableWidget {
                background-color: #16213E;
                color: white;
                gridline-color: #8A2BE2;
                font-size: 11px;
                selection-background-color: #8A2BE2;
            }
            QHeaderView::section {
                background-color: #0F3460;
                color: white;
                padding: 6px;
                font-weight: bold;
                border: 1px solid #8A2BE2;
            }
        """)
        self.init_ui()
        self.center_window()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Верхний текст", "Нижний текст", "Дата", 
            "Просмотры", "Скачивания", "Лайки"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.table)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        from .constants import BUTTON_STYLE
        
        export_csv_btn = QPushButton("Экспорт в CSV")
        export_csv_btn.setStyleSheet(BUTTON_STYLE)
        export_csv_btn.clicked.connect(self.export_to_csv)
        
        refresh_btn = QPushButton("Обновить")
        refresh_btn.setStyleSheet(BUTTON_STYLE)
        refresh_btn.clicked.connect(self.load_data)
        
        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet(BUTTON_STYLE)
        close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(export_csv_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.load_data()
    
    def load_data(self):
        stats = self.db.get_statistics()
        self.table.setRowCount(len(stats))
        
        for row_idx, row_data in enumerate(stats):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)
    
    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить статистику", "meme_statistics.csv", "CSV Files (*.csv)"
        )
        if file_path:
            self.db.export_to_csv(file_path)
            QMessageBox.information(self, "Успех", "Статистика экспортирована в CSV")
    
    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() // 2 - 400,
            screen.height() // 2 - 250,
            800, 500
        )
