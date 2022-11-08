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

def forme(phrase):
    phrase = phrase.replace('é','e')
    phrase = phrase.replace('è','e')
    phrase = phrase.replace('à','a')
    phrase = phrase.replace('ù','u')
    phrase = phrase.replace('â','a')
    phrase = phrase.replace('ï','i')
    phrase = phrase.replace('ê','e')
    phrase = phrase.upper()
    return phrase