import serial
import pygame
import numpy as np
import threading
import struct
import math
import sys

# === CONFIGURATION ===
SERIAL_PORT = 'COM10'
BAUD_RATE = 230400
WINDOW_SIZE = 800
MAX_DISTANCE_CM = 20  # Range on screen (radius)
SCALE_FACTOR = (WINDOW_SIZE / 2) / MAX_DISTANCE_CM # Pixels per CM
MIN_INTENSITY = 220   # Filtrer le bruit (Points faibles) - Augmente a 220

# === COLORS ===
COLOR_BG = (0, 20, 0)      # Dark Green/Black
COLOR_GRID = (0, 80, 0)    # Dim Green
COLOR_POINT = (0, 255, 0)  # Bright Neon Green
COLOR_TEXT = (0, 180, 0)

# === SHARED DATA ===
scan_points = [] # List of (x, y) tuples in screen coordinates
scan_lock = threading.Lock()
running = True

def serial_reader_thread(port):
    global running
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=0.1)
    except Exception as e:
        print(f"Error opening port: {e}")
        running = False
        return

    PACKET_SIZE = 60
    
    while running:
        try:
            if ser.read(1) == b'\xFA':
                if ser.read(1) == b'\xFA':
                    packet_data = ser.read(PACKET_SIZE)
                    if len(packet_data) == PACKET_SIZE:
                        # Process packet
                        new_pts = []
                        cx, cy = WINDOW_SIZE // 2, WINDOW_SIZE // 2
                        
                        for i in range(12):
                            offset = i * 5
                            angle_packed, dist_mm, intensity = struct.unpack_from('<HHB', packet_data, offset)
                            
                            dist_cm = dist_mm / 10.0
                            
                            # Filter: Range AND Intensity
                            # Note: dist_mm > 0 check is implicit since dist_cm > 0
                            if 0 < dist_cm <= MAX_DISTANCE_CM and intensity > MIN_INTENSITY:
                                angle_rad = math.radians(angle_packed / 100.0)
                                
                                # Convert Polar to Cartesian (Screen coords)
                                # Note: Pygame Y is down. Standard Math Angle 0 is Right.
                                # Lidar Angle usually standard.
                                x = cx + (math.cos(angle_rad) * dist_cm * SCALE_FACTOR)
                                y = cy + (math.sin(angle_rad) * dist_cm * SCALE_FACTOR) # +Y is down
                                
                                new_pts.append((int(x), int(y)))
                        
                        if new_pts:
                            with scan_lock:
                                # Simple "fade" logic: just append, we clear screen every frame or keep buffer
                                # For radar effect, we can keep a rolling buffer
                                scan_points.extend(new_pts)
                                # Keep buffer size manageable
                                if len(scan_points) > 2000:
                                    del scan_points[:100]
                                    
        except Exception:
            pass
    ser.close()

def draw_grid(screen, font):
    cx, cy = WINDOW_SIZE // 2, WINDOW_SIZE // 2
    
    # Draw Circles (5, 10, 15 cm)
    for r_cm in [5, 10, 15]:
        radius = int(r_cm * SCALE_FACTOR)
        pygame.draw.circle(screen, COLOR_GRID, (cx, cy), radius, 1)
        
        # Label
        text = font.render(f"{r_cm}cm", True, COLOR_TEXT)
        screen.blit(text, (cx + radius + 5, cy))

    # Crosshairs
    pygame.draw.line(screen, COLOR_GRID, (0, cy), (WINDOW_SIZE, cy), 1)
    pygame.draw.line(screen, COLOR_GRID, (cx, 0), (cx, WINDOW_SIZE), 1)

def main():
    global running, scan_points
    
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("LD19 RADAR - SONAR VIEW")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 16)
    
    # Start Serial Thread
    t = threading.Thread(target=serial_reader_thread, args=(SERIAL_PORT,), daemon=True)
    t.start()
    
    # Fade Surface (for trails)
    fade_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
    fade_surf.fill((0, 0, 0))
    fade_surf.set_alpha(15) # Transparency level (Higher = faster fade)

    print("Radar started.")
    
    try:
        while running:
            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False

            # Drawing
            # Instead of screen.fill, we blit a semi-transparent black surface to create trails
            screen.blit(fade_surf, (0,0))
            
            # Draw Static Grid
            draw_grid(screen, font)
            
            # Draw Points
            with scan_lock:
                for pt in scan_points:
                    pygame.draw.circle(screen, COLOR_POINT, pt, 2)
                
                # Clear buffer periodically or rely on fade? 
                # With 'fade_surf', we should CLEAR scan_points after drawing them once
                # so they get 'baked' into the screen and fade out.
                scan_points = [] 

            pygame.display.flip()
            clock.tick(60)
            
    except KeyboardInterrupt:
        pass
    finally:
        running = False
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
