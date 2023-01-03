import Windows
import Utils
import Communicate
from Cryptage import cleOk
import threading as th
from SimpleReceiver import SimpleReceiver


class Utilisateur:
    def __init__(self):
        self.socket = Utils.creer_socket()
        self._receiver = SimpleReceiver(self.socket)
        self._process_msg = th.Thread(target=Communicate.process_msg, args=(self._receiver.queue_recv, self))
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
        self.addr_destinataire = None

        # --- Informations relatives au menu principal ---
        self.main_menu = None
        self.demande_connexion = False

        # --- Informations relatives a la fenêtre de communication ---
        self.communication_window = None

    def __del__(self):
        self._receiver.terminate()
        self.socket.close()

# ------------------ Main ------------------


def connexion():
    """
    Permet à l'utilisateur d'entrer son nom d'utilisateur
    :return:
    """
    fenetre = Windows.ConnectWindow()
    name = fenetre.show()
    return name


def menu_principal(client, msg_info):
    """
    Fonction qui affiche la fenêtre principale de l'application
    :return:
    """
    client.main_menu = Windows.Menu(client, msg_info)
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
    :return: True si l'utilisateur a pu communiquer avec un tiers, False sinon
    """

    a_communique = False

    # Demande du nom du destinataire
    fenetre = Windows.SimpleInputWindow('Communiquer', 'Entrez le nom du destinataire :')
    nom_destinataire = fenetre.show()
    if nom_destinataire is not None:
        utilisateur.nom_destinataire = nom_destinataire
        # Demande à l'arbitre des coordonnées du destinataire
        if Communicate.demander_coordonnees(utilisateur):
            print("JAI LES COORDONNES")
            # Demande à l'arbitre de la clé de session (KS)
            if Communicate.demander_ks(utilisateur):
                # L'arbitre a accepté la demande, on affiche la fenêtre de communication pendant que l'utilisateur B
                # accepte la demande
                utilisateur.communication_window = Windows.DiscussWindow(utilisateur)
                utilisateur.communication_window.show_waiting_text()
                a_communique = utilisateur.communication_window.show()

                utilisateur.communication_window = None
    return a_communique


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
    while not end:
        action = menu_principal(utilisateur, msg_info)
        msg_info = ''

        if action == 'quit':
            end = True

        elif action == 'createKey':
            print('Création de la clé')
            if creation_cle():
                msg_info = 'Clé créée avec succès'

        elif action == 'editKey':
            print('Modification de la clé')
            if creation_cle(update=True):
                msg_info = 'Clé modifiée avec succès'

        elif action == 'delKey':
            print('Suppression de la clé')
            if supression_cle():
                msg_info = 'Clé supprimée avec succès'

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
                if not demarrer_communication_initialisateur():
                    msg_info = 'La communication a été refusée'

        else:
            print('Action inconnue')


if __name__ == '__main__':
    username = connexion()
    utilisateur = Utilisateur()

    if username is not None:
        utilisateur.nom = username
        actions()

    utilisateur.__del__()
