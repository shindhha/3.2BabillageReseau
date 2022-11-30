from Client import Client
import socket
import cryptage

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def reception(client):
    global s
    (reponse,client.coord_S) = s.recvfrom(1024) # reception des message en provenence du serveur

    tab1 = reponse.decode().split(',') # decoupe de la reponse suivant les virgules
        
    if (tab1[2] == 'T1'): # verification commande d'ajout de la clé effectuer
        client.clefTemporaire = None 
        print ("echec de l'ajout de la clé")
    elif (cryptager.decrypter(tab1[0],client.clefTemporaire).split(',')[2] == 'T1'): # verification cas echec ajout de la clé
        client.clef = client.clefTemporaire
        client.clefTemporaire = None
        print("ajout de la clef avec succès")
    
    if (cryptage.decrypter(tab1[0], client.clef).split(',')[2] == 'T2'): # verification commande de modification de clé bien exécuté
        client.clefTemporaire = None
        print ("echec de la modification de la clé")
    elif (cryptage.decrypter(tab1[0],client.clefTemporaire).split(',')[2] == 'T2'):
        client.clef = client.clefTemporaire
        client.clefTemporaire = None
        print("modification de la clef avec succès")
        
    if (cryptage.decrypter(tab[0],client.clef).split(',')[2] == 'T3'): # verification commande de supression de clef bien exécuté
        client.clef = None
        print("suppression de le clef avec succès")
    elif (len(cryptage.crypter(tab[0],client.clef).split(',')) == 2):
        print("echec de la supression de la clef")


def t1(client):
    global s
    if (client.clef == None):
        nouvelleClef = input('entrez la clef: ')
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