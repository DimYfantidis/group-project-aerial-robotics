from pymavlink import mavutil


def connect_vehicle(connection_string=None):
    """
    Connects to a vehicle using pymavlink.

    If connection_string is None, defaults to 'udp:127.0.0.1:14551'.
    Waits for a heartbeat and returns a mavutil.mavlink_connection instance.
    """
    if connection_string is None:
        connection_string = 'udp:127.0.0.1:14551'
    print(f"[Connecting to vehicle on: {connection_string}]")
    mav = mavutil.mavlink_connection(connection_string)
    mav.wait_heartbeat()
    print("Heartbeat received from system (system %u component %u)" %
          (mav.target_system, mav.target_component))
    return mav


def upload_mission(mav, waypoints_3d):
    """
    Uploads a mission to the vehicle using pymavlink.

    Each waypoint in waypoints_3d is a tuple (lat, lon, alt) where:
      - lat, lon are in degrees,
      - alt is in meters (relative altitude).

    The function clears any existing mission, sends the mission count,
    then waits for MISSION_REQUEST_INT messages to send each waypoint.
    """
    count = len(waypoints_3d)
    print(f"[Uploading mission with {count} waypoints]")

    # Clear any existing mission
    mav.mav.mission_clear_all_send(mav.target_system, mav.target_component)
    # Optionally wait for ACK (omitted for brevity)

    # Send the mission count
    mav.mav.mission_count_send(mav.target_system, mav.target_component, count)

    for i, (lat, lon, alt) in enumerate(waypoints_3d):
        lat_int = int(lat * 1e7)
        lon_int = int(lon * 1e7)
        # Wait for the autopilot to request a mission item
        msg = mav.recv_match(type='MISSION_REQUEST_INT',
                             blocking=True, timeout=10)
        if msg is None:
            print("Timeout waiting for MISSION_REQUEST_INT; aborting mission upload.")
            return
        seq = msg.seq
        mav.mav.mission_item_int_send(
            mav.target_system,
            mav.target_component,
            seq,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            0, 1,     # current, autocontinue
            0, 0, 0, 0,  # params 1-4 (not used)
            lat_int, lon_int, alt
        )
        print(f"Sent waypoint {seq+1}/{count}")

    # Wait for mission acknowledgment
    ack = mav.recv_match(type='MISSION_ACK', blocking=True, timeout=10)
    if ack is None:
        print("No mission ack received.")
    else:
        print("Mission uploaded successfully.")

# TODO: Implement set_geofence
def set_geofence(mav, flight_coords, fence_altitude=10):
    pass

# TODO: Implement hover to make the drone hover in place for a given duration while processing the images
def hover(mav, duration=10):
    pass

# TODO: Implement resume_mission to resume the mission after processing the images
def resume_mission(mav):
    pass
