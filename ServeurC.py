import socket

class Communication:

    def _init_(self, comm, coord):
        self.comm = comm
        self.coord = coord

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
coordServeur = ('127.0.0.1',12345)
s.bind(coordServeur)
s.listen(2)

(commA,coordA) = s.accept()
A = Communication(commA, coordA)

(commB, coordB) = s.accept()
B = Communication(commB, coordB)

