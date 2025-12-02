# =============================================================================
# THEME.PY - Centralized Color and Style Definitions (Monochrome)
# =============================================================================

# -----------------------------------------------------------------------------
# BASE PALETTE
# -----------------------------------------------------------------------------
BLACK = "#1a1a1a"
WHITE = "#f0f0f0"
GREY_DARK = "#2b2b2b"
GREY_MEDIUM = "#404040"
GREY_LIGHT = "#666666"
ACCENT = "#00aaff" # A muted blue for highlights

# -----------------------------------------------------------------------------
# BACKGROUND COLORS
# -----------------------------------------------------------------------------
BG_MAIN = BLACK
BG_SIDEBAR = "#212121"
BG_PANEL = GREY_DARK
BG_CANVAS = GREY_DARK
BG_DARK = BLACK
BG_ROAD = GREY_MEDIUM
BG_INTERSECTION = GREY_DARK

# -----------------------------------------------------------------------------
# TEXT COLORS
# -----------------------------------------------------------------------------
TEXT_PRIMARY = WHITE
TEXT_SECONDARY = "#b3b3b3"
TEXT_MUTED = "#808080"
TEXT_DISABLED = GREY_LIGHT

# -----------------------------------------------------------------------------
# ACCENT COLORS
# -----------------------------------------------------------------------------
ACCENT_PRIMARY = ACCENT
ACCENT_SECONDARY = ACCENT
ACCENT_TERTIARY = ACCENT

# -----------------------------------------------------------------------------
# STATUS COLORS - Traffic Light (Monochrome friendly)
# -----------------------------------------------------------------------------
LIGHT_GREEN = "#77dd77"  # Soft Green
LIGHT_YELLOW = "#fdfd96" # Soft Yellow
LIGHT_RED = "#ff6961"    # Soft Red

# -----------------------------------------------------------------------------
# STATUS COLORS - Performance Indicators (Using shades of the accent color)
# -----------------------------------------------------------------------------
STATUS_GOOD = "#50c878" # Emerald
STATUS_WARNING = "#fcae1e" # Amber
STATUS_ERROR = "#ff6347" # Tomato

# -----------------------------------------------------------------------------
# MEMBERSHIP FUNCTION, RULE, AND OUTPUT COLORS
# -----------------------------------------------------------------------------
MF_LOW = STATUS_GOOD
MF_MEDIUM = STATUS_WARNING
MF_HIGH = STATUS_ERROR

RULE_KEEP = STATUS_GOOD
RULE_KEEP_ALT = "#3d9a5f" # Darker Emerald
RULE_SWITCH = STATUS_ERROR
RULE_SWITCH_TIME = "#ff8596" # Lighter Tomato
RULE_SWITCH_EMPTY = "#ff4d64" # Darker Tomato
RULE_CONFLICT = STATUS_WARNING

OUT_SWITCH = STATUS_ERROR
OUT_HOLD = STATUS_WARNING
OUT_KEEP = STATUS_GOOD

# -----------------------------------------------------------------------------
# GAUGE COLORS
# -----------------------------------------------------------------------------
GAUGE_UNDER_CAPACITY = "#334c44" # Dark green-ish
GAUGE_OVER_CAPACITY = "#4d3333"  # Dark red-ish
GAUGE_CAPACITY_LINE = ACCENT
GAUGE_DEMAND_LINE = STATUS_WARNING

# -----------------------------------------------------------------------------
# FLOW INDICATOR COLORS
# -----------------------------------------------------------------------------
FLOW_PRIMARY = ACCENT
FLOW_LOW = STATUS_ERROR
FLOW_MED = STATUS_WARNING
FLOW_HIGH = STATUS_GOOD

# -----------------------------------------------------------------------------
# CAR COLORS
# -----------------------------------------------------------------------------
CAR_NORMAL = ACCENT
CAR_WAITING = STATUS_ERROR
CAR_ANGRY = "#d450ff" # A brighter purple for "angry"

# -----------------------------------------------------------------------------
# UI ELEMENT COLORS
# -----------------------------------------------------------------------------
BORDER_LIGHT = GREY_MEDIUM
BORDER_DARK = "#202020"
BORDER_HIGHLIGHT = GREY_LIGHT
OVERFLOW_QUEUE = "#b366ff" # Muted purple

# -----------------------------------------------------------------------------
# FONTS - Using Segoe UI for consistency across all UI elements
# -----------------------------------------------------------------------------
# Font Family
FONT_FAMILY = "Segoe UI"

# Section Headers
FONT_TITLE = (FONT_FAMILY, 14, "bold")        # Main section headers
FONT_HEADING = (FONT_FAMILY, 12, "bold")      # Sub-section headers

# Body Text
FONT_NORMAL = (FONT_FAMILY, 10)               # Standard text
FONT_SMALL = (FONT_FAMILY, 9)                 # Smaller body text

# Graph/Canvas Text
FONT_TINY = (FONT_FAMILY, 8)                  # Graph titles, axis labels
FONT_MINI = (FONT_FAMILY, 7)                  # Small graph labels
FONT_MICRO = (FONT_FAMILY, 6)                 # Smallest text (membership values)

# Value Displays (Numbers)
FONT_VALUE_LARGE = (FONT_FAMILY, 20, "bold")  # Main metric values
FONT_VALUE_MEDIUM = (FONT_FAMILY, 12, "bold") # Secondary values
FONT_VALUE_SMALL = (FONT_FAMILY, 10, "bold")  # Small value displays

# Labels
FONT_LABEL = (FONT_FAMILY, 9)                 # Form labels
FONT_LABEL_BOLD = (FONT_FAMILY, 9, "bold")    # Bold labels

# Special
FONT_SCORE = (FONT_FAMILY, 11, "bold")        # Fuzzy score display
FONT_STATUS = (FONT_FAMILY, 8, "bold")        # Status indicators

# -----------------------------------------------------------------------------
# STYLE CONSTANTS
# -----------------------------------------------------------------------------
CORNER_RADIUS = 4
BORDER_WIDTH = 1
SASH_WIDTH = 8

# Padding Constants
PAD_TINY = 2          # Minimal spacing (grid cells, tight layouts)
PAD_SMALL = 5         # Standard small spacing
PAD_MEDIUM = 10       # Section padding, frame margins
PAD_LARGE = 15        # Section separator spacing
PAD_XLARGE = 20       # Major section dividers

# Semantic Padding (for specific use cases)
PAD_SECTION_TOP = (PAD_LARGE, PAD_SMALL)      # Section header (top, bottom)
PAD_SECTION_START = (PAD_XLARGE, PAD_SMALL)   # First section after title
PAD_ROW = PAD_TINY                             # Between rows in a group
PAD_ELEMENT = PAD_SMALL                        # Between elements in a row
PAD_FRAME = PAD_MEDIUM                         # Frame internal padding
PAD_BUTTON = PAD_XLARGE                        # Around buttons

# -----------------------------------------------------------------------------
# HELPER FUNCTION - Get color for efficiency value
# -----------------------------------------------------------------------------
def get_efficiency_color(efficiency):
    """Return color based on efficiency percentage"""
    if efficiency >= 80:
        return STATUS_GOOD
    elif efficiency >= 50:
        return STATUS_WARNING
    else:
        return STATUS_ERROR

# -----------------------------------------------------------------------------
# HELPER FUNCTION - Get color for flow status
# -----------------------------------------------------------------------------
def get_flow_status(current_flow, target_flow):
    """Return status text, color based on flow ratio"""
    if current_flow < target_flow * 0.5:
        return "⚠ Congested", STATUS_ERROR
    elif current_flow >= target_flow * 0.9:
        return "✓ Flowing", STATUS_GOOD
    else:
        return "~ Building", STATUS_WARNING

# -----------------------------------------------------------------------------
# HELPER FUNCTION - Get color for score region
# -----------------------------------------------------------------------------
def get_score_color(score):
    """Return color based on fuzzy score"""
    if score < 35:
        return STATUS_ERROR
    elif score < 65:
        return STATUS_WARNING
    else:
        return STATUS_GOOD

# -----------------------------------------------------------------------------
# HELPER FUNCTION - Get capacity warning color
# -----------------------------------------------------------------------------
def get_capacity_color(target_flow, theoretical_capacity):
    """Return color based on demand vs capacity"""
    if target_flow > theoretical_capacity * 1.2:
        return STATUS_ERROR      # Over capacity - will congest
    elif target_flow > theoretical_capacity * 0.9:
        return STATUS_WARNING    # Near capacity
    else:
        return ACCENT_PRIMARY    # Under capacity - OK

# -----------------------------------------------------------------------------
# HELPER FUNCTION - Get gauge bar color
# -----------------------------------------------------------------------------
def get_gauge_bar_color(current_flow, target_flow):
    """Return bar color based on flow performance"""
    if current_flow >= target_flow * 0.9:
        return STATUS_GOOD       # Meeting demand
    elif current_flow >= target_flow * 0.6:
        return STATUS_WARNING    # Partial
    else:
        return STATUS_ERROR      # Congested
