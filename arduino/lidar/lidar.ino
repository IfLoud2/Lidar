#include <Arduino.h>

#define HEADER_BYTE 0xFA

// Structure for a single point in the packet
struct PointData {
    uint16_t angle; // Angle * 100
    uint16_t dist;  // Distance in mm
    uint8_t intensity;
};

void setup() {
  Serial.begin(230400);   // High speed for binary data
  Serial1.begin(230400);  // LD19 LiDAR native speed
  
  // Optional: Blink LED to indicate start
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  delay(100);
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  if (Serial1.available() >= 47) {
    if (Serial1.read() == 0x54) { // Header START_BYTE
      // VER_LEN is usually 0x2C (12 points), but we just read the block
      uint8_t buffer[46];
      Serial1.readBytes(buffer, 46);
      
      // Calculate start and end angles
      // Protocol: Angle is in 0.01 degrees resolution
      float start_angle = ((buffer[3] << 8) | buffer[2]) * 0.01;
      float end_angle = ((buffer[41] << 8) | buffer[40]) * 0.01;
      
      // Handle the 360-degree wrap-around case
      float diff = end_angle - start_angle;
      if (diff < 0) {
        diff += 360;
      }
      
      // Calculate step per point (12 points total)
      float step = diff / 11.0;
      
      // Prepare binary packet header
      Serial.write(HEADER_BYTE);
      Serial.write(HEADER_BYTE);
      
      // Process and send 12 points
      for (int i = 0; i < 12; i++) {
        // Extract distance and intensity
        uint16_t dist = (buffer[5 + i*3] << 8) | buffer[4 + i*3];
        uint8_t intensity = buffer[6 + i*3];
        
        // Interpolate angle
        float current_angle = start_angle + (step * i);
        if (current_angle >= 360) {
          current_angle -= 360;
        }
        
        // Pack angle as uint16 (x100 to keep precision)
        uint16_t angle_packed = (uint16_t)(current_angle * 100);
        
        // Send 5 bytes per point: Angle(2) + Dist(2) + Intensity(1)
        // Little Endian is standard for Arduino
        Serial.write((uint8_t)(angle_packed & 0xFF));
        Serial.write((uint8_t)(angle_packed >> 8));
        
        Serial.write((uint8_t)(dist & 0xFF));
        Serial.write((uint8_t)(dist >> 8));
        
        Serial.write(intensity);
      }
    }
  }
}
