This Kubernetes (minikube) project uses TCP to send video streams between a client and server for object detection.
The directory contains a server.py file and a client.py file along with their docker containers.

The server.py file runs a server that generates a ball bouncing animation in a 500 by 500 frame. The server sends the video stram to the client using aiortc TCPSocketSignlaing. The server can be run as follows:

Usage:

    python3 server.py
    
The client.py file recives ball frames from the server and calculates the coordinates of the ball using OpenCV thresholding. These OpenCV calculations are conducted in separate multiprocessing queue. These "estimated" coordinates are then sent back to the server where the error between actual and estimated positions are presented. The client can be run as follows.

Usage:

    python3 client.py

Additionally, a demo video, docker containers, and unit tests are provided.

