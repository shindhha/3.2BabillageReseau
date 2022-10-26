import socket
import sqlite3
import os

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

initDb()
ajout('A','ABC')

connectionBd = sqlite3.connect(cheminBd)
cursor = connectionBd.cursor()
test = cursor.execute(" SELECT * FROM clefs")
print (test.fetchall())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
coordServeur = ('127.0.0.1',12345)
s.bind(coordServeur)