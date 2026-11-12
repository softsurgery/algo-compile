"""
Color themes and syntax highlighting presets for Algoo Code Editor.
Provides predefined palettes for Dark and Light modes (Algoo, VS Code, Monokai, Nord, Dracula, Solarized, Classic).
"""

from typing import Dict, Any

DEFAULT_SYNTAX_COLORS_DARK: Dict[str, str] = {
    "keyword": "#89b4fa",
    "control": "#cba6f7",
    "type": "#fab387",
    "builtin": "#94e2d5",
    "operator": "#f38ba8",
    "string": "#a6e3a1",
    "literal": "#a6e3a1",
    "comment": "#6c7086",
}

DEFAULT_SYNTAX_COLORS_LIGHT: Dict[str, str] = {
    "keyword": "#0969da",
    "control": "#8250df",
    "type": "#953800",
    "builtin": "#0550ae",
    "operator": "#cf222e",
    "string": "#0a7029",
    "literal": "#1a7f37",
    "comment": "#6e7781",
}

SYNTAX_PRESETS: Dict[str, Dict[str, Any]] = {
    "Algoo": {
        "description": "Palette moderne Algoo (Catppuccin Mocha & GitHub Primer)",
        "dark": DEFAULT_SYNTAX_COLORS_DARK,
        "light": DEFAULT_SYNTAX_COLORS_LIGHT,
    },
    "VS Code": {
        "description": "Palette officielle Visual Studio Code (Dark+ & Light+)",
        "dark": {
            "keyword": "#569cd6",
            "control": "#c586c0",
            "type": "#4ec9b0",
            "builtin": "#dcdcaa",
            "operator": "#d4d4d4",
            "string": "#ce9178",
            "literal": "#b5cea8",
            "comment": "#6a9955",
        },
        "light": {
            "keyword": "#0000ff",
            "control": "#af00db",
            "type": "#267f99",
            "builtin": "#795e26",
            "operator": "#000000",
            "string": "#a31515",
            "literal": "#098658",
            "comment": "#008000",
        },
    },
    "Monokai": {
        "description": "Palette emblématique Monokai Pro & Sublime Text",
        "dark": {
            "keyword": "#f92672",
            "control": "#fd971f",
            "type": "#66d9ef",
            "builtin": "#a6e22e",
            "operator": "#f92672",
            "string": "#e6db74",
            "literal": "#ae81ff",
            "comment": "#75715e",
        },
        "light": {
            "keyword": "#d33682",
            "control": "#cb4b16",
            "type": "#268bd2",
            "builtin": "#859900",
            "operator": "#d33682",
            "string": "#b58900",
            "literal": "#6c71c4",
            "comment": "#93a1a1",
        },
    },
    "Nord": {
        "description": "Teintes froides et reposantes inspirées du Grand Nord",
        "dark": {
            "keyword": "#81a1c1",
            "control": "#bf616a",
            "type": "#8fbcbb",
            "builtin": "#88c0d0",
            "operator": "#d8dee9",
            "string": "#a3be8c",
            "literal": "#b48ead",
            "comment": "#616e88",
        },
        "light": {
            "keyword": "#5e81ac",
            "control": "#bf616a",
            "type": "#8fbcbb",
            "builtin": "#88c0d0",
            "operator": "#4c566a",
            "string": "#a3be8c",
            "literal": "#b48ead",
            "comment": "#9099a9",
        },
    },
    "Dracula": {
        "description": "Thème officiel Dracula à fort contraste",
        "dark": {
            "keyword": "#ff79c6",
            "control": "#ffb86c",
            "type": "#8be9fd",
            "builtin": "#50fa7b",
            "operator": "#f8f8f2",
            "string": "#f1fa8c",
            "literal": "#bd93f9",
            "comment": "#6272a4",
        },
        "light": {
            "keyword": "#d63384",
            "control": "#fd7e14",
            "type": "#0dcaf0",
            "builtin": "#198754",
            "operator": "#212529",
            "string": "#ffc107",
            "literal": "#6f42c1",
            "comment": "#6c757d",
        },
    },
    "Solarized": {
        "description": "Palette équilibrée et scientifique Solarized",
        "dark": {
            "keyword": "#859900",
            "control": "#cb4b16",
            "type": "#b58900",
            "builtin": "#268bd2",
            "operator": "#93a1a1",
            "string": "#2aa198",
            "literal": "#d33682",
            "comment": "#586e75",
        },
        "light": {
            "keyword": "#859900",
            "control": "#cb4b16",
            "type": "#b58900",
            "builtin": "#268bd2",
            "operator": "#657b83",
            "string": "#2aa198",
            "literal": "#d33682",
            "comment": "#93a1a1",
        },
    },
    "Classic": {
        "description": "Palette pédagogique classique style Thonny & IDLE",
        "dark": {
            "keyword": "#ff7700",
            "control": "#ff5555",
            "type": "#55ffff",
            "builtin": "#aa55ff",
            "operator": "#ffffff",
            "string": "#00ff00",
            "literal": "#ffaa00",
            "comment": "#888888",
        },
        "light": {
            "keyword": "#7f0055",
            "control": "#ff5500",
            "type": "#0000c0",
            "builtin": "#900090",
            "operator": "#000000",
            "string": "#2a00ff",
            "literal": "#0000ff",
            "comment": "#3f7f5f",
        },
    },
}


def get_syntax_preset(preset_name: str) -> Dict[str, Any]:
    """Retrieves preset definition by name, falling back to 'Algoo' if not found."""
    return SYNTAX_PRESETS.get(preset_name, SYNTAX_PRESETS["Algoo"])


def get_default_syntax_colors(is_dark: bool) -> Dict[str, str]:
    """Returns the default palette colors for dark or light mode."""
    return dict(DEFAULT_SYNTAX_COLORS_DARK if is_dark else DEFAULT_SYNTAX_COLORS_LIGHT)
