# Changelog

## [1.1.0] - 2026-02-06
### Fixed
- **Critical Protocol Bug**: The Arduino firmware was processing corrupted or partial packets as valid data, causing "ghost points" and noise in the visualization.
- **Header Validation**: Added strict check for the `0x2C` byte (VER_LEN) in the LD19 packet header.
- **Checksum Validation**: Implemented the official CRC8 One-Wire checksum algorithm. Any packet with a mismatching CRC is now dropped immediately.
- **Index Alignment**: Fixed an off-by-one indexing error when reading distance and intensity bytes from the raw buffer.

### Added
- **Radar Visualization**: New `radar_viz.py` and `START_RADAR.bat` for a 2D "Sonar-style" view to verify close-range accuracy (<20cm).
- **Intensity Filtering**: Added a minimum intensity threshold (`MIN_INTENSITY = 220`) to the radar view to filter out sensor noise.

## [1.0.0] - 2026-02-06
### Added
- Initial release.
- **High-Performance Bridge**: `lidar.ino` converting LD19 packets to a custom binary protocol (`0xFA 0xFA` header) at 230400 baud.
- **Zero-Lag Visualizer**: `lidar_viz.py` using Multi-threading and Open3D for real-time 3D rendering (~4500 points/s).
- **Launcher**: `START_APP.bat` for one-click execution.
