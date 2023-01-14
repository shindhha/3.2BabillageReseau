import socket
import Database
import Communicate
import signal
import threading as th
from FiableSocket import FiableSocket


# --- Informations relatives au pirate automatisée ---
# le pirate recevra les messages de seulement la première communication effectuée par 2 utilisateurs.
# Les autres communications ne seront pas reçues par le pirate. Pour que le pirate reçoit d'autres communications, il
# faut relancer le serveur et que 2 utilisateurs rentrent en communication.
pirate_active = True
pirate_ip = 'localhost'
pirate_port = 5001


def create_socket(ip: str, port: int) -> tuple[socket, int]:
    """
    Créé un socket UDP et la bind sur l'adresse et le port d'écoute
    :return: socket
    """

    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ok = False
    while not ok:
        try:
            sck.bind((ip, port))
            ok = True
        except socket.error as e:
            port = 0
            print('Erreur lors de la création du socket : ', e, '\n Le port d\'écoute est-t-il déjà utilisé ?')

    if ip == '':
        print('WARN : Le serveur écoute sur toutes les interfaces réseau !')
        # Liste de toutes les ip sur lesquelles le serveur écoute
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            print(' - ', ip + ':' + str(sck.getsockname()[1]))
    else:
        print("Serveur démarré sur", socket.gethostbyname(socket.gethostname()) + ':' + str(sck.getsockname()[1]))
    return sck, sck.getsockname()[1]


def stop_server(signum, frame):
    """
    Fonction appelée lors de la réception d'un signal d'arrêt du serveur
    :param signum: Le numéro du signal
    :param frame: Le frame du signal
    :return: None
    """
    print('Arrêt du serveur')
    Communicate.end = True
    fs.recv_queue.put((None, 'end')) # Débloque la fonction bloquante de Queue.get()

    fs.__del__()


if __name__ == "__main__":
    listening_ip: str = ''  # '' = all interfaces
    listening_port: int = 5000

    print('Démarrage du serveur... Appuyez sur Ctrl-C pour arrêter le serveur')
    signal.signal(signal.SIGINT, stop_server)  # Ctrl-C pour arrêter le serveur

    sck, listening_port = create_socket(listening_ip, listening_port)
    if sck is not None:
        # Initialisation des infos du pirate
        Communicate.pirate_fin = not pirate_active
        Communicate.addr = (pirate_ip, pirate_port)
        Communicate.pirate_users = [] if pirate_active else [None, None]

        Database.init_db()
        fs = FiableSocket(sck)
        recvthread = th.Thread(target=Communicate.recv, args=(fs,))
        recvthread.start()

        while not Communicate.end:
            # Permet de ne pas terminer le thread principal, responsable de l'arrêt du serveur (Ctrl+C)
            pass



