import multiprocessing as mp
from zlib import crc32
import time
import threading as th

class FiableSocket:
    """
    Envoie un message puis attend l'ACK du message. Si le message est modifié lors de l'envoi, le destinataire ne renverra
    pas d'ACK, comme si le message était perdu.

    Si le client ne reçoit pas d'ACK, il renvoie le message.

    /!\ Tant que le client n'a pas reçu l'ACK, il ne peut pas passer au message suivant /!\

    L'échange est effectué de la manière suivante (cas No1) :

         Util 1                                  Util 2
            |                                       |
            |         Envoi d'un message            |
            |  ---------------------------------->  |
            |                                       |
            |         Envoi d'un ACK                |
            |  <----------------------------------  |
            |                                       |
            v                                       v



    En cas d'erreur (cas No2) :

         Util 1                                  Util 2
            |              Envoi d'un               |
            |       message (perdu / corrompu)      |
            | -/--/--/--/--/->                      |
            |                                       |
            |                                       |
            |              .  .  .                  |
            |                                       |
            |                                       |
            |         Envoi d'un message            |
            |  ---------------------------------->  |
            |                                       |
            |         Envoi d'un ACK                |
            |  <----------------------------------  |
            v                                       v


    (Cas No3) :
         Util 1                                  Util 2
            |                                       |
            |         Envoi d'un message            |
            |  ---------------------------------->  |
            |                                       |
            |            Envoi d'un ACK             |
            |          (corrompu / perdu)           |
            |                  <-\--\--\--\--\--\-  |
            |                                       |
            |                                       |
            |             .   .   .                 |
            |                                       |
            |                                       |
            |         Envoi d'un message            |
            |  ---------------------------------->  |
            |                                       |
            |         Envoi d'un ACK                |
            |  <----------------------------------  |
            v                                       v

    Ce cas pose un problème : Le serveur reçoit 2 fois le message, correctement transmis, et donc exécute 2 fois le même
    message.
    Pour régler ce problème, on créée donc dans le message un numéro, qui s'incrémente lorsque un nouveau message est
    envoyé. On le borne en 0 et 98, sachant que 99 est réservé pour les messages d'ACK.



    Le message est envoyé sous la forme suivante :
        - 8 caractères pour la clé de contrôle du message
        - 1 caractère pour le type (0 -> Message / 1 -> ACK)
        - 2 caractères pour vérifier si le message est identique a un message déjà arrivé (Voir cas 3)
        - Le message
    """
    def __init__(self, socket):
        self.socket = socket
        self.destinataire = ('localhost', 5000)

        self.attente_ack = False

        self.last_msg_send = ""
        self.msg_send_cpteur: int = 0

        self.send_queue = mp.Queue()
        self.recv_queue = mp.Queue()

        self.last_msg_recv: dict[tuple[str, int], str] = {}

        self.thread_run = True

        self.thread_send = th.Thread(target=self.threaded_send)
        self.thread_send.start()
        self.thread_recv = th.Thread(target=self.threaded_recv)
        self.thread_recv.start()


    def __del__(self):
        debug_print("Démarrage de la destruction de l'objet FiableSocket")
        self.thread_run = False
        self.attente_ack = False
        debug_print("Attente de la fin du thread d'envoi")
        try:
            self.socket.sendto(b"", ('127.0.0.1', self.socket.getsockname()[1]))
            debug_print("Envoi d'un message vide pour débloquer le thread d'envoi")
        except OSError as e:
            pass
        self.thread_send.join()
        self.thread_recv.join()
        debug_print("FiableSocket détruit")


    def get_cpteur(self):
        """
        :return: La variable compteur incrémentée de 1. Revient à zéro lorsqu'elle dépasse 98
        """
        cpt = self.msg_send_cpteur
        self.msg_send_cpteur = (self.msg_send_cpteur + 1) % 99
        return cpt

    def sendto(self, message: str, addr: tuple[str, int]):
        self.send_queue.put((addr, message))

    def threaded_send(self):
        """
        Gère l'envoi des messages ainsi que leur ré-envoi si le ACK n'est pas reçu
        """
        while self.thread_run:
            if not self.send_queue.empty() and not self.attente_ack:

                # Récupération & envoi du message
                addr, message = self.send_queue.get()
                self.last_msg_send = checksum_msg_encode(0, self.get_cpteur(), message)

                self.destinataire = addr
                self.socket.sendto(self.last_msg_send.encode(), addr)
                debug_print("Envoi du message : " + message)

                # Attente du ACK. Le message est renvoyé toutes les 2 secondes en cas de perte / dégradation
                self.attente_ack = True
                while self.attente_ack:
                    time.sleep(2)
                    if self.attente_ack:
                        self.socket.sendto(self.last_msg_send.encode(), addr)
                        debug_print("Ré-envoi du message : " + message)

        debug_print("Fin du thread d'envoi")


    def threaded_recv(self):
        """
        S'occupe de la réception des messages. Gère le décodage du message et la réception des ACK.
        /!\ Ignore les messages si leurs sommes de contrôle est invalide.
        /!\ Ignore les messages si ils ont déja été reçus (voir cas No3 dans la documentation de la classe)
        """
        while self.thread_run:

            # Récupération du message
            msg, addr = self.socket.recvfrom(1024)
            debug_print("Message reçu : " + msg.decode())
            msg = msg.decode()

            checksum, type_msg, cpteur, message = checksum_msg_decode(msg)
            debug_print("Checksum : " + str(checksum) + " / Type : " + str(type_msg) + " / Cpteur : " + str(cpteur) + " / Message : " + message)

            if type_msg == 0:
                # Réception d'un message
                # On vérifie si le message est bien intègre
                msg_ok = valider_checksum(checksum, type_msg, cpteur, message)

                if msg_ok:
                    debug_print(f"Message valide reçu : {checksum}-{type_msg}-{message}")
                    # Vérification si le message n'a pas déjà été reçu (Cas No3)
                    if addr not in self.last_msg_recv or self.last_msg_recv[addr] != msg:
                        self.last_msg_recv[addr] = msg

                        # Envoi du message sur la partie réception
                        self.recv_queue.put((addr, message))
                        debug_print(f"Message envoyé sur la queue : {checksum}-{type_msg}-{message}")

                    # On envoie l'ACK
                    self.socket.sendto(checksum_msg_encode(1, 99,'ACK').encode(), self.destinataire)
                    debug_print(f"Envoi de l'ACK : {checksum_msg_encode(1, 99,'ACK')}")

                else:
                    debug_print(f"Message corrompu reçu : {checksum}-{type_msg}-{cpteur}-{message}")

            if type_msg == 1:
                # Réception d'un ACK
                # On vérifie si le message est bien intègre
                msg_ok = valider_checksum(checksum, type_msg, cpteur, message)

                if msg_ok:
                    # On a reçu l'ACK du dernier message envoyé, on peut donc envoyer le prochain message
                    self.attente_ack = False
                    debug_print(f"Réception d'un ACK : {checksum}-{type_msg}-{message}")
                else:
                    debug_print(f"Réception ACK corrompu reçu : {checksum}-{type_msg}-{message}")

        debug_print("Fin du thread de réception")




def debug_print(msg):
    """
    Utilisé pour afficher tous les messages de débug de la classe FiableSocket avec horodatage
    :param msg: Le message à afficher sur la sortie standard
    """
    if True:
        heure = time.strftime("%H:%M:%S", time.localtime())
        print(f"[FiableSocket] - [{heure}] - {msg}")

def checksum_msg_encode(typemsg: int, msg_cpteur: int, msg: str) -> str:
    """
    Permet de générer un message avec sa somme de contrôle

    Format du message :
        Du caractère 1 à 8 :
            -> somme de contrôle CRC32 en valeur hexadécimale
        Caractère 9 :
            -> Le type du message (0 pour un message, 1 pour un ACK)
        Du caractère 10 à 11 :
            -> Valeur incrémentale sur 2 caractères
        Du caractère 12 à la fin :
            -> Le contenu du message

    :param typemsg: le type du message (0 ou 1)
    :param msg_cpteur: Valeur incrémentale permettant de différencier 2 messages qui ont un contenu identique
    :param msg: Le contenu du message à fiabiliser
    :return: Le message avec le protocole de fiabilisation
    """
    msg_concat = str(typemsg) + str(msg_cpteur).zfill(2) + msg
    checksum = crc32(msg_concat.encode())
    hex_checksum = hex(checksum)[2:].zfill(8)
    return hex_checksum + msg_concat

def checksum_msg_decode(msg: str) -> tuple[int, int, int,str]:
    """
    Permet d'extraire les informations d'un message fiabilisé avec la méthode checksum_msg_encode
    :param msg: La chaîne de caractère reçu dans laquelle les informations doivent être extraites
    :return: Un tuple contenant chacunes des informations (checksum, type_message, compteur, contenu_msg)
    """
    try:
        checksum = int(msg[:8], 16) # Conversion du checksum en int à partir de l'hexa (16)
        typemsg = int(msg[8])
        cpteur = int(msg[9:11])
        content = msg[11:]
    except ValueError:
        return 0, 0, 0, ""

    return checksum, typemsg, cpteur, content

def valider_checksum(checksum: int, typemsg: int, cpteur: int ,msg: str) -> bool:
    """
    Permet de valider la somme de contrôle d'un message dont les valeurs ont été extraites par la fonction
    checksum_msg_decode
    :param checksum: La comme du contrôle à vérifier sur le message
    :param typemsg: Le type du message
    :param cpteur: Le compteur incrémental appartenant au message
    :param msg: Le contenu du message
    :return: True si la somme de contrôle est correcte, False sinon
    """
    return checksum == crc32((str(typemsg) + str(cpteur).zfill(2) + msg).encode())
