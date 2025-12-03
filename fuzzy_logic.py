# =============================================================================
# FUZZY_LOGIC.PY - Fuzzy Logic Controller for Traffic Management
# =============================================================================
# Uses realistic traffic engineering inputs based on:
# - Vehicle-actuated signal control (gap-out logic)
# - Webster's optimal cycle theory
# - Real-world traffic timing parameters (saturation headway ~2 sec/veh)
# =============================================================================

import theme
from theme import (
    MF_LOW, MF_MEDIUM, MF_HIGH,
    RULE_KEEP, RULE_KEEP_ALT, RULE_SWITCH, RULE_SWITCH_TIME, 
    RULE_SWITCH_EMPTY, RULE_CONFLICT,
    OUT_SWITCH, OUT_HOLD, OUT_KEEP,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, TEXT_DISABLED,
    ACCENT_PRIMARY, ACCENT_TERTIARY,
    STATUS_GOOD, STATUS_WARNING, STATUS_ERROR,
    FLOW_PRIMARY, FLOW_LOW, FLOW_MED, FLOW_HIGH,
    BG_PANEL, BG_DARK, BORDER_DARK,
    get_score_color
)


class FuzzyLogicController:
    """
    Fuzzy Logic Controller for Traffic Signal Management
    
    Uses REALISTIC traffic engineering inputs:
    
    1. CLEARANCE TIME (seconds) - Time needed to clear active queue
       - Based on saturation flow rate (~1800 veh/hr = 2 sec/car headway)
       - Short = quick clearance, can consider switching
       - Long = big queue, needs more green time
       
    2. QUEUE IMBALANCE RATIO - How unfair is the current situation?
       - = max_waiting_queue / (active_queue + 1)
       - Low ratio = active lane is well-served
       - High ratio = waiting lanes are being neglected
       
    3. URGENCY INDEX - Weighted combination of wait time and queue size
       - Based on driver patience studies (~30-60 sec before frustration)
       - = (max_wait_time / 45) * (1 + waiting_queue/10)
       - Captures the "pressure" from angry waiting drivers
    
    Output:
        - Score 0-100: Lower = SWITCH, Higher = KEEP
    """
    
    # -------------------------------------------------------------------------
    # TRAFFIC ENGINEERING PARAMETERS
    # -------------------------------------------------------------------------
    
    # Saturation headway (typical value: 2 seconds between cars at full green)
    SATURATION_HEADWAY = 2.0  # seconds per vehicle
    
    # Driver patience threshold (research shows ~30-60 sec before frustration)
    PATIENCE_THRESHOLD = 45.0  # seconds
    
    # -------------------------------------------------------------------------
    # MEMBERSHIP FUNCTION DEFINITIONS (Based on Traffic Engineering)
    # -------------------------------------------------------------------------
    
    # Clearance Time Sets (seconds to clear queue at saturation flow)
    # Short: can clear quickly, consider switching if others waiting
    # Medium: moderate queue, standard timing
    # Long: big queue (15-25+ cars), needs extended green
    CLEAR_SHORT = [0, 0, 6, 14]        # < 14 sec = small queue (< 7 cars)
    CLEAR_MED = [10, 18, 30, 45]       # 18-30 sec = medium queue (9-15 cars)
    CLEAR_LONG = [30, 45, 80, 80]      # > 45 sec = large queue (22+ cars)
    
    # Queue Imbalance Ratio Sets (waiting/active)
    # Low: fair service, active lane is busy
    # Medium: moderate imbalance
    # High: waiting lanes are being neglected (but only trigger switch for small active queues)
    IMBAL_LOW = [0, 0, 0.8, 2.0]       # Active queue is larger or equal
    IMBAL_MED = [1.5, 2.5, 4.0, 6.0]   # 2.5-4x more waiting
    IMBAL_HIGH = [4.0, 6.0, 15, 15]    # 6x+ more waiting = unfair (high bar)
    
    # Urgency Index Sets (pressure from waiting drivers)
    # Based on patience studies: frustration starts at ~30-60 sec
    # Raised thresholds to allow large batches to clear
    URG_LOW = [0, 0, 0.4, 1.0]         # Patient drivers
    URG_MED = [0.7, 1.2, 1.8, 2.5]     # Getting impatient
    URG_HIGH = [1.8, 2.5, 6.0, 6.0]    # Frustrated, urgent switch needed
    
    # Rule Weights - Tuned for realistic driving behavior and large batches
    RULE_WEIGHTS = {
        'keep_clearing': 1.8,    # Keep serving a significant queue (stronger)
        'keep_efficient': 1.3,   # Keep when things are balanced
        'keep_batch': 1.6,       # Let current batch through (stronger)
        'switch_imbalance': 1.1, # Switch when unfair to waiting (weaker)
        'switch_urgent': 1.3,    # Switch when drivers frustrated (weaker)
        'switch_empty': 1.6,     # Switch when active is empty
        'conflict': 0.6,         # Big queues everywhere = tough decision
        'balance': 0.8
    }
    
    # Output Centroids
    OUT_SWITCH_CENTROID = 15
    OUT_BALANCE_CENTROID = 50
    OUT_KEEP_CENTROID = 85
    
    # -------------------------------------------------------------------------
    # MEMBERSHIP FUNCTION CALCULATION
    # -------------------------------------------------------------------------
    
    @staticmethod
    def trapmf(x, abcd):
        """Trapezoidal membership function"""
        a, b, c, d = abcd
        if x <= a or x >= d:
            return 0.0
        if b <= x <= c:
            return 1.0
        if a < x < b:
            return (x - a) / (b - a)
        if c < x < d:
            return (d - x) / (d - c)
        return 0.0
    
    # -------------------------------------------------------------------------
    # DERIVED INPUT CALCULATIONS (Traffic Engineering)
    # -------------------------------------------------------------------------
    
    def calc_clearance_time(self, queue_length):
        """
        Estimate time (seconds) to clear a queue at saturation flow.
        Based on typical headway of 2 seconds between vehicles.
        """
        return queue_length * self.SATURATION_HEADWAY
    
    def calc_imbalance_ratio(self, active_q, max_waiting_q):
        """
        Calculate how imbalanced the traffic distribution is.
        High ratio = waiting lanes being neglected (unfair).
        """
        return max_waiting_q / (active_q + 1)  # +1 to avoid division by zero
    
    def calc_urgency_index(self, max_wait_time, max_waiting_q):
        """
        Calculate urgency based on wait time and queue size.
        Combines driver frustration (time) with traffic pressure (queue).
        Research shows frustration starts at ~30-60 seconds.
        """
        time_factor = max_wait_time / self.PATIENCE_THRESHOLD
        queue_factor = 1 + max_waiting_q / 10.0
        return time_factor * queue_factor
    
    # -------------------------------------------------------------------------
    # MAIN CALCULATION
    # -------------------------------------------------------------------------
    
    def calculate(self, active_q, max_waiting_q, max_wait_time, flow_ratio):
        """
        Calculate fuzzy logic decision score using realistic traffic inputs.
        
        Args:
            active_q: Number of cars in active (green) lane
            max_waiting_q: Maximum cars waiting in any other lane
            max_wait_time: Longest wait time in seconds
            flow_ratio: current_flow / target_flow (for display only)
            
        Returns:
            tuple: (score, mu_clear, mu_imbal, mu_urg, mu_flow, rules, sets)
        """
        # DERIVE REALISTIC INPUTS
        clearance_time = self.calc_clearance_time(active_q)
        imbalance_ratio = self.calc_imbalance_ratio(active_q, max_waiting_q)
        urgency_index = self.calc_urgency_index(max_wait_time, max_waiting_q)
        
        # 1. FUZZIFICATION
        
        # Clearance Time memberships
        mu_clear_short = self.trapmf(clearance_time, self.CLEAR_SHORT)
        mu_clear_med = self.trapmf(clearance_time, self.CLEAR_MED)
        mu_clear_long = self.trapmf(clearance_time, self.CLEAR_LONG)
        
        # Imbalance Ratio memberships
        mu_imbal_low = self.trapmf(imbalance_ratio, self.IMBAL_LOW)
        mu_imbal_med = self.trapmf(imbalance_ratio, self.IMBAL_MED)
        mu_imbal_high = self.trapmf(imbalance_ratio, self.IMBAL_HIGH)
        
        # Urgency Index memberships
        mu_urg_low = self.trapmf(urgency_index, self.URG_LOW)
        mu_urg_med = self.trapmf(urgency_index, self.URG_MED)
        mu_urg_high = self.trapmf(urgency_index, self.URG_HIGH)
        
        # 2. RULE EVALUATION
        w = self.RULE_WEIGHTS
        
        # KEEP RULES - Reasons to keep the current green light
        
        # R1: Keep clearing a long queue (significant work to do)
        # Stronger effect when active queue is large
        active_queue_factor = min(1.0, active_q / 10.0)  # 0-1 based on queue size
        r1_clearing = min(mu_clear_long, 1 - mu_urg_high) * w['keep_clearing'] * (1 + active_queue_factor * 0.5)
        
        # R2: Keep when balanced (low imbalance, medium clearance)
        r1_efficient = min(mu_imbal_low, mu_clear_med, 1 - mu_urg_high) * w['keep_efficient']
        
        # R3: Keep to let current batch through (medium/long queue, low urgency)
        # Extended to include both medium and long clearance
        r1_batch = min(max(mu_clear_med, mu_clear_long), mu_imbal_low, mu_urg_low) * w['keep_batch'] * (1 + active_queue_factor * 0.3)
        
        r1_total = max(r1_clearing, r1_efficient, r1_batch)
        
        # SWITCH RULES - Reasons to switch to another lane
        # All switch rules are weakened when active queue is large
        switch_damping = max(0.3, 1.0 - active_q / 25.0)  # Reduces to 0.3 at 25 cars
        
        # R4: Switch when high imbalance (waiting lanes neglected)
        r2_imbalance = min(mu_imbal_high, max(mu_clear_short, mu_clear_med)) * w['switch_imbalance'] * switch_damping
        
        # R5: Switch when urgency is high (frustrated drivers)
        r2_urgent = mu_urg_high * w['switch_urgent'] * switch_damping
        
        # R6: Switch when active lane nearly empty and others waiting
        r2_empty = min(mu_clear_short, max(mu_imbal_med, mu_imbal_high)) * w['switch_empty']
        
        # R7: Switch for moderate imbalance + moderate urgency
        r2_combined = min(mu_imbal_med, mu_urg_med) * w['balance'] * switch_damping
        
        r2_total = max(r2_imbalance, r2_urgent, r2_empty, r2_combined)
        
        # CONFLICT RULES - Both sides have strong needs
        
        # R8: Conflict - long clearance AND high urgency from waiting
        r3_conflict = min(mu_clear_long, mu_urg_high) * w['conflict']
        
        # R9: Balanced conflict - medium everything
        r3_balanced = min(mu_clear_med, mu_imbal_med, mu_urg_med) * w['balance']
        
        r3_total = max(r3_conflict, r3_balanced)
        
        # 3. DEFUZZIFICATION - Weighted average
        num = (r1_total * self.OUT_KEEP_CENTROID + 
               r2_total * self.OUT_SWITCH_CENTROID + 
               r3_total * self.OUT_BALANCE_CENTROID)
        den = r1_total + r2_total + r3_total + 0.001
        score = num / den
        
        # 4. ADJUSTMENTS - Fine-tuning based on edge cases
        
        # Batch bonus: Keep serving if queue is significant (scaled for larger batches)
        batch_bonus = 0
        if active_q > 3 and urgency_index < 2.0:
            # Stronger bonus that scales with queue size up to 25 cars
            batch_bonus = min(25, (active_q - 3) * 1.5)
            # Extra bonus for very large batches (15+ cars)
            if active_q > 15:
                batch_bonus += min(10, (active_q - 15) * 2)
        
        # Empty lane penalty: Strong push to switch if active is empty
        empty_penalty = 0
        if active_q <= 1 and max_waiting_q > 2:
            empty_penalty = -25
        
        # Urgency penalty: Override batch bonus if very urgent
        # Weakened to allow large batches more time
        urgency_penalty = 0
        if urgency_index > 2.5:
            urgency_penalty = -8 * (urgency_index - 2.5)
        
        score = max(0, min(100, score + batch_bonus + empty_penalty + urgency_penalty))
        
        # 5. RETURN DATA for visualization
        # Store derived inputs for display
        self._last_inputs = {
            'clearance_time': clearance_time,
            'imbalance_ratio': imbalance_ratio,
            'urgency_index': urgency_index
        }

        # pack the rules return

        return (
            score,
            (mu_clear_short, mu_clear_med, mu_clear_long),
            (mu_imbal_low, mu_imbal_med, mu_imbal_high),
            (mu_urg_low, mu_urg_med, mu_urg_high),
            (0, 0, 0),  # Placeholder for 4th input (not used)
            (r1_clearing, r1_efficient,r1_batch, r2_imbalance, r2_empty, r2_urgent, r3_balanced,r3_conflict, r3_total,r1_total),
            (self.CLEAR_SHORT, self.CLEAR_MED, self.CLEAR_LONG,
             self.IMBAL_LOW, self.IMBAL_MED, self.IMBAL_HIGH,
             self.URG_LOW, self.URG_MED, self.URG_HIGH)
        )


# =============================================================================
# FUZZY VISUALIZATION FUNCTIONS
# =============================================================================

class FuzzyVisualizer:
    """Handles all fuzzy logic visualization on canvas widgets"""
    
    @staticmethod
    def draw_membership_3(cv, title, val, mus, sets_low, sets_med, sets_high, max_range):
        """
        Draw membership function with 3 sets (Low/Med/High)
        
        Args:
            cv: Canvas widget
            title: Graph title
            val: Current input value
            mus: Tuple of (mu_low, mu_med, mu_high) membership values
            sets_low, sets_med, sets_high: Trapezoidal set definitions [a,b,c,d]
            max_range: X-axis maximum value
        """
        cv.delete("all")
        
        # Get canvas dimensions
        w = cv.winfo_width()
        h = cv.winfo_height()
        if w < 50:
            w = 160
        if h < 50:
            h = 120
        
        pad = 15
        gw, gh = w - 2 * pad, h - 2 * pad - 15
        ox, oy = pad, h - pad - 10
        
        # Title
        cv.create_text(w / 2, 8, text=title, fill=TEXT_PRIMARY, font=theme.FONT_TINY)
        
        # Axis
        cv.create_line(ox, oy, ox + gw, oy, fill=BORDER_DARK)
        
        # Format axis labels based on range
        if max_range <= 2:
            cv.create_text(ox, oy + 10, text="0", fill=TEXT_MUTED, font=theme.FONT_MINI, anchor='n')
            cv.create_text(ox + gw, oy + 10, text=f"{max_range:.1f}", fill=TEXT_MUTED, font=theme.FONT_MINI, anchor='n')
        else:
            cv.create_text(ox, oy + 10, text="0", fill=TEXT_MUTED, font=theme.FONT_MINI, anchor='n')
            cv.create_text(ox + gw, oy + 10, text=f"{int(max_range)}+", fill=TEXT_MUTED, font=theme.FONT_MINI, anchor='n')
        
        scale_x = gw / max_range
        
        def draw_poly(abcd, col):
            a, b, c_pt, d = abcd
            def cx(v):
                return ox + min(v * scale_x, gw)
            pts = [cx(a), oy, cx(b), oy - gh, cx(c_pt), oy - gh, cx(d), oy]
            cv.create_polygon(pts, outline=col, fill="", width=2)
        
        # Draw membership functions
        draw_poly(sets_low, MF_LOW)
        draw_poly(sets_med, MF_MEDIUM)
        draw_poly(sets_high, MF_HIGH)
        
        # Membership values display
        mu_low, mu_med, mu_high = mus
        cv.create_text(ox + 5, 20, text=f"S:{mu_low:.1f}", fill=MF_LOW, font=theme.FONT_MICRO, anchor='w')
        cv.create_text(w / 2, 20, text=f"M:{mu_med:.1f}", fill=MF_MEDIUM, font=theme.FONT_MICRO, anchor='center')
        cv.create_text(w - pad - 5, 20, text=f"H:{mu_high:.1f}", fill=MF_HIGH, font=theme.FONT_MICRO, anchor='e')
        
        # Current value indicator
        ix = ox + min(val * scale_x, gw)
        cv.create_line(ix, oy, ix, oy - gh, fill=TEXT_PRIMARY, width=2)
        
        # Format value display
        if max_range <= 2:
            val_text = f"{val:.2f}"
        elif max_range <= 10:
            val_text = f"{val:.1f}"
        else:
            val_text = f"{val:.0f}s"
        cv.create_text(ix, oy - gh - 5, text=val_text, fill=ACCENT_PRIMARY, font=theme.FONT_MINI)
    
    @staticmethod
    def draw_rules_expanded(cv, rules, flow_ratio, mu_f):
        """
        Draw expanded rule visualization with traffic engineering labels
        
        Args:
            cv: Canvas widget for rules
            rules: Tuple of rule activation values
            flow_ratio: Current flow ratio
            mu_f: Flow membership values tuple (unused but kept for interface)
        """
        r1_total, r2_imbalance, r2_urgent, r3_total, r2_empty, r1_batch = rules
        
        cv.delete("all")
        
        # Get canvas dimensions
        w = cv.winfo_width()
        h = cv.winfo_height()
        if w < 100:
            w = 495
        if h < 50:
            h = 130
        
        # Responsive layout
        label_width = min(120, w * 0.24)
        bar_start = label_width + 8
        bar_end = w - 100
        bar_width = max(bar_end - bar_start, 100)
        bar_height = 14
        row_spacing = 20
        
        def bar(y, txt, v, col, weight=""):
            cv.create_text(label_width, y + bar_height / 2, text=txt, fill=TEXT_PRIMARY, anchor='e', font=theme.FONT_SMALL)
            cv.create_rectangle(bar_start, y, bar_start + bar_width, y + bar_height, fill=BG_DARK, outline="")
            bw = bar_width * min(v, 2.0) / 2.0
            cv.create_rectangle(bar_start, y, bar_start + bw, y + bar_height, fill=col, outline="")
            cv.create_text(bar_start + bar_width + 8, y + bar_height / 2, text=f"{v:.2f}", fill=TEXT_MUTED, anchor='w', font=theme.FONT_TINY)
            if weight:
                cv.create_text(bar_start + bar_width + 45, y + bar_height / 2, text=weight, fill=TEXT_DISABLED, anchor='w', font=theme.FONT_TINY)
        
        # KEEP rules (green shades) - reasons to keep green
        bar(4, "KEEP Clear", r1_total, RULE_KEEP, "w:1.4")
        bar(4 + row_spacing, "Batch", r1_batch, RULE_KEEP_ALT, "w:1.3")
        
        # SWITCH rules (red shades) - reasons to switch
        bar(4 + row_spacing * 2, "Imbalance", r2_imbalance, RULE_SWITCH, "w:1.3")
        bar(4 + row_spacing * 3, "Urgency", r2_urgent, RULE_SWITCH_TIME, "w:1.5")
        bar(4 + row_spacing * 4, "Empty", r2_empty, RULE_SWITCH_EMPTY, "w:1.6")
        
        # CONFLICT rule (orange) - tough decisions
        bar(4 + row_spacing * 5, "CONFLICT", r3_total, RULE_CONFLICT, "w:0.7")
    
    @staticmethod
    def draw_flow_indicator(cv, flow_ratio, mu_f):
        """
        Draw flow indicator showing throughput status
        
        Args:
            cv: Canvas widget
            flow_ratio: Current flow ratio
            mu_f: Flow membership values (unused, kept for interface compatibility)
        """
        cv.delete("all")
        
        w = cv.winfo_width()
        if w < 100:
            w = 400
        h = 35
        
        # Flow label and value
        cv.create_text(10, h / 2, text="FLOW:", fill=FLOW_PRIMARY, font=theme.FONT_LABEL_BOLD, anchor='w')
        cv.create_text(55, h / 2, text=f"{flow_ratio:.2f}x", fill=FLOW_PRIMARY, font=theme.FONT_VALUE_MEDIUM, anchor='w')
        
        # Simple progress bar showing flow ratio
        bar_x = 120
        bar_w = min(150, w - 200)
        bar_h = 16
        bar_y = (h - bar_h) / 2
        
        cv.create_rectangle(bar_x, bar_y, bar_x + bar_w, bar_y + bar_h, fill=BG_DARK, outline=BORDER_DARK)
        
        # Fill based on flow ratio (1.0 = full)
        fill_w = min(bar_w, bar_w * flow_ratio)
        if flow_ratio < 0.7:
            fill_color = FLOW_LOW
        elif flow_ratio > 1.1:
            fill_color = FLOW_HIGH
        else:
            fill_color = FLOW_MED
        cv.create_rectangle(bar_x, bar_y, bar_x + fill_w, bar_y + bar_h, fill=fill_color, outline="")
        
        # Target line at 1.0
        target_x = bar_x + bar_w
        cv.create_line(target_x, bar_y - 2, target_x, bar_y + bar_h + 2, fill=TEXT_MUTED, width=1)
        
        # Status text
        if flow_ratio < 0.7:
            status, status_color = "BELOW TARGET", FLOW_LOW
        elif flow_ratio > 1.2:
            status, status_color = "EXCEEDING", FLOW_HIGH
        else:
            status, status_color = "ON TARGET", FLOW_MED
        cv.create_text(w - 10, h / 2, text=status, fill=status_color, font=theme.FONT_STATUS, anchor='e')
    
    @staticmethod
    def draw_output_expanded(cv, score, rules, threshold):
        """
        Draw output with dynamic threshold indicator
        
        Args:
            cv: Canvas widget
            score: Calculated fuzzy score
            rules: Tuple of rule activation values
            threshold: Switch threshold value
        """
        r1_clearing, r1_efficient, r1_batch, r2_imbalance, r2_empty, r2_urgent, r3_balance, r3_conflict, r3_total, r1_total = rules
        r2_total = max(r2_imbalance, r2_urgent, r2_empty)
        
        cv.delete("all")
        
        # Get canvas dimensions
        w = cv.winfo_width()
        h = cv.winfo_height()
        if w < 100:
            w = 495
        if h < 50:
            h = 80
        
        pad = 20
        gw, gh = w - 2 * pad, h - 2 * pad
        ox, oy = pad, h - pad
        
        # Axis
        cv.create_line(ox, oy, ox + gw, oy, fill=TEXT_DISABLED)
        cv.create_text(ox, oy + 10, text="SWITCH", fill=STATUS_ERROR, font=theme.FONT_TINY, anchor="w")
        cv.create_text(ox + gw / 2, oy + 10, text="HOLD", fill=STATUS_WARNING, font=theme.FONT_TINY, anchor="center")
        cv.create_text(ox + gw, oy + 10, text="KEEP", fill=STATUS_GOOD, font=theme.FONT_TINY, anchor="e")
        
        def to_x(v):
            return ox + (v / 100 * gw)
        
        # Output membership regions
        cv.create_polygon(to_x(0), oy, to_x(15), oy - gh, to_x(35), oy, outline=BG_DARK, fill="")
        cv.create_polygon(to_x(25), oy, to_x(50), oy - gh, to_x(75), oy, outline=BG_DARK, fill="")
        cv.create_polygon(to_x(65), oy, to_x(85), oy - gh, to_x(100), oy, outline=BG_DARK, fill="")
        
        # Active fills
        switch_strength = min(r2_total, 1.5) / 1.5
        hold_strength = min(r3_total, 1.5) / 1.5
        keep_strength = min(r1_total, 1.5) / 1.5
        
        if switch_strength > 0.05:
            alpha_h = int(gh * switch_strength)
            cv.create_polygon(to_x(0), oy, to_x(15), oy - alpha_h, to_x(35), oy, fill=OUT_SWITCH, outline="")
        if hold_strength > 0.05:
            alpha_h = int(gh * hold_strength)
            cv.create_polygon(to_x(25), oy, to_x(50), oy - alpha_h, to_x(75), oy, fill=OUT_HOLD, outline="")
        if keep_strength > 0.05:
            alpha_h = int(gh * keep_strength)
            cv.create_polygon(to_x(65), oy, to_x(85), oy - alpha_h, to_x(100), oy, fill=OUT_KEEP, outline="")
        
        # Threshold line
        tx = to_x(threshold)
        cv.create_line(tx, oy, tx, oy - gh, fill=ACCENT_PRIMARY, width=1, dash=(3, 3))
        cv.create_text(tx, oy - gh - 5, text=f"T:{threshold:.0f}", fill=ACCENT_PRIMARY, font=theme.FONT_MINI)
        
        # Score indicator
        cx = to_x(score)
        cv.create_line(cx, oy, cx, oy - gh - 10, fill=TEXT_PRIMARY, width=3)
        
        # Score color
        score_color = get_score_color(score)
        cv.create_text(cx, oy - gh - 18, text=f"{int(score)}%", fill=score_color, font=theme.FONT_SCORE)
        
        # Decision indicator
        if score < threshold:
            cv.create_text(ox + gw - 50, 10, text="→ SWITCH", fill=STATUS_ERROR, font=theme.FONT_LABEL_BOLD)
        else:
            cv.create_text(ox + gw - 50, 10, text="→ KEEP", fill=STATUS_GOOD, font=theme.FONT_LABEL_BOLD)
