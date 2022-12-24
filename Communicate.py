import Cryptage
from multiprocessing import Queue

status_list = ["idle", "createKey"]
status = "idle"

retour_infos = Queue()
"""
Permet au thread principal d'obtenir les informations que reçoient le thread de réception de messages
"""


def set_status(s):
    """
    Fonction qui modifie la variable globale status. L'objectif est de permettre au thread de réception de savoir
    quelles sont les actions a effectuer
    :param s: Le nouveau status
    :return: True si le changement a été effectué, False sinon
    """
    global status
    if s in status_list:
        status = s
    return s in status_list


def process_msg(queue, client):
    """
    Fonction qui s'occupe du traitement des messages reçues dans une file (multiprocess.Queue)
    :param queue: La file de réception
    :param client: L'objet client contenant toutes les informations nécessaires au traitement des messages
    :return: None
    """
    global status

    end = False
    while not end:
        msg = queue.get()
        server = queue.get()

        print('Message reçu : ' + msg)
        print('status : ' + status)

        if msg != 'end':
            process_errors(msg)

            if status == 'createKey':
                process_create_key(msg, client.temp_cle)



        else:
            end = True
    print('process_msg terminé')


def process_errors(msg):
    """
    Fonction qui traite les erreurs reçues par le serveur
    :param msg: Le message d'erreur
    :param server: Le serveur qui a envoyé le message
    :return: None
    """
    msg_split = msg.split(',')
    if msg_split[-1] == 'T0':
        print('Erreur: ' + msg)


def process_create_key(msg, cle):
    """
    Traite les messages de connexion reçus par le serveur et place les informations dans la file retour_infos
    (true si la connexion a réussi, false sinon)

    INFO :
        Format du msg reçu : <Nom de l’arbitre,Nom utilisateur, T1>
        La clé est valide si ce message est reçu en étant chiffré avec notre clé privée, sinon la clé n'a pas été
        acceptée par l'arbitre.

    :param msg: Le message de connexion
    :param cle: La clé saisie par l'utilisateur
    :return: None
    """

    print('process_create_key')
    crypte = msg.split(',')[-1]
    clair = Cryptage.decrypter(msg, cle).split(',')[-1]

    if crypte == 'T1':
        retour_infos.put(False)
    elif clair == 'T1':
        retour_infos.put(True)
    else:
        retour_infos.put(False)


def create_key(client):
    """
    Permet d'envoyer au serveur le message de création de clé.

    INFO :
        Format du msg envoyé : <Nom utilisateur, Nom de l’arbitre, T1, clef privé de l’utilisateur>

    :return: True si la clé a été créée, False sinon
    """
    set_status('createKey')
    nom_utilisateur = client.nom
    nom_arbitre = client.nom_arbitre
    cle = client.temp_cle

    msg = nom_utilisateur + ',' + nom_arbitre + ',T1,' + cle
    client.socket.sendto(msg.encode(), client.addr_arbitre)

    return retour_infos.get()
