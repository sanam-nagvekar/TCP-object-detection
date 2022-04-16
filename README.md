## TCP Client-Server for Object Detection with Minikube Deployment

This Kubernetes (minikube) project uses TCP to send video streams between a client and server for object detection.
The directory contains a server.py file and a client.py file along with their docker containers.  


### Server

The server.py file uses TCP Socket Signaling to run a server that generates and exports a video stream. Specifically, the server uses OpenCV to generate a ball bouncing animation in a 500 by 500 frame. The `BallObject()` class contains the properties of the video frame and ball animation -- properties include initial positions, ball and frame dimensions, ball velocity, and more. Furthermore, the class' method `ball_movement()` is used to check if the ball hits the edge of the frame and to animate the ball's movement. The `TransportFrame()` class uses aiortc frame transport to send images to the client. Furthermore the class converts the ball images into video frames that can be processed by the client. The server can be run from the terminal as follows:

    python3 server.py    

### Client
The client.py file recives ball frames from the server and calculates the coordinates of the ball using OpenCV thresholding. These OpenCV calculations are conducted in a separate multiprocessing queue which is generated in the `TransportTrack()` method. The x-position and y-position of the ball (estimated coordinates) are then sent back to the server through the client `TransportFrame()` class. The server then uses the distance formula to calculate and print the error between the actual (server-side) and estimated (client-side) ball coordinates. The client can be run as follows:

    python3 client.py

### Docker and Kubernetes Minikube
Docker files for the server and client have been created and are stored in `server_docker` and `client_docker` folders respectively. Futhermore, Kubernetes minikube is used to create a local deployment of the client/server system. Note that a `server_test.py` has been provided to conduct pytest unit tests for the functions contained `server.py`. Lastly, a demo of the client/server system in action is presented in the `client-server-demo.mp4` file.

