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
        self._shms = []
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


    def recv(self):
        metaInfo = self.redisDB.hget("var", "result")
        if metaInfo is not None:
            try:
                metaInfo = json.loads(metaInfo)
            except json.JSONDecodeError as e:
                metaInfo = None
        frames = [frame.copy() for frame in self.sharedFrames]
        return frames, metaInfo