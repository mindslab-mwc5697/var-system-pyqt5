import json
import os
from multiprocessing import shared_memory

import cv2
import numpy
import redis


class Client:
    def __init__(self):
        self.redisDB = redis.Redis(host='localhost', port=6379, db=0)
        self.sharedFrames = []
        self._cachedShmTime = []
        self._shms = []
        self.redisDB.hdel("var", "face")
        self.redisDB.hdel("var", "object")
        self.redisDB.hdel("var", "result")
        self._createSharedMemory()

    def _createSharedMemory(self):
        for i in range(4):
            if os.path.exists(f"/dev/shm/channel_{i}"):
                shm = shared_memory.SharedMemory(size=numpy.prod((360, 640, 3))
                                                      * numpy.dtype(numpy.uint8).itemsize,
                                                 name=f"channel_{i}")
                shmFrame = numpy.ndarray((360, 640, 3), dtype=numpy.uint8, buffer=shm.buf)
                self.sharedFrames.append(shmFrame)
                self._shms.append(shm)

    def _update(self):
        for i in range(4):
            if os.path.exists(f"/dev/shm/channel_{i}"):
                shm = shared_memory.SharedMemory(size=numpy.prod((360, 640, 3))
                                                      * numpy.dtype(numpy.uint8).itemsize,
                                                 name=f"channel_{i}")
                shmFrame = numpy.ndarray((360, 640, 3), dtype=numpy.uint8, buffer=shm.buf)
                self.sharedFrames[i] = shmFrame
                self._shms[i] = shm

    def recv(self):
        metaInfo = self.redisDB.hget("var", "result")
        if metaInfo is not None:
            try:
                metaInfo = json.loads(metaInfo)
            except json.JSONDecodeError as e:
                metaInfo = None
        else:
            metaInfo = {
                "action": [""],
                "area": [""],
                "regi": [""],
                "time": "",
            }

        self._update()
        frames = [frame.copy() for frame in self.sharedFrames]

        faceImg = self.redisDB.hget("var", "face")
        objImg = self.redisDB.hget("var", "object")
        faceImg = numpy.zeros((360, 360, 3), dtype=numpy.uint8) if faceImg is None \
                              else numpy.reshape(numpy.frombuffer(faceImg, dtype=numpy.uint8), (360, 360, 3))
        objImg = numpy.zeros((360, 360, 3), dtype=numpy.uint8) if objImg is None \
            else numpy.reshape(numpy.frombuffer(objImg, dtype=numpy.uint8), (360, 360, 3))
        frames.append(faceImg)
        frames.append(objImg)
        return frames, metaInfo