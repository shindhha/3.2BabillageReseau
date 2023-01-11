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
                 destinataire text
                 )''')

    conn.commit()
    conn.close()


def test_exist_ip_port(ip: str, port: int) -> bool:
    """
    Permet de voir si le couple spécifié en paramètre existe dans la BD
    :param ip: L'ip du couple
    :param port: Le port du couple
    :return: True si le couple existe, false sinon
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT * FROM clefs WHERE ip = (?) AND port = (?)", (ip, port))

    existe = len(c.fetchall()) > 0

    conn.close()

    return existe


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

    # On interdit la création d'un nouvel utilisateur si sa connexion existe déjà. permety de retouver un utilisateur
    # à partir du couple ip : port.
    if test_exist_ip_port(ip, port):
        retour = False

    if retour:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        try:
            c.execute("INSERT INTO clefs VALUES (?, ?, ?, ?, NULL)", (nom, clef, ip, port))
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


def get_addr(nom: str) -> tuple[str, int] | None:
    """
    Récupère l'adresse d'un utilisateur (IP, PORT)
    :param nom: nom de l'utilisateur
    :return: Un tuple (ip, port) de l'utilisateur, None si l'utilisateur n'existe pas ou si l'adresse n'est pas renseignée
    """
    addr = None

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("JE RECUPERE L'ADRESSE DE", nom)
    c.execute("SELECT ip, port FROM clefs WHERE nom = (?)", (nom,))

    all_rows = c.fetchall()

    if len(all_rows) == 1:
        addr = all_rows[0]
        addr = (addr[0], int(addr[1]))

    conn.close()

    return addr


def set_destinataire(nom: str, destinataire: str) -> bool:
    """
    Permet de définir le destinataire de la communication pour un échange de messages
    :param nom: L'utilisateur à définir
    :param destinataire: Le nom du destinataire
    :return: true si le destinataire a été définie, false sinon
    """
    defini = False

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM clefs WHERE nom = (?)", (nom,))
    destinataire_existe = c.fetchone()[0] == 1

    if destinataire_existe:
        c.execute("UPDATE clefs SET destinataire = (?) WHERE nom = (?)", (destinataire, nom))
        defini = True
        conn.commit()

    conn.close()

    return defini


def get_destinataire(utilisateur: str) -> str | None:
    """
    Permet d'obtenir le nom d'un destinataire d'un utilisateur
    :param utilisateur: L'utilisateur sur lequel on cherche le destinataire
    :return: Le nom du destinataire ou None si le destinataire pas défini
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT destinataire FROM clefs WHERE nom = (?)", utilisateur)
    nom_destinataire = c.fetchone()[0]

    conn.close()

    return nom_destinataire


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


def get_username(addr: tuple[str, int]) -> str | None:
    """
    Permet d'obtenir le nom d'utilisateur d'une personne à partir d'une adresse (ip, port)
    :param addr: L'adresse pour laquelle on recherche le nom d'utilisateur
    :return: Le nom d'utilisateur ou None s'il n'a pas été trouvé
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    ip = addr[0]
    port = addr[1]

    c.execute("SELECT nom FROM clefs WHERE ip = (?) AND port = (?)", (ip, port))
    all_rows = c.fetchall()

    nom_util = None
    if len(all_rows) > 0:
        nom_util = all_rows[0]

    conn.close()

    return nom_util


def desactiver_communication(addr: tuple[str, int]):
    """
    Permet de s'assurer que les communications avec un autre utilisateur sont désactivées pour l'adresse mise en paramètre.
    Si la communication est active, on dé-bind le champ destinataire pour les 2 noms d'utilisateur
    :param addr: L'adresse pour laquelle on désactive la communication
    :return: None
    """

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT destinataire FROM clefs WHERE ip = (?) AND port = (?)", (addr[0], addr[1]))

    destinataire = c.fetchone()
    if destinataire is not None:  # Si la requête SQL a retourné des lignes
        destinataire = destinataire[0]
        print("DESTINATAIRE :", destinataire)
        if destinataire is not None:  # Si le destinataire est défini pour la ligne de d'adresse demandée
            c.execute("UPDATE clefs SET destinataire = NULL WHERE ip = (?) AND port = (?)", (addr[0], addr[1]))
            c.execute("UPDATE clefs SET destinataire = NULL WHERE nom = (?)", (destinataire,))
            conn.commit()

    conn.close()