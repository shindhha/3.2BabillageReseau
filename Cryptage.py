import random

texte = 'antoine'
clef = 'b'

lettres = {}
accent = ['é','è','ë','ê','à','â','ä','û','ü','ù','ï','î','ö','ô','ç']

# creation du dictionnaire contenant l'alphabet utilisé pour le cryptage / décryptage
for i in range (32 , 92):
    lettres[i - 32] = chr (i)
# exclusion du caractère '\'
for i in range (93 , 123):
    lettres[i - 32 - 1] = chr (i)

longeur = len(lettres)
for i in range (len(accent)):
    lettres[longeur + i] = accent[i]


def cleOk(clef: str) -> bool:
    for i in clef: # selection des lettres de la cle 1 par 1
        ok = False
        for n in range (len(lettres)): # comparaison de la lettre de la cle avec toutes les lettres de notre alphabet
            if i != ',' and i == lettres.get(n): # si lettres dans alphabet alors ok
                ok =True
                break
        if (not ok):
            return False
    return True

def messageOk(message: str) -> bool:
    for i in message:
        ok = False
        for n in range (len(lettres)): # comparaison de la lettre du message avec toutes les lettres de notre alphabet
            if i == lettres.get(n): # lettres du message presente dans l'alphabet
                ok = True
                break
        if not ok: # La lettre n'a pas été trouvée dans tout l'alphabet
            return False
    return True



def crypter(phrase: str, clef: str) -> str:
    rang = 0
    nouvelPhrase = ''
    while rang < len(phrase):
        lettrePhrase = list(lettres.values()).index(phrase[rang]) # selection de l'indice de la lettre a crypter
        lettreCle = list(lettres.values()).index(clef[rang % len(clef)]) # selection de l'indice de la lettre de la cle de cryptage
        nouvelPhrase += lettres[(lettrePhrase + lettreCle) % len(lettres)] # cryptage par vigenère
        rang += 1
    return nouvelPhrase


def decrypter(phrase: str, clef: str) -> str:
    rang = 0
    nouvelPhrase = ''
    while rang < len(phrase):
        lettrePhrase = list(lettres.values()).index(phrase[rang]) # selection de l'indice de la lettre à crypter
        lettreCle = list(lettres.values()).index(clef[rang % len(clef)]) # selection de l'indice de la lettre de la cle de cryptage
        nouvelPhrase += lettres[(lettrePhrase - lettreCle) % len(lettres)] # décryptage avec la méthode de Vigenère
        rang += 1
    return nouvelPhrase


def clefSession(clef1: str,clef2: str) -> str:
    ks = '' # initialisation de la clef de session
    if len(clef1) > len(clef2):
        longeurClef = random.randint(len(clef2), len(clef1)) # creation de la longueur de la cle de session
    else :
        longeurClef = random.randint(len(clef1), len(clef2))
    for i in range(longeurClef):
        choixClef = random.randint(1,2) # tirage de la cle à utiliser pour le caractère de rang i
        if (choixClef == 1):
            ks += clef1[random.randint(1,len(clef1) - 1)] # si clef 1 tiré alors choix du caractère de clef 1 à utiliser pour l'ajouter à la clé de session
        else:
            ks += clef2[random.randint(1,len(clef2) - 1)] # si clef 2 tiré alors choix du caractère de clef 2 à utiliser pour l'ajouter à la clé de session
    return ks
