import queue

import Windows
import Utils
import Communicate
from Cryptage import cleOk
import threading as th
from SimpleReceiver import SimpleReceiver
from FiableSocket import FiableSocket
import socket
import re


class Utilisateur:
    def __init__(self, fiable_socket: FiableSocket):
        self.fiable_socket: FiableSocket = fiable_socket
        self._process_msg = th.Thread(target=Communicate.process_msg, args=(self.fiable_socket.recv_queue, self))
        self._process_msg.start()

        # --- Informations relatives à l'utilisateur ---
        self.cle = None
        self.temp_cle = None  # Contient la clé durant la phase de validation de la clé par l'arbitre
        self.nom = None

        # --- Informations relatives à l'arbitre ---
        self.nom_arbitre = 'C'
        self.addr_arbitre = ('localhost', 5000)

        # --- Informations relatives à la communication avec un tiers ---
        self.nom_destinataire = None
        self.ks = None

        # --- Informations relatives au menu principal ---
        self.main_menu = None
        self.demande_connexion = False

        # --- Informations relatives a la fenêtre de communication ---
        self.communication_window = None
        self.msg_attente = []

    def __del__(self):
        self.fiable_socket.recv_queue.put((None, 'end'))
        self.fiable_socket.__del__()



# ------------------ Main ------------------


def connexion():
    """
    Permet à l'utilisateur d'entrer son nom d'utilisateur
    :return:
    """
    fenetre = Windows.ConnectWindow()
    name = fenetre.show()
    return name


def menu_principal(client, msg_info, couleur):
    """
    Fonction qui affiche la fenêtre principale de l'application
    :return:
    """
    client.main_menu = Windows.Menu(client, msg_info, couleur)
    action = client.main_menu.show()
    client.main_menu = None
    return action


def message_erreur(msg):
    """
    Affiche une fenêtre d'erreur
    :param msg: Le message d'erreur
    :return: None
    """
    fenetre = Windows.ErrorWindow(msg)
    fenetre.show()


def creation_cle(update=False):
    """
    Affiche la fenêtre permettant de créer une clé
    :param update: Si True, la fenêtre est utilisée pour modifier une clé existante
    :return: True si la clé a été créée, None sinon
    """

    end = False
    retour = None
    while not end:

        # Affichage de la fenêtre de saisie de la clé
        if update:
            fenetre = Windows.SimpleInputWindow('Modifier votre clé', 'Entrez votre nouvelle clé :')
        else:
            fenetre = Windows.SimpleInputWindow('Créer votre clé', 'Entrez votre clé :')
        cle = fenetre.show()

        if cle is None:  # Si l'utilisateur a cliqué sur Annuler
            end = True
        else:  # Traitement de la clé saisie
            if not cleOk(cle) or len(cle) == 0:
                message_erreur('La clé saisie est invalide')
            else:
                # La clé est valide, envoi au serveur
                utilisateur.temp_cle = cle
                if not update:
                    arbitre_ok = Communicate.create_key(utilisateur)
                else:
                    arbitre_ok = Communicate.edit_key(utilisateur)
                print("Réponse de l'arbitre : ", arbitre_ok)
                if arbitre_ok:
                    utilisateur.cle = cle
                    utilisateur.temp_cle = None
                    end = True
                    retour = True
                else:
                    message_erreur("L'arbitre a refusé la clé")
    return retour


def supression_cle():
    """
    Fonction qui permet de supprimer la clé de l'utilisateur
    :return: True si la clé a été supprimée, None sinon
    """

    code_retour = Communicate.delete_key(utilisateur)
    if code_retour:
        utilisateur.cle = None
        return True
    else:
        Windows.ErrorWindow('La clé n\'a pas pu être supprimée').show()


def demarrer_communication_initialisateur():
    """
    Permet de démarrer la communication avec un tiers en tant qu'initialisateur
    :return: None si la communication a été démarrée, sinon une chaine de caractère indiquant l'erreur
    """

    erreur = None

    # Demande du nom du destinataire
    fenetre = Windows.SimpleInputWindow('Communiquer', 'Entrez le nom du destinataire :')
    nom_destinataire = fenetre.show()
    if nom_destinataire is not None and len(nom_destinataire) > 0:
        utilisateur.nom_destinataire = nom_destinataire
    else:
        erreur = 'Nom du destinataire invalide'

    if erreur is None:
        if Communicate.demander_ks(utilisateur):
            # L'arbitre a accepté la demande, on affiche la fenêtre de communication pendant que l'utilisateur B
            # accepte la demande
            utilisateur.communication_window = Windows.DiscussWindow(utilisateur)
            utilisateur.communication_window.show_waiting_text()
            a_communique = utilisateur.communication_window.show()

            utilisateur.communication_window = None
            utilisateur.ks = None
        else:
            erreur = 'L\'arbitre a refusé la demande'

    return erreur


def rejoindre_communication():
    """
    Permet de rejoindre une communication qui a été initialisée par un autre utilisateur
    :return: None
    """
    Communicate.set_status('discuss')
    utilisateur.communication_window = Windows.DiscussWindow(utilisateur)
    utilisateur.communication_window.show_welcome_text()
    utilisateur.communication_window.enable_communication()
    utilisateur.communication_window.show()

    utilisateur.communication_window = None
    utilisateur.ks = None
    Communicate.set_status('idle')


def accepter_refuser_demande():
    """
    Affiche la fenêtre permettant à l'utilisateur de répondre à une demande de communication
    :return: True si l'utilisateur a accepté la demande, False sinon
    """
    fenetre = Windows.YesNoWindow('Demande de communication', 'Accepter la demande de communication emise par '
                                  + utilisateur.nom_destinataire + ' ?')
    return fenetre.show()


def actions():
    """
    Fonction qui gère les actions de l'utilisateur effectuées depuis la fenêtre principale
    :return:
    """
    end = False
    msg_info = ''
    couleur = 'green'
    while not end:
        action = menu_principal(utilisateur, msg_info, couleur)
        msg_info = ''

        if action == 'quit':
            end = True

        elif action == 'createKey':
            print('Création de la clé')
            if creation_cle():
                msg_info = 'INFO : Clé créée avec succès'
                couleur = 'green'


        elif action == 'editKey':
            print('Modification de la clé')
            if creation_cle(update=True):
                msg_info = 'INFO : Clé modifiée avec succès'
                couleur = 'green'

        elif action == 'delKey':
            print('Suppression de la clé')
            if supression_cle():
                msg_info = 'INFO : Clé supprimée avec succès'
                couleur = 'green'

        elif action == 'communiquer':
            print('Communiquer')
            if utilisateur.demande_connexion:
                demande_ok = Windows.YesNoWindow('Demande de communication',
                                                 'Accepter la demande de communication de '
                                                 + utilisateur.nom_destinataire + ' ?').show()
                Communicate.accepter_refuser_dialogue(utilisateur, demande_ok)
                if demande_ok:
                    rejoindre_communication()

                utilisateur.demande_connexion = False

            else:
                erreur = demarrer_communication_initialisateur()
                if erreur is not None:
                    msg_info = 'ERREUR : ' + erreur
                    couleur = 'red'

        else:
            print('Action inconnue')


def ask_ip(sck: FiableSocket) -> tuple[str, int] | tuple["False", int] :
    """
    Permet de demander l'ip et le port de l'arbitre et de tester le bind de la socket au serveur
    :return: Si IP et PORT correctent alors on renvoie un tuple avec l'ip et le port
             sinon on renvoie un tuple avec "False" et le port
    """

    ipRgx = re.compile(r"^((1?[0-9]{1,2}|2[0-4][0-9]|25[0-5]).){3}(1?[0-9]{1,2}|2[0-4][0-9]|25[0-5])$|^localhost$")

    tentative = 0
    ip = "False"
    port = 5000
    while not ipRgx.match(ip):
        ipport = Windows.SimpleInputWindow('Saisie des coordonnées',
                                           'Entrez l\'ip et le port de l\'arbitre \n(IP:PORT, port facultatif)').show()
        if ipport is not None:
            if ipport.find(':') != -1:
                ip, port = ipport.split(':')
                try:
                    port = int(port)
                    ok = True
                except ValueError:
                    tentative += 1
                    ok = False
            else:
                ip = ipport
                port = 5000
                ok = True

        # Test si trop de tentatives effectuée
        if tentative == 5:
            ip = "False"
            Windows.ErrorWindow('Trop de tentatives effectuées').show()
            return ip, port
        elif ipport is None:
            ip = "False"
            return ip, port

        tentative += 1

    if ipport is not None:
        if ok:
            try:
                sck.sendto('PING', (ip, port))
                sck.recv_queue.get(timeout=4)
            except queue.Empty:
                ok = False
                Windows.ErrorWindow('Impossible de se connecter à l\'arbitre').show()
                ip, port = None, None

        return ip, port


if __name__ == '__main__':

    ip, port = None, None
    ipCorrect = True

    fs = FiableSocket(Utils.creer_socket())

    while ip is None:
        ip, port = ask_ip(fs)
        # Test si trop d'erreur
        if ip == "False":
            ipCorrect = False
            break

    if ipCorrect:
        username = connexion()
        utilisateur = Utilisateur(fs)

        if username is not None:
            utilisateur.nom = username
            utilisateur.addr_arbitre = (ip, port)
            actions()

        utilisateur.__del__()

    else:
        print('Fin du programme')
        fs.__del__()
