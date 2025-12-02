# =============================================================================
# THEME.PY - Centralized Color and Style Definitions (Muted Dark Mode)
# =============================================================================

# -----------------------------------------------------------------------------
# BASE PALETTE - Softer, less harsh dark tones
# -----------------------------------------------------------------------------
BLACK = "#141414"
WHITE = "#e0e0e0"
GREY_DARK = "#1e1e1e"
GREY_MEDIUM = "#2d2d2d"
GREY_LIGHT = "#4a4a4a"
ACCENT = "#5a9bcf"  # Muted steel blue

# -----------------------------------------------------------------------------
# BACKGROUND COLORS - Subtle variations for depth
# -----------------------------------------------------------------------------
BG_MAIN = "#0f0f0f"
BG_SIDEBAR = "#181818"
BG_PANEL = "#1c1c1c"
BG_CANVAS = "#1a1a1a"
BG_DARK = "#0c0c0c"
BG_ROAD = "#252525"
BG_INTERSECTION = "#1e1e1e"

# -----------------------------------------------------------------------------
# TEXT COLORS - Softer whites, better contrast hierarchy
# -----------------------------------------------------------------------------
TEXT_PRIMARY = "#d4d4d4"
TEXT_SECONDARY = "#9a9a9a"
TEXT_MUTED = "#666666"
TEXT_DISABLED = "#4a4a4a"

# -----------------------------------------------------------------------------
# ACCENT COLORS - Muted, cohesive palette
# -----------------------------------------------------------------------------
ACCENT_PRIMARY = "#5a9bcf"   # Muted steel blue
ACCENT_SECONDARY = "#6ba3c7" # Slightly lighter blue
ACCENT_TERTIARY = "#7eb8d8"  # Softer highlight blue

# -----------------------------------------------------------------------------
# STATUS COLORS - Traffic Light (Muted, easier on eyes)
# -----------------------------------------------------------------------------
LIGHT_GREEN = "#5b9a5b"   # Muted sage green
LIGHT_YELLOW = "#c9a227"  # Muted gold
LIGHT_RED = "#b85450"     # Muted coral red

# -----------------------------------------------------------------------------
# STATUS COLORS - Performance Indicators (Desaturated)
# -----------------------------------------------------------------------------
STATUS_GOOD = "#4a8f6a"    # Muted teal green
STATUS_WARNING = "#b8923a" # Muted amber/ochre
STATUS_ERROR = "#a65d5d"   # Muted dusty rose/red

# -----------------------------------------------------------------------------
# MEMBERSHIP FUNCTION, RULE, AND OUTPUT COLORS
# -----------------------------------------------------------------------------
MF_LOW = STATUS_GOOD
MF_MEDIUM = STATUS_WARNING
MF_HIGH = STATUS_ERROR

RULE_KEEP = "#4a8f6a"      # Muted green
RULE_KEEP_ALT = "#3d7a5a"  # Darker muted green
RULE_SWITCH = "#a65d5d"    # Muted red
RULE_SWITCH_TIME = "#b87878" # Lighter muted red
RULE_SWITCH_EMPTY = "#8f4a4a" # Darker muted red
RULE_CONFLICT = STATUS_WARNING

OUT_SWITCH = STATUS_ERROR
OUT_HOLD = STATUS_WARNING
OUT_KEEP = STATUS_GOOD

# -----------------------------------------------------------------------------
# GAUGE COLORS - Subtle, non-distracting
# -----------------------------------------------------------------------------
GAUGE_UNDER_CAPACITY = "#1f2f2a"  # Very dark muted green
GAUGE_OVER_CAPACITY = "#2f1f1f"   # Very dark muted red
GAUGE_CAPACITY_LINE = ACCENT_PRIMARY
GAUGE_DEMAND_LINE = "#b8923a"     # Muted amber

# -----------------------------------------------------------------------------
# FLOW INDICATOR COLORS
# -----------------------------------------------------------------------------
FLOW_PRIMARY = ACCENT_PRIMARY
FLOW_LOW = STATUS_ERROR
FLOW_MED = STATUS_WARNING
FLOW_HIGH = STATUS_GOOD

# -----------------------------------------------------------------------------
# CAR COLORS - Muted but still distinguishable
# -----------------------------------------------------------------------------
CAR_NORMAL = "#5a9bcf"     # Muted blue
CAR_WAITING = "#a65d5d"    # Muted red
CAR_ANGRY = "#8a6a9a"      # Muted purple

# -----------------------------------------------------------------------------
# UI ELEMENT COLORS - Subtle borders and accents
# -----------------------------------------------------------------------------
BORDER_LIGHT = "#3a3a3a"
BORDER_DARK = "#1a1a1a"
BORDER_HIGHLIGHT = "#505050"
OVERFLOW_QUEUE = "#7a6a8a"  # Muted lavender

# -----------------------------------------------------------------------------
# FONTS - Using Segoe UI for consistency across all UI elements
# -----------------------------------------------------------------------------
# Font Family
FONT_FAMILY = "Segoe UI"

# Font Scale (can be modified at runtime)
_font_scale = 1.0

def set_font_scale(scale):
    """Set the global font scale (1.0 = 100%)"""
    global _font_scale
    _font_scale = scale

def get_font_scale():
    """Get the current font scale"""
    return _font_scale

def scaled_font(base_size, bold=False):
    """Create a scaled font tuple"""
    size = max(6, int(base_size * _font_scale))
    if bold:
        return (FONT_FAMILY, size, "bold")
    return (FONT_FAMILY, size)

# Base font sizes (before scaling)
_BASE_TITLE = 14
_BASE_HEADING = 12
_BASE_NORMAL = 10
_BASE_SMALL = 9
_BASE_TINY = 8
_BASE_MINI = 7
_BASE_MICRO = 6
_BASE_VALUE_LARGE = 20
_BASE_VALUE_MEDIUM = 12
_BASE_VALUE_SMALL = 10
_BASE_LABEL = 9
_BASE_SCORE = 11
_BASE_STATUS = 8

# Font getter functions (use these for dynamic scaling)
def get_font_title(): return scaled_font(_BASE_TITLE, bold=True)
def get_font_heading(): return scaled_font(_BASE_HEADING, bold=True)
def get_font_normal(): return scaled_font(_BASE_NORMAL)
def get_font_small(): return scaled_font(_BASE_SMALL)
def get_font_tiny(): return scaled_font(_BASE_TINY)
def get_font_mini(): return scaled_font(_BASE_MINI)
def get_font_micro(): return scaled_font(_BASE_MICRO)
def get_font_value_large(): return scaled_font(_BASE_VALUE_LARGE, bold=True)
def get_font_value_medium(): return scaled_font(_BASE_VALUE_MEDIUM, bold=True)
def get_font_value_small(): return scaled_font(_BASE_VALUE_SMALL, bold=True)
def get_font_label(): return scaled_font(_BASE_LABEL)
def get_font_label_bold(): return scaled_font(_BASE_LABEL, bold=True)
def get_font_score(): return scaled_font(_BASE_SCORE, bold=True)
def get_font_status(): return scaled_font(_BASE_STATUS, bold=True)

# Static font tuples (for backwards compatibility - these won't scale dynamically)
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

# Base Padding Constants (will be scaled with font)
_PAD_TINY_BASE = 2
_PAD_SMALL_BASE = 5
_PAD_MEDIUM_BASE = 10
_PAD_LARGE_BASE = 15
_PAD_XLARGE_BASE = 20

# Padding Constants (dynamically scaled)
PAD_TINY = 2          # Minimal spacing (grid cells, tight layouts)
PAD_SMALL = 5         # Standard small spacing
PAD_MEDIUM = 10       # Section padding, frame margins
PAD_LARGE = 15        # Section separator spacing
PAD_XLARGE = 20       # Major section dividers

def update_padding_scale():
    """Update padding values based on current font scale"""
    global PAD_TINY, PAD_SMALL, PAD_MEDIUM, PAD_LARGE, PAD_XLARGE
    global PAD_SECTION_TOP, PAD_SECTION_START, PAD_ROW, PAD_ELEMENT, PAD_FRAME, PAD_BUTTON
    
    scale = _font_scale
    PAD_TINY = max(1, int(_PAD_TINY_BASE * scale))
    PAD_SMALL = max(2, int(_PAD_SMALL_BASE * scale))
    PAD_MEDIUM = max(5, int(_PAD_MEDIUM_BASE * scale))
    PAD_LARGE = max(8, int(_PAD_LARGE_BASE * scale))
    PAD_XLARGE = max(10, int(_PAD_XLARGE_BASE * scale))
    
    # Update semantic padding
    PAD_SECTION_TOP = (PAD_LARGE, PAD_SMALL)
    PAD_SECTION_START = (PAD_XLARGE, PAD_SMALL)
    PAD_ROW = PAD_TINY
    PAD_ELEMENT = PAD_SMALL
    PAD_FRAME = PAD_MEDIUM
    PAD_BUTTON = PAD_XLARGE

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
