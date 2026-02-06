# High-Performance LiDAR Visualization (LD19)

This project implements a low-latency, high-performance visualization system for the LDROBOT LD19 LiDAR using an Arduino (Seeed XIAO nRF52840) and Python (Open3D).

## Key Features
- **Binary Protocol**: Optimized custom protocol reduces data overhead by 300% compared to CSV.
- **Zero-Lag**: Uses a multi-threaded "Producer-Consumer" architecture in Python to separate data acquisition from rendering.
- **High Speed**: Operates at **230400 baud** to handle the 4500 points/second flux.

## Structure
- `arduino/lidar/lidar.ino`: The firmware for the microcontroller.
- `python/lidar_viz.py`: The PC-side visualization script.

## Getting Started

### 1. Arduino Setup
1. Open `arduino/lidar/lidar.ino` in the Arduino IDE.
2. Select your board (Seeed XIAO nRF52840).
3. Connect the LiDAR to the XIAO:
   - **LiDAR TX** -> **XIAO RX** (D7 on nRF52840)
   - **LiDAR PWM** -> **GND** (To enable the motor)
4. Upload the code.
5. **Close the Serial Monitor** (The Python script needs the port).

### 2. Python Setup
1. Install dependencies:
   ```bash
   pip install open3d pyserial numpy
   ```
2. Check the COM port in `python/lidar_viz.py` (Line 9):
   ```python
   SERIAL_PORT = 'COM10' # Change this if needed
   ```
3. Run the script:
   ```bash
   python python/lidar_viz.py
   ```

## Troubleshooting
- **Permission Denied**: Close any other software using the COM port (Arduino IDE, other terminals).
- **Lag**: Ensure `BAUD_RATE` is 230400 on both sides.
