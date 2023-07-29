import numpy as np
from aStar import Map
from scipy.interpolate import CubicSpline as cs
from camera import MobileCamera
from control import *
cam = MobileCamera("http://192.168.0.117:1111/video")


class Box:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pos = [self.x, self.y]
        self.dest = None
        self.reachtime = np.inf

    def Dist(self, point):
        delX = self.x-point[0]
        delY = self.y-point[1]
        return np.sqrt(delX**2+delY**2)


class Bot:
    def __init__(self, id):
        self.id = id
        self.x, self.y, self.theta = self.getPos()
        self.pos = [self.x, self.y]
        self.x_prev = None
        self.y_prev = None
        self.theta_prev = None
        self.pos_prev = [self.x_prev, self.y_prev]
        self.box = None
        self.target = None
        self.path = None
        self.t = None
        self.reachedBox = False
        self.position = None
        self.dxdy = None
        self.speed = None
        self.omega = None

    def distFromBox(self, box):
        delX = self.x-box.x
        delY = self.y-box.y
        return np.sqrt(delX**2+delY**2)

    def distFromPoint(self, point):
        delX = self.x-point[0]
        delY = self.y-point[1]
        return np.sqrt(delX**2+delY**2)

    def assignBox(self, box):
        self.box = box
        self.target = box.dest

    def getPos(self):
        pos = None
        count=0
        while not pos:
            count+=1
            pos = cam.getPosOfID(self.id)
        print(pos,count)
        return pos

    def updatePos(self):
        self.x_prev = self.x
        self.y_prev = self.y
        self.theta_prev = self.theta
        self.pos_prev = [self.x_prev, self.y_prev]
        self.speed = self.distFromPoint(self.pos_prev)
        self.omega = self.theta - self.theta_prev
        self.x, self.y, self.theta = self.getPos()
        self.pos = [self.x, self.y]
        if self.distFromBox(self.box) <= 0.2:
            MagnetOn(self.id)
            self.reachedBox = True

        if self.distFromPoint(self.target) <= 0.2:
            MagnetOff(self.id)

        if self.reachedBox:
            self.box.x = self.x
            self.box.y = self.y
            self.box.pos = [self.x, self.y]

    def path2box(self, map, mapT):
        w, h = map.shape
        m = Map(w, h, map, self.pos, self.box.pos, mapT)
        path, t = m.getPath()
        self.box.reachtime = t[0]
        return path[::-1], t[::-1]

    def path2target(self, map, mapT, tStart):
        w, h = map.shape
        m = Map(w, h, map, self.box.pos, self.target, mapT, tStart)
        path, t = m.getPath()
        return path[::-1], t[::-1]

    def createPath(self, map, mapT):
        path1, t1 = self.path2box(map, mapT)
        path2, t2 = self.path2target(map, mapT, t1[-1])
        self.path = np.insert(path2, 0, path1[:-1], axis=0)
        self.t = np.insert(t2, 0, t1[:-1], axis=0)
        self.position = cs(self.t, self.path)
        self.dxdy = self.position.derivative(1)
        return self.path, self.t, t1[-1]

    def orientation(self, t):
        der = self.dxdy(t).reshape(-1, 2)
        return np.arctan2(der[:, 0], der[:, 1])*180/np.pi

    def returnPos(self, t):
        pt = self.position(t/10)
        self.updatePos(pt)
        return pt
