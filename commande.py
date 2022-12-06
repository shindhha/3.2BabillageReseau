from Client import Client
import socket
import cryptage
from random import randrange

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def relierSocket (client):
    global s
    while client.port == None:
        try :
            client.port = randrange(12345,55555) # choix du port aleatoire
            s.bind(('localhost',client.port)) # test bind socket sur le port choisit
            client.coordonee = ('localhost', client.port) # stockage coordonee client
        except OSError: # verification port non utilisé
            client.port = None

def reception(client):
    global s
    while True:
        (reponse,client.coord_S) = s.recvfrom(1024) # reception des message en provenence du serveur
    
        phrase = reponse.decode() # recupere la reponse envoyé par le serveur
        verif = cryptage.decrypter(phrase, client.clefTemporaire)
        
        if (phrase[len(phrase) - 2] + phrase[len(phrase) - 1] == 'T1'): # verification commande d'ajout de la clé effectuer
            print ("echec de l'ajout de la clé")
        elif (verif[len(phrase) - 2] + verif[len(phrase) - 1] == 'T1'): # verification cas echec ajout de la clé
            client.clef = client.clefTemporaire
            print("ajout de la clef avec succès")

        
        verifvraie = cryptage.decrypter(phrase,client.clefTemporaire)
        veriffaux = cryptage.decrypter(phrase,client.clef)

        if (veriffaux[len(phrase) - 2] + veriffaux[len(phrase) - 1] == 'T2'): # verification commande de modification de clé bien exécuté
            print ("echec de la modification de la clé")
        elif (verifvraie[len(phrase) - 2] + verifvraie[len(phrase) - 1] == 'T2'):
            client.clef = client.clefTemporaire
            print("modification de la clef avec succès")

            verif = cryptage.decrypter(phrase,client.clefTemporaire)
        if (verif[len(phrase) - 2] + verif[len(phrase) - 1] == 'T3'): # verification commande de supression de clef bien exécuté
            client.clef = None
            print("suppression de le clef avec succès")
        elif (verif[len(phrase) - len(client.nomArbitre) : len(phrase) - 1] == client.nomArbitre):
            print("echec de la supression de la clef")


def t1(client):
    global s
    if (client.clef == None):
        nouvelleClef = input('entrez la clef: ')
        if (not cryptage.cleOk(nouvelleClef)):
            print ('la cle contient un caractere speciale non autorise')
        else:
            message = client.nom + ',' + client.nomArbitre + ',T1,' + nouvelleClef # creation du message de création d'une clé
            client.clefTemporaire = nouvelleClef

            s.sendto(message.encode(), client.coord_S) # envoie du message au serveur

            print("En attente de verification .....")

    else:
        print("vous possedez deja une clef privee")


def t2(client):
    global s
    if (client.clef != None):
        nouvelleClef = input('entrez la nouvelle clef: ')
        client.clefTemporaire = nouvelleClef
        message = client.nom + ',' + client.nomArbitre + ',' + cryptage.crypter("T2," + client.clef + "," + nouvelleClef,client.clef) # creation du message de modification de la clé
        s.sendto(message.encode(), client.coord_S) # envoie du message au serveur

        print("En attente de verification .....")

    else:
        print("votre clef n'est pas initialisée")



def t3(client):
    global s
    if (client.clef != None):
        message = client.nom + ',' + client.nomArbitre + ',' + cryptage.crypter('T3,' + client.clef, client.clef) # creation du message de suppression de la clé
        s.sendto(message.encode(),client.coord_S) # envoie du message au serveur

        print("En attente de verification .....")
        
    else:
        print("votre clef n'est pas initialisé")


def t4(client):
    global s
    if (client.clef != None):
        utilisateurB = input('entrez le nom de l\'utilisateur avec qui comuniquer: ')
        message = cryptage.crypter(client.nom + ',' + client.nomArbitre + ',' + utilisateurB + ',T4',client.clef) #creation du message de demande de communication avec un utilisateur
        s.sendto(message.encode(),client.coord_S) # envoie du message au serveur

        print("En attente de verification .....")
        (reponse, client.coord_S) = s.recvfrom(1024) # reception de la reponse du serveur

        tabReponse = cryptage.decrypter(reponse.decode(),client.clef).split(',') # decryptage de la reponse
        if (tabReponse[2] == 'T4'): #verificaton commande bien exécuté
            client.ks = tabReponse[3]
            s.sendto(tabReponse[4].encode,client.coord_S)
            #TODO fonction bloquante recv, reception message userB et envoie confirm serveur