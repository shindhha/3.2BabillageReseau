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
        self.ks = None

        # --- Informations relatives à l'arbitre ---
        self.nom_arbitre = 'C'
        self.addr_arbitre = ('localhost', 12345)


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


def menu_principal(msg_info):
    """
    Fonction qui affiche la fenêtre principale de l'application
    :return:
    """
    fenetre = Windows.Menu(msg_info)
    action = fenetre.show()
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


def actions():
    """
    Fonction qui gère les actions de l'utilisateur effectuées depuis la fenêtre principale
    :return:
    """
    end = False
    msg_info = ''
    while not end:
        action = menu_principal(msg_info)
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

        else:
            print('Action inconnue')


if __name__ == '__main__':
    username = connexion()
    utilisateur = Utilisateur()

    if username is not None:
        utilisateur.nom = username
        actions()

    utilisateur.__del__()
