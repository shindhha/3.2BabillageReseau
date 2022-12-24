import socket


def creer_socket():
    """
    Créer une socket UDP + bind pour recevoir directement des infos
    :return: socket
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 0)) # Bind sur le port 0 pour que le système choisisse un port libre
    return sock