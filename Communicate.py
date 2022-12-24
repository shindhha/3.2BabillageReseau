import Cryptage
from multiprocessing import Queue

status_list = ["idle", "createKey", "editKey"]
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
        print('Nouveau status : ' + status)
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

            elif status == 'editKey':
                process_edit_key(msg, client.temp_cle, client.cle)



        else:
            end = True
    print('process_msg terminé')


# -------- Fonctions de process des messages reçus par le serveur --------


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
    Traite les messages reçus par le serveur à propos de la création de la première clé et place les informations dans
    la file retour_infos (True si la clé a été crée, False sinon)

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


def process_edit_key(msg, nv_cle, ancienne_cle):
    """
    Traite les messages reçus par le serveur à propos de la modification de la clé et place les informations dans
    la file retour_infos (True si la clé a été modifiée, False sinon)

    INFO :
        Format du msg reçu : <Nom utilisateur, Nom de l’arbitre,T2>
        La clé est valide si ce message est reçu en étant chiffré avec notre nouvelle clé privée, si le message
        est chiffré avec l'ancienne clé, la clé n'a pas été acceptée par l'arbitre.

    :param msg: Le message de connexion
    :param nv_cle: La nouvelle clé saisie par l'utilisateur
    :param ancienne_cle: L'ancienne clé saisie par l'utilisateur
    :return: None
    """

    print('process_edit_key')

    decrypt_nv_cle = Cryptage.decrypter(msg, nv_cle).split(',')[-1]
    decrypt_ancienne_cle = Cryptage.decrypter(msg, ancienne_cle).split(',')[-1]

    if decrypt_ancienne_cle == 'T2':
        retour_infos.put(False)
    elif decrypt_nv_cle == 'T2':
        retour_infos.put(True)
    else:
        retour_infos.put(False)


# -------- Fonctions d'envoi de messages au serveur --------

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


def edit_key(client):
    """
    Permet d'envoyer au serveur le message de modification de clé.

    INFO :
        Format du msg envoyé : <Nom utilisateur, Nom de l’arbitre, Eold<T2, old clef privée de l’utilisateur, new clef privée>>

    :return: True si la clé a été modifiée, False sinon
    """
    set_status('editKey')
    nom_utilisateur = client.nom
    nom_arbitre = client.nom_arbitre

    cle = client.temp_cle
    cle_old = client.cle

    msg_crypt = "T2," + cle_old + "," + cle
    msg_crypt = Cryptage.crypter(msg_crypt, cle_old)

    msg = nom_utilisateur + ',' + nom_arbitre + ',' + msg_crypt
    client.socket.sendto(msg.encode(), client.addr_arbitre)

    return retour_infos.get()
