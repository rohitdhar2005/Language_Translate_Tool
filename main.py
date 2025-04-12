import sys
import os
import json
import googletrans
from googletrans import Translator
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QComboBox, QPushButton, 
                            QTextEdit, QListWidget, QListWidgetItem, QFrame, 
                            QMessageBox, QGridLayout, QGroupBox)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor

class TranslationHistoryItem(QWidget):
    restore_signal = pyqtSignal(object)
    delete_signal = pyqtSignal(str)
    
    def __init__(self, translation_data, parent=None):
        super().__init__(parent)
        self.translation_data = translation_data
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Language information
        lang_label = QLabel(f"{self.translation_data['source_lang']} → {self.translation_data['target_lang']}")
        lang_label.setFixedWidth(150)
        lang_label.setStyleSheet("font-weight: bold;")
        
        # Source text (truncated if needed)
        display_text = self.translation_data['source_text']
        if len(display_text) > 50:
            display_text = display_text[:50] + "..."
        text_label = QLabel(display_text)
        text_label.setStyleSheet("color: #444;")
        
        # Action buttons
        restore_btn = QPushButton("Restore")
        restore_btn.setFixedWidth(70)
        restore_btn.setStyleSheet("color: #4a6cf7; border: none; background: none;")
        restore_btn.clicked.connect(self.restore_clicked)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setFixedWidth(70)
        delete_btn.setStyleSheet("color: #4a6cf7; border: none; background: none;")
        delete_btn.clicked.connect(self.delete_clicked)
        
        layout.addWidget(lang_label)
        layout.addWidget(text_label, 1)  # Give text label more space
        layout.addWidget(restore_btn)
        layout.addWidget(delete_btn)
        layout.setContentsMargins(10, 5, 10, 5)
        
    def restore_clicked(self):
        self.restore_signal.emit(self.translation_data)
        
    def delete_clicked(self):
        self.delete_signal.emit(self.translation_data['id'])

class FeatureCard(QGroupBox):
    def __init__(self, icon, title, description, parent=None):
        super().__init__(parent)
        self.setTitle("")
        self.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #eee;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Icon label
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 24))
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Title label
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        # Description label
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666;")
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        
        # Add hover effect
        self.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #eee;
                padding: 15px;
            }
            QGroupBox:hover {
                border: 1px solid #4a6cf7;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }
        """)

class TranslationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.translator = Translator()
        self.translations_history = []
        self.load_history()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("LinguaTranslate - Translation App")
        self.setMinimumSize(900, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QLabel {
                font-family: 'Segoe UI', sans-serif;
                color: #333;
            }
            QComboBox {
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #ddd;
                background-color: white;
                min-width: 150px;
            }
            QPushButton {
                background-color: #4a6cf7;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a5ce5;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #4a6cf7; color: white; border-radius: 5px;")
        header_layout = QHBoxLayout(header)
        
        logo = QLabel("Lingua<span style='color: #ffd700;'>Translate</span>")
        logo.setStyleSheet("font-size: 24px; font-weight: bold;")
        logo.setTextFormat(Qt.RichText)
        
        header_layout.addWidget(logo)
        header_layout.addStretch()
        
        main_layout.addWidget(header)
        
        # Translation container
        translation_group = QGroupBox("Translation")
        translation_layout = QVBoxLayout(translation_group)
        
        # Language controls
        lang_control = QFrame()
        lang_control.setStyleSheet("background-color: #f0f2f5; border-radius: 5px;")
        lang_layout = QHBoxLayout(lang_control)
        
        # Source language
        source_lang_layout = QHBoxLayout()
        source_lang_label = QLabel("From:")
        self.source_lang_combo = QComboBox()
        
        # Add language options
        languages = googletrans.LANGUAGES
        self.source_lang_combo.addItem("Detect Language", "auto")
        for code, language in languages.items():
            self.source_lang_combo.addItem(language.capitalize(), code)
        
        source_lang_layout.addWidget(source_lang_label)
        source_lang_layout.addWidget(self.source_lang_combo)
        
        # Swap button
        self.swap_btn = QPushButton("⇆")
        self.swap_btn.setFixedSize(40, 40)
        self.swap_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a6cf7;
                color: white;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #3a5ce5;
            }
        """)
        self.swap_btn.clicked.connect(self.swap_languages)
        
        # Target language
        target_lang_layout = QHBoxLayout()
        target_lang_label = QLabel("To:")
        self.target_lang_combo = QComboBox()
        
        # Add language options
        for code, language in languages.items():
            self.target_lang_combo.addItem(language.capitalize(), code)
        
        # Set default target to English
        self.target_lang_combo.setCurrentIndex(self.target_lang_combo.findData("en"))
        
        target_lang_layout.addWidget(target_lang_label)
        target_lang_layout.addWidget(self.target_lang_combo)
        
        lang_layout.addLayout(source_lang_layout)
        lang_layout.addWidget(self.swap_btn)
        lang_layout.addLayout(target_lang_layout)
        
        translation_layout.addWidget(lang_control)
        
        # Text areas
        text_areas_layout = QHBoxLayout()
        
        # Source text
        source_layout = QVBoxLayout()
        source_label = QLabel("Enter text to translate:")
        self.source_text = QTextEdit()
        self.source_text.setPlaceholderText("Enter text to translate...")
        
        # Clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f2f5;
                color: #666;
                border: 1px solid #ddd;
            }
            QPushButton:hover {
                background-color: #e0e2e5;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_text)
        
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_text)
        source_layout.addWidget(self.clear_btn, alignment=Qt.AlignRight)
        
        # Target text
        target_layout = QVBoxLayout()
        target_label = QLabel("Translation:")
        self.target_text = QTextEdit()
        self.target_text.setPlaceholderText("Translation will appear here...")
        self.target_text.setReadOnly(True)
        
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_text)
        target_layout.addSpacing(40)  # Space for the clear button on the other side
        
        text_areas_layout.addLayout(source_layout)
        text_areas_layout.addLayout(target_layout)
        
        translation_layout.addLayout(text_areas_layout)
        
        # Translate button
        translate_btn_layout = QHBoxLayout()
        translate_btn_layout.addStretch()
        
        self.translate_btn = QPushButton("Translate")
        self.translate_btn.setFixedSize(150, 40)
        self.translate_btn.clicked.connect(self.translate_text)
        
        translate_btn_layout.addWidget(self.translate_btn)
        translate_btn_layout.addStretch()
        
        translation_layout.addLayout(translate_btn_layout)
        
        # Attribution
        attribution = QLabel("Powered by Google Translate API")
        attribution.setAlignment(Qt.AlignCenter)
        attribution.setStyleSheet("color: #666; font-size: 12px;")
        
        translation_layout.addWidget(attribution)
        
        main_layout.addWidget(translation_group)
        
        # History section
        history_group = QGroupBox("Recent Translations")
        history_layout = QVBoxLayout(history_group)
        
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #eee;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #f9f9f9;
            }
        """)
        
        history_layout.addWidget(self.history_list)
        
        main_layout.addWidget(history_group)
        
        # Features section
        features_group = QGroupBox("Why Choose LinguaTranslate?")
        features_layout = QGridLayout(features_group)
        
        features = [
            ("🌐", "100+ Languages", "Translate between more than 100 languages with high accuracy and natural-sounding results."),
            ("⚡", "Fast & Reliable", "Get instant translations powered by Google's advanced technology for quick and reliable results."),
            ("📱", "User Friendly", "Easy-to-use interface that makes translation simple and efficient."),
            ("🔒", "Secure & Private", "Your content remains private and secure. We don't store your translations longer than necessary."),
            ("🇮🇳", "Global Languages", "Translate to and from major languages from around the world including many regional languages."),
            ("💬", "Context Aware", "Google's AI understands context and nuance to provide more accurate translations.")
        ]
        
        for i, (icon, title, desc) in enumerate(features):
            row, col = divmod(i, 3)
            card = FeatureCard(icon, title, desc)
            features_layout.addWidget(card, row, col)
        
        main_layout.addWidget(features_group)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Load history
        self.update_history_ui()
    
    def translate_text(self):
        source_text = self.source_text.toPlainText().strip()
        
        if not source_text:
            QMessageBox.warning(self, "Input Required", "Please enter text to translate.")
            return
        
        source_lang = self.source_lang_combo.currentData()
        target_lang = self.target_lang_combo.currentData()
        
        try:
            # Show "Translating..." message
            self.target_text.setPlainText("Translating...")
            QApplication.processEvents()  # Update UI
            
            # Perform translation
            if source_lang == "auto":
                translation = self.translator.translate(source_text, dest=target_lang)
                detected_source = translation.src
                source_lang_name = googletrans.LANGUAGES.get(detected_source, "Unknown").capitalize()
            else:
                translation = self.translator.translate(source_text, src=source_lang, dest=target_lang)
                source_lang_name = self.source_lang_combo.currentText()
            
            translated_text = translation.text
            target_lang_name = self.target_lang_combo.currentText()
            
            # Update target text
            self.target_text.setPlainText(translated_text)
            
            # Save to history
            translation_data = {
                "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                "source_lang": source_lang_name,
                "target_lang": target_lang_name,
                "source_text": source_text,
                "target_text": translated_text,
                "source_lang_code": source_lang if source_lang != "auto" else translation.src,
                "target_lang_code": target_lang,
                "timestamp": datetime.now().isoformat()
            }
            
            self.translations_history.insert(0, translation_data)
            
            # Keep only the last 10 translations
            if len(self.translations_history) > 10:
                self.translations_history = self.translations_history[:10]
            
            # Save history to file
            self.save_history()
            
            # Update history UI
            self.update_history_ui()
            
        except Exception as e:
            self.target_text.setPlainText("")
            QMessageBox.critical(self, "Translation Error", f"Failed to translate: {str(e)}")
    
    def swap_languages(self):
        source_index = self.source_lang_combo.currentIndex()
        target_index = self.target_lang_combo.currentIndex()
        
        # Don't swap if source language is set to auto-detect
        if self.source_lang_combo.currentData() == "auto":
            QMessageBox.information(self, "Cannot Swap", "Cannot swap when source language is set to auto-detect.")
            return
        
        self.source_lang_combo.setCurrentIndex(target_index)
        self.target_lang_combo.setCurrentIndex(source_index - 1)  # -1 because source has "auto" option
        
        # If there's already content, swap that too
        if self.source_text.toPlainText().strip() and self.target_text.toPlainText().strip():
            source_content = self.source_text.toPlainText()
            target_content = self.target_text.toPlainText()
            
            self.source_text.setPlainText(target_content)
            self.target_text.setPlainText(source_content)
    
    def clear_text(self):
        self.source_text.clear()
        self.target_text.clear()
    
    def restore_translation(self, translation_data):
        # Set languages
        source_lang_index = self.source_lang_combo.findData(translation_data["source_lang_code"])
        if source_lang_index == -1:  # If not found, might be because it was auto-detected
            source_lang_index = 0  # Set to "auto"
        self.source_lang_combo.setCurrentIndex(source_lang_index)
        
        target_lang_index = self.target_lang_combo.findData(translation_data["target_lang_code"])
        if target_lang_index != -1:
            self.target_lang_combo.setCurrentIndex(target_lang_index)
        
        # Set text
        self.source_text.setPlainText(translation_data["source_text"])
        self.target_text.setPlainText(translation_data["target_text"])
    
    def delete_translation(self, translation_id):
        self.translations_history = [t for t in self.translations_history if t["id"] != translation_id]
        self.save_history()
        self.update_history_ui()
    
    def update_history_ui(self):
        self.history_list.clear()
        
        if not self.translations_history:
            item = QListWidgetItem()
            widget = QLabel("No translations yet")
            widget.setStyleSheet("padding: 10px;")
            item.setSizeHint(widget.sizeHint())
            self.history_list.addItem(item)
            self.history_list.setItemWidget(item, widget)
            return
        
        for translation in self.translations_history:
            item = QListWidgetItem()
            widget = TranslationHistoryItem(translation)
            widget.restore_signal.connect(self.restore_translation)
            widget.delete_signal.connect(self.delete_translation)
            
            item.setSizeHint(widget.sizeHint())
            self.history_list.addItem(item)
            self.history_list.setItemWidget(item, widget)
    
    def save_history(self):
        history_path = os.path.join(os.path.expanduser("~"), ".linguatranslate_history.json")
        try:
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(self.translations_history, f)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_history(self):
        history_path = os.path.join(os.path.expanduser("~"), ".linguatranslate_history.json")
        try:
            if os.path.exists(history_path):
                with open(history_path, "r", encoding="utf-8") as f:
                    self.translations_history = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslationApp()
    window.show()
    sys.exit(app.exec_())
