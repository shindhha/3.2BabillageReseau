import socket

nom = 'A'
nomArbitre = 'C'


def t1(clef):
    message = nom + ',' + nomArbitre + ',T1,' + clef
    return message





s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

coord_S = ('127.0.0.1', 12345)

nouvelleClef = input('entrez la clef: ')

s.sendto(t1(nouvelleClef).encode(), coord_S)

(reponse, coord_S) = s.recvfrom(1024)

print(reponse.decode())