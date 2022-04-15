# Sanam Nagvekar
# TCP Client/Server Example

''' 

Run this server python program from the
terminal using (python3 server.py) 

'''

import numpy as np
import cv2

import asyncio
import argparse

from av import VideoFrame
from aiortc import VideoStreamTrack, RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, MediaStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling, add_signaling_arguments, BYE

class BallObject():

    '''
    This class contains the properties of a ball objects. This includes
    aspects of the ball such as the color, radius, and movement.
    '''

    def __init__(self):

        ''' Initializes the properties of the ball and ball motion '''

        self.radius = 30
        self.color = (0, 225, 0)

        self.xPos = 50
        self.yPos = 400
        self.xVel = 10
        self.yVel = 10

        self.frameWidth = 500
        self.frameHeight = 500

    def hit_edge(self, frameEdge, x):

        '''
        This is used to check if the ball has touched
        the edge of the screen. Function returns true
        if the ball has touched the edge and returns 
        false otherwise.
        '''

        if (x >= frameEdge or x <= 0):
            return True
        return False

    def ball_movement(self):

        '''
        This method creates a a new image frame with the ball's
        current position. The method also generates the movement
        of the ball by incrementing its xPos and yPos. The method 
        (hit_edge) is also called to check if the ball has hit the
        frame's edge. If so, the ball's vel/movement is reversed. 
        '''

        # if (self.xPos >= frameWidth or self.xPos <= 0):
        #     self.xVel *= -1
        # if (self.yPos >= frameHeight or self.Pos <= 0):
        #     self.yVel *= -1

        if self.hit_edge(self.frameWidth, self.xPos):
            self.xVel *= -1
        if self.hit_edge(self.frameHeight, self.yPos):
            self.yVel *= -1

        self.xPos += self.xVel
        self.yPos += self.yVel

        img = np.zeros((self.frameHeight, self.frameWidth, 3), dtype = 'uint8')
        cv2.circle(img, (self.xPos, self.yPos), self.radius, self.color, -1)
        return (img, self.xPos, self.yPos)



class TransportFrame(VideoStreamTrack):
    '''
    This class uses aiortc frame transport to send images to 
    the client. The VideoStreamTrack class converts the ball 
    images into video frames that can be processed by the client.  
    '''

    def __init__(self, ball):
        ''' The ball's starting positions are initialized '''

        super().__init__()
        self.ball =  ball
        self.x = 50
        self.y = 400


    async def recv(self):
        ''' 
        Used VideoFrame instead of MediaStream. VideoFrame
        was well documented in the GitHub package. 
        '''

        pts, time_base = await self.next_timestamp()
        img, self.x, self.y = self.ball.ball_movement()
        frame = VideoFrame.from_ndarray(img, format = "bgr24")
        frame.pts = pts
        frame.time_base = time_base
        return frame


async def active(pc, signaling):
    '''
    This function keeps the communication between sever and client
    active. 
    '''

    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
        elif obj is BYE:
            print("Exiting")
            break


def error_calculator(xServ, yServ, xClient, yClient):
    ''' 
    Error between the server and client ball are calculated
    using distance formula. The server coords, client coords,
    and calculated errors are printed. 
    '''

    error = ( (yServ - yClient)**2 + (xServ - xClient)**2 )**(1/2)

    print("Server Ball Coordinates: " + str(xServ) + ", " + str(yServ))
    print("Client Ball Coordinates: " + str(xClient) + ", " + str(yClient))
    print("Error: " + str(error))

class ServerBall():
    '''
    I ran into errors with displaying the actual
    ball coordinates using the BallObject() class.
    This new class resolves the issues and is used
    to track the actual ball coordinates instead.
    '''

    def __init__(self):
        ''' Initialization of ball parameters '''
        self.xPos = 50
        self.yPos = 400
        self.xVel = 10
        self.yVel = 10

async def main(pc, signaling):
    '''
    Using aiortc to create an offer for the client.
    This method runs ansyc and used TCPSocketSignaling.
    '''
    
    ball = BallObject()
    ballServer = ServerBall()
    track = TransportFrame(ball)

    await signaling.connect()
    pc.createDataChannel('chat')

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        async def on_message(message):
            ''' Recieves client message and displays the coordinates and error'''


            if (ballServer.xPos >= 500 or ballServer.xPos <= 0):
                ballServer.xVel *= -1
            if (ballServer.yPos >= 500 or ballServer.yPos <= 0):
                ballServer.yVel *= -1

            ballServer.xPos += ballServer.xVel
            ballServer.yPos += ballServer.yVel

            if (message.startswith("coords")):
                clientPos = message[7:].split(",")
                error_calculator(ballServer.xPos, ballServer.yPos, int(clientPos[0]), int(clientPos[1]))

    pc.addTrack(track)
    await pc.setLocalDescription(await pc.createOffer())
    await signaling.send(pc.localDescription)
    await active(pc, signaling)


if __name__ == "__main__":

    print("Started Server Program")
    parser = argparse.ArgumentParser(description="Ball Position Detector - Server")
    add_signaling_arguments(parser)
    args = parser.parse_args()
    signaling = TcpSocketSignaling(args.signaling_host, args.signaling_port)
    pc = RTCPeerConnection()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            main(pc, signaling)
        )
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(signaling.close())
        loop.run_until_complete(pc.close())
