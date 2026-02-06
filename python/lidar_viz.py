import serial
import open3d as o3d
import numpy as np
import threading
import struct
import time
from collections import deque

# === CONFIGURATION ===
SERIAL_PORT = 'COM10'  # Adjust this to your specific COM port
BAUD_RATE = 230400    # Must match Arduino
MAX_POINTS = 2000     # Number of points to keep in the view
POINT_LIFETIME = 0.5  # Seconds to keep a point before fading/removing (approx)

# === SHARED VARIABLES ===
# Deque is thread-safe for appends/pops in CPython
scan_buffer = deque(maxlen=MAX_POINTS)
scan_lock = threading.Lock()
running = True

def serial_reader_thread(port):
    """
    Background thread that reads binary data from the serial port
    and pushes decoded points into the shared buffer.
    """
    global running
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=0.1)
        print(f"Connected to {port} at {BAUD_RATE} baud.")
    except Exception as e:
        print(f"Error opening serial port: {e}")
        running = False
        return

    print("Reader thread started. Waiting for data...")
    
    # Packet structure: 12 points * 5 bytes = 60 bytes
    PACKET_SIZE = 60
    
    while running:
        try:
            # Sync: Look for Header 0xFA 0xFA
            # Read one byte at a time until we find the first header byte
            if ser.read(1) == b'\xFA':
                if ser.read(1) == b'\xFA':
                    # Found header, read the rest of the packet
                    packet_data = ser.read(PACKET_SIZE)
                    
                    if len(packet_data) == PACKET_SIZE:
                        # Unpack 12 points
                        # Format: For each point (Angle:H, Dist:H, Intensity:B)
                        # We parse manually or with struct loop
                        
                        new_points = []
                        for i in range(12):
                            offset = i * 5
                            # <HHB = Little Endian, UShort, UShort, UByte
                            angle_packed, dist_raw, intensity = struct.unpack_from('<HHB', packet_data, offset)
                            
                            if dist_raw > 0: # Filter invalid points
                                angle_deg = angle_packed / 100.0
                                new_points.append((angle_deg, dist_raw, intensity))
                                
                        if new_points:
                            with scan_lock:
                                scan_buffer.extend(new_points)
                                
        except serial.SerialException as e:
            print(f"Serial Error: {e}")
            break
        except Exception as e:
            print(f"Error in reader: {e}")
            continue
            
    ser.close()
    print("Serial port closed.")

def visualizer_thread():
    """
    Main thread that handles Open3D rendering.
    """
    global running
    
    # Initialize Visualizer
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="LD19 LiDAR - High Performance", width=1024, height=768)
    
    # Create Point Cloud object
    pcd = o3d.geometry.PointCloud()
    vis.add_geometry(pcd)
    
    # Add Coordinate Frame (Origin)
    axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=100, origin=[0, 0, 0])
    vis.add_geometry(axis)
    
    # View Control Options
    opt = vis.get_render_option()
    opt.background_color = np.asarray([0.05, 0.05, 0.05]) # Dark background
    opt.point_size = 3.0
    
    print("Visualizer started. Press 'Q' in the window to quit.")
    
    try:
        while running:
            # 1. Get snapshot of data
            with scan_lock:
                if len(scan_buffer) > 0:
                    data_snapshot = list(scan_buffer)
                else:
                    data_snapshot = []
            
            if data_snapshot:
                # 2. Convert to NumPy for vectorization
                # Structure: [(angle, dist, int), ...]
                data_np = np.array(data_snapshot)
                
                angles_deg = data_np[:, 0]
                distances = data_np[:, 1]
                intensities = data_np[:, 2]
                
                # Polar to Cartesian
                angles_rad = np.radians(angles_deg)
                x = distances * np.cos(angles_rad)
                y = distances * np.sin(angles_rad)
                z = np.zeros_like(x)
                
                # Stack to Nx3 array
                points_3d = np.column_stack((x, y, z))
                
                # 3. Update Point Cloud
                pcd.points = o3d.utility.Vector3dVector(points_3d)
                
                # Optional: Color mapping based on Intensity or Distance
                # Here: Distance-based coloring (Rainbow)
                # Normalize distance for color (e.g., 0 to 3000mm)
                colors = np.zeros((len(distances), 3))
                norm_dist = np.clip(distances / 3000.0, 0, 1)
                
                # Simple Red-to-Blue gradient
                colors[:, 0] = 1 - norm_dist  # Red component
                colors[:, 2] = norm_dist      # Blue component
                colors[:, 1] = 0.2           # Constant Green
                
                pcd.colors = o3d.utility.Vector3dVector(colors)
                
                vis.update_geometry(pcd)
            
            # 4. Render
            keep_running = vis.poll_events()
            vis.update_renderer()
            
            if not keep_running:
                running = False
                
            # Cap FPS slightly to not starve CPU if needed, but 0 is fine for max speed
            time.sleep(0.005)
            
    except KeyboardInterrupt:
        running = False
    finally:
        vis.destroy_window()

if __name__ == "__main__":
    # Start Serial Thread
    t_serial = threading.Thread(target=serial_reader_thread, args=(SERIAL_PORT,), daemon=True)
    t_serial.start()
    
    # Start Visualizer (Must be in main thread for Open3D sometimes)
    visualizer_thread()
    
    # Cleanup
    running = False
    t_serial.join(timeout=1.0)
    print("Exiting...")
