import random

texte = 'antoine'
clef = 'b'

lettres = {}

for i in  range (ord('A'),ord('Z') + 1):
    lettres[i - ord('A')] = chr(i)
lettres[26] = ' '
for i in range(27,37):
    lettres[i] = str(i - 27)
lettres[37] = ','
lettres[38] = '-'
lettres[39] = '.'

def forme(phrase):
    phrase = phrase.replace('é','e')
    phrase = phrase.replace('è','e')
    phrase = phrase.replace('à','a')
    phrase = phrase.replace('ù','u')
    phrase = phrase.replace('â','a')
    phrase = phrase.replace('ï','i')
    phrase = phrase.replace('ê','e')
    phrase = phrase.replace('ô','o')
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
    longeurClef = random.randint(len(clef1), len(clef2))
    for i in range(longeurClef):
        choixClef = random.randint(1,2)
        if (choixClef == 1):
            ks += clef1[random.randint(1,len(clef1) - 1)]
        else:
            ks += clef2[random.randint(1,len(clef2) - 1)]
    return ks