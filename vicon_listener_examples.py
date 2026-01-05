#!/usr/bin/env python4
"""
Example usage of the Vicon listener script.
This demonstrates how to use the minimal Vicon DataStream client.
"""

from vicon_listener import ViconStreamClient
import time


def track_object_simple(object_name, host, port, duration_seconds=10):
    """
    Simple example: Connect and track an object for a specified duration.
    
    Args:
        object_name: Name of the tracked object (e.g., "robot_1")
        host: IP address of Vicon PC (e.g., "192.168.30.152")
        port: Port number (default 801)
        duration_seconds: How long to track for
    """
    client = ViconStreamClient(host, port)
    client.connect()
    client.enable_segment_data()
    
    print(f"Tracking {object_name} for {duration_seconds} seconds...\n")
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < duration_seconds:
        client.get_frame()
        time.sleep(0.01)
        
        translation = client.get_segment_global_translation(object_name, object_name)
        rotation = client.get_segment_global_rotation_quaternion(object_name, object_name)
        
        if translation:
            frame_count += 1
            x, y, z = translation
            print(f"Frame {frame_count}: pos=({x:.2f}, {y:.2f}, {z:.2f})", end="")
            
            if rotation:
                qx, qy, qz, qw = rotation
                print(f" rot=({qx:.2f}, {qy:.2f}, {qz:.2f}, {qw:.2f})")
            else:
                print()
    
    client.disconnect()
    print(f"\nTracked {frame_count} frames over {time.time() - start_time:.1f} seconds")


def list_available_objects(host, port):
    """
    Example: Connect and list all available tracked objects.
    
    Args:
        host: IP address of Vicon PC
        port: Port number
    """
    client = ViconStreamClient(host, port)
    client.connect()
    client.enable_segment_data()
    
    # Request a frame to populate subject list
    client.get_frame()
    time.sleep(0.1)
    
    count = client.get_subject_count()
    print(f"Found {count} tracked objects:\n")
    
    for i in range(count):
        name = client.get_subject_name(i)
        print(f"  {i+1}. {name}")
    
    client.disconnect()


if __name__ == "__main__":
    # Example 1: List all objects
    print("=" * 50)
    print("Example 1: List all tracked objects")
    print("=" * 50)
    try:
        list_available_objects("192.168.30.153", 801)
    except Exception as e:
        print(f"Error: {e}")
    
    # print("\n" + "=" * 50)
    # print("Example 2: Track a single object")
    # print("=" * 50)
    # try:
    #     track_object_simple("robot_1", "192.168.30.153", 801, duration_seconds=5)
    # except Exception as e:
    #     print(f"Error: {e}")
