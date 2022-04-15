# Sanam Nagvekar
# TCP Client/Server Example


''' 

Run this client python program from the
terminal using (python3 client.py) 

'''

import numpy as np
import cv2

import argparse
import asyncio

from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.signaling import TcpSocketSignaling, add_signaling_arguments, BYE

from multiprocessing import Process, Queue, Value


class TransportFrame(MediaStreamTrack):
    '''
    Frames from server are recieved and tramitted 
    using the MediaStream track.
    '''

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        '''Async recieves the frames'''
        frame = await self.track.recv()
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
            if obj.type == "offer":
                await pc.setLocalDescription(await pc.createAnswer())
                await signaling.send(pc.localDescription)
        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
        elif obj is BYE:
            print("Exiting")
            break

def ball_detection(queue, X, Y):
    '''
    Uses OpenCV to threshold and calculate the x and y
    coordinates of the ball. Also starts a multiprocessing
    queue to run OpenCV code.
    '''

    img = queue.get()
    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(grayscale, 127, 255, 0)
    M = cv2.moments(thresh)
    X.value = int(M["m10"] / M["m00"])
    Y.value = int(M["m01"] / M["m00"])

async def TransportTrack(pc, track):
    '''
    Images are sent to the process_a multiprocessing
    queue where the ball's coords are calculated.
    '''

    VideoStream = TransportFrame(track)
    dc = pc.createDataChannel('coords')

    X = Value('i', 0)
    Y = Value('i', 0)
    process_q = Queue()

    while(True):
        try:
            process_a = Process(target = ball_detection, args = (process_q, X, Y))
            process_a.start()
            frame = await VideoStream.recv()

            img = frame.to_ndarray(format="bgr24")
            cv2.imshow("Server generated stream", img)
            cv2.waitKey(1)
            process_q.put(img)
            process_a.join()
            dc.send("coords:" + str(X.value) + "," + str(Y.value))
        except Exception:
            pass


async def main(pc, signaling):
    '''
    Using aiortc to create an offer and accept an answer.
    This method runs ansyc and used TCPSocketSignaling.

    '''
    await signaling.connect()

    @pc.on("track")
    async def on_track(track):
        await TransportTrack(pc, track)

    @pc.on("datachannel")
    def on_datachannel(channel):
        print('Received from channel:',channel)

        @channel.on("message")
        def on_message(message):
            print('Message from channel ',channel, ":", message)

    await active(pc, signaling)


if __name__ == "__main__":
    print("Started Client Program")
    parser = argparse.ArgumentParser(description="Ball Position Detector - Client")

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
        loop.run_until_complete(cv2.destroyAllWindows())