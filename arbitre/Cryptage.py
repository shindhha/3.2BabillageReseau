import random

lettres = {}
# creation du dictionnaire contenant l'alphabet utiliser pour le cryptage / decryptage
for i in  range (ord('A'),ord('Z') + 1):
    lettres[i - ord('A')] = chr(i)
lettres[26] = ' '
for i in range(27,37):
    lettres[i] = str(i - 27)
lettres[37] = ','
lettres[38] = '-'
lettres[39] = '.'
lettres[40] = '?'
lettres[41] = '!'
lettres[42] = ':'
lettres[43] = ';'

def cleOk(clef):
    clef = clef.upper()
    for i in clef: # selection des lettres de la cle 1 par 1
        ok = False
        for n in range (len(lettres)): # comparaison de la lettre de la cle avec toute les lettres de notre alphabet
            if (i != ',' and i == lettres.get(n)): #si lettres dans alphabet alors ok
                ok =True
                break
        if (not ok):
            return False
    return True

def messageOk(message):
    message = forme(message) # formalisation du message
    for i in message:
        ok = False
        for n in range (len(lettres)): # comparaison de la lettre du message avec toute les lettres de notre alphabet
            if (i == lettres.get(n)): # lettres du message presente dans l'alphabet
                ok = True
                break
        if (not ok): # boucle finis sans trouvez la lettres dans l'alphabet
            return False
    return True


def forme(phrase):
    phrase = phrase.replace('é','e')
    phrase = phrase.replace('è','e')
    phrase = phrase.replace('à','a')
    phrase = phrase.replace('â','a')
    phrase = phrase.replace('ù','u')
    phrase = phrase.replace('ï','i')
    phrase = phrase.replace('ê','e')
    phrase = phrase.replace('ô','o')
    phrase = phrase.replace('ç','c')
    phrase = phrase.upper()
    return phrase


def crypter(phrase, clef):
    phrase = forme(phrase)
    clef = clef.upper()
    rang = 0
    nouvelPhrase = ''
    while rang < len(phrase):
        lettrePhrase = list(lettres.values()).index(phrase[rang]) # selection de l'indice de la lettre a crypter
        lettreCle = list(lettres.values()).index(clef[rang % len(clef)]) # selection de l'indice de la lettre de la cle de cryptage
        nouvelPhrase += lettres[(lettrePhrase + lettreCle) % len(lettres)] # cryptage par vigenère
        rang += 1
    return nouvelPhrase


def decrypter(phrase,clef):
    phrase = phrase.upper()
    clef = clef.upper()
    rang = 0
    nouvelPhrase = ''
    while rang < len(phrase):
        lettrePhrase = list(lettres.values()).index(phrase[rang]) # selection de l'indice de la lettre a crypter
        lettreCle = list(lettres.values()).index(clef[rang % len(clef)]) # selection de l'indice de la lettre de la cle de cryptage
        nouvelPhrase += lettres[(lettrePhrase - lettreCle) % len(lettres)] # decryptage par vigenère
        rang += 1
    return nouvelPhrase


def clefSession(clef1,clef2):
    ks = '' # initialisation de la clef de session
    if (len(clef1) > len(clef2)): 
        longeurClef = random.randint(len(clef2), len(clef1)) # creation de la longeur de la cle de session
    else :
        longeurClef = random.randint(len(clef1), len(clef2))
    for i in range(longeurClef):
        choixClef = random.randint(1,2) # tirage de la cle a utiliser pour le caractere de rang i
        if (choixClef == 1):
            ks += clef1[random.randint(1,len(clef1) - 1)] # si clef 1 tiré alors choix du caractere de clef 1 a utilise pour ajouter a la cle de session
        else:
            ks += clef2[random.randint(1,len(clef2) - 1)] # si clef 2 tiré alors choix du caractere de clef 2 a utilise pour ajouter a la cle de session
    return ks
