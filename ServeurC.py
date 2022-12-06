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
    cursor.execute("INSERT INTO clefs VALUES (?,?,?,?)", (nom,cle,ip,port)) # si pas créer creation de l'utilisateur et ajout de sa clef
    connectionBd.commit()
    connectionBd.close()

def modif(cle, utilisateur):
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    cursor.execute("UPDATE clefs SET clef = (?) WHERE nom = (?)",(cle,utilisateur)) # modification valeur de la clef de l'utilisateur donné
    connectionBd.commit()
    connectionBd.close()

def suppr(utilisateur):
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    cursor.execute("DELETE FROM clefs WHERE nom = (?) ",(utilisateur))#supression de la clé et de l'utilisateur
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
    cle = cursor.execute(" SELECT nom FROM clefs WHERE nom = (?) ", ( utilisateur,))

    return cle.fetchone()[0]
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
    print (user)

    try :
        return user.fetchone()[0]
    except Exception :
        return None
    
    connectionBd.close()

if __name__ == "__main__":

    initDb()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    coordServeur = ('127.0.0.1',12345)
    s.bind(coordServeur)
    

    while True:

        (message,comm) = s.recvfrom(1024)
        message = message.decode() # recuperation du message reçu 
        if (selectUtilisateurPort(comm[1]) != None): #verification utilisateur deja créer ou premiere connection
            longeur = len (selectUtilisateurPort(comm[1])) + len(nomArbitre) + 1 # longeur du message avant type (avant t1 t2 ou t3)
            TypeMessage = message[longeur] + message[longeur +1] #selection des 2 caractere decrivant le type du message
        else :
            TypeMessage = None
        print (TypeMessage)


        if (TypeMessage == None): # verification de la requette reçu
            try :
                tab = message.split(',')
                ajout(tab[0],tab[3],comm)
                aEnvoyer = cryptage.crypter(nomArbitre + ',' + tab[0] + ',T1',tab[3]) # creation du message de validation a envoyer dans le cas ou l'instruction est passé
                print (aEnvoyer)
                

            except Exception as e:
                raise e
                aEnvoyer = nomArbitre + ',' + tab[0] + ',T1' # creation du message d'echec de l'ajout

            s.sendto(aEnvoyer.encode(),comm) # envoie du message de validation


        
        