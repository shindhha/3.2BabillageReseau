import Cryptage
from multiprocessing import Queue

status_list = ["idle", "createKey", "editKey", "deleteKey", "initDialog", "waitAccept", "discuss"]
status = "idle"

retour_infos = Queue()
"""
Permet au thread principal d'obtenir les informations sur les messages que le thread de réception a recueillis
"""


def set_status(s):
    """
    Fonction qui modifie la variable globale status. L'objectif est de permettre au thread de réception de savoir
    quelles sont les actions à effectuer
    :param s: Le nouveau status
    :return: True si le changement a été effectué, False sinon.
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
        addr, msg = queue.get()

        print('Message reçu : ' + msg)
        print('status : ' + status)


        if msg != 'end':
            msg_traite = process_demande_dialog(msg, client)

            if status == 'createKey':
                msg_traite |= process_create_key(msg, client.temp_cle)

            elif status == 'editKey':
                msg_traite |= process_edit_key(msg, client.temp_cle, client.cle)

            elif status == 'deleteKey':
                msg_traite |= process_delete_key(msg, client.cle)

            elif status == 'initDialog':
                msg_traite |= process_init_dialog(msg, client)

            elif status == 'waitAccept':
                process_accept_refuse_dialog(msg, client)

            elif status == 'discuss':
                process_discuss(msg, client)

            # On log les messages si on est pas encore dans la fenêtre de discussion mais qu'un échange a voulu être
            # démarré par un autre utilisateur
            if not msg_traite and status != status_list[-1] and client.ks is not None:
                msg_decrypt = Cryptage.decrypter(msg, client.ks)
                client.msg_attente.append(msg_decrypt)

        else:
            end = True
    print('process_msg terminé')


# -------- Fonctions de process des messages reçus par le serveur --------
def process_create_key(msg, cle):
    """
    Traite les messages reçus par le serveur à propos de la création de la première clé et place les informations dans
    la file retour_infos (True si la clé a été crée, False sinon)

    INFO :
        Format du msg reçu : <Nom de l’arbitre,Nom utilisateur, T1>
        La clé est valide si ce message est reçu en étant chiffré avec notre clé privée, sinon la clé n'a pas été
        acceptée par l'arbitre.

    :param msg: Le message reçus par le serveur
    :param cle: La clé saisie par l'utilisateur
    :return: True si le message a été traité par cette fonction, False sinon
    """
    traite = False

    if cle is not None:
        print('process_create_key')
        crypte = msg.split(',')[-1]
        clair = Cryptage.decrypter(msg, cle).split(',')[-1]

        if crypte == 'T1':
            retour_infos.put(False)
            traite = True
        elif clair == 'T1':
            retour_infos.put(True)
            traite = True
        else:
            retour_infos.put(False)

    set_status('idle')

    return traite


def process_edit_key(msg, nv_cle, ancienne_cle):
    """
    Traite les messages reçus par le serveur à propos de la modification de la clé et place les informations dans
    la file retour_infos (True si la clé a été modifiée, False sinon)

    INFO :
        Format du msg reçu : <Nom utilisateur, Nom de l’arbitre,T2>
        La clé est valide si ce message est reçu en étant chiffré avec notre nouvelle clé privée, si le message
        est chiffré avec l'ancienne clé, la clé n'a pas été acceptée par l'arbitre.

    :param msg: Le message reçu par le serveur
    :param nv_cle: La nouvelle clé saisie par l'utilisateur
    :param ancienne_cle: L'ancienne clé saisie par l'utilisateur
    :return: True si le message a été traité par cette fonction, False sinon
    """
    traite = False

    print('process_edit_key')

    if nv_cle is not None and ancienne_cle is not None:
        decrypt_nv_cle = Cryptage.decrypter(msg, nv_cle).split(',')[-1]
        decrypt_ancienne_cle = Cryptage.decrypter(msg, ancienne_cle).split(',')[-1]

        if decrypt_ancienne_cle == 'T2':
            retour_infos.put(False)
            traite = True
        elif decrypt_nv_cle == 'T2':
            retour_infos.put(True)
            traite = True
        else:
            retour_infos.put(False)

    set_status('idle')

    return traite

def process_delete_key(msg, cle):
    """
    Traite les messages reçus par le serveur à propos de la suppression de la clé et place les informations dans
    la file retour_infos (True si la clé a été supprimée, False sinon)

    INFO :
        Format du message de succès : Eclef <Nom de l’arbitre, Nom utilisateur, T3>
        Format du message d’échec : Eclef <Nom de l’arbitre, Nom utilisateur>

    :param msg: Le message reçu par le serveur
    :param cle: La clé saisie par l'utilisateur
    :return: True si le message a été traité par cette fonction, False sinon
    """
    traite = False
    print('process_delete_key')

    decrypt_cle = Cryptage.decrypter(msg, cle).split(',')[-1]

    if decrypt_cle == 'T3':
        retour_infos.put(True)
        traite = True
    else:
        retour_infos.put(False)

    set_status('idle')

    return traite


def process_init_dialog(msg, client):
    """
    Traite les messages reçus par le serveur durant la phase d'initialisation du dialogue et s'occupe de l'envoi de ks à B

    INFO :
        Format du message reçu : Eclef_A<Nom de l’arbitre, Nom utilisateur A, T4, Ks, Eclef_B<Nom de l’arbitre, Nom utilisateur A, Nom utilisateur B, Ks>>
        Si utilisateur B n'as pas été trouvé, le message reçu est : Eclef_A<Nom de l’arbitre, Nom utilisateur A, T4>

        Format du message à envoyer a B : Eclef_B<Nom de l’arbitre, Nom utilisateur A, Nom utilisateur B, Ks>

    :param msg: Le message reçu par le serveur
    :param cle: La clé de l'utilisateur
    :param socket: Le socket à utiliser pour envoyer le message vers l'utilisateur B
    :return: true si le message a été traité, false sinon
    """
    traite = False

    print('process_init_dialog')
    cle = client.cle

    decrypt_msg = Cryptage.decrypter(msg, cle)
    msg_split = decrypt_msg.split(',')

    if len(msg_split) == 3 and msg_split[-1] == 'T4':
        retour_infos.put(False)
        traite = True
    elif len(msg_split) >= 4 and msg_split[2] == 'T4':
        ks = msg_split[3]
        client.ks = ks

        position_fin_ks = decrypt_msg.find(ks) + len(ks) + 1
        partie_a_envoyer = decrypt_msg[position_fin_ks:]

        set_status('waitAccept')
        client.fiable_socket.sendto(partie_a_envoyer, client.addr_arbitre)

        retour_infos.put(True)
        traite = True
        #set_status('idle')
    return traite
        
        
def process_demande_dialog(msg, client):
    """
    Traite le message de demande de communication émis par l'utilisateur A vers B (nous)
    (C'est la 2° partie du message T4 que reçoit A par le serveur)
    + Fais clignoter le bouton communiquer de l'interface graphique pour indiquer à l'utilisateur qu'il a une
    demande de communication

    INFO :
        Format du message reçu : Eclef_B<Nom de l’arbitre, Nom utilisateur A, Nom utilisateur B, Ks>>

    :param msg: Le message reçu de A
    :param client: L'objet utilisateur contenant les informations de l'utilisateur B
    :param emetteur: Les coordonnées (IP, PORT) de l'utilisateur A
    :return: True si le message a été traité, false sinon
    """
    traite = False

    cle = client.cle
    nom_client = client.nom
    nom_arbitre = client.nom_arbitre

    print("DEBUG :", cle, nom_client, nom_arbitre)

    if cle is not None and nom_client is not None and nom_arbitre is not None:
        decrypt_msg = Cryptage.decrypter(msg, cle)
        msg_split = decrypt_msg.split(',')

        if len(msg_split) == 4:
            if msg_split[2] == nom_client and msg_split[0] == nom_arbitre:
                client.nom_destinataire = msg_split[1]
                client.ks = msg_split[3]
                client.demande_connexion = True
                try:
                    client.main_menu.update_conn_btn()
                except Exception:  # Exception levée si la fenêtre principale n'est pas ouverte
                    pass
            traite = True
    return traite


def process_accept_refuse_dialog(msg, client):
    """
    Traite le message de réponse à la demande de communication émise par l'utilisateur B vers A (nous)
    S'occupe de fermer la fenêtre de dialogue qui attend si la réponse est négative, ou s'occupe de dé-geler la fenêtre
    de communication si la réponse est positive

    INFO :
        Format du msg envoyé si comm accepté : EKs<Nom utilisateur B, Nom utilisateur A,T5>.
        Format du msg envoyé si comm refusé : EKs<T5, Nom utilisateur B, Nom utilisateur A>.

    NB : Le message de refus n'es pas dans le sujet.

    :param msg: Le message reçu de B
    :param client: L'objet utilisateur contenant les informations de l'utilisateur A
    :return: None
    """
    cle = client.ks

    if cle is not None:
        decrypt_msg = Cryptage.decrypter(msg, cle)
        if client.communication_window is not None:
            if decrypt_msg[-2:] == 'T5':
                client.communication_window.show_welcome_text()
                client.communication_window.enable_communication()
                set_status('discuss')
            else:
                client.communication_window.queue_recv.put("A refuse la demande de communication")
                set_status('idle')

def process_discuss(msg, client):
    """
    Traite les messages reçus par le serveur durant la phase de discussion et place les nouveaux messages dans la file
    de la fenêtre de discussion (DiscussWindow.queue_recv)
    :param msg: Le message reçu par le serveur
    :param client: L'objet utilisateur contenant les informations de l'utilisateur
    :return: None
    """

    if client.communication_window is not None:
        cle = client.ks

        msg_decrypt = Cryptage.decrypter(msg, cle)
        client.communication_window.queue_recv.put(msg_decrypt)


# -------- Fonctions d'envoi de messages au serveur / client B --------

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
    client.fiable_socket.sendto(msg, client.addr_arbitre)

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
    client.fiable_socket.sendto(msg, client.addr_arbitre)

    return retour_infos.get()


def delete_key(client):
    """
    Permet d'envoyer au serveur le message de suppression de clé.

    INFO :
        Format du msg envoyé : < Nom utilisateur, Nom de l’arbitre, Eclef <T3,clef privée>>.

    :return: True si la clé a été supprimée, False sinon
    """
    set_status('deleteKey')
    nom_utilisateur = client.nom
    nom_arbitre = client.nom_arbitre
    cle = client.cle

    msg_crypt = "T3," + cle
    msg_crypt = Cryptage.crypter(msg_crypt, cle)

    msg = nom_utilisateur + ',' + nom_arbitre + ',' + msg_crypt
    client.fiable_socket.sendto(msg, client.addr_arbitre)

    return retour_infos.get()


def demander_ks(client):
    """
    Permet d'envoyer au serveur le message de demande de dialogue avec un autre client.

    INFO :
        Format du msg envoyé : Eclef< Nom de l’utilisateur A, Nom de l’arbitre, Nom de l’utilisateur B, T4>.

    :return: True si l'arbitre est OK avec la demande, False sinon
    """
    set_status('initDialog')
    cle = client.cle
    nom_utilisateur = client.nom
    nom_arbitre = client.nom_arbitre
    nom_destinataire = client.nom_destinataire

    msg_crypt = nom_utilisateur + ',' + nom_arbitre + ',' + nom_destinataire + ',T4'
    msg_crypt = Cryptage.crypter(msg_crypt, cle)
    client.fiable_socket.sendto(msg_crypt, client.addr_arbitre)

    return retour_infos.get()


def accepter_refuser_dialogue(client, accepter):
    """
    Permet de déclarer à l'autre client si on accepte ou non sa demande de dialogue.

    INFO :
        Dans ce cas-là, nous sommes l'utilisateur B
        Format du msg envoyé si on accepte : EKs<Nom utilisateur B, Nom utilisateur A,T5>.
        Format du msg envoyé si on refuse : EKs<T5, Nom utilisateur B, Nom utilisateur A>.
    :param client: L'objet Utilisateur contenant les informations du client
    :param accepter: Booléen indiquant si on accepte ou non la demande de dialogue
    :return: None
    """

    nom_utilisateur = client.nom
    nom_destinataire = client.nom_destinataire
    cle = client.cle
    ks = client.ks

    msg_base = nom_utilisateur + ',' + nom_destinataire
    if accepter:
        msg_crypt = msg_base + ',T5'
    else:
        msg_crypt = 'T5,' + msg_base

    msg_crypt = Cryptage.crypter(msg_crypt, ks)
    client.fiable_socket.sendto(msg_crypt, client.addr_arbitre)


def envoyer_message(client, message):
    """
    Permet d'envoyer un message à notre destinataire.
    :param client: L'objet utilisateur contenat les informations de l'utilisateur
    :param message: Le message à envoyer a B
    :return: None
    """
    cle = client.ks

    msg_crypt = Cryptage.crypter(message, cle)

    client.fiable_socket.sendto(msg_crypt, client.addr_arbitre)
