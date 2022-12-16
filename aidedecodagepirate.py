aDecoder = input('entrez le message a decoder manuellement : \n')
longeurCle = 4

sousPhrase = ['','','','']

for i in range (len(aDecoder)):
    sousPhrase[i % longeurCle] += aDecoder[i]

print('\n')

for i in range(longeurCle):
    print (sousPhrase[i])


for n in range(longeurCle): # boucle sur les 4 sous-message
    repetition = {} # dictionnaire recapitulant les repetitions de chaque lettres dans les sous-message
    somme = 0
    for i in sousPhrase[n]: # selection des caracteres de la sous-message 1 par 1
        if (n == 0):
            print (i)
        if (repetition.get(i,"None") == "None"): # verification si lettre deja dans dictionnaire ou premiere apparition
            repetition[i] = 1 # cas premiere apparition: ajout de la lettre dans le dictionaire et nombre d'apparition a 1
        else:
            repetition[i] = repetition.get(i) + 1 # cas deja dans le dictionaire: ajout de 1 au nombre d'aparition de la lettre
    print ("\n")
    print (repetition)
    for i in repetition:
        somme += repetition.get(i)
    print (somme)