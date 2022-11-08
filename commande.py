from Client import Client
import socket
import cryptage

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def t1(client):
    global s
    nouvelleClef = input('entrez la clef: ')
    message = client.nom + ',' + client.nomArbitre + ',T1,' + nouvelleClef # creation du message a envoyé au serveur
    clef = nouvelleClef

    s.sendto(message.encode(), client.coord_S) # envoie du message au serveur

    print("En attente de verification .....")
    (reponse, client.coord_S) = s.recvfrom(1024) # reception de la reponse
    tab1 = reponse.decode().split(',') # decoupe de la reponse avec les virgules

    if (tab1[0] == client.nomArbitre ): # verification commande bien passé suivant message renvoyer par le serveur
        print ("echec de l'ajout de la clé")
    else:
        print("ajout de la clef avec succès")
        client.clef = nouvelleClef



def t2(client):
    global s
    if (client.clef != None):
        nouvelleClef = input('entrez la nouvelle clef: ')
        message = client.nom + ',' + client.nomArbitre + ',' + cryptage.crypter("T2," + client.clef + "," + nouvelleClef,client.clef) # creation du message a envoyé au serveur crypter avec ancienne clé
        s.sendto(message.encode(), client.coord_S) # envoie du message au serveur

        print("En attente de verification .....")
        (reponse, client.coord_S) = s.recvfrom(1024) # reception de la reponse

        if (cryptage.decrypter(reponse.decode().split(',')[0], client.clef) == client.nomArbitre): # verification commande bien passé suivant message renvoyer par le serveur
            print ("echec de la modification de la clé")
        else:
            client.clef = nouvelleClef
            print("modification de la clef avec succès")
    else:
        print("votre clef n'est pas initialisée")