texte = 'antoine'
clef = 'b'

lettres = {}

for i in  range (ord('A'),ord('Z') + 1):
    lettres[i - ord('A')] = chr(i)
lettres[26] = ' '
for i in range(27,37):
    lettres[i] = i - 27

def crypter(phrase, clef):
    phrase = phrase.upper()
    clef = clef.upper()
    rang = 0
    nouvelPhrase = ''
    while rang < len(phrase):
        nouvelPhrase += lettres[(list(lettres.values()).index(phrase[rang]) + list(lettres.values()).index(clef[rang % len(clef)])) % len(lettres)]
        rang += 1
    return nouvelPhrase

def decrypter(phrase,clef):
    phrase = phrase.upper()
    clef = clef.upper()
    rang = 0
    nouvelPhrase = ''
    while rang < len(phrase):
        nouvelPhrase += lettres[(list(lettres.values()).index(phrase[rang]) - list(lettres.values()).index(clef[rang % len(clef)])) % len(lettres)]
        rang += 1
    return nouvelPhrase

print(lettres)