import json
import multiprocessing
import select
import socket


class Report(multiprocessing.Process):
    def __init__(self, recvQueue):
        super(Report, self).__init__()
        self.recvQueue = recvQueue
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind(('', 1235))
        serverSocket.listen(1)
        serverSocket.settimeout(1)
        self.serverSocket = serverSocket

    def toBytes(self, frames, metaInfo):
        ret, data = None, {}
        for i, frame in enumerate(frames):
            data[f"channel_{i}"] = frame.tolist()
            data["meta"] = metaInfo
            ret = json.dumps(data).encode('utf-8')
        return ret

    def run(self) -> None:
        super(Report, self).run()
        # select 함수에서 관찰될 소켓 리스트 설정
        sockets = [self.serverSocket]
        # clientSocket, address = self.serverSocket.accept()
        accepted = []

        while True:
            frames, metaInfo = self.recvQueue.get()
            for socket in sockets:
                readReady, writeReady, notReady = select.select(sockets, [], [])
                if socket == self.serverSocket:
                    try:
                        client, address, = socket.accept()
                        print(address, 'is connected', flush=True)
                        accepted.append(address[0])
                        sockets.append(client)
                    except BlockingIOError as e:
                        pass
                else:
                    try:
                        data = self.toBytes(frames, metaInfo)
                        ret = socket.send(data)
                        print(f"REPORT TO {address} : {ret}")
                    except BrokenPipeError as e:
                        pass
                    except ConnectionResetError as e:
                        pass
