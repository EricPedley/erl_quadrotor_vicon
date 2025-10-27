# Devcontainer for erl_quadrotor_vicon

This devcontainer is configured to run a ROS1 (Noetic) catkin development environment for the repository.

Key points
- Base image: ros:noetic-ros-core (Ubuntu 20.04 / Focal). Change to another ROS distro (e.g., melodic) by editing `devcontainer.json` and the Dockerfile.
- Networking: By default the container is started with `--network=host` (see `devcontainer.json` `runArgs`). This is recommended for Vicon DataStream and multicast because the plugin uses TCP port 801 and multicast (239.0.0.0:44801) in some modes. Host networking makes ROS master and Vicon streams work seamlessly.
- Forwarded ports: `11311` (ROS master), `801` (Vicon DataStream), `44801` (multicast sample port) are listed in `forwardPorts` for convenience. When using host networking these entries are informational only.
- X11: The X11 socket is bind-mounted so GUI tools can be displayed on the host. Ensure `xhost +local:root` (or a safer policy) is set on the host before opening GUI apps from the container.

Note about X11 mount error
- If you attempted to open the container and saw an error like "invalid mount config for type 'bind': bind source path does not exist: /tmp/.X11-unix", that means the devcontainer tried to bind-mount your host's `/tmp/.X11-unix` but that path did not exist on your host (this can happen on some systems or remote setups).

Remediation options:
1. Preferred: create the path on your host and allow X11 access, then reopen the container:

```bash
# on your host (not in the container)
mkdir -p /tmp/.X11-unix
# allow local root to connect to your X server (choose a safer policy if needed)
xhost +local:root
```

2. If you don't need GUI apps, no action is required — the devcontainer has been updated to avoid failing when `/tmp/.X11-unix` is missing. You can still use the container for building and running ROS nodes (console-only).

3. If you prefer automatic X11 mounts, you can re-add a bind mount in your personal devcontainer config or by editing `devcontainer.json` after ensuring the host path exists.

Post-create actions
- After the container is created the `postCreateCommand` will:
  - find all `package.xml` files inside the repository and symlink their parent directories into `/workspace/catkin_ws/src`
  - run `catkin_make` in `/workspace/catkin_ws`

How to use
1. Open this repository in VS Code.
2. Use the Command Palette -> `Remote-Containers: Reopen in Container`.
3. Once the container is built and opened, the workspace will be available at `/workspaces/erl_quadrotor_vicon` and a catkin workspace at `/workspace/catkin_ws`.
4. To source the environment in a terminal: `source /opt/ros/noetic/setup.bash && source /workspace/catkin_ws/devel/setup.bash`.

Notes and alternatives
- If you do NOT want host networking, remove `"--network=host"` from `devcontainer.json` and instead expose ports explicitly by adding `runArgs` like `"-p","11311:11311","-p","801:801"`. Multicast may still fail without host networking.
- If your host uses a different ROS distro (Melodic/Kinetic), switch the Docker base image and ROS setup lines accordingly.

Troubleshooting
- If Vicon streams aren't visible, ensure the Vicon machine is reachable from the host. With host networking, the container shares the host's interfaces so connectivity mirrors the host.
- For GUI apps, export DISPLAY on the host and allow access: `xhost +local:root` (or restrict as desired).
