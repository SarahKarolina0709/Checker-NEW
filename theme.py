# theme.py

class Theme:
    """
    Defines the color palette, fonts, and other styling constants for the application.
    """
    # Light Color Palette (to fix transparency issues)
    BACKGROUND = "#FFFFFF"  # Pure white
    FRAME_BG = "#F5F5F5"    # Light gray
    FRAME_BORDER = "#E0E0E0"  # Border gray
    TEXT = "#333333"        # Dark gray text
    TEXT_DIM = "#666666"    # Medium gray
    TEXT_DISABLED = "#CCCCCC"  # Light gray for disabled
    PRIMARY = "#0078D4"     # Microsoft blue
    PRIMARY_HOVER = "#106EBE"  # Darker blue on hover
    SECONDARY = "#5C2D91"   # Purple
    SUCCESS = "#107C10"     # Green
    WARNING = "#FF8C00"     # Orange
    ERROR = "#D13438"       # Red

    # Fonts
    FONT_FAMILY_MAIN = "Roboto" # A clean, modern font. Ensure it's installed.
    FONT_FAMILY_CODE = "Fira Code" # A good font for monospaced text.
    
    FONT_SIZE_XL = 24
    FONT_SIZE_L = 18
    FONT_SIZE_M = 14
    FONT_SIZE_S = 12
    FONT_SIZE_XS = 10

    # Padding & Spacing
    PAD_XL = 20
    PAD_L = 15
    PAD_M = 10
    PAD_S = 5
    PAD_XS = 2

    # Corner Radius
    CORNER_RADIUS = 8
