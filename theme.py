# =============================================================================
# THEME.PY - Centralized Color and Style Definitions
# =============================================================================

# -----------------------------------------------------------------------------
# BACKGROUND COLORS
# -----------------------------------------------------------------------------
BG_MAIN = "#121212"          # Main application background
BG_SIDEBAR = "#181818"       # Sidebar background
BG_PANEL = "#222222"         # Panel/frame background
BG_CANVAS = "#2b2b2b"        # Main canvas background
BG_DARK = "#111111"          # Darker elements (gauges, graphs)
BG_ROAD = "#333333"          # Road surface
BG_INTERSECTION = "#222222"  # Intersection center

# -----------------------------------------------------------------------------
# TEXT COLORS
# -----------------------------------------------------------------------------
TEXT_PRIMARY = "#ffffff"     # Main text
TEXT_SECONDARY = "#aaaaaa"   # Secondary/label text
TEXT_MUTED = "#888888"       # Muted/dimmed text
TEXT_DISABLED = "#666666"    # Disabled/weight text

# -----------------------------------------------------------------------------
# ACCENT COLORS
# -----------------------------------------------------------------------------
ACCENT_PRIMARY = "#00bfff"   # Cyan - primary accent (headers, highlights)
ACCENT_SECONDARY = "#ff8800" # Orange - secondary accent (section headers)
ACCENT_TERTIARY = "#00ffff"  # Bright cyan - timer/indicators

# -----------------------------------------------------------------------------
# STATUS COLORS - Traffic Light
# -----------------------------------------------------------------------------
LIGHT_GREEN = "#00ff00"
LIGHT_YELLOW = "#ffff00"
LIGHT_RED = "#ff0000"

# -----------------------------------------------------------------------------
# STATUS COLORS - Performance Indicators
# -----------------------------------------------------------------------------
STATUS_GOOD = "#00ff00"      # Good/success/flowing
STATUS_WARNING = "#ffaa00"   # Warning/building/partial
STATUS_ERROR = "#ff4444"     # Error/congested/critical

# -----------------------------------------------------------------------------
# MEMBERSHIP FUNCTION COLORS (Fuzzy Logic)
# -----------------------------------------------------------------------------
MF_LOW = "#00ff00"           # Low membership - green
MF_MEDIUM = "#ffaa00"        # Medium membership - orange
MF_HIGH = "#ff0000"          # High membership - red

# -----------------------------------------------------------------------------
# RULE COLORS (Fuzzy Logic)
# -----------------------------------------------------------------------------
RULE_KEEP = "#00ff00"        # Keep rules - green
RULE_KEEP_ALT = "#00cc00"    # Keep batch - darker green
RULE_SWITCH = "#ff4444"      # Switch queue - red
RULE_SWITCH_TIME = "#ff00ff" # Switch time - magenta
RULE_SWITCH_EMPTY = "#ff0066"# Switch empty - pink
RULE_CONFLICT = "#ff8800"    # Conflict - orange

# -----------------------------------------------------------------------------
# OUTPUT REGION COLORS
# -----------------------------------------------------------------------------
OUT_SWITCH = "#cf3030"       # Switch region fill
OUT_HOLD = "#cf8f30"         # Hold region fill
OUT_KEEP = "#30cf30"         # Keep region fill

# -----------------------------------------------------------------------------
# GAUGE COLORS
# -----------------------------------------------------------------------------
GAUGE_UNDER_CAPACITY = "#1a3a1a"   # Green zone background
GAUGE_OVER_CAPACITY = "#3a1a1a"   # Red zone background
GAUGE_CAPACITY_LINE = "#00aaff"   # Capacity marker
GAUGE_DEMAND_LINE = "#ff8800"     # Demand marker (orange)

# -----------------------------------------------------------------------------
# FLOW INDICATOR COLORS
# -----------------------------------------------------------------------------
FLOW_PRIMARY = "#00bfff"     # Flow text/values
FLOW_LOW = "#ff4444"         # Underperforming
FLOW_MED = "#ffaa00"         # On target
FLOW_HIGH = "#00ff00"        # Exceeding

# -----------------------------------------------------------------------------
# CAR COLORS (aligned with STATUS colors for consistency)
# -----------------------------------------------------------------------------
CAR_NORMAL = "#00ffff"       # Moving car - cyan (matches ACCENT_TERTIARY)
CAR_WAITING = "#ff4444"      # Stopped/waiting car - red (matches STATUS_ERROR)
CAR_ANGRY = "#aa00ff"        # Frustrated car - purple (rage indicator)

# -----------------------------------------------------------------------------
# UI ELEMENT COLORS
# -----------------------------------------------------------------------------
BORDER_LIGHT = "#555555"     # Light borders
BORDER_DARK = "#333333"      # Dark borders
BORDER_HIGHLIGHT = "#444444" # Highlight borders
OVERFLOW_QUEUE = "#800080"   # Purple - virtual queue overflow

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
