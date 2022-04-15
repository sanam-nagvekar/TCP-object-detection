import server
import pytest


def test_BallObject():
    ball = server.BallObject()

    assert ball.radius == 10
    assert ball.frameWidth == 500
    assert ball.frameHeight == 500


def test_TransportFrame():

    ball = server.BallObject()
    track = server.TransportFrame(ball)

    assert track.x == 50
    assert track.y == 400


def test_error_calculator():

    assert server.error_calculator(10,10,10,10) is None