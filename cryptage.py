import random

texte = 'antoine'
clef = 'b'

lettres = {}
accent = ['é','è','ë','ê','à','â','ä','û','ü','ù','ï','î','ö','ô','ç']

# creation du dictionnaire contenant l'alphabet utiliser pour le cryptage / decryptage
for i in range (32 , 92):
    lettres[i - 32] = chr (i)
# esclusion du carcater '\'
for i in range (93 , 123):
    lettres[i - 32 - 1] = chr (i)

longeur = len(lettres)
for i in range (len(accent)):
    lettres[longeur + i] = accent[i]


def cleOk(clef: str) -> bool:
    for i in clef: # selection des lettres de la cle 1 par 1
        ok = False
        for n in range (len(lettres)): # comparaison de la lettre de la cle avec toute les lettres de notre alphabet
            if (i != ',' and i == lettres.get(n)): #si lettres dans alphabet alors ok
                ok =True
                break
        if (not ok):
            return False
    return True

def messageOk(message: str) -> bool:
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
        lettrePhrase = list(lettres.values()).index(phrase[rang]) # selection de l'indice de la lettre a crypter
        lettreCle = list(lettres.values()).index(clef[rang % len(clef)]) # selection de l'indice de la lettre de la cle de cryptage
        nouvelPhrase += lettres[(lettrePhrase - lettreCle) % len(lettres)] # decryptage par vigenère
        rang += 1
    return nouvelPhrase


def clefSession(clef1: str,clef2: str) -> str:
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


print (crypter("La raison du plus fort est toujours la meilleure : Nous l'allons montrer tout à l'heure. Un Agneau se désaltérait Dans le courant d'une onde pure. Un Loup survient à jeun, qui cherchait aventure, Et que la faim en ces lieux attirait. Qui te rend si hardi de troubler mon breuvage ? Dit cet animal plein de rage: Tu seras châtié de ta témérité. Sire, répond l'Agneau, que Votre Majesté Ne se mette pas en colère ; Mais plutôt qu'elle considère Que je me vas désaltérant Dans le courant, Plus de vingt pas au-dessous d'Elle ; Et que par conséquent, en aucune façon, Je ne puis troubler sa boisson. Tu la troubles, reprit cette bête cruelle, Et je sais que de moi tu médis l'an passé. Comment l'aurais-je fait si je n'étais pas né ? Reprit l'Agneau ; je tette encor ma mère Si ce n'est toi, c'est donc ton frère. Je n'en ai point. C'est donc quelqu'un des tiens: Car vous ne m'épargnez guère,Vous, vos Bergers et vos Chiens. On me l'a dit : il faut que je me venge. Là-dessus, au fond des forêts Le loup l'emporte et puis le mange, Sans autre forme de procès.",'lupe'))
