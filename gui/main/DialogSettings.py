from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QComboBox, QCheckBox, QSpinBox, QPushButton, QTabWidget,
    QFormLayout, QFrame, QLineEdit, QFileDialog, QMessageBox, QWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from gui.constants import Constants
from config.config import Config
from logger import log
from gui.message import show_message


class DialogSettings(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(Constants.SETTINGS_DIALOG_TITLE)
        self.setWindowIcon(QIcon("res/icons/Setting--Streamline-Unicons.png"))
        self.setFixedSize(400, 300)
        
        # Load the current configuration
        self.config_data = Config.get_all_settings()
        
        log("DialogSettings.__init__", "Loading settings", level="info")
        
        # Create the main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create tabs for better organization
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Track original theme to detect changes
        self.original_theme = self.config_data.get("THEME", Constants.SETTINGS_THEME_DARK)
        
        # Create tabs
        self.create_general_tab()
        self.create_storage_tab()
        self.create_cloud_tab()
        
        # Create buttons layout
        self.create_buttons()
        
        # Set the main layout
        self.setLayout(self.main_layout)
    
    def create_general_tab(self):
        """Create the general settings tab"""
        general_tab = QWidget()
        self.tab_widget.addTab(general_tab, Constants.SETTINGS_TAB_GENERAL)
        
        # Create layout for general tab
        general_layout = QFormLayout(general_tab)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([Constants.SETTINGS_THEME_LIGHT, Constants.SETTINGS_THEME_DARK, Constants.SETTINGS_THEME_CLASSIC])
        current_theme = self.config_data.get("THEME", Constants.SETTINGS_THEME_DARK)
        self.theme_combo.setCurrentText(current_theme)
        general_layout.addRow(Constants.SETTINGS_THEME, self.theme_combo)
        
        # Connect theme combo box change signal
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        # Media privacy limit (0-9)
        self.privacy_spin = QSpinBox()
        self.privacy_spin.setRange(0, 9)
        self.privacy_spin.setValue(int(self.config_data.get("MEDIA_PRIVACY_LEVEL", 0)))
        general_layout.addRow(Constants.SETTINGS_PRIVACY_LIMIT, self.privacy_spin)
        
        # Latest media duration in days (1-365)
        self.latest_days_spin = QSpinBox()
        self.latest_days_spin.setRange(1, 365)
        self.latest_days_spin.setValue(int(self.config_data.get("LATEST_DURATION_DAYS", 7)))
        self.latest_days_spin.setSuffix(" gün")
        general_layout.addRow(Constants.SETTINGS_LATEST_DURATION, self.latest_days_spin)
        
        # Initial media index
        self.initial_index_combo = QComboBox()
        self.initial_index_combo.addItems([Constants.SETTINGS_INITIAL_BEGINNING, Constants.SETTINGS_INITIAL_END])
        initial_index = self.config_data.get("INITIAL_MEDIA_INDEX", Constants.SETTINGS_INITIAL_BEGINNING)
        self.initial_index_combo.setCurrentText(initial_index)
        general_layout.addRow(Constants.SETTINGS_INITIAL_INDEX, self.initial_index_combo)
        
        # Delete original after upload
        self.delete_original_check = QCheckBox()
        self.delete_original_check.setChecked(self.config_data.get("DELETE_ORIGINAL_AFTER_UPLOAD", False))
        general_layout.addRow(Constants.SETTINGS_DELETE_ORIGINAL, self.delete_original_check)
    
    def create_storage_tab(self):
        """Create the storage settings tab"""
        storage_tab = QFrame()
        storage_layout = QFormLayout(storage_tab)
        
        # Local storage enabled
        self.local_storage_check = QCheckBox()
        self.local_storage_check.setChecked(self.config_data.get("LOCAL_STORAGE_ENABLED", True))
        storage_layout.addRow(Constants.SETTINGS_LOCAL_STORAGE, self.local_storage_check)
        
        # Media directory
        self.media_dir_edit = QLineEdit(self.config_data.get("MEDIA_DIR", ""))
        storage_layout.addRow(Constants.SETTINGS_MEDIA_DIR, self.media_dir_edit)
        
        # Thumbnails directory
        self.thumbnails_dir_edit = QLineEdit(self.config_data.get("THUMBNAILS_DIR", ""))
        storage_layout.addRow(Constants.SETTINGS_THUMBNAILS_DIR, self.thumbnails_dir_edit)
        
        self.tab_widget.addTab(storage_tab, Constants.SETTINGS_TAB_STORAGE)
    
    def create_cloud_tab(self):
        """Create the cloud settings tab"""
        cloud_tab = QFrame()
        cloud_layout = QFormLayout(cloud_tab)
        
        # S3 bucket name
        self.s3_bucket_edit = QLineEdit(self.config_data.get("S3_BUCKET_NAME", ""))
        cloud_layout.addRow(Constants.SETTINGS_S3_BUCKET, self.s3_bucket_edit)
        
        # CloudFront settings
        self.cloudfront_domain_edit = QLineEdit(self.config_data.get("CLOUDFRONT_DOMAIN", ""))
        cloud_layout.addRow(Constants.SETTINGS_CLOUDFRONT_DOMAIN, self.cloudfront_domain_edit)
        
        self.cloudfront_key_id_edit = QLineEdit(self.config_data.get("CLOUDFRONT_KEY_ID", ""))
        cloud_layout.addRow(Constants.SETTINGS_CLOUDFRONT_KEY_ID, self.cloudfront_key_id_edit)
        
        self.cloudfront_key_path_edit = QLineEdit(self.config_data.get("CLOUDFRONT_KEY_PATH", ""))
        cloud_layout.addRow(Constants.SETTINGS_CLOUDFRONT_KEY_PATH, self.cloudfront_key_path_edit)
        
        self.tab_widget.addTab(cloud_tab, Constants.SETTINGS_TAB_CLOUD)
    
    def create_buttons(self):
        """Create the buttons at the bottom of the dialog"""
        button_layout = QHBoxLayout()
        
        # Save button
        self.save_button = QPushButton(Constants.SETTINGS_BUTTON_SAVE)
        self.save_button.clicked.connect(self.save_settings)
        
        # Cancel button
        self.cancel_button = QPushButton(Constants.SETTINGS_BUTTON_CANCEL)
        self.cancel_button.clicked.connect(self.reject)
        
        # Add buttons to layout
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        self.main_layout.addLayout(button_layout)
    
    def on_theme_changed(self, new_theme):
        """Handle theme combo box changes"""
        if new_theme != self.original_theme:
            log("DialogSettings.on_theme_changed", f"Theme will change to: {new_theme}", level="info")
            show_message(
                "Tema değişikliği uygulamanın yeniden başlatılmasından sonra etkin olacaktır.",
                level="info"
            )
    
    def save_settings(self):
        """Save settings using Config class methods"""
        # Update config data with new values
        settings_to_update = {
            "THEME": self.theme_combo.currentText(),
            "MEDIA_PRIVACY_LEVEL": self.privacy_spin.value(),
            "LATEST_DURATION_DAYS": self.latest_days_spin.value(),
            "INITIAL_MEDIA_INDEX": self.initial_index_combo.currentText(),
            "DELETE_ORIGINAL_AFTER_UPLOAD": self.delete_original_check.isChecked(),
            "LOCAL_STORAGE_ENABLED": self.local_storage_check.isChecked(),
            "MEDIA_DIR": self.media_dir_edit.text(),
            "THUMBNAILS_DIR": self.thumbnails_dir_edit.text(),
            "S3_BUCKET_NAME": self.s3_bucket_edit.text(),
            "CLOUDFRONT_DOMAIN": self.cloudfront_domain_edit.text(),
            "CLOUDFRONT_KEY_ID": self.cloudfront_key_id_edit.text(),
            "CLOUDFRONT_KEY_PATH": self.cloudfront_key_path_edit.text()
        }
        
        log("DialogSettings.save_settings", "Saving settings", level="info")
        
        # Use Config class to update settings
        if Config.update_settings(settings_to_update):
            self.accept()
        else:
            log("DialogSettings.save_settings", "Failed to save settings", level="error")
            show_message("Ayarlar kaydedilemedi.", level="error")
