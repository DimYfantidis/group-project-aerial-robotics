# Description

Small OpenGL simulator for determining the UAV's horizon limits, i.e. the HFOV and VFOV **in meters** for a given altitude, $h$ and for given FOV values measured as angles. 


# Setup Requirements

* Windows OS
* Python3 Interpreter
* MSVC compiler
* CMake ver. >3.1

To build and run the simulator past this command after navigating within the `./opengl-simulator` workspace:
```
python setup.py -build-depend -build-proj -run
```
