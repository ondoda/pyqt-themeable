import re
from typing import List, Dict, Optional, Callable
from PySide6 import QtWidgets

class Theme():
    """Represents a theme."""
    def __init__(self, name:str, theme_obj:dict):
        """
        Initialize a Theme.

        Args:
            name (str): The name of the theme.
            theme_obj (dict): The theme object containing theme attributes.
        """
        self.name:str = name
        self.theme_obj:dict = theme_obj

    def __str__(self):
        """
        Get the string representation of the theme.

        Returns:
            str: The name of the theme.
        """
        return self.name

    def __repr__(self):
        """
        Get the string representation of the theme.

        Returns:
            str: The name of the theme.
        """
        return self.name


class ThemeProvider:
    """Singleton class for managing themes."""
    _instance: Optional['ThemeProvider'] = None
    _observers: List[Callable] = []
    base_theme: Theme
    themes: Dict[str, Theme]
    current_theme: Optional['Theme']

    def __new__(cls) -> 'ThemeProvider':
        """
        Create a new instance of ThemeProvider if it doesn't exist.

        Returns:
            ThemeProvider: The ThemeProvider instance.
        """
        if cls._instance is None:
            cls._instance = super(ThemeProvider, cls).__new__(cls)
            cls._instance.themes = {}
            cls._instance.current_theme = None
        return cls._instance

    def addTheme(self, name:str, theme_obj:dict):
        """
        Add a new theme to the ThemeProvider.

        Args:
            name (str): The name of the theme.
            theme_obj (dict): The theme object containing theme attributes.
        """
        if (self.base_theme is not None):
            theme_obj = {**self.base_theme.theme_obj, **theme_obj}

        self.themes[name] = Theme(name, theme_obj)

    def addBase(self, base_obj:dict):
        """
        Add a base theme to the ThemeProvider.

        Args:
            base_obj (dict): The base theme object containing base theme attributes.
        """
        self.base_theme = Theme("_base_", base_obj)

    def setTheme(self, name:str):
        """
        Set the current theme.

        Args:
            name (str): The name of the theme to set.
        """
        self.current_theme = self.themes[name]
        self.notifyObservers()

    def incrementTheme(self):
        """
        Increment the current theme to the next available theme.
        """
        themes = list(self.themes.keys())
        current_index = themes.index(self.current_theme.name)
        next_index = (current_index + 1) % len(themes)
        self.setTheme(themes[next_index])

    def getThemes(self):
        """
        Get the names of all available themes.

        Returns:
            dict_keys: The names of all available themes.
        """
        return self.themes.keys()

    def getCurrentTheme(self) -> Theme:
        """
        Get the current theme.

        Returns:
            Theme: The current theme.
        """
        return self.current_theme

    def getAttr(self, key:str, modifier:int = None):
        """
        Get the attribute value for a given key.

        Args:
            key (str): The key of the attribute.
            modifier (int, optional): The modifier value for the attribute. Defaults to None.

        Returns:
            str: The attribute value.
        """
        try:
            attr:str = self.current_theme.theme_obj.get(key, "#000000")

            if modifier:
                attr:str = self.modifyColor(attr, modifier)

            return attr

        except AttributeError:
            raise Exception("No Theme set")

    def modifyColor(self, hex_color:str, factor=500):
        """
        Modify a hex color by applying a factor.

        Args:
            hex_color (str): The hex color to modify.
            factor (int, optional): The factor to apply. Defaults to 500.

        Returns:
            str: The modified hex color.
        """
        rgb_color = hex_to_rgb(hex_color)
        darker_rgb_color = tuple(max(int(c * (1 - (factor/1000))), 0) for c in rgb_color)
        return rgb_to_hex(darker_rgb_color)

    def addObserver(self, callback:Callable):
        """
        Add an observer callback to the ThemeProvider.

        Args:
            callback (Callable): The observer callback function.
        """
        self._observers.append(callback)

    def notifyObservers(self):
        """
        Notify all observers of a theme change.
        """
        for callback in self._observers:
            callback()

    def __str__(self):
        """
        Get the string representation of the current theme.

        Returns:
            str: The name of the current theme.
        """
        return self.current_theme.name

    def __repr__(self):
        """
        Get the string representation of the current theme.

        Returns:
            str: The name of the current theme.
        """
        return self.current_theme.name


class Themeable():
    """Mixin class for making widgets themeable."""
    def __init__(self, widget:QtWidgets.QWidget = None, style_sheet:str = None):
        """
        Initialize a Themeable object.

        Args:
            widget (QtWidgets.QWidget, optional): The widget to apply the theme to. Defaults to None.
            style_sheet (str, optional): The style sheet to apply. Defaults to None.
        """
        self.provider:ThemeProvider = ThemeProvider()
        self.provider.addObserver(self.onThemeChange)
        self.style_sheet = style_sheet
        self.widget = widget

        self.widget.setStyleSheet(self.getThemeStyle())

    def _replacePlaceholders(self):
        """
        Replace theme placeholders in the style sheet with actual attribute values.

        Returns:
            str: The updated style sheet.
        """
        def replacer(match):
            attribute:str = match.group(1)
            mod:str = match.group(2)
            if mod:
                modify:int = int(mod.replace("[", "").replace("]", ""))
                return self.provider.getAttr(attribute, modify)
            else:
                return self.provider.getAttr(attribute)

        return re.sub(r'theme\.(\w+)(\[\d+\])?', replacer, self.style_sheet)

    def setWidget(self, widget:QtWidgets.QWidget):
        """
        Set the widget to apply the theme to.

        Args:
            widget (QtWidgets.QWidget): The widget to apply the theme to.
        """
        self.widget = widget

    def setThemeStyle(self, style_sheet:str):
        """
        Set the style sheet for the theme.

        Args:
            style_sheet (str): The style sheet to apply.
        """
        self.style_sheet = style_sheet

    def getThemeStyle(self):
        """
        Get the style sheet with theme placeholders replaced by attribute values.

        Returns:
            str: The updated style sheet.
        """
        if self.style_sheet is None:
            raise Exception("No StyleSheet set")

        if self.provider is None:
            raise Exception("No ThemeProvider set")

        return self._replacePlaceholders()

    def onThemeChange(self):
        """
        Callback function for handling theme changes.
        """
        self.widget.setStyleSheet(self.getThemeStyle())


def hex_to_rgb(hex_color:str) -> tuple:
    """
    Convert a hex color to RGB tuple.

    Args:
        hex_color (str): The hex color to convert.

    Returns:
        tuple: The RGB tuple.
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb_color:tuple) -> str:
    """
    Convert an RGB tuple to a hex color.

    Args:
        rgb_color (tuple): The RGB tuple to convert.

    Returns:
        str: The hex color.
    """
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

    