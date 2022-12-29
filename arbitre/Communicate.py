import socket

import Database
import Cryptage

end = False
nom_arbitre = 'C'


def recv(socket):
    """
    Fonction qui permet de recevoir en boucle les messages des clients
    :param socket: Le socket de connexion
    :return: Le message reçu
    """

    while not end:
        msg, addr = socket.recvfrom(1024)
        msg = msg.decode()
        if not end:
            process_ping(msg, addr, socket)
            process_T1(msg, addr, socket)
            process_classic(msg, addr, socket)
            process_T4(msg, addr, socket)


def process_ping(msg, addr, sck):
    """
    Permet de traiter un message de type ping (utilisé par les clients pour tester si le serveur est en ligne)
    :param msg: le message reçu
    :param addr: l'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    :return: None
    """
    if msg.upper() == 'PING':
        sck.sendto(b'PONG', addr)


def process_T1(msg, addr, sck):
    """
    S'occupe du traitement de tous les messages de type T1 (création d'une nouvelle clé)

    Message reçu : <Nom utilisateur, Nom de l’arbitre, T1, clef privé de l’utilisateur>

    Envoi Eclef <Nom de l’arbitre,Nom utilisateur, T1> si la clé a été créée, sinon envoi de
    <Nom de l’arbitre, Nom utilisateur, T1> si la clé n'a pas été créée

    :param msg: Le message reçu
    :param addr: L'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    :return: None
    """

    msg_split = msg.split(',')
    if len(msg_split) > 3 and msg_split[2] == 'T1':
        nom_util = msg_split[0].upper()
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
            sck.sendto(msg.encode(), addr)
        else:
            # Envoi de <Nom de l’arbitre, Nom utilisateur, T1>
            msg = nom_arbitre + ',' + nom_util + ',T1'
            sck.sendto(msg.encode(), addr)


def process_classic(msg, addr, sck):
    """
    Permet de vérifier qu'un message donné est bien du type T2, T3 ou T6. Si c'est le cas, lance l'exécution du message
    par le serveur

    Message reçu : - <Nom utilisateur, Nom de l’arbitre, Eold<T2, old clef privée de l’utilisateur, new clef privée>>
                   - <Nom utilisateur, Nom de l’arbitre, Eclef<T3,clef privée>>
                   - <Nom utilisateur, Nom de l’arbitre, Eclef<T6, utilisateur B>>

    :param msg: Le message reçu
    :param addr: L'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    :return: None
    """

    msg_splitted = msg.split(',')
    if len(msg_splitted) >= 2 and msg_splitted[1] == nom_arbitre:
        nom_utilisateur = msg_splitted[0].upper()
        cle_chiffrement = Database.get_key(nom_utilisateur)

        if cle_chiffrement is not None:
            # On recherche la partie du message qui est chiffrée
            partie_clair = nom_utilisateur + ',' + nom_arbitre + ','
            partie_chiffree = msg[len(partie_clair):]

            dechiffre = Cryptage.decrypter(partie_chiffree, cle_chiffrement)
            if dechiffre[:2] == 'T2':
                print('Traitement du message T2 de ' + nom_utilisateur + ' (' + msg + ')')
                T2_execute(dechiffre, nom_utilisateur, addr, sck)
            elif dechiffre[:2] == 'T3':
                print('Traitement du message T3 de ' + nom_utilisateur + ' (' + msg + ')')
                T3_execute(dechiffre, nom_utilisateur, addr, sck)
            elif dechiffre[:2] == 'T6':
                print('Traitement du message T6 de ' + nom_utilisateur + ' (' + msg + ')')
                # T6_execute(dechiffre, nom_utilisateur, addr, sck)


def process_T4(msg, addr, sck):
    """
    Permet de vérifier qu'un message donné est bien du type T4. Si c'est le cas, lance l'exécution du message
    par le serveur

    Message reçu : Eclef< Nom de l’utilisateur A, Nom de l’arbitre, Nom de l’utilisateur B, T4>.

    :param msg: Le message reçu
    :param addr: L'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    :return: None
    """

    keys = Database.get_all_keys()
    cle_trouve = False
    index = 0

    while not cle_trouve and index < len(keys):
        key = keys[index]
        msg_dechiffre = Cryptage.decrypter(msg, key)

        if msg_dechiffre[:2] == 'T4':
            msg_split = msg_dechiffre.split(',')
            if len(msg_split) == 4 and msg_split[2] == nom_arbitre:
                util_a = msg_split[0].upper()
                if key == Database.get_key(util_a):
                    cle_trouve = True
                    print('Traitement du message T4 de ' + util_a + ' (' + msg + ')')
                    T4_execute(msg_dechiffre, util_a, addr, sck)
                else:
                    print("WARN : " + util_a + " a envoyé un message T4 qui a été déchiffré avec une autre clé que la sienne")


def T2_execute(msg, user, addr, sck):
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
    :return: None
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
    sck.sendto(msg.encode(), addr)


def T3_execute(msg, user, addr, sck):
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
        sck.sendto(msg.encode(), addr)


def T4_execute(msg, user, addr, sck):
    """
    Fonction utilisée par process_T4 et qui s'occupe d'exécuter le message T4 une fois que sa clé a été trouvée
    (Début de discussion entre 2 utilisateur, génération de KS)

    Envoi Eclef_A<Nom de l’arbitre, Nom utilisateur A, T4, Ks, Eclef_B<Nom de l’arbitre, Nom utilisateur A, Nom utilisateur B, Ks>>
    si l'utilisateur B a été trouvé, sinon envoi de Eclef_A<Nom de l’arbitre, Nom utilisateur A, T4>

    :param msg: La partie du message du protocole T4 qui contient les informations à traiter
                (Eclef< Nom de l’utilisateur A, Nom de l’arbitre, Nom de l’utilisateur B, T4>.)
    :param user: L'utilisateur qui a envoyé ce message
    :param addr: L'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    :return: None
    """
    msg_split = msg.split(',')
    user_b = msg_split[2].upper()

    user_a_key = Database.get_key(user)
    user_b_key = Database.get_key(user_b)

    if user_a_key is not None and user_b_key is not None:
        # génération de la clé de session
        ks = Cryptage.clefSession(user_a_key, user_b_key)

        # Envoi du message Eclef_A<Nom de l’arbitre, Nom utilisateur A, T4, Ks, Eclef_B<Nom de l’arbitre, Nom utilisateur A, Nom utilisateur B, Ks>>
        msg_partie_b = nom_arbitre + ',' + user + ',' + user_b + ',' + ks
        msg_partie_b = Cryptage.crypter(msg_partie_b, user_b_key)
        msg = nom_arbitre + ',' + user + ',T4,' + ks + ',' + msg_partie_b
        msg = Cryptage.crypter(msg, user_a_key)
        sck.sendto(msg.encode(), addr)
    else:
        # Envoi du message Eclef_A<Nom de l’arbitre, Nom utilisateur A, T4>
        msg = nom_arbitre + ',' + user + ',T4'
        msg = Cryptage.crypter(msg, user_a_key)
        sck.sendto(msg.encode(), addr)


def T6_execute(msg, user, addr, sck):
    """
    Fonction utilisée par process_classic et qui s'occupe d'envoyer à l'expéditeur du message les coordonnées
    (IP:PORT) de l'utilisateur demandé (utilisateur B)

    Envoi Eclef<Nom utilisateur B, IP, PORT, T6>, si l'utilisateur demandé a été trouvé, sinon envoi de
    Eclef<Nom utilisateur A, T6> si l'utilisateur demandé n'a pas été trouvé

    :param msg: La partie du message du protocole T3 qui contient les informations à traiter
                (Eclef<T6, utilisateur B>)
    :param user: L'utilisateur qui a envoyé ce message
    :param addr: L'adresse du client
    :param sck: Le socket à utiliser pour l'envoi
    :return: None
    """
    user_key = Database.get_key(user)
    msg_decode = msg.split(',')

    if len(msg_decode) == 2 and user_key is not None:
        util_b = msg_decode[1].upper()
        util_b_addr = Database.get_addr(util_b)
        if util_b_addr is not None:
            msg = util_b + ',' + util_b_addr[0] + ',' + str(util_b_addr[1]) + ',T6'
        else:
            msg = user + ',T6'
        msg = Cryptage.crypter(msg, user_key)

        sck.sendto(msg.encode(), addr)



