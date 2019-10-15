# VR_project

Course: Virtual Reality Engineering | Guide: Prof. Manivannan M.

VR Project is the directory for Unity Project (containg TCP server and Object controller codes)
CNN directory contains the Tensorflow frameworks for CNN model and python codes for real time USB camera codes.

Specifications:
Unity project should be run on computer with Unity installed computer (any compatible OS)
Python code will only work in Ubuntu OS with Tensorflow, Python3, OpenCV and CUDA support for GPUs installed and any other dependencies. Preferably a computer with high end NVIDIA GPUs would be required for good performance.

In ubuntu terminal move to /CNN/src directory from home using:
 cd ~/CNN/src
To run the real time USB code with left camera and right camera devices numbered as 1 and 2
python3 stereoTracking.py --cameraF=1 --cameraS=2

First run the Unity server by clicking the run button in Unity IDE.
Then run the python code in Ubuntu which will initiate the python client. 

Note: 
1) Please ensure you are in front of the camera before running the python code so as to register your initial position as origin. 
2) Please ensure both computers are in the same network for TCP socket connections and change the port and IP address accordingly
