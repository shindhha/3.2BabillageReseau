import socket
import Database
import Communicate
import signal
import threading as th


listening_ip: str = ''  # '' = all interfaces
listening_port: int = 5000

def create_socket():
    """
    Créé un socket UDP et la bind sur l'adresse et le port d'écoute
    :return: socket
    """
    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sck.bind((listening_ip, listening_port))
    except socket.error as e:
        print('Erreur lors de la création du socket : ', e, '\n Le port d\'écoute est-t-il déjà utilisé ?')
        return None

    if listening_ip == '':
        print('WARN : Le serveur écoute sur toutes les interfaces réseau !')
        # Liste de toutes les ip sur lesquelles le serveur écoute
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            print(' - ', ip + ':' + str(listening_port))
    else:
        print("Serveur démarré sur", socket.gethostbyname(socket.gethostname()) + ':' + str(listening_port))
    return sck


def stop_server(signum, frame):
    """
    Fonction appelée lors de la réception d'un signal d'arrêt du serveur
    :param signum: Le numéro du signal
    :param frame: Le frame du signal
    :return: None
    """
    print('Arrêt du serveur')
    Communicate.end = True

    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sck.sendto(b'end', ('localhost', listening_port))  # Envoi d'un message pour débloquer recvfrom


if __name__ == "__main__":
    print('Démarrage du serveur... Appuyez sur Ctrl-C pour arrêter le serveur')
    signal.signal(signal.SIGINT, stop_server)  # Ctrl-C pour arrêter le serveur

    sck = create_socket()
    if sck is not None:
        Database.init_db()
        recvthread = th.Thread(target=Communicate.recv, args=(sck,))
        recvthread.start()

        while not Communicate.end:
            # Permet de ne pas terminer le thread principal, responsable de l'arrêt du serveur (Ctrl+C)
            pass



