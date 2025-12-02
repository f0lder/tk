# =============================================================================
# NEURO-TRAFFIC: Fuzzy Logic Traffic Signal Controller
# =============================================================================
# Main Application File
# =============================================================================

import tkinter as tk
from tkinter import ttk
import random
import time
from collections import deque

# Local imports
from car import Car
from theme import (
    # Background colors
    BG_MAIN, BG_SIDEBAR, BG_PANEL, BG_CANVAS, BG_DARK,
    BG_ROAD, BG_INTERSECTION,
    # Text colors
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, TEXT_DISABLED,
    # Accent colors
    ACCENT_PRIMARY, ACCENT_SECONDARY, ACCENT_TERTIARY,
    # Status colors
    LIGHT_GREEN, LIGHT_YELLOW, LIGHT_RED,
    STATUS_GOOD, STATUS_WARNING, STATUS_ERROR,
    # Gauge colors
    GAUGE_UNDER_CAPACITY, GAUGE_OVER_CAPACITY,
    GAUGE_CAPACITY_LINE, GAUGE_DEMAND_LINE,
    # Other colors
    OVERFLOW_QUEUE, BORDER_LIGHT, BORDER_DARK,
    # Fonts
    FONT_TITLE, FONT_HEADING, FONT_NORMAL, FONT_SMALL, FONT_TINY, FONT_MINI, FONT_MICRO,
    FONT_VALUE_LARGE, FONT_VALUE_MEDIUM, FONT_VALUE_SMALL,
    FONT_LABEL, FONT_LABEL_BOLD, FONT_STATUS,
    # Padding constants
    PAD_TINY, PAD_SMALL, PAD_MEDIUM, PAD_LARGE, PAD_XLARGE,
    PAD_SECTION_TOP, PAD_SECTION_START, PAD_ROW, PAD_ELEMENT, PAD_FRAME, PAD_BUTTON,
    # Helpers
    get_efficiency_color, get_flow_status, get_capacity_color, get_gauge_bar_color
)
from fuzzy_logic import FuzzyLogicController, FuzzyVisualizer
from about import AboutWindow
from settings import SettingsWindow


class UltimateTrafficApp(tk.Tk):
    """Main Traffic Simulation Application"""
    
    def __init__(self):
        super().__init__()
        self.title("Neuro-Traffic: Fuzzy Logic Signal Controller")
        self.geometry("1700x980")
        self.configure(bg=BG_MAIN)
        
        self.setup_styles()
        
        # Initialize fuzzy logic controller
        self.fuzzy_controller = FuzzyLogicController()
        self.fuzzy_viz = FuzzyVisualizer()

        # --- STATE ---
        self.cars = []
        self.virtual_queues = {'N': 0, 'S': 0, 'E': 0, 'W': 0}
        
        self.lights = {'N': 'red', 'S': 'red', 'E': 'red', 'W': 'red'}
        self.phase_order = ['N', 'S', 'E', 'W']
        self.current_phase_idx = 0
        self.fsm_state = 'GREEN'
        self.state_timer = 0
        
        self.current_min_green = 50
        self.current_max_green = 200
        
        # METRICS
        self.exit_timestamps = deque()
        self.current_flow = 0.0
        self.target_flow = 40.0
        self.theoretical_capacity = 24.0  # Will be updated dynamically
        self.spawn_credit = 0.0
        self.last_frame_time = time.time()
        
        # Lane wait time tracking
        self.lane_wait_times = {'N': deque(maxlen=50), 'S': deque(maxlen=50), 
                                'E': deque(maxlen=50), 'W': deque(maxlen=50)}
        self.lane_mean_wait = {'N': 0, 'S': 0, 'E': 0, 'W': 0}
        
        # Wait time history with timestamps for max wait in last 60 sec
        # Each entry is (timestamp, wait_seconds)
        self.lane_wait_history = {'N': deque(), 'S': deque(), 
                                  'E': deque(), 'W': deque()}
        
        # Throughput history (last 60 samples, ~1 per second)
        self.throughput_history = deque(maxlen=60)
        self.history_update_time = time.time()
        
        # Cached canvas dimensions
        self.canvas_width = 700
        self.canvas_height = 800
        self.sidebar_width = 650
        
        self.setup_ui()
        self.run_simulation()

    # =========================================================================
    # UI SETUP
    # =========================================================================
    
    def setup_styles(self):
        """Configure ttk styles to match the app's theme."""
        self.style = ttk.Style()
        self.style.theme_use('default')

        # --- Frames ---
        self.style.configure('TFrame', background=BG_SIDEBAR)
        self.style.configure('Dark.TFrame', background=BG_DARK)
        self.style.configure('Viz.TFrame', background='black', relief='sunken', borderwidth=2)

        # --- PanedWindow ---
        self.style.configure('TPanedwindow', background=BG_MAIN)
        self.style.map('TPanedwindow.Sash', background=[('!active', BG_MAIN)], troughcolor=[('!active', BG_MAIN)])

        # --- Labels ---
        self.style.configure('TLabel', background=BG_SIDEBAR, foreground=TEXT_PRIMARY, font=FONT_NORMAL)
        self.style.configure('Dark.TLabel', background=BG_DARK, foreground=TEXT_PRIMARY, font=FONT_LABEL_BOLD)
        self.style.configure('Header.TLabel', background=BG_DARK, foreground=TEXT_MUTED, font=FONT_LABEL_BOLD)
        self.style.configure('Primary.TLabel', background=BG_SIDEBAR, foreground=ACCENT_PRIMARY, font=FONT_LABEL)
        self.style.configure('Demand.TLabel', background=BG_SIDEBAR, foreground=GAUGE_DEMAND_LINE, font=FONT_LABEL)
        self.style.configure('RealWorld.TLabel', background=BG_SIDEBAR, foreground=ACCENT_TERTIARY, font=FONT_LABEL)
        self.style.configure('Value.Primary.TLabel', background=BG_SIDEBAR, foreground=ACCENT_PRIMARY, font=FONT_VALUE_MEDIUM)
        self.style.configure('Value.Demand.TLabel', background=BG_SIDEBAR, foreground=GAUGE_DEMAND_LINE, font=FONT_VALUE_MEDIUM)
        self.style.configure('Value.RealWorld.TLabel', background=BG_SIDEBAR, foreground=ACCENT_TERTIARY, font=FONT_VALUE_MEDIUM)
        self.style.configure('Status.TLabel', background=BG_SIDEBAR, foreground=TEXT_MUTED, font=FONT_STATUS)
        self.style.configure('Overall.Status.TLabel', background=BG_DARK, foreground=TEXT_MUTED, font=FONT_STATUS)
        self.style.configure('Small.TLabel', background=BG_SIDEBAR, foreground=TEXT_PRIMARY, font=FONT_VALUE_SMALL)
        self.style.configure('Small.Muted.TLabel', background=BG_SIDEBAR, foreground=TEXT_MUTED, font=FONT_VALUE_SMALL)
        self.style.configure('LOS.TLabel', background=BG_SIDEBAR, font=FONT_VALUE_MEDIUM)
        self.style.configure('Overall.LOS.TLabel', background=BG_DARK, font=FONT_VALUE_LARGE)
        self.style.configure('Section.TLabel', background=BG_SIDEBAR, foreground=TEXT_SECONDARY, font=FONT_LABEL)
        
        # --- Button ---
        self.style.configure('TButton', font=FONT_LABEL_BOLD, foreground=TEXT_PRIMARY)
        self.style.map('TButton',
            background=[('!active', ACCENT_SECONDARY), ('active', ACCENT_PRIMARY)],
        )

        # --- Scale ---
        self.style.configure('Horizontal.TScale', background=BG_SIDEBAR)

    def setup_ui(self):
        """Setup the main UI layout"""
        # Top menu
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)

        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.open_about)

        # Main container - PanedWindow for resizable sidebar
        self.main_pane = ttk.PanedWindow(self, orient='horizontal', style='TPanedwindow')
        self.main_pane.pack(fill='both', expand=True, padx=PAD_SMALL, pady=PAD_SMALL)

        # Left: Traffic simulation canvas
        viz_frame = ttk.Frame(self.main_pane, style='Viz.TFrame')
        self.canvas = tk.Canvas(viz_frame, bg=BG_CANVAS, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.main_pane.add(viz_frame, weight=1)

        # Right: Dashboard sidebar
        self.sidebar = ttk.Frame(self.main_pane, width=650)
        self.main_pane.add(self.sidebar, weight=0)
        
        self._setup_scrollable_sidebar()
        
        ctrl = self.scrollable_frame
        self._setup_flow_analyzer(ctrl)
        self._setup_lane_stats(ctrl)
        self._setup_fuzzy_engine(ctrl)
        self._setup_controls(ctrl)
        
        self.sidebar.bind('<Configure>', self._on_sidebar_resize)

    def open_about(self):
        AboutWindow(self)

    def open_settings(self):
        SettingsWindow(self)

    def _setup_scrollable_sidebar(self):
        """Setup scrollable sidebar content"""
        self.sidebar_canvas = tk.Canvas(self.sidebar, bg=BG_SIDEBAR, highlightthickness=0)
        self.sidebar_scrollbar = ttk.Scrollbar(self.sidebar, orient='vertical', command=self.sidebar_canvas.yview)
        self.scrollable_frame = tk.Frame(self.sidebar_canvas, bg=BG_SIDEBAR)
        
        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox('all'))
        )
        
        self.sidebar_canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.sidebar_canvas.configure(yscrollcommand=self.sidebar_scrollbar.set)
        
        self.sidebar_scrollbar.pack(side='right', fill='y')
        self.sidebar_canvas.pack(side='left', fill='both', expand=True)
        
        self.sidebar_canvas.bind('<Enter>', lambda e: self._bind_mousewheel())
        self.sidebar_canvas.bind('<Leave>', lambda e: self._unbind_mousewheel())

    def _setup_flow_analyzer(self, parent):
        """Setup Flow Analyzer section"""
        bench_frame = tk.LabelFrame(
            parent, text="FLOW ANALYZER",
            font=FONT_LABEL_BOLD, fg=ACCENT_PRIMARY, bg=BG_SIDEBAR,
            bd=1, relief='solid'
        )
        bench_frame.pack(fill='x', padx=PAD_MEDIUM, pady=PAD_SECTION_TOP)
        
        content = tk.Frame(bench_frame, bg=BG_SIDEBAR)
        content.pack(fill='x', padx=PAD_FRAME, pady=PAD_SMALL)
        
        header = tk.Frame(content, bg=BG_DARK)
        header.pack(fill='x', pady=(0, PAD_TINY))
        
        tk.Label(header, text="Metric", font=FONT_LABEL_BOLD, fg=TEXT_MUTED, bg=BG_DARK, width=14, anchor='w').pack(side='left', padx=PAD_SMALL)
        tk.Label(header, text="Value", font=FONT_LABEL_BOLD, fg=TEXT_MUTED, bg=BG_DARK, width=8).pack(side='left')
        tk.Label(header, text="Status", font=FONT_LABEL_BOLD, fg=TEXT_MUTED, bg=BG_DARK).pack(side='right', padx=PAD_SMALL)
        
        row1 = tk.Frame(content, bg=BG_SIDEBAR)
        row1.pack(fill='x', pady=PAD_ROW)
        
        tk.Label(
            row1, text="⬤ Simulation:",
            fg=ACCENT_PRIMARY, bg=BG_SIDEBAR, font=FONT_LABEL, width=14, anchor='w'
        ).pack(side='left')
        
        self.lbl_my_flow = tk.Label(
            row1, text="0.0",
            fg=ACCENT_PRIMARY, bg=BG_SIDEBAR, font=FONT_VALUE_MEDIUM, width=8, anchor='e'
        )
        self.lbl_my_flow.pack(side='left')
        
        self.lbl_flow_status = tk.Label(
            row1, text="",
            fg=TEXT_MUTED, bg=BG_SIDEBAR, font=FONT_STATUS
        )
        self.lbl_flow_status.pack(side='right')
        
        row2 = tk.Frame(content, bg=BG_SIDEBAR)
        row2.pack(fill='x', pady=PAD_ROW)
        
        tk.Label(
            row2, text="⬤ Demand:",
            fg=GAUGE_DEMAND_LINE, bg=BG_SIDEBAR, font=FONT_LABEL, width=14, anchor='w'
        ).pack(side='left')
        
        self.lbl_target_flow = tk.Label(
            row2, text="40",
            fg=GAUGE_DEMAND_LINE, bg=BG_SIDEBAR, font=FONT_VALUE_MEDIUM, width=8, anchor='e'
        )
        self.lbl_target_flow.pack(side='left')
        
        self.lbl_efficiency = tk.Label(
            row2, text="--%",
            fg=TEXT_MUTED, bg=BG_SIDEBAR, font=FONT_STATUS
        )
        self.lbl_efficiency.pack(side='right')
        
        row3 = tk.Frame(content, bg=BG_SIDEBAR)
        row3.pack(fill='x', pady=PAD_ROW)
        
        tk.Label(
            row3, text="⬤ Real-World:",
            fg=ACCENT_TERTIARY, bg=BG_SIDEBAR, font=FONT_LABEL, width=14, anchor='w'
        ).pack(side='left')
        
        self.lbl_realworld = tk.Label(
            row3, text="28-36",
            fg=ACCENT_TERTIARY, bg=BG_SIDEBAR, font=FONT_VALUE_MEDIUM, width=8, anchor='e'
        )
        self.lbl_realworld.pack(side='left')
        
        self.lbl_comparison = tk.Label(
            row3, text="HCM typical",
            fg=TEXT_MUTED, bg=BG_SIDEBAR, font=FONT_STATUS
        )
        self.lbl_comparison.pack(side='right')
        
        gauge_container = tk.Frame(content, bg=BG_SIDEBAR)
        gauge_container.pack(fill='x', pady=PAD_ELEMENT)
        self.gauge_canvas = tk.Canvas(
            gauge_container, height=45,
            bg=BG_DARK, highlightthickness=1, highlightbackground=BORDER_DARK
        )
        self.gauge_canvas.pack(fill='x', expand=True)
        
        tk.Label(
            content, text="History (60s)",
            font=FONT_LABEL, fg=TEXT_SECONDARY, bg=BG_SIDEBAR
        ).pack(anchor='w', pady=(PAD_SMALL, 0))
        
        self.cv_history = tk.Canvas(
            content, height=80, bg=BG_DARK,
            highlightthickness=1, highlightbackground=BORDER_DARK
        )
        self.cv_history.pack(fill='x', pady=(PAD_TINY, PAD_SMALL))

    def _setup_lane_stats(self, parent):
        """Setup Lane Statistics section with mean wait time and LOS"""
        stats_frame = tk.LabelFrame(
            parent, text="LANE STATISTICS",
            font=FONT_LABEL_BOLD, fg=ACCENT_SECONDARY, bg=BG_SIDEBAR,
            bd=1, relief='solid'
        )
        stats_frame.pack(fill='x', padx=PAD_MEDIUM, pady=PAD_SECTION_START)
        
        header = tk.Frame(stats_frame, bg=BG_SIDEBAR)
        header.pack(fill='x', padx=PAD_FRAME, pady=(PAD_SMALL, 0))
        
        tk.Label(header, text="Lane", font=FONT_LABEL_BOLD, fg=TEXT_SECONDARY, bg=BG_SIDEBAR, width=5).pack(side='left')
        tk.Label(header, text="Avg", font=FONT_LABEL_BOLD, fg=TEXT_SECONDARY, bg=BG_SIDEBAR, width=7).pack(side='left')
        tk.Label(header, text="Max(60s)", font=FONT_LABEL_BOLD, fg=TEXT_SECONDARY, bg=BG_SIDEBAR, width=8).pack(side='left')
        tk.Label(header, text="LOS", font=FONT_LABEL_BOLD, fg=TEXT_SECONDARY, bg=BG_SIDEBAR, width=4).pack(side='left')
        tk.Label(header, text="Grade", font=FONT_LABEL_BOLD, fg=TEXT_SECONDARY, bg=BG_SIDEBAR).pack(side='right')
        
        self.lane_labels = {}
        for lane in ['N', 'S', 'E', 'W']:
            row = tk.Frame(stats_frame, bg=BG_SIDEBAR)
            row.pack(fill='x', padx=PAD_FRAME, pady=PAD_ROW)
            
            tk.Label(row, text=lane, font=FONT_LABEL, fg=TEXT_PRIMARY, bg=BG_SIDEBAR, width=5).pack(side='left')
            
            wait_lbl = tk.Label(row, text="0.0s", font=FONT_VALUE_SMALL, fg=TEXT_PRIMARY, bg=BG_SIDEBAR, width=7)
            wait_lbl.pack(side='left')
            
            max_wait_lbl = tk.Label(row, text="0.0s", font=FONT_VALUE_SMALL, fg=TEXT_MUTED, bg=BG_SIDEBAR, width=8)
            max_wait_lbl.pack(side='left')
            
            los_lbl = tk.Label(row, text="A", font=FONT_VALUE_MEDIUM, fg=STATUS_GOOD, bg=BG_SIDEBAR, width=4)
            los_lbl.pack(side='left')
            
            grade_lbl = tk.Label(row, text="Free Flow", font=FONT_STATUS, fg=STATUS_GOOD, bg=BG_SIDEBAR)
            grade_lbl.pack(side='right')
            
            self.lane_labels[lane] = {'wait': wait_lbl, 'max_wait': max_wait_lbl, 'los': los_lbl, 'grade': grade_lbl}
        
        overall_row = tk.Frame(stats_frame, bg=BG_DARK)
        overall_row.pack(fill='x', padx=PAD_FRAME, pady=(PAD_SMALL, PAD_SMALL))
        
        tk.Label(overall_row, text="Overall:", font=FONT_LABEL_BOLD, fg=TEXT_PRIMARY, bg=BG_DARK).pack(side='left', padx=PAD_SMALL)
        self.lbl_overall_los = tk.Label(overall_row, text="A", font=FONT_VALUE_LARGE, fg=STATUS_GOOD, bg=BG_DARK)
        self.lbl_overall_los.pack(side='left', padx=PAD_MEDIUM)
        self.lbl_overall_desc = tk.Label(overall_row, text="Free Flow", font=FONT_STATUS, fg=STATUS_GOOD, bg=BG_DARK)
        self.lbl_overall_desc.pack(side='right', padx=PAD_SMALL)

    def _setup_fuzzy_engine(self, parent):
        """Setup 3D Logic Engine section"""
        fuzzy_frame = tk.Frame(parent, bg=BG_SIDEBAR)
        fuzzy_frame.pack(fill='x', padx=PAD_MEDIUM, pady=(PAD_LARGE, 0))
        
        mf_container = tk.LabelFrame(
            fuzzy_frame, text="FUZZY ENGINE - Membership Functions",
            font=FONT_LABEL_BOLD, fg=ACCENT_SECONDARY, bg=BG_SIDEBAR,
            bd=1, relief='solid'
        )
        mf_container.pack(fill='x', pady=PAD_ELEMENT)
        
        inputs_row = tk.Frame(mf_container, bg=BG_SIDEBAR)
        inputs_row.pack(fill='x', padx=PAD_FRAME, pady=PAD_SMALL)
        inputs_row.columnconfigure(0, weight=1)
        inputs_row.columnconfigure(1, weight=1)
        inputs_row.columnconfigure(2, weight=1)
        
        def create_graph_canvas(parent_frame, col):
            frame = tk.Frame(parent_frame, bg=BG_SIDEBAR)
            frame.grid(row=0, column=col, sticky='nsew', padx=PAD_TINY, pady=PAD_TINY)
            canvas = tk.Canvas(
                frame, bg=BG_DARK, height=120,
                highlightthickness=1, highlightbackground=BORDER_DARK
            )
            canvas.pack(fill='both', expand=True)
            return canvas
        
        self.cv_input_a = create_graph_canvas(inputs_row, 0)
        self.cv_input_b = create_graph_canvas(inputs_row, 1)
        self.cv_input_c = create_graph_canvas(inputs_row, 2)
        
        rules_container = tk.LabelFrame(
            fuzzy_frame, text="Rule Weights",
            font=FONT_LABEL_BOLD, fg=TEXT_SECONDARY, bg=BG_SIDEBAR,
            bd=1, relief='solid'
        )
        rules_container.pack(fill='x', pady=PAD_ELEMENT)
        
        rules_content = tk.Frame(rules_container, bg=BG_SIDEBAR)
        rules_content.pack(fill='x', padx=PAD_FRAME, pady=PAD_SMALL)
        self.cv_rules = tk.Canvas(
            rules_content, height=130, bg=BG_DARK,
            highlightthickness=1, highlightbackground=BORDER_DARK
        )
        self.cv_rules.pack(fill='x', expand=True)
        
        output_container = tk.LabelFrame(
            fuzzy_frame, text="Decision Output",
            font=FONT_LABEL_BOLD, fg=TEXT_SECONDARY, bg=BG_SIDEBAR,
            bd=1, relief='solid'
        )
        output_container.pack(fill='x', pady=PAD_ELEMENT)
        
        output_content = tk.Frame(output_container, bg=BG_SIDEBAR)
        output_content.pack(fill='x', padx=PAD_FRAME, pady=PAD_SMALL)
        self.cv_output = tk.Canvas(
            output_content, height=80, bg=BG_DARK,
            highlightthickness=1, highlightbackground=BORDER_DARK
        )
        self.cv_output.pack(fill='x', expand=True)

    def _setup_controls(self, parent):
        """Setup Controls section"""
        control_frame = tk.LabelFrame(
            parent, text="CONTROLS",
            font=FONT_LABEL_BOLD, fg=ACCENT_PRIMARY, bg=BG_SIDEBAR,
            bd=1, relief='solid'
        )
        control_frame.pack(fill='x', padx=PAD_MEDIUM, pady=PAD_SECTION_START)
        
        content = tk.Frame(control_frame, bg=BG_SIDEBAR)
        content.pack(fill='x', padx=PAD_FRAME, pady=PAD_SMALL)
        
        demand_row = tk.Frame(content, bg=BG_SIDEBAR)
        demand_row.pack(fill='x', pady=PAD_ROW)
        
        tk.Label(
            demand_row, text="Demand (cars/min):",
            fg=TEXT_SECONDARY, bg=BG_SIDEBAR, font=FONT_LABEL
        ).pack(side='left')
        
        self.rate_var = tk.DoubleVar(value=40)
        self.lbl_rate_val = tk.Label(
            demand_row, text="40",
            fg=ACCENT_PRIMARY, bg=BG_SIDEBAR, font=FONT_VALUE_MEDIUM
        )
        self.lbl_rate_val.pack(side='right')
        
        def update_rate(v):
            val = float(v)
            self.lbl_rate_val.config(text=f"{val:.0f}")
            self.target_flow = val
            self.lbl_target_flow.config(text=f"{val:.0f}")
            self.update_capacity_estimate()
            self.draw_gauge()
        
        ttk.Scale(
            content, from_=10, to=200,
            variable=self.rate_var, command=update_rate, style='Horizontal.TScale'
        ).pack(fill='x', pady=PAD_ELEMENT)
        
        ttk.Button(
            content, text="SURGE TRAFFIC",
            command=self.surge_traffic
        ).pack(fill='x', pady=(PAD_ELEMENT, PAD_SMALL))

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================
    
    def _bind_mousewheel(self):
        self.sidebar_canvas.bind_all('<MouseWheel>', self._on_mousewheel)
    
    def _unbind_mousewheel(self):
        self.sidebar_canvas.unbind_all('<MouseWheel>')
    
    def _on_mousewheel(self, event):
        self.sidebar_canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
    
    def _on_sidebar_resize(self, event):
        new_width = event.width - 20
        if new_width > 100:
            items = self.sidebar_canvas.find_all()
            if items:
                self.sidebar_canvas.itemconfig(items[0], width=new_width)
            self.sidebar_width = new_width
    
    def _update_canvas_dimensions(self):
        """Update cached canvas dimensions"""
        try:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            if w > 10 and h > 10:
                if w != self.canvas_width or h != self.canvas_height:
                    self.canvas_width = w
                    self.canvas_height = h
                    for car in self.cars:
                        car.update_canvas_size(w, h)
        except:
            pass

    # =========================================================================
    # SIMULATION LOOP
    # =========================================================================
    
    def run_simulation(self):
        """Main simulation loop"""
        current_time = time.time()
        delta = current_time - self.last_frame_time
        self.last_frame_time = current_time
        if delta > 0.1:
            delta = 0.016
        
        if not hasattr(self, '_dim_update_counter'):
            self._dim_update_counter = 0
        self._dim_update_counter += 1
        if self._dim_update_counter >= 30:
            self._dim_update_counter = 0
            self._update_canvas_dimensions()
        
        # Spawn cars based on demand
        target_cpm = self.rate_var.get()
        target_cps = target_cpm / 60.0
        self.spawn_credit += target_cps * delta
        
        spawn_limit = 10
        while self.spawn_credit >= 1.0 and spawn_limit > 0:
            self.spawn_credit -= 1.0
            lane = random.choice(['N', 'S', 'E', 'W'])
            if self.can_spawn_freely(lane):
                self.spawn_car_direct(lane)
            else:
                self.virtual_queues[lane] += 1
            spawn_limit -= 1
        
        self.update_physics()
        self.manage_virtual_queues()
        
        # Calculate queue states
        queues = {'N': 0, 'S': 0, 'E': 0, 'W': 0}
        max_wait_ticks = 0
        
        for c in self.cars:
            if not c.is_virtual:
                queues[c.lane] += 1
                seconds_waiting = c.wait_time / 60.0
                if seconds_waiting > max_wait_ticks:
                    max_wait_ticks = seconds_waiting
        
        for lane in queues:
            queues[lane] += self.virtual_queues[lane]
        
        flow_ratio = self.current_flow / max(self.target_flow, 1.0)
        
        self.update_fsm(queues, max_wait_ticks, flow_ratio)
        self.calculate_flow_metrics()
        self.draw(queues)
        
        self.after(16, self.run_simulation)

    # =========================================================================
    # FSM (FINITE STATE MACHINE)
    # =========================================================================
    
    def update_fsm(self, queues, max_wait_time_sec, flow_ratio):
        """Update traffic light state machine"""
        self.state_timer += 1
        active_lane = self.phase_order[self.current_phase_idx]
        active_load = queues[active_lane]
        
        waiting_loads = [queues[l] for l in self.phase_order if l != active_lane]
        max_waiting = max(waiting_loads) if waiting_loads else 0
        
        # Calculate fuzzy logic
        score, mu_a, mu_b, mu_c, mu_f, rules, sets = self.fuzzy_controller.calculate(
            active_load, max_waiting, max_wait_time_sec, flow_ratio
        )
        
        # Adaptive timers
        if active_load <= 2:
            self.current_min_green = 30
        elif active_load <= 5:
            self.current_min_green = 50
        else:
            self.current_min_green = min(120, 40 + active_load * 8)
        
        self.current_max_green = min(300, 100 + active_load * 15)
        
        # FSM transitions
        switch_threshold = 35
        
        if self.fsm_state == 'GREEN':
            self.lights[active_lane] = 'green'
            should_switch = False
            
            if self.state_timer > self.current_min_green and score < switch_threshold:
                should_switch = True
            if self.state_timer > self.current_max_green:
                should_switch = True
            if active_load == 0 and max_waiting > 0 and self.state_timer > 20:
                should_switch = True
            
            if should_switch:
                self.fsm_state = 'YELLOW'
                self.state_timer = 0
                self.lights[active_lane] = 'yellow'
                
        elif self.fsm_state == 'YELLOW':
            if self.state_timer > 45:
                self.fsm_state = 'ALL_RED'
                self.state_timer = 0
                self.lights[active_lane] = 'red'
                
        elif self.fsm_state == 'ALL_RED':
            cx, cy = self.canvas_width / 2, self.canvas_height / 2
            occupied = any(cx - 100 < c.x < cx + 100 and cy - 100 < c.y < cy + 100 for c in self.cars)
            if not occupied and self.state_timer > 15:
                self.current_phase_idx = (self.current_phase_idx + 1) % 4
                self.fsm_state = 'GREEN'
                self.state_timer = 0
        
        # Calculate derived inputs for visualization
        clearance_time = active_load * 2.0  # SATURATION_HEADWAY = 2.0 sec
        imbalance_ratio = max_waiting / (active_load + 1)
        urgency_index = (max_wait_time_sec / 45.0) * (1 + max_waiting / 10.0)
        
        # Update fuzzy visualizations with new realistic inputs
        self.fuzzy_viz.draw_membership_3(
            self.cv_input_a, "Clearance (sec)", clearance_time, mu_a,
            sets[0], sets[1], sets[2], 60
        )
        self.fuzzy_viz.draw_membership_3(
            self.cv_input_b, "Imbalance Ratio", imbalance_ratio, mu_b,
            sets[3], sets[4], sets[5], 10
        )
        self.fuzzy_viz.draw_membership_3(
            self.cv_input_c, "Urgency Index", urgency_index, mu_c,
            sets[6], sets[7], sets[8], 5
        )
        self.fuzzy_viz.draw_rules_expanded(self.cv_rules, rules, flow_ratio, mu_f)
        self.fuzzy_viz.draw_output_expanded(self.cv_output, score, rules, switch_threshold)

    # =========================================================================
    # PHYSICS & SPAWNING
    # =========================================================================
    
    def can_spawn_freely(self, lane):
        """Check if a car can spawn without collision"""
        w, h = self.canvas_width, self.canvas_height
        for c in self.cars:
            if c.lane == lane and not c.is_virtual:
                dist = 0
                if lane == 'N':
                    dist = abs(c.y - (-20))
                elif lane == 'S':
                    dist = abs(c.y - (h + 20))
                elif lane == 'W':
                    dist = abs(c.x - (-20))
                elif lane == 'E':
                    dist = abs(c.x - (w + 20))
                if dist < 16:
                    return False
        return True
    
    def spawn_car_direct(self, lane):
        """Spawn a car directly on the road"""
        if not hasattr(self, 'start_time'):
            self.start_time = time.time()
        self.cars.append(Car(lane, self.canvas_width, self.canvas_height))
    
    def manage_virtual_queues(self):
        """Move cars from virtual queues to road when space is available"""
        for lane in ['N', 'S', 'E', 'W']:
            if self.virtual_queues[lane] > 0:
                if self.can_spawn_freely(lane):
                    self.virtual_queues[lane] -= 1
                    self.spawn_car_direct(lane)
    
    def update_physics(self):
        """Update car positions and handle exits"""
        lane_cars = {'N': [], 'S': [], 'E': [], 'W': []}
        for c in self.cars:
            lane_cars[c.lane].append(c)
        
        lane_cars['N'].sort(key=lambda c: c.y, reverse=True)
        lane_cars['S'].sort(key=lambda c: c.y)
        lane_cars['W'].sort(key=lambda c: c.x, reverse=True)
        lane_cars['E'].sort(key=lambda c: c.x)
        
        w, h = self.canvas_width, self.canvas_height
        cx, cy = w / 2, h / 2
        
        alive = []
        for lane in ['N', 'S', 'E', 'W']:
            light = self.lights[lane]
            for i, car in enumerate(lane_cars[lane]):
                car_ahead = lane_cars[lane][i - 1] if i > 0 else None
                car.update(light, car_ahead)
                
                # Count car when it passes through intersection center
                if not car.counted:
                    passed = False
                    if lane == 'N' and car.y > cy:
                        passed = True
                    elif lane == 'S' and car.y < cy:
                        passed = True
                    elif lane == 'W' and car.x > cx:
                        passed = True
                    elif lane == 'E' and car.x < cx:
                        passed = True
                    
                    if passed:
                        car.counted = True
                        now = time.time()
                        self.exit_timestamps.append(now)
                        # Track wait time for this lane (convert ticks to seconds)
                        wait_sec = car.wait_time / 60.0
                        self.lane_wait_times[lane].append(wait_sec)
                        # Also track with timestamp for max wait calculation
                        self.lane_wait_history[lane].append((now, wait_sec))
                
                # Keep car alive until it leaves canvas
                if -100 < car.x < w + 100 and -100 < car.y < h + 100:
                    alive.append(car)
        self.cars = alive

    # =========================================================================
    # METRICS
    # =========================================================================
    
    def calculate_flow_metrics(self):
        """Calculate and display flow metrics"""
        now = time.time()
        while self.exit_timestamps and self.exit_timestamps[0] < now - 60:
            self.exit_timestamps.popleft()
        
        count = len(self.exit_timestamps)
        elapsed = now - self.start_time if hasattr(self, 'start_time') else 1
        
        self.current_flow = (count / elapsed) * 60 if elapsed < 60 and elapsed > 1 else float(count)
        
        self.lbl_my_flow.config(text=f"{self.current_flow:.1f}")
        self.update_capacity_estimate()
        
        if self.target_flow > 0:
            satisfaction = (self.current_flow / self.target_flow) * 100
            self.lbl_efficiency.config(text=f"{satisfaction:.0f}%", foreground=get_efficiency_color(satisfaction))
        
        status_text, status_color = get_flow_status(self.current_flow, self.target_flow)
        self.lbl_flow_status.config(text=status_text, foreground=status_color)
        
        self.draw_gauge()
        
        if now - self.history_update_time >= 1.0:
            self.history_update_time = now
            self.throughput_history.append(self.current_flow)
            self.draw_history_graph()
        
        self.update_lane_stats()
        self.update_realworld_comparison()
    
    def update_realworld_comparison(self):
        """Update real-world throughput comparison in Flow Analyzer"""
        flow = self.current_flow
        demand = self.target_flow
        
        REAL_WORLD_CAPACITY = 75
        expected_rw_low = min(demand * 0.70, REAL_WORLD_CAPACITY * 0.85)
        expected_rw_high = min(demand * 0.90, REAL_WORLD_CAPACITY)
        
        self.realworld_expected_low = expected_rw_low
        self.realworld_expected_high = expected_rw_high
        
        self.lbl_realworld.config(text=f"{expected_rw_low:.0f}-{expected_rw_high:.0f}")
        
        if flow < expected_rw_low:
            perc = ((expected_rw_low - flow) / expected_rw_low) * 100 if expected_rw_low > 0 else 0
            comp_text, comp_color = f"-{perc:.0f}% vs Real", STATUS_WARNING
        elif flow <= expected_rw_high:
            comp_text, comp_color = "Realistic ✓", STATUS_GOOD
        else:
            perc = ((flow - expected_rw_high) / expected_rw_high) * 100 if expected_rw_high > 0 else 0
            comp_text, comp_color = f"+{perc:.0f}% vs Real", ACCENT_PRIMARY
        
        self.lbl_comparison.config(text=comp_text, foreground=comp_color)
        
        ratio = flow / max(demand, 1)
        if ratio >= 0.95: status, color = "Meeting demand ✓", STATUS_GOOD
        elif ratio >= 0.8: status, color = f"{ratio*100:.0f}% of demand", STATUS_WARNING
        else: status, color = "Under capacity", STATUS_ERROR
        
        self.lbl_flow_status.config(text=status, foreground=color)
    
    def update_capacity_estimate(self):
        """Calculate theoretical intersection capacity based on current conditions"""
        saturation_flow_per_lane = 20
        demand_factor = min(1.0, self.target_flow / 60)
        green_efficiency = 0.25 + (demand_factor * 0.15)
        self.theoretical_capacity = saturation_flow_per_lane * green_efficiency * 4
    
    def draw_gauge(self):
        """Draw the flow gauge with Simulation, Demand, and Real-World indicators"""
        c = self.gauge_canvas
        c.delete("all")
        
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 50: w = 400
        if h < 10: h = 45
        
        rw_min = getattr(self, 'realworld_expected_low', self.target_flow * 0.7)
        rw_max = getattr(self, 'realworld_expected_high', self.target_flow * 0.9)
        max_scale = max(self.target_flow, rw_max, self.current_flow, 50) * 1.15
        
        def to_x(val): return (val / max_scale) * w
        
        rw_min_x, rw_max_x = to_x(rw_min), to_x(rw_max)
        c.create_rectangle(rw_min_x, 0, rw_max_x, h, fill='#1a3a2a', outline="")
        
        c.create_line(rw_min_x, 5, rw_min_x, h-5, fill=ACCENT_TERTIARY, width=2)
        c.create_line(rw_max_x, 5, rw_max_x, h-5, fill=ACCENT_TERTIARY, width=2)
        c.create_line(rw_min_x, h-5, rw_max_x, h-5, fill=ACCENT_TERTIARY, width=1, dash=(2,2))
        c.create_text((rw_min_x + rw_max_x)/2, h-2, text="Real-World", fill=ACCENT_TERTIARY, font=FONT_MICRO, anchor='s')
        
        demand_x = to_x(self.target_flow)
        c.create_line(demand_x, 3, demand_x, h-8, fill=GAUGE_DEMAND_LINE, width=3)
        c.create_polygon(demand_x-5, 3, demand_x+5, 3, demand_x, 10, fill=GAUGE_DEMAND_LINE)
        c.create_text(demand_x, 3, text=f"{self.target_flow:.0f}", fill=GAUGE_DEMAND_LINE, font=FONT_MICRO, anchor='s')
        
        flow_x = min(to_x(self.current_flow), w - 2)
        bar_y1, bar_y2 = 15, h - 12
        ratio = self.current_flow / max(self.target_flow, 1)
        bar_color = STATUS_GOOD if ratio >= 0.9 else (STATUS_WARNING if ratio >= 0.7 else STATUS_ERROR)
        c.create_rectangle(2, bar_y1, flow_x, bar_y2, fill=bar_color, outline=ACCENT_PRIMARY, width=1)
        
        c.create_text(flow_x + 5, (bar_y1+bar_y2)/2, text=f"{self.current_flow:.0f}", fill=TEXT_PRIMARY, font=FONT_LABEL_BOLD, anchor='w')
        
        for val in [0, 25, 50, 75, 100]:
            if val <= max_scale:
                x = to_x(val)
                c.create_line(x, h-3, x, h, fill=TEXT_MUTED, width=1)
                if 0 < val < max_scale * 0.95:
                    c.create_text(x, h, text=str(val), fill=TEXT_MUTED, font=FONT_MICRO, anchor='n')

    # =========================================================================
    # LANE STATISTICS & LEVEL OF SERVICE
    # =========================================================================
    
    def get_los_grade(self, avg_delay):
        """Calculate Level of Service (LOS) based on average delay (HCM criteria)."""
        if avg_delay <= 10: return 'A', 'Free Flow', STATUS_GOOD
        if avg_delay <= 20: return 'B', 'Stable', STATUS_GOOD
        if avg_delay <= 35: return 'C', 'Acceptable', STATUS_WARNING
        if avg_delay <= 55: return 'D', 'Unstable', STATUS_WARNING
        if avg_delay <= 80: return 'E', 'Poor', STATUS_ERROR
        return 'F', 'Failure', STATUS_ERROR
    
    def update_lane_stats(self):
        """Update lane statistics display"""
        now = time.time()
        total_wait, total_count, overall_max_wait = 0, 0, 0
        
        for lane in ['N', 'S', 'E', 'W']:
            while self.lane_wait_history[lane] and self.lane_wait_history[lane][0][0] < now - 60:
                self.lane_wait_history[lane].popleft()
            
            avg_wait = sum(self.lane_wait_times[lane]) / len(self.lane_wait_times[lane]) if self.lane_wait_times[lane] else 0
            max_wait = max(entry[1] for entry in self.lane_wait_history[lane]) if self.lane_wait_history[lane] else 0
            
            overall_max_wait = max(overall_max_wait, max_wait)
            self.lane_mean_wait[lane] = avg_wait
            total_wait += avg_wait
            total_count += 1
            
            grade, desc, color = self.get_los_grade(avg_wait)
            max_color = STATUS_GOOD if max_wait <= 20 else (STATUS_WARNING if max_wait <= 45 else STATUS_ERROR)
            
            self.lane_labels[lane]['wait'].config(text=f"{avg_wait:.1f}s")
            self.lane_labels[lane]['max_wait'].config(text=f"{max_wait:.1f}s", foreground=max_color)
            self.lane_labels[lane]['los'].config(text=grade, foreground=color)
            self.lane_labels[lane]['grade'].config(text=desc, foreground=color)
        
        overall_avg = total_wait / total_count if total_count > 0 else 0
        grade, desc, color = self.get_los_grade(overall_avg)
        self.lbl_overall_los.config(text=grade, foreground=color)
        self.lbl_overall_desc.config(text=f"{desc} (avg:{overall_avg:.0f}s max:{overall_max_wait:.0f}s)", foreground=color)
    
    def draw_history_graph(self):
        """Draw throughput history line graph"""
        c = self.cv_history
        c.delete("all")
        
        w, h = c.winfo_width(), c.winfo_height()
        if w < 50: w = 400
        if h < 20: h = 100
        
        pad = 10
        gw = w - 2 * pad
        gh = h - 2 * pad
        
        max_val = max(max(self.throughput_history) if self.throughput_history else 0, self.target_flow, 10) * 1.1
        
        for i in range(5): c.create_line(pad, pad + (gh * i / 4), pad + gw, pad + (gh * i / 4), fill=BORDER_DARK, dash=(2, 4))
        
        demand_y = pad + gh - (self.target_flow / max_val * gh)
        c.create_line(pad, demand_y, pad + gw, demand_y, fill=GAUGE_DEMAND_LINE, width=1, dash=(4, 2))
        c.create_text(pad + gw + 2, demand_y, text="Dem", fill=GAUGE_DEMAND_LINE, font=FONT_MICRO, anchor='w')
        
        if len(self.throughput_history) > 1:
            n = len(self.throughput_history)
            points = [item for i, val in enumerate(self.throughput_history) for item in (pad + (i / (n - 1)) * gw if n > 1 else pad, pad + gh - (val / max_val * gh))]
            c.create_line(points, fill=ACCENT_PRIMARY, width=2, smooth=True)
            if points:
                lx, ly = points[-2], points[-1]
                c.create_oval(lx - 4, ly - 4, lx + 4, ly + 4, fill=ACCENT_PRIMARY, outline=TEXT_PRIMARY)
        
        c.create_text(pad - 2, pad, text=f"{int(max_val)}", fill=TEXT_MUTED, font=FONT_MICRO, anchor='e')
        c.create_text(pad - 2, pad + gh, text="0", fill=TEXT_MUTED, font=FONT_MICRO, anchor='e')
        c.create_text(pad + gw - 5, pad + 5, text=f"{self.current_flow:.1f}", fill=TEXT_PRIMARY, font=FONT_VALUE_SMALL, anchor='ne')

    # =========================================================================
    # DRAWING
    # =========================================================================
    
    def draw(self, queues):
        """Draw the main traffic simulation canvas"""
        c = self.canvas
        c.delete("all")
        
        w, h = self.canvas_width, self.canvas_height
        cx, cy = w / 2, h / 2
        rw = max(80, min(min(w, h) * 0.15, 150))
        
        c.create_rectangle(cx - rw / 2, 0, cx + rw / 2, h, fill=BG_ROAD, outline="")
        c.create_rectangle(0, cy - rw / 2, w, cy + rw / 2, fill=BG_ROAD, outline="")
        c.create_rectangle(cx - rw / 2, cy - rw / 2, cx + rw / 2, cy + rw / 2, fill=BG_INTERSECTION, outline=TEXT_PRIMARY, dash=(2, 2))
        
        if self.virtual_queues['N'] > 0: c.create_rectangle(cx - 20, 0, cx + 20, 10, fill=OVERFLOW_QUEUE)
        if self.virtual_queues['S'] > 0: c.create_rectangle(cx - 20, h - 10, cx + 20, h, fill=OVERFLOW_QUEUE)
        if self.virtual_queues['W'] > 0: c.create_rectangle(0, cy + 20, 10, cy - 20, fill=OVERFLOW_QUEUE)
        if self.virtual_queues['E'] > 0: c.create_rectangle(w - 10, cy + 20, w, cy - 20, fill=OVERFLOW_QUEUE)
        
        for car in self.cars:
            if not car.is_virtual:
                c.create_rectangle(car.x - 6, car.y - 6, car.x + 6, car.y + 6, fill=car.get_color(), outline="black")
        
        for lane, total_q in queues.items():
            txt, pos = f"Q: {total_q}", (0, 0)
            if lane == 'N': pos = (cx, cy - rw / 2 - 50)
            elif lane == 'S': pos = (cx, cy + rw / 2 + 50)
            elif lane == 'W': pos = (cx - rw / 2 - 50, cy)
            elif lane == 'E': pos = (cx + rw / 2 + 50, cy)
            c.create_text(pos, text=txt, fill=TEXT_PRIMARY, font=FONT_VALUE_SMALL)
        
        self._draw_light(c, 'N', cx - rw / 2 - 25, cy - rw / 2 - 25)
        self._draw_light(c, 'S', cx + rw / 2 + 25, cy + rw / 2 + 25)
        self._draw_light(c, 'W', cx - rw / 2 - 25, cy + rw / 2 + 25)
        self._draw_light(c, 'E', cx + rw / 2 + 25, cy - rw / 2 - 25)
    
    def _draw_light(self, c, lane, x, y):
        """Draw a traffic light"""
        col = self.lights[lane]
        fill = LIGHT_GREEN if col == 'green' else (LIGHT_YELLOW if col == 'yellow' else LIGHT_RED)
        
        c.create_oval(x - 22, y - 22, x + 22, y + 22, fill=BG_DARK, outline=BORDER_DARK, width=1)
        
        if col == 'green' and lane == self.phase_order[self.current_phase_idx]:
            pct = min(1.0, self.state_timer / max(1, self.current_min_green))
            c.create_arc(x - 20, y - 20, x + 20, y + 20, start=90, extent=-360 * pct, style="arc", outline=ACCENT_TERTIARY, width=4)
        
        c.create_oval(x - 12, y - 12, x + 12, y + 12, fill=fill, outline=TEXT_PRIMARY, width=2)

    # =========================================================================
    # ACTIONS
    # =========================================================================
    
    def surge_traffic(self):
        """Add a surge of traffic to a random lane"""
        self.virtual_queues[random.choice(['N', 'S', 'E', 'W'])] += 15

if __name__ == "__main__":
    app = UltimateTrafficApp()
    app.mainloop()