import socket
import sqlite3
import os
import cryptage


nomAbritre = 'C'
cheminBd = 'Bd_babillage.db'

def initDb():
    if (not(os.path.exists(cheminBd) and os.path.isfile(cheminBd))):
        connectionBd = sqlite3.connect(cheminBd)
        cursor = connectionBd.cursor()
        cursor.execute(""" CREATE TABLE clefs (nom TEXT, clef TEXT, CONSTRAINT pk_clefs PRIMARY KEY (nom)) """)
        connectionBd.close()

def ajout(nom,cle):
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    cursor.execute("INSERT INTO clefs VALUES (?,?)", (nom,cle))
    connectionBd.commit()
    connectionBd.close()

def afficherBd():
    connectionBd = sqlite3.connect(cheminBd)
    cursor = connectionBd.cursor()
    lignes = cursor.execute(" SELECT * FROM clefs ")
    print (lignes.fetchall())

if __name__ == "__main__":

    initDb()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    coordServeur = ('127.0.0.1',12345)
    s.bind(coordServeur)

    while True:
        (message,comm) = s.recvfrom(1024)
        tab = message.decode().split(',')
        if (tab[2] == 'T1'):
            ajout(tab[0],tab[3])
            aEnvoyer = cryptage.crypter(nomAbritre,tab[3]) + ',' + cryptage.crypter(tab[0],tab[3]) + ',T1'
            s.sendto(aEnvoyer.encode(),comm)

