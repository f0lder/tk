# =============================================================================
# CAR.PY - Car Entity for Traffic Simulation
# =============================================================================

import math

# Import theme colors
try:
    from theme import CAR_NORMAL, CAR_WAITING, CAR_ANGRY
except ImportError:
    # Fallback colors if theme not available
    CAR_NORMAL = "#00ffff"
    CAR_WAITING = "#ff4444"
    CAR_ANGRY = "#aa00ff"


class Car:
    """
    Car entity for traffic simulation
    
    Attributes:
        lane: Direction ('N', 'S', 'E', 'W')
        x, y: Current position
        speed: Current speed
        wait_time: Ticks spent waiting (used for patience calculation)
    """
    
    def __init__(self, lane, canvas_width, canvas_height):
        self.lane = lane
        self.w, self.h = canvas_width, canvas_height
        self.cx, self.cy = self.w / 2, self.h / 2
        self.gap = 60
        self.stop_line_offset = 120
        self.is_virtual = False
        
        self.length = 20
        self.width = 16
        
        self.speed = 0
        self.max_speed = 8
        self.accel = 0.5
        self.decel = 1.0
        self.wait_time = 0
        self.counted = False  # Track if car has been counted as passing intersection
        
        # Set start position and direction based on lane
        if lane == 'N':
            self.x, self.y = self.cx - self.gap / 2, -50
            self.dx, self.dy = 0, 1
            self.stop_y = self.cy - self.stop_line_offset
        elif lane == 'S':
            self.x, self.y = self.cx + self.gap / 2, self.h + 50
            self.dx, self.dy = 0, -1
            self.stop_y = self.cy + self.stop_line_offset
        elif lane == 'W':
            self.x, self.y = -50, self.cy + self.gap / 2
            self.dx, self.dy = 1, 0
            self.stop_x = self.cx - self.stop_line_offset
        elif lane == 'E':
            self.x, self.y = self.w + 50, self.cy - self.gap / 2
            self.dx, self.dy = -1, 0
            self.stop_x = self.cx + self.stop_line_offset
    
    def update_canvas_size(self, new_width, new_height):
        """Update stop lines when canvas resizes (cars keep their positions)"""
        old_cx, old_cy = self.cx, self.cy
        self.w, self.h = new_width, new_height
        self.cx, self.cy = self.w / 2, self.h / 2
        
        # Update stop lines to new center
        if self.lane == 'N':
            self.stop_y = self.cy - self.stop_line_offset
            self.x = self.x - old_cx + self.cx
        elif self.lane == 'S':
            self.stop_y = self.cy + self.stop_line_offset
            self.x = self.x - old_cx + self.cx
        elif self.lane == 'W':
            self.stop_x = self.cx - self.stop_line_offset
            self.y = self.y - old_cy + self.cy
        elif self.lane == 'E':
            self.stop_x = self.cx + self.stop_line_offset
            self.y = self.y - old_cy + self.cy

    def update(self, light_color, car_ahead):
        """Update car position based on traffic light and car ahead"""
        if self.is_virtual:
            return

        target_speed = self.max_speed
        
        # Calculate distance to stop line
        dist_to_stop = 9999
        if self.lane == 'N':
            dist_to_stop = self.stop_y - self.y
        elif self.lane == 'S':
            dist_to_stop = self.y - self.stop_y
        elif self.lane == 'W':
            dist_to_stop = self.stop_x - self.x
        elif self.lane == 'E':
            dist_to_stop = self.x - self.stop_x
        
        # Stop at red/yellow lights
        if dist_to_stop > -10:
            if light_color in ['red', 'yellow'] and dist_to_stop < 50:
                target_speed = 0
        
        # Collision avoidance - balanced spacing
        if car_ahead and not car_ahead.is_virtual:
            dist_to_car = math.sqrt((self.x - car_ahead.x) ** 2 + (self.y - car_ahead.y) ** 2)
            if dist_to_car < 24:
                target_speed = 0
            elif dist_to_car < 50:
                target_speed = min(target_speed, car_ahead.speed)
        
        # Apply acceleration/deceleration
        if self.speed < target_speed:
            self.speed = min(self.speed + self.accel, target_speed)
        elif self.speed > target_speed:
            self.speed = max(self.speed - self.decel, target_speed)
        
        # Update position
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        
        # Track wait time
        if self.speed < 0.5:
            self.wait_time += 1

    def get_color(self):
        """Get car color based on state"""
        if self.wait_time > 600:
            return CAR_ANGRY      # Rage - waited too long
        if self.speed < 0.5:
            return CAR_WAITING    # Stopped/waiting
        return CAR_NORMAL         # Moving normally
