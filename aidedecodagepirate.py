import cryptage
import socket
import threading as th

port_pirate = 5001
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('localhost', port_pirate))
fin_ecoute_msg = False

phrase = ''
sousPhrase = [] # listes accueillant les sous phrases
repetition = [] # listes des dictionnaires recapitulant les repetitions de chaques lettres dans les sous-messages

longeurCle = int(input('entrez la longeur de la clef : '))

lettres = {}
accent = ['é','è','ë','ê','à','â','ä','û','ü','ù','ï','î','ö','ô','ç']

# creation du dictionnaire contenant l'alphabet utiliser pour le cryptage / decryptage avec les caracteres de la table ascii
for i in range (32 , 92):
    lettres[i - 32] = chr (i)
# exclusion du caractère '\'
for i in range (93 , 123):
    lettres[i - 32 - 1] = chr (i)

longueur = len(lettres)
for i in range (len(accent)):
    lettres[longueur + i] = accent[i]


def initialisation() -> None:
    global sousPhrase
    global repetition
    global phrase
    for i in range(longeurCle):
        sousPhrase.append('')
        repetition.append({})
    phrase = ''


def collage() -> None:
    global phrase
    global fin_ecoute_msg
    while not fin_ecoute_msg:
        (recu,coord) = s.recvfrom(1024)
        recu = recu.decode()
        enTrop = len(recu) % longeurCle # calcul du nombre de caractères à retirer pour tomber sur une phrase de logeur = 0 modulo longueurCle
        aAjouter = recu[:len(recu) - enTrop] # suppression si besoins des derniers caractères
        phrase += aAjouter # ajout du message au reste de la phrase
        print("Réception d'un nouveau message. Taille du buffer : " + str(len(phrase)) + " caractères")

    print("Fin du thread d'écoute des messages")


def decoupage() -> list[str]:
    for i in range (len(phrase)):
        sousPhrase[i % longeurCle] += phrase[i] # decoupage de la phrase en sous-phrase
    return sousPhrase


def frequence(listeSousPhrase: list[str]) -> list[dict]:
    # boucle sur tous les sous-messages
    for n in range(longeurCle):
        for i in listeSousPhrase[n]: # selection des caractères du sous-message 1 par 1
            if (repetition[n].get(i,"None") == "None"): # verification si lettre deja dans dictionnaires ou premiere apparition
                repetition[n][i] = 1 # cas premiere apparition: ajout de la lettre dans le dictionnaire et nombre d'apparitions à 1
            else:
                repetition[n][i] = repetition[n].get(i) + 1 # cas deja dans le dictionaire: ajout de 1 au nombre d'apparition de la lettre
    return repetition


def clePossible(dicoFrequence) -> list[str]:
    clefs = ['','']
    valeurDeE = list(lettres.values()).index('e')
    valeurDeSpace = list(lettres.values()).index(' ')
    for n in range(len(dicoFrequence)):
        caractere = maximunDico(repetition[n])
        valeur = list(lettres.values()).index(caractere)
        lettreCle1 = lettres.get((valeur - valeurDeE) % len(lettres))
        lettreCle2 = lettres.get((valeur - valeurDeSpace) % len(lettres))
        clefs[0] += lettreCle1
        clefs[1] += lettreCle2
    return clefs


def maximunDico(dictionaire: dict) -> str:
    max = ''
    valeurMax = 0
    for i in dictionaire:
        if dictionaire.get(i) > valeurMax:
            valeurMax = dictionaire.get(i)
            max = i
    return max

def lancement() -> None:
    global fin_ecoute_msg
    initialisation()
    thread = th.Thread(target=collage)
    thread.start()

    input("Le pirate est en train d'écouter les messages... Appuyez sur Entree pour lancer l'analyse")
    fin_ecoute_msg = True
    s.sendto(b'',('localhost', port_pirate))

    collage()


    decoupe = decoupage()
    apparition = frequence(decoupe)
    tableau = clePossible(apparition)
    print ('\ndecryptage avec la cle 1 : ' + tableau[0])
    a = cryptage.decrypter(phrase,tableau[0])
    print (a)
    print ('\ndecryptage avec la cle 2 : ' + tableau[1])
    a = cryptage.decrypter(phrase,tableau[1])
    print (a)
    next = input('\nvoulez vous essayer de decoder avec une autre clef ? (o = oui ; n = non) : ')
    while (next == 'o'):
        nvCle = input('\nentrez la nouvelle cle :')
        a = cryptage.decrypter(phrase,nvCle)
        print('\nnouveau decodage : \n' + a)
        next = input('\nvoulez vous continuer de réessayer de decoder avec une autre clef ? (o = oui ; n = non) : ')


lancement()