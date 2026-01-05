# Vicon DataStream Communication Overview

## Underlying Communication Scheme

The Vicon DataStream SDK uses a **TCP/IP socket-based protocol** to communicate with Vicon Nexus or Tracker software running on a PC. Here's how it works:

### Connection Details
- **Protocol**: TCP/IP
- **Default Port**: 801 (on the Vicon PC)
- **Stream Modes**: 
  - `ServerPush`: Server automatically sends frames
  - `ClientPull`: Client requests frames on-demand

### Message Format
All messages follow a simple binary framing protocol:

```
[4 bytes: Size (little-endian)] [4 bytes: Command ID (little-endian)] [N bytes: Payload]
```

### Key Operations
1. **Connect**: Establish TCP connection to Vicon server
2. **EnableSegmentData**: Tell server to stream segment tracking data
3. **GetFrame**: Request a new frame (in ClientPull mode)
4. **GetSubjectCount**: Get number of tracked objects
5. **GetSubjectName**: Get name of tracked object by index
6. **GetSegmentGlobalTranslation**: Get position (X, Y, Z) in meters
7. **GetSegmentGlobalRotationQuaternion**: Get rotation as quaternion (X, Y, Z, W)

### Data Format
- **Position**: 3x double (24 bytes) representing X, Y, Z coordinates in millimeters
- **Rotation (Quaternion)**: 4x double (32 bytes) representing QX, QY, QZ, QW

## Vicon Python Listener Script

The included `vicon_listener.py` provides a minimal Python implementation that:

1. Connects to a Vicon server via socket
2. Enables segment data
3. Continuously requests frames
4. Extracts and prints position and rotation of a tracked object

### Usage

```bash
python3 vicon_listener.py <object_name> [host] [port]
```

### Examples

```bash
# Track "robot_1" on default host/port
python3 vicon_listener.py robot_1

# Track "quadrotor" on specific IP
python3 vicon_listener.py quadrotor 192.168.30.152 801

# Track a specific segment
python3 vicon_listener.py my_object 10.0.0.5 801
```

### Output
```
Frame 1: Position: X=1.234, Y=2.345, Z=0.567 | Rotation: QX=0.000, QY=0.000, QZ=0.707, QW=0.707
Frame 2: Position: X=1.250, Y=2.360, Z=0.575 | Rotation: QX=0.000, QY=0.000, QZ=0.707, QW=0.707
...
```

## How the ROS Bridge Works

The ROS `vicon_bridge` uses the C++ DataStream SDK to:

1. **Connect** to the Vicon server with `Client::Connect(host_name_)`
2. **Enable Data**: `EnableSegmentData()` to stream tracking data
3. **Set Stream Mode**: ClientPull or ServerPush mode via `SetStreamMode()`
4. **Get Frames**: Call `GetFrame()` in a loop
5. **Extract Data**: For each frame, iterate through subjects/segments and call:
   - `GetSegmentCount(subject_name)` - how many segments per subject
   - `GetSegmentGlobalTranslation(subject_name, segment_name)` - position
   - `GetSegmentGlobalRotationQuaternion(...)` - orientation
6. **Publish**: Forward the data as ROS transforms and messages

## Connection Example from C++ Code

From `vicon_bridge.cpp`:
```cpp
// Connect
while (!vicon_client_.IsConnected().Connected) {
    vicon_client_.Connect(host_name_);  // e.g., "192.168.30.152:801"
    sleep(1);
}

// Enable segment data
vicon_client_.EnableSegmentData();

// In main loop:
while (true) {
    if (stream_mode_ == "ClientPull") {
        client.GetFrame();  // Request a frame
    }
    
    unsigned int subjectCount = vicon_client_.GetSubjectCount().SubjectCount;
    
    for (int i = 0; i < subjectCount; i++) {
        std::string subjectName = vicon_client_.GetSubjectName(i).SubjectName;
        unsigned int segmentCount = vicon_client_.GetSegmentCount(subjectName).SegmentCount;
        
        for (int j = 0; j < segmentCount; j++) {
            std::string segmentName = vicon_client_.GetSegmentName(subjectName, j).SegmentName;
            
            auto trans = vicon_client_.GetSegmentGlobalTranslation(subjectName, segmentName);
            auto rot = vicon_client_.GetSegmentGlobalRotationQuaternion(subjectName, segmentName);
            
            // trans.Translation = [X, Y, Z] in meters
            // rot.Rotation = [X, Y, Z, W] quaternion
        }
    }
}
```

## Notes

- **Coordinate System**: Default is Z-up with Forward/Left axes (configurable)
- **Data Format**: Position in millimeters, rotation as quaternion
- **Latency**: Typically < 10ms per frame at 100 Hz capture rate
- **No Authentication**: The DataStream API doesn't use authentication
- **Network**: Must be on same network as Vicon PC or have network route configured
