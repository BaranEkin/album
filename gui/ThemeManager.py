from PyQt5.QtGui import QPalette, QColor
from gui.constants import Constants


class ThemeManager:
    """
    A class to manage application themes and apply them to the application.
    Provides color schemes for Light, Dark, and Classic themes.
    """

    # Theme identifiers
    THEME_LIGHT = Constants.SETTINGS_THEME_LIGHT
    THEME_DARK = Constants.SETTINGS_THEME_DARK
    THEME_CLASSIC = Constants.SETTINGS_THEME_CLASSIC

    # Light Theme Colors - Original app styling
    LIGHT_THEME = {
        "window_background": "#F0F0F0",
        "widget_background": "#F0F0F0",
        "thumbnail_background": "#FFFFFF",
        "image_viewer_background": "#A0A0A0",
        "text_primary": "#000000",
        "text_secondary": "#555555",
        "accent_color": "#2196F3",
        "selection_background": "#90CAF9",
        "browser_background": "#FFFFFF",
        "title_text_color": "#00008B",
        "location_text_color": "#8B0000",
        "date_text_color": "#006400",
    }

    # Dark Theme Colors - Based on design_dark.py
    DARK_THEME = {
        "window_background": "#262626",
        "widget_background": "#262626",
        "thumbnail_background": "#2E2E2E",
        "image_viewer_background": "#1A1A1A",
        "text_primary": "#D4D4D4",
        "text_secondary": "#8F8F8F",
        "accent_color": "#4a90e2",
        "selection_background": "#2E2E2E",
        "browser_background": "#2E2E2E",
        "title_text_color": "#5D8ADB",
        "location_text_color": "#DE563E",
        "date_text_color": "#6FC967",
    }

    # Classic Theme Colors - Album Classic
    CLASSIC_THEME = {
        "window_background": "#F0F0F0",
        "widget_background": "#F0F0F0",
        "thumbnail_background": "#FFFFFF",
        "image_viewer_background": "#000000",
        "text_primary": "#000000",
        "text_secondary": "#555555",
        "accent_color": "#0078D7",
        "selection_background": "#ADD8E6",
        "browser_background": "#F5F5F5",
        "title_text_color": "#0000FF",
        "location_text_color": "#800000",
        "date_text_color": "#008000",
    }

    @classmethod
    def get_theme_colors(cls, theme_name):
        """Get the color dictionary for the specified theme"""
        if theme_name == cls.THEME_DARK:
            return cls.DARK_THEME
        elif theme_name == cls.THEME_CLASSIC:
            return cls.CLASSIC_THEME
        else:
            # Default to light theme
            return cls.LIGHT_THEME

    @classmethod
    def apply_theme(cls, app, theme_name):
        """Apply the specified theme to the application"""
        colors = cls.get_theme_colors(theme_name)

        # Create a palette for the application
        palette = QPalette()

        # Set window and widget backgrounds
        palette.setColor(QPalette.Window, QColor(colors["window_background"]))
        palette.setColor(QPalette.WindowText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.Base, QColor(colors["widget_background"]))
        palette.setColor(QPalette.AlternateBase, QColor(colors["window_background"]))

        # Set text colors
        palette.setColor(QPalette.Text, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ButtonText, QColor(colors["text_primary"]))

        # Set highlight colors
        palette.setColor(QPalette.Highlight, QColor(colors["accent_color"]))
        palette.setColor(QPalette.HighlightedText, QColor("white"))

        # Set disabled colors
        palette.setColor(
            QPalette.Disabled, QPalette.WindowText, QColor(colors["text_secondary"])
        )
        palette.setColor(
            QPalette.Disabled, QPalette.Text, QColor(colors["text_secondary"])
        )
        palette.setColor(
            QPalette.Disabled, QPalette.ButtonText, QColor(colors["text_secondary"])
        )

        if theme_name == cls.THEME_DARK:
            palette.setColor(QPalette.Button, QColor(colors["window_background"]))
        # Apply the palette to the application
        app.setPalette(palette)

        # Return the colors dictionary for custom styling
        return colors

    @classmethod
    def get_stylesheet(cls, theme_name):
        """Generate a minimal stylesheet for the application based on the theme"""
        colors = cls.get_theme_colors(theme_name)

        # Only style the specific areas we need to customize
        return f"""
        /* Only apply background colors to specific components */
        QScrollArea#imageViewer {{
            background-color: {colors["image_viewer_background"]};
        }}
        
        QListView#thumbnailList {{
            background-color: {colors["thumbnail_background"]};
        }}
        
        /* Set background for image label */
        LabelImageViewer {{
            background-color: {colors["image_viewer_background"]};
        }}
        
        /* Frame backgrounds */
        QFrame#menuFrame {{
            background-color: {colors["widget_background"]};
            border-right: 1px solid {colors["window_background"]};
        }}
        
        QFrame#bottomFrame {{
            background-color: {colors["widget_background"]};
            border-top: 1px solid {colors["window_background"]};
        }}
        
        /* Browser components styling */
        TextBrowserDate#titleBrowser {{
            background-color: {colors["browser_background"]};
            color: {colors["title_text_color"]};
        }}
        
        TextBrowserDate#locationBrowser {{
            background-color: {colors["browser_background"]};
            color: {colors["location_text_color"]};
        }}
        
        TextBrowserDate#dateBrowser {{
            background-color: {colors["browser_background"]};
            color: {colors["date_text_color"]};
        }}
        
        /* Dialog components styling */
        QTextBrowser#notesBrowser {{
            background-color: {colors["browser_background"]};
            color: {colors["text_primary"]};
        }}
        
        QTextBrowser#peopleBrowser {{
            background-color: {colors["browser_background"]};
            color: {colors["date_text_color"]};
        }}
        
        /* Album container styling */
        QWidget#albumsContainer {{
            background-color: {colors["widget_background"]};
        }}
        """
