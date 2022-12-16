import socket
import sqlite3
import os
import cryptage


nomArbitre = 'C'
cheminBd = 'Bd_babillage.db'

def initDb():
    if (not(os.path.exists(cheminBd) and os.path.isfile(cheminBd))):
        connectionBd = sqlite3.connect(cheminBd) # connection a la base de données
        cursor = connectionBd.cursor() # creation du curseur permetant l'ecriture dans la base en langage sql
        cursor.execute(""" CREATE TABLE clefs (nom TEXT, clef TEXT, ip TEXT, port TEXT,ks TEXT,destinataire TEXT, CONSTRAINT pk_clefs PRIMARY KEY (nom)) """) # requete de creation de la table
        connectionBd.close() # deconnection de la base

def refreshBd():
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    cursor.execute("DROP TABLE clefs") # supression de la table
    cursor.execute(""" CREATE TABLE clefs (nom TEXT, clef TEXT, ip TEXT, port TEXT,ks TEXT,destinataire TEXT, CONSTRAINT pk_clefs PRIMARY KEY (nom)) """) # requete de creation de la table
    connectionBd.commit()
    connectionBd.close()


def ajoutClef(nom,cle,connection):
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    ip = connection[0] # separation de l'IP et du PORT dans la connection
    port = connection[1]
    cursor.execute("INSERT INTO clefs VALUES (?,?,?,?,NULL,NULL)", (nom,cle,ip,port,)) # si pas créer creation de l'utilisateur et ajout de sa clef 
    connectionBd.commit()
    connectionBd.close()


def modif(cle, utilisateur):
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    cursor.execute("UPDATE clefs SET clef = (?) WHERE nom = (?)",(cle,utilisateur,)) # modification valeur de la clef de l'utilisateur donné
    connectionBd.commit()
    connectionBd.close()


def suppr(utilisateur):
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    cursor.execute("DELETE FROM clefs WHERE nom = (?) ",(utilisateur,))#supression de la clé et de l'utilisateur
    connectionBd.commit()
    connectionBd.close()


def afficherBd():
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    lignes = cursor.execute(" SELECT * FROM clefs ") #selection de toute la base de donnée
    print (lignes.fetchall())


def selectCleUtilisateur(utilisateur):
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    cle = cursor.execute(" SELECT clef FROM clefs WHERE nom = (?) ", ( utilisateur,)) #selection de l'ip et du port d'un utilisateur donnée

    try:
        return cle.fetchone()[0]
    except Exception:
        return None
    connectionBd.close()


def utilisateur():
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    users = cursor.execute("SELECT nom FROM clefs")

    return users.fetchall()
    connectionBd.close()


def selectUtilisateurPort(port) :
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    user = cursor.execute("SELECT nom FROM clefs WHERE port = (?)",(port,))

    try :
        return user.fetchone()[0]
    except Exception :
        return None
    connectionBd.close()


def selectConnectionUtilisateur(nom) :
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    connection = cursor.execute("SELECT ip, port FROM clefs Where nom = (?)",(nom,))

    try:
        comm = connection.fetchall()
        return (comm[0][0],int (comm[0][1]),)
    except Exception as e:
        raise e 
        return None
    connectionBd.close()


def modifKsDestinataire(nom,ks,destinataire) :
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    connection = cursor.execute("UPDATE clefs SET ks = (?) WHERE nom = (?)",(ks,nom,))
    connection = cursor.execute("UPDATE clefs SET destinataire = (?) WHERE nom = (?)",(destinataire,nom,))
    connectionBd.commit()
    connectionBd.close()


def suprimerKsDestinataire(nom) :
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    connection = cursor.execute("UPDATE clefs SET ks = NULL WHERE nom = (?)",(nom,))
    connection = cursor.execute("UPDATE clefs SET Destinataire = NULL WHERE nom = (?)",(nom,))
    connectionBd.commit()
    connectionBd.close()


def selectDestinataire(nom) :
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    connection = cursor.execute("SELECT destinataire FROM clefs WHERE nom = (?)",(nom,))

    try:
        return connection.fetchone()[0]
    except Exception as e :
        raise echec
        return None
    connectionBd.close()

def selectKs(nom) :
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    connection = cursor.execute("SELECT ks FROM clefs WHERE nom = (?)",(nom,))

    return connection.fetchone()[0]
    connectionBd.close()


def verifierConnection(comm) :
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    connection = cursor.execute("SELECT destinataire FROM clefs WHERE port = (?)",(comm[1],))

    try:
        connect = connection.fetchone()[0]
        if (connect != None):
            return True
        else :
            return False
    except Exception :
        return False


if __name__ == "__main__":

    initDb()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    coordServeur = ('127.0.0.1',12345)
    s.bind(coordServeur)
    suppressionDonnées = input('voulez vous remettre la base de données a zéro ? (entrez oui pour confirmer) :')

    if (suppressionDonnées == 'oui'):
        refreshBd()
    

    while True:

        (message,comm) = s.recvfrom(2048)
        ip = comm[0]
        port = comm[1]
        message = message.decode() # recuperation du message reçu 
        if (selectUtilisateurPort(port) != None): #verification utilisateur deja créer ou premiere connection
            longeur = len (selectUtilisateurPort(comm[1])) + len(nomArbitre) + 2 # longeur du message avant type (avant t1 t2 ou t3)
            recept = cryptage.decrypter(message[longeur:len(message)],selectCleUtilisateur(selectUtilisateurPort(port))) # decodage du message avec la clef de l'utilisateur
            receptComm = cryptage.decrypter(message,selectCleUtilisateur(selectUtilisateurPort(port)))
        else :
            longeur = None
        if (verifierConnection(comm)):

            verif = cryptage.decrypter(message,selectKs(selectUtilisateurPort(comm[1]))) # decryptage du message envoyé avec la clé ks

            envoyeur = selectUtilisateurPort(comm[1]) # recuperation du nom de l'envoyeur
            destinataire = selectDestinataire(envoyeur) # recuperation du nom du destinataire du message
            connectionDestinataire = selectConnectionUtilisateur(destinataire) # recuperation de 'adresse IP et du port du destinataire

            if (verif[len(message) - 2] + verif[len(message) - 1] == 'T5'): # verification acceptation de la connexion par B
                aEnvoyer = cryptage.crypter('T5',selectKs(selectUtilisateurPort(comm[1])))
                s.sendto(aEnvoyer.encode(),connectionDestinataire)

            elif(verif == 'T0'): # verification refus de la connexion par B
                s.sendto(message.encode(),connectionDestinataire) # transmition du refus a l'utilsateur A
                suprimerKsDestinataire(envoyeur) # réinitialisation de ks et du destinataire des 2 utilisateurs
                suprimerKsDestinataire(destinataire)

            elif (verif[len(message) - 2] + verif[len(message) - 1] == 'T6'): # verification message a transmettre a l'utilisateur avec lequel l'envoyeur est connecter
                if (verif[0:len(message) - 2] == 'FIN'):
                    suprimerKsDestinataire(envoyeur)
                    suprimerKsDestinataire(destinataire)
                s.sendto(message.encode(),connectionDestinataire)
                

        if (longeur == None): # verification de la requette reçu
            try :
                tab = message.split(',')
                ajoutClef(tab[0].upper(),tab[3].upper(),comm)
                aEnvoyer = cryptage.crypter(nomArbitre + ',' + tab[0] + ',T1',tab[3]) # creation du message de validation a envoyer dans le cas ou l'instruction est passé  

            except sqlite3.IntegrityError as e:
                aEnvoyer = nomArbitre + ',' + tab[0] + ',T1' # creation du message d'echec de l'ajout
                s.sendto('ce nom d utilisateur est deja utiliser, veuillez en choisir un autre,T0'.encode(),comm )
            except Exception:
                aEnvoyer = nomArbitre + ',' + tab[0] + ',T1'

            s.sendto(aEnvoyer.encode(),comm) # envoie du message de validation


        elif (len(recept) >= 2 and recept[0] + recept[1] == 'T2'):
            try:
                partie1 = message[0:longeur] # selection premiere partie du message non crypter
                partie2 = cryptage.decrypter(message[longeur:len(message)],selectCleUtilisateur(selectUtilisateurPort(port))) # selcetion second partie du message + decryptage avec ancenne clef utilisateur
                nvMessage = partie1 + partie2 # assemblage des 2 partie
                tab = nvMessage.split(',') # decoupage du message sous forme de tableau en fonction des virgules

                modif(tab[4],tab[0].upper())

                aEnvoyer = cryptage.crypter(tab[0] + ',' + tab[1] + ',T2',tab[4]) # creation message de validation
            except Exception:
                aEnvoyer = cryptage.crypter(tab[0] + ',' + tab[1] + ',' + ',T2',tab[3]) # creation message d'echec

            s.sendto(aEnvoyer.encode(),comm)

        elif (len(recept) >= 2 and recept[0] + recept[1] == 'T3'):
            try:
                partie1 = message[0:longeur] # selection premiere partie du message non crypter
                partie2 = cryptage.decrypter(message[longeur:len(message)],selectCleUtilisateur(selectUtilisateurPort(port))) # selcetion second partie du message + decryptage avec ancenne clef utilisateur
                nvMessage = partie1 + partie2 # assemblage des 2 partie
                tab = nvMessage.split(',') # decoupage du message sous forme de tableau en fonction des virgules
                
                suppr(tab[0].upper())
                
                aEnvoyer = cryptage.crypter(tab[0] + ',' + tab[1] + ',T3',tab[3])

            except Exception as e:
                raise e
                aEnvoyer = cryptage.crypter(tab[0] + ',' + tab[1] ,tab[3])
            
            s.sendto(aEnvoyer.encode(),comm)

        elif (receptComm[len(message) - 2] + receptComm[len(message) - 1] == 'T4'):

            tab = receptComm.split(',')

            clefCorrespondant = selectCleUtilisateur(tab[2]) # recuperation de la clef de l'utilsateur B
            clefEnvoyeur = selectCleUtilisateur(tab[0]) # recuperation de la clef de l'utilisateur A
            discusssionCorrespondant = selectDestinataire(tab[0]) # verification si le correspondant est deja en discusssion avec quelqu'un

            if (clefCorrespondant != None): # verrification correspondant existant
                if (discusssionCorrespondant == None): #verification que le correspondant n'est pas deja en discussion avec quelqu'un d'autre
                    ks = cryptage.clefSession(clefEnvoyeur,clefCorrespondant) # creation de la clef de session pour la communication

                    # creation du message de confirmation de creation de ks
                    aEnvoyer = cryptage.crypter(tab[1] + ',' + tab[0] + ',T4,' + ks + ',' + cryptage.crypter(tab[1] + ',' + tab[0] + ',' + tab[2] + ',' + ks, clefCorrespondant),clefEnvoyeur )

                    modifKsDestinataire(tab[0],ks,tab[2]) # creation d'une possible connection entre utilisateur A (tab[0]) et l'utilisateur B (tab[2]) pour l'utilisateur A
                    modifKsDestinataire(tab[2],ks,tab[0]) # creation d'une possible connection entre utilisateur A (tab[0]) et l'utilisateur B (tab[2]) pour l'utilisateur B

                    s.sendto(aEnvoyer.encode(),comm)

                    connectionB = selectConnectionUtilisateur(tab[2]) # recuperation de la connection a l'utilisateur B
                    (message,comm) = s.recvfrom(1024) # recuperation de la second partie du message a envoyer a B
                    s.sendto(message,connectionB)
                else:
                    s.sendto('le correspondant discute deja avec quelqu un,T0'.encode(),comm)

            else:
                s.sendto('correspondant inexistant,T0'.encode(),comm)
        