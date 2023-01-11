import sqlite3
from Cryptage import cleOk

db_path = 'database.db'


def init_db():
    """
    Initialise la base de données
    :return None
    """

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS clefs
                 (
                 nom text primary key not null, 
                 clef text, 
                 ip text,
                 port text,
                 ks text
                 )''')

    conn.commit()
    conn.close()


def create_key(nom, clef, ip, port):
    """
    Crée une clé dans la base de données pour un utilisateur donné
    :param nom: nom de l'utilisateur
    :param clef: clef de l'utilisateur
    :param ip: ip de l'utilisateur
    :param port: port de l'utilisateur
    :return: True si la clé a été créée, False sinon
    """
    retour = cleOk(clef)

    if retour:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        try:
            c.execute("INSERT INTO clefs VALUES (?, ?, ?, ?, '')", (nom, clef, ip, port))
            conn.commit()
        except sqlite3.Error:
            retour = False
        conn.close()

    return retour


def update_key(nom, clef):
    """
    Met à jour la clé d'un utilisateur
    :param nom: nom de l'utilisateur
    :param clef: nouvelle clef de l'utilisateur
    :return: True si la clé a été mise à jour, False sinon
    """
    retour = cleOk(clef)

    if retour:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("UPDATE clefs SET clef = ? WHERE nom = ?", (clef, nom))

        try:
            conn.commit()
        except sqlite3.Error:
            retour = False
        conn.close()

    return retour


def get_key(nom):
    """
    Récupère la clé d'un utilisateur
    :param nom: nom de l'utilisateur
    :return: la clé de l'utilisateur, None si l'utilisateur n'existe pas
    """
    clef = None

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT clef FROM clefs WHERE nom = (?)", (nom,))

    all_rows = c.fetchall()

    if len(all_rows) == 1:
        clef = all_rows[0][0]

    conn.close()

    return clef


def delete_key(nom):
    """
    Supprime la clé d'un utilisateur
    :param nom: nom de l'utilisateur
    :return: True si la clé a été supprimée, False sinon
    """
    retour = True

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("DELETE FROM clefs WHERE nom = ?", (nom,))

    try:
        conn.commit()
    except sqlite3.Error:
        retour = False
    conn.close()

    return retour


def get_addr(nom) -> tuple[str, int] | None:
    """
    Récupère l'adresse d'un utilisateur (IP, PORT)
    :param nom: nom de l'utilisateur
    :return: Un tuple (ip, port) de l'utilisateur, None si l'utilisateur n'existe pas ou si l'adresse n'est pas renseignée
    """
    addr = None

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT ip, port FROM clefs WHERE nom = (?)", (nom,))

    all_rows = c.fetchall()

    if len(all_rows) == 1:
        addr = all_rows[0]

    conn.close()

    return addr


def get_all_keys() -> list[str]:
    """
    Récupère toutes les clés de la base de données
    :return: Un tuple contenant toutes les clés de la base de données
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT DISTINCT clef FROM clefs")

    all_rows = c.fetchall()

    liste = []
    for row in all_rows:
        liste.append(row[0])

    conn.close()

    return liste
