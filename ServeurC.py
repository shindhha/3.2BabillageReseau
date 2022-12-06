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
        cursor.execute(""" CREATE TABLE clefs (nom TEXT, clef TEXT, ip TEXT, port TEXT, CONSTRAINT pk_clefs PRIMARY KEY (nom)) """) # requete de creation de la table
        connectionBd.close() # deconnection de la base

def ajout(nom,cle,connection):
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    ip = connection[0] # separation de l'IP et du PORT dans la connection
    port = connection[1]
    cursor.execute("INSERT INTO clefs VALUES (?,?,?,?)", (nom,cle,ip,port,)) # si pas créer creation de l'utilisateur et ajout de sa clef
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
    cursor.execute("DELETE FROM clefs WHERE nom =(?)",(utilisateur,))#supression de la clé et de l'utilisateur
    connectionBd.commit()
    connectionBd.close()

def afficherBd():
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    lignes = cursor.execute(" SELECT * FROM clefs ")
    print (lignes.fetchall())

def cleUtilisateur(utilisateur):
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    cle = cursor.execute(" SELECT clef FROM clefs WHERE nom = (?)",(utilisateur,))

    return cle.fetchone()[0]


if __name__ == "__main__":

    initDb()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    coordServeur = ('127.0.0.1',12345)
    s.bind(coordServeur)
    

    while True:

        (message,comm) = s.recvfrom(1024)
        tab = message.decode().split(',') # decoupage du message reçu en fonction des virgules



        if (tab[2] == 'T1'): # verification de la requette reçu
            try :
                ajout(tab[0],tab[3],comm)
                aEnvoyer = cryptage.crypter(nomArbitre + ',' + tab[0] + ',T1',tab[3]) # creation du message de validation a envoyer dans le cas ou l'instruction est passé

            except Exception:
                aEnvoyer = nomArbitre + ',' + tab[0] + ',T1' # creation du message de validation de la creation de cle

            s.sendto(aEnvoyer.encode(),comm) # envoie du message de validation


        
        elif (cryptage.decrypter(tab[2],cleUtilisateur(tab[0])).split(',')[0] == 'T2'): # verification de la requette reçu

            tab2 = cryptage.decrypter(tab[2],cleUtilisateur(tab[0])).split(',') # decoupage de la partie crypté du message reçu

            try:
                oldCle = cleUtilisateur(tab[0])
                modif(tab2[2],tab[0])
                aEnvoyer = cryptage.crypter(tab[0] + ',' + nomArbitre + ',T2', cleUtilisateur(tab[0])) # creation du message de validation a envoyer dans le cas ou l'instruction est passé

            except Exception:
                aEnvoyer = cryptage.crypter(nomArbitre + tab[0] + ',T2', oldCle) # creation du message de validation de la modification de cle
            s.sendto(aEnvoyer.encode(),comm) # envoie du message de validation



        elif (cryptage.decrypter(tab[2],cleUtilisateur(tab[0])).split(',')[0] == 'T3'): # verification de la requette reçu

            tab2 = cryptage.decrypter(tab[2],cleUtilisateur(tab[0])).split(',')

            try:
                suppr(tab[0])
                aEnvoyer = cryptage.crypter(nomArbitre + ',' + tab[0] + ',T3',tab2[1]) # creation du message de validation de la supression de clé

            except Exception as e:
                raise e
                aEnvoyer = cryptage.crypter(tab[0] + ',' + nomArbitre, tab2[1])
            
            s.sendto(aEnvoyer.encode(), comm) # envoie du message de validation