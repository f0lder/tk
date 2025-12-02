# Neuro-Traffic: Fuzzy Logic Traffic Signal Controller

A real-time traffic simulation with an intelligent fuzzy logic controller that optimizes signal timing for maximum throughput while maintaining fairness across all lanes.

![Python](https://img.shields.io/badge/Python-3.x-blue) ![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green) ![Fuzzy Logic](https://img.shields.io/badge/AI-Fuzzy%20Logic-orange)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Fuzzy Logic Algorithm](#fuzzy-logic-algorithm)
   - [Inputs](#inputs)
   - [Membership Functions](#membership-functions)
   - [Fuzzy Rules](#fuzzy-rules)
   - [Defuzzification](#defuzzification)
   - [Post-Processing Adjustments](#post-processing-adjustments)
4. [Finite State Machine (FSM)](#finite-state-machine-fsm)
5. [Metrics & Calculations](#metrics--calculations)
6. [Car Physics](#car-physics)
7. [File Structure](#file-structure)
8. [Usage](#usage)

---

## Overview

Neuro-Traffic simulates a 4-way intersection with intelligent traffic light control. Instead of using fixed timing cycles, the system uses **fuzzy logic** to make real-time decisions about when to switch lights based on **realistic traffic engineering principles**:

- **Clearance Time**: Time needed to clear the current queue (based on saturation flow rate)
- **Queue Imbalance**: How unfairly cars are distributed across lanes
- **Driver Urgency**: Combined measure of wait time and frustration level

The goal is to maximize **throughput** (cars per minute) while ensuring **fairness** (no lane waits too long).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Application (app.py)                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Simulation │  │     FSM     │  │   Fuzzy Controller  │ │
│  │    Loop     │──│  (States)   │──│   (Decision Logic)  │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│         │                │                    │             │
│         ▼                ▼                    ▼             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Car Physics │  │   Metrics   │  │   Visualization     │ │
│  │  (car.py)   │  │ Calculator  │  │   (fuzzy_logic.py)  │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Fuzzy Logic Algorithm

The fuzzy logic controller uses a **Mamdani-type** inference system with trapezoidal membership functions.

### Inputs

The controller uses **3 derived inputs** based on traffic engineering principles:

| Input | Formula | Range | Meaning |
|-------|---------|-------|---------|
| **Clearance Time** | `active_queue × 2.0 sec` | 0-60+ sec | Time to clear current queue at saturation flow (1800 veh/hr) |
| **Imbalance Ratio** | `max_waiting / (active + 1)` | 0-10+ | How much more traffic is waiting vs being served |
| **Urgency Index** | `(wait_time / 45) × (1 + wait_q/10)` | 0-5+ | Combined frustration from time waiting AND queue size |

#### Why These Inputs?

**1. Clearance Time (Traffic Engineering Standard)**
- Based on **saturation headway** of 2 seconds per vehicle
- This is the actual time gap between cars passing through at green light
- Industry standard: ~1800 vehicles/hour/lane = 2 sec/vehicle

**2. Imbalance Ratio (Fairness Metric)**
- Measures how "unfair" the current signal is to waiting drivers
- A ratio of 1.0 means equal queues (fair)
- A ratio of 4.0+ means waiting lanes have 4x more cars (unfair, needs switch)

**3. Urgency Index (Driver Psychology)**
- Research shows driver frustration starts at ~30-60 seconds of waiting
- The index combines both queue pressure AND time pressure
- Accounts for the fact that 5 cars waiting 60 seconds is worse than 10 cars waiting 10 seconds

### Membership Functions

Each input is fuzzified using **3-level trapezoidal membership functions** (Short/Low, Medium, Long/High).

#### Clearance Time Membership

```
Membership
    1.0 ┤     ╱‾‾‾╲         ╱‾‾‾╲         ╱‾‾‾‾‾‾
        │    ╱     ╲       ╱     ╲       ╱
    0.5 ┤   ╱       ╲     ╱       ╲     ╱
        │  ╱         ╲   ╱         ╲   ╱
    0.0 ┼─╱───────────╲─╱───────────╲─╱────────────
        0    4   10   12  20  30     60 (seconds)
             SHORT     MEDIUM       LONG
```

| Set | Parameters [a, b, c, d] | Interpretation |
|-----|------------------------|----------------|
| SHORT | [0, 0, 4, 10] | Quick clearance (< 5 cars) - can consider switching |
| MEDIUM | [6, 12, 20, 30] | Moderate queue (6-15 cars) |
| LONG | [20, 30, 60, 60] | Large queue (15+ cars) - needs more green time |

#### Imbalance Ratio Membership

```
Membership
    1.0 ┤     ╱‾‾‾╲         ╱‾‾‾╲         ╱‾‾‾‾‾‾
        │    ╱     ╲       ╱     ╲       ╱
    0.5 ┤   ╱       ╲     ╱       ╲     ╱
        │  ╱         ╲   ╱         ╲   ╱
    0.0 ┼─╱───────────╲─╱───────────╲─╱────────────
        0  0.5  1.5  2.0  2.5  4.0     10 (ratio)
             LOW       MEDIUM       HIGH
```

| Set | Parameters [a, b, c, d] | Interpretation |
|-----|------------------------|----------------|
| LOW | [0, 0, 0.5, 1.5] | Fair distribution (active queue larger or equal) |
| MEDIUM | [0.8, 1.5, 2.5, 4.0] | Moderate imbalance (1.5-2.5x more waiting) |
| HIGH | [2.5, 4.0, 10, 10] | Severe imbalance (4x+ more waiting = unfair!) |

#### Urgency Index Membership

```
Membership
    1.0 ┤     ╱‾‾‾╲         ╱‾‾‾╲         ╱‾‾‾‾‾‾
        │    ╱     ╲       ╱     ╲       ╱
    0.5 ┤   ╱       ╲     ╱       ╲     ╱
        │  ╱         ╲   ╱         ╲   ╱
    0.0 ┼─╱───────────╲─╱───────────╲─╱────────────
        0  0.3  0.7  0.8  1.2  1.8     5 (index)
             LOW       MEDIUM       HIGH
```

| Set | Parameters [a, b, c, d] | Interpretation |
|-----|------------------------|----------------|
| LOW | [0, 0, 0.3, 0.7] | Patient drivers (< 30 sec wait, small queues) |
| MEDIUM | [0.5, 0.8, 1.2, 1.8] | Getting impatient (30-60 sec, moderate queues) |
| HIGH | [1.2, 1.8, 5.0, 5.0] | Frustrated drivers (> 60 sec or long queues) |

#### Trapezoidal Membership Function Formula

```python
def trapmf(x, [a, b, c, d]):
    if x <= a or x >= d:
        return 0.0
    if b <= x <= c:
        return 1.0
    if a < x < b:
        return (x - a) / (b - a)  # Rising edge
    if c < x < d:
        return (d - x) / (d - c)  # Falling edge
```

### Fuzzy Rules

The controller uses **9 rules** organized into 3 categories:

#### KEEP Rules (High score → Keep current green)

| Rule | Condition | Weight | Description |
|------|-----------|--------|-------------|
| R1 | Clearance=LONG ∧ ¬Urgency=HIGH | 1.4 | Keep clearing a big queue |
| R2 | Imbalance=LOW ∧ Clearance=MED ∧ ¬Urgency=HIGH | 1.2 | Keep when balanced |
| R3 | Clearance=MED/LONG ∧ Imbalance=LOW ∧ Urgency=LOW | 1.3 | Let current batch through |

#### SWITCH Rules (Low score → Switch to next lane)

| Rule | Condition | Weight | Description |
|------|-----------|--------|-------------|
| R4 | Imbalance=HIGH ∧ Clearance=SHORT/MED | 1.3 | Switch when unfair to waiting lanes |
| R5 | Urgency=HIGH | 1.5 | Switch when drivers are frustrated |
| R6 | Clearance=SHORT ∧ Imbalance=MED/HIGH | 1.6 | Switch when active lane nearly empty |
| R7 | Imbalance=MED ∧ Urgency=MED | 0.9 | Combined moderate pressure |

#### CONFLICT Rules (Medium score → Hold/balance)

| Rule | Condition | Weight | Description |
|------|-----------|--------|-------------|
| R8 | Clearance=LONG ∧ Urgency=HIGH | 0.7 | Big queue but high urgency - tough decision |
| R9 | Clearance=MED ∧ Imbalance=MED ∧ Urgency=MED | 0.9 | Everything moderate - balanced |

#### Rule Evaluation

Rules use **MIN** (AND) and **MAX** (OR) operators:

```python
# Example: R1 - Keep clearing a big queue
r1_clearing = min(mu_clear_long, 1 - mu_urg_high) * weight['keep_clearing']

# Combine all KEEP rules
r1_total = max(r1_clearing, r1_efficient, r1_batch)
```

### Defuzzification

Uses **weighted average** (Center of Gravity approximation):

```python
# Output centroids
OUT_SWITCH = 15    # Low score region
OUT_BALANCE = 50   # Middle score region  
OUT_KEEP = 85      # High score region

# Defuzzification formula
score = (r1_total × 85 + r2_total × 15 + r3_total × 50) / (r1_total + r2_total + r3_total + 0.001)
```

### Post-Processing Adjustments

After defuzzification, three adjustments are applied:

#### 1. Batch Bonus
```python
if active_q > 5 and urgency_index < 1.5:
    batch_bonus = min(12, (active_q - 5) × 2)
# Encourages completing large batches when urgency isn't critical
```

#### 2. Empty Lane Penalty
```python
if active_q <= 1 and max_waiting_q > 2:
    empty_penalty = -25
# Strongly encourages switching when active lane is empty
```

#### 3. Urgency Penalty
```python
if urgency_index > 2.0:
    urgency_penalty = -10 × (urgency_index - 2.0)
# Override batch bonus when drivers are very frustrated
```

#### Final Score
```python
final_score = clamp(score + batch_bonus + empty_penalty + urgency_penalty, 0, 100)
```

---

## Finite State Machine (FSM)

The traffic light controller uses a 3-state FSM:

```
                    ┌──────────────────────────┐
                    │         GREEN            │
                    │  (Active lane = green)   │
                    └──────────┬───────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │   Conditions to switch:             │
            │   • timer > min_green AND score < 35│
            │   • timer > max_green               │
            │   • active_q = 0 AND waiting > 0    │
            └──────────────────┼──────────────────┘
                               ▼
                    ┌──────────────────────────┐
                    │         YELLOW           │
                    │   (45 ticks ≈ 0.75s)     │
                    └──────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────────┐
                    │        ALL_RED           │
                    │  (Clear intersection)    │
                    └──────────┬───────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │   Transition when:                  │
            │   • No cars in intersection         │
            │   • timer > 15 ticks                │
            └──────────────────┼──────────────────┘
                               │
                               ▼
                    ┌──────────────────────────┐
                    │     GREEN (next lane)    │
                    │   phase_idx = (idx+1) % 4│
                    └──────────────────────────┘
```

### Adaptive Green Times

The minimum and maximum green times adapt to traffic conditions:

```python
# Minimum green time
if active_load <= 2:
    min_green = 30 ticks (0.5 seconds)
elif active_load <= 5:
    min_green = 50 ticks (0.83 seconds)
else:
    min_green = min(120, 40 + active_load × 8)

# Maximum green time  
max_green = min(300, 100 + active_load × 15)
```

---

## Metrics & Calculations

### Throughput (Cars/Minute)

```python
# Count cars that exited in last 60 seconds
count = len([t for t in exit_timestamps if t > now - 60])

# Calculate flow rate
if elapsed < 60:
    current_flow = (count / elapsed) × 60  # Extrapolate to per-minute
else:
    current_flow = count  # Direct count over last minute
```

### Theoretical Capacity

```python
saturation_flow_per_lane = 20  # cars/min at continuous green
base_efficiency = 0.25
demand_factor = min(1.0, target_flow / 60)
green_efficiency = 0.25 + (demand_factor × 0.15)  # 0.25 to 0.40

theoretical_capacity = 20 × green_efficiency × 4 lanes
# Range: ~20 to ~32 cars/minute depending on demand
```

### Efficiency

```python
efficiency = (current_flow / theoretical_capacity) × 100%
```

### Flow Status

| Condition | Status |
|-----------|--------|
| flow ≥ target | "✓ MEETING DEMAND" (green) |
| flow ≥ 0.8 × target | "NEAR TARGET" (yellow) |
| flow < 0.8 × target | "BELOW TARGET" (red) |

---

## Car Physics

### Car Properties

| Property | Value | Description |
|----------|-------|-------------|
| Max Speed | 8 px/frame | Top speed when moving freely |
| Acceleration | 0.5 px/frame² | Speed increase rate |
| Deceleration | 1.0 px/frame² | Speed decrease rate |
| Stop Distance | 18 px | Minimum gap between cars |
| Slowdown Distance | 40 px | Distance to start matching speed |

### Collision Avoidance

```python
dist_to_car = sqrt((x - car_ahead.x)² + (y - car_ahead.y)²)

if dist_to_car < 18:
    target_speed = 0  # Full stop
elif dist_to_car < 40:
    target_speed = min(max_speed, car_ahead.speed)  # Match speed
```

### Car States (Visual)

| Wait Time | Color | State |
|-----------|-------|-------|
| 0-600 ticks, moving | Cyan | Normal |
| 0-600 ticks, stopped | Red | Waiting |
| > 600 ticks | Purple | Angry (frustrated) |

---

## File Structure

```
tk/
├── app.py           # Main application, UI, simulation loop, FSM
├── car.py           # Car entity with physics
├── fuzzy_logic.py   # Fuzzy controller and visualization
├── theme.py         # Colors, fonts, styling constants
└── README.md        # This documentation
```

### Module Responsibilities

| File | Responsibility |
|------|----------------|
| **app.py** | Main window, simulation loop, FSM, metrics, drawing |
| **car.py** | Car position, velocity, collision avoidance, state |
| **fuzzy_logic.py** | Membership functions, rule evaluation, defuzzification, canvas visualization |
| **theme.py** | All colors, fonts, padding constants, helper functions |

---

## Usage

### Running the Application

```bash
python app.py
```

### Controls

- **Traffic Demand Slider**: Adjust arrival rate (10-200 cars/minute)
- **SURGE TRAFFIC Button**: Add 15 cars instantly to a random lane
- **Drag Sidebar Edge**: Resize the control panel

### Reading the Dashboard

1. **Flow Analyzer**: Shows current throughput vs demand vs capacity
2. **Membership Functions**: Real-time fuzzy input visualization
3. **Rule Weights**: Active rule strengths (green=KEEP, red=SWITCH)
4. **Decision Output**: Final score with SWITCH/KEEP decision

### Interpreting the Output

- **Score < 35**: System recommends SWITCH (move to next lane)
- **Score ≥ 35**: System recommends KEEP (continue current green)
- **Higher score**: Stronger confidence in keeping current lane green

---

## Algorithm Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FUZZY LOGIC PIPELINE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  RAW INPUTS              DERIVED INPUTS         FUZZIFICATION       │
│  ──────────              ──────────────         ─────────────       │
│  • Active Queue ───┬───► Clearance Time ──────► μ_short/med/long   │
│  • Waiting Queue ──┼───► Imbalance Ratio ─────► μ_low/med/high     │
│  • Wait Time ──────┴───► Urgency Index ───────► μ_low/med/high     │
│                                                       │             │
│                                                       ▼             │
│                                               RULE EVALUATION       │
│                                               ────────────────      │
│                                               9 Rules (MIN/MAX)     │
│                                                       │             │
│                      DEFUZZIFICATION          POST-PROCESS    │    │
│                      ───────────────          ────────────    │    │
│                      Weighted Average ◄───────────────────────┘    │
│                            │                                       │
│                            ▼                                       │
│                      Base Score (0-100)                            │
│                            │                                       │
│                            ├──► + Batch Bonus (big queue)          │
│                            ├──► - Empty Penalty (active empty)     │
│                            └──► - Urgency Penalty (very frustrated)│
│                                     │                              │
│                                     ▼                              │
│                              Final Score ──► FSM Decision          │
│                              (0-100)         (SWITCH if < 35)      │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## License

MIT License - Feel free to use and modify for educational purposes.
