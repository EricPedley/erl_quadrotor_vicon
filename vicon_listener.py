#!/usr/bin/env python3
"""
Barebones Vicon DataStream client in Python.
Listens to a single tracked object by name and prints its position and rotation.

The Vicon DataStream SDK uses a TCP/IP protocol. This script implements
a minimal client that:
1. Connects to the Vicon server at the specified host:port
2. Enables segment data
3. Requests frames in ClientPull mode
4. Extracts and prints the position/rotation of a named tracked object
"""

import socket
import struct
import sys
import time


class ViconStreamClient:
    def __init__(self, host, port):
        """Initialize connection to Vicon DataStream server."""
        self.host = host
        self.port = port
        self.socket = None
        self.is_connected = False

    def connect(self):
        """Connect to the Vicon DataStream server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            print(f"Connected to Vicon server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to Vicon server: {e}")
            sys.exit(1)

    def disconnect(self):
        """Disconnect from the Vicon server."""
        if self.socket:
            self.socket.close()
            self.is_connected = False

    def _send_bytes(self, data):
        """Send raw bytes to the server."""
        if not self.is_connected:
            print("Not connected to server")
            return False
        try:
            self.socket.sendall(data)
            return True
        except Exception as e:
            print(f"Error sending data: {e}")
            return False

    def _recv_bytes(self, num_bytes):
        """Receive exactly num_bytes from the server."""
        data = b""
        while len(data) < num_bytes:
            try:
                chunk = self.socket.recv(num_bytes - len(data))
                if not chunk:
                    print("Connection closed by server")
                    return None
                data += chunk
            except Exception as e:
                print(f"Error receiving data: {e}")
                return None
        return data

    def _send_command(self, command_id, payload=b""):
        """
        Send a command following Vicon's DataStream protocol.
        
        The protocol uses a simple framing:
        - 4 bytes: size (little-endian)
        - 4 bytes: command ID (little-endian)
        - N bytes: payload
        """
        packet = struct.pack("<I", 4 + len(payload)) + struct.pack("<I", command_id) + payload
        return self._send_bytes(packet)

    def _read_response(self):
        """Read a response packet from the server."""
        size_data = self._recv_bytes(4)
        if not size_data:
            return None, None
        
        size = struct.unpack("<I", size_data)[0]
        
        if size < 4:
            print(f"Invalid packet size: {size}")
            return None, None
        
        cmd_id_data = self._recv_bytes(4)
        if not cmd_id_data:
            return None, None
        
        cmd_id = struct.unpack("<I", cmd_id_data)[0]
        
        payload_size = size - 4
        payload = b""
        if payload_size > 0:
            payload = self._recv_bytes(payload_size)
            if payload is None:
                return None, None
        
        return cmd_id, payload

    def get_frame(self):
        """Request a new frame from the server (ClientPull mode)."""
        # Command ID for GetFrame is typically 1
        return self._send_command(1)

    def enable_segment_data(self):
        """Enable segment data in the stream."""
        # Command ID for EnableSegmentData is typically 9
        return self._send_command(9)

    def get_subject_count(self):
        """Get the number of subjects in the current frame."""
        # Send GetSubjectCount command (ID typically 2)
        self._send_command(2)
        cmd_id, payload = self._read_response()
        
        if payload and len(payload) >= 4:
            count = struct.unpack("<I", payload[:4])[0]
            return count
        return 0

    def get_subject_name(self, subject_index):
        """Get the name of a subject by index."""
        payload = struct.pack("<I", subject_index)
        self._send_command(3, payload)
        cmd_id, response = self._read_response()
        
        if response:
            # Extract null-terminated string
            name = response.split(b'\x00')[0].decode('utf-8', errors='ignore')
            return name
        return ""

    def get_segment_count(self, subject_name):
        """Get the number of segments for a subject."""
        payload = subject_name.encode('utf-8') + b'\x00'
        self._send_command(4, payload)
        cmd_id, response = self._read_response()
        
        if response and len(response) >= 4:
            count = struct.unpack("<I", response[:4])[0]
            return count
        return 0

    def get_segment_global_translation(self, subject_name, segment_name):
        """Get the global translation (position) of a segment."""
        payload = subject_name.encode('utf-8') + b'\x00' + segment_name.encode('utf-8') + b'\x00'
        self._send_command(6, payload)
        cmd_id, response = self._read_response()
        
        if response and len(response) >= 12:
            x, y, z = struct.unpack("<ddd", response[:24])
            return (x, y, z)
        return None

    def get_segment_global_rotation_quaternion(self, subject_name, segment_name):
        """Get the global rotation of a segment as a quaternion."""
        payload = subject_name.encode('utf-8') + b'\x00' + segment_name.encode('utf-8') + b'\x00'
        # Command ID for GetSegmentGlobalRotationQuaternion is typically 12
        self._send_command(12, payload)
        cmd_id, response = self._read_response()
        
        if response and len(response) >= 32:
            x, y, z, w = struct.unpack("<dddd", response[:32])
            return (x, y, z, w)
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 vicon_listener.py <object_name> [host] [port]")
        print("Example: python3 vicon_listener.py robot_1 192.168.30.152 801")
        sys.exit(1)

    object_name = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else "192.168.30.152"
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 801

    print(f"Vicon Listener")
    print(f"Tracking object: {object_name}")
    print(f"Connecting to {host}:{port}...")

    client = ViconStreamClient(host, port)
    client.connect()

    # Enable segment data
    client.enable_segment_data()
    time.sleep(0.1)

    try:
        print(f"\nListening for {object_name}...\n")
        frame_count = 0

        while True:
            # Request a new frame
            if not client.get_frame():
                print("Failed to get frame")
                break

            time.sleep(0.01)  # Small delay to let server respond

            # Get translation (position)
            translation = client.get_segment_global_translation(object_name, object_name)

            # Get rotation (quaternion)
            rotation = client.get_segment_global_rotation_quaternion(object_name, object_name)

            if translation:
                frame_count += 1
                x, y, z = translation
                print(f"Frame {frame_count}: Position: X={x:.3f}, Y={y:.3f}, Z={z:.3f}", end="")
                
                if rotation:
                    qx, qy, qz, qw = rotation
                    print(f" | Rotation: QX={qx:.3f}, QY={qy:.3f}, QZ={qz:.3f}, QW={qw:.3f}")
                else:
                    print()
            else:
                print("Could not find object or connection lost")
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()
        print("Disconnected")


if __name__ == "__main__":
    main()
