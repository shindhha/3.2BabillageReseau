from Client import Client
import socket
import cryptage
from random import randrange

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def relierSocket (client):
    global s
    while client.port == None:
        try :
            client.port = randrange(12345,55555) # choix du port aleatoire
            s.bind(('127.0.0.1',client.port)) # test bind socket sur le port choisit
            client.coordonee = ('127.0.0.1', client.port) # stockage coordonee client
        except OSError: # verification port non utilisé
            client.port = None

def reception(client):
    global s
    while client.go:
        (reponse,client.coord_Serveur) = s.recvfrom(1024) # reception des message en provenence du serveur
    
        phrase = reponse.decode() # recupere la reponse envoyé par le serveur
        verif = cryptage.decrypter(phrase, client.clefTemporaire)

        #TODO faire refus connection
        if (client.ks != None): 
            verif = cryptage.decrypter(phrase,client.ks)
            if (verif == 'T5'):
                print ('vous etes connectez a ' + client.destinataire)
            elif (verif == 'T0'):
                print (client.destinataire + 'a refuser votre demande de communication')
                client.ks = None
                client.destinataire = None
            elif (verif[len(phrase) - 2] + verif[len(phrase) - 1] == 'T6'): # reception du message du correspondant 
                if (verif[0:len(phrase) - 2] == 'fin'): # verification si demande de fin de communication 
                    print (client.destinataire + 'a mit fin a la discussion')
                    client.destinataire = None
                    client.ks = None
                else: # sinon affichage du message recu
                    print ('Vous avez un nouveau message de ' + client.destinataire + " :")
                    print (verif[0:len(phrase) - 2])

        if (phrase[len(phrase)-2] +  phrase[len(phrase) - 1] == 'T0'): # recuperation du message d'erreur en cas de problemes sur le serveur
            client.ks = None
            client.destinataire = None
            print (phrase[0:len(phrase) - 2])

        if (phrase[len(phrase) - 2] + phrase[len(phrase) - 1] == 'T1'): # verification commande d'ajout de la clé effectuer
            print ("echec de l'ajout de la clé")
        elif (verif[len(phrase) - 2] + verif[len(phrase) - 1] == 'T1'): # verification cas echec ajout de la clé
            client.clef = client.clefTemporaire
            print("ajout de la clef avec succès")

        if (client.clef != None):
            verifvraie = cryptage.decrypter(phrase,client.clefTemporaire)
            veriffaux = cryptage.decrypter(phrase,client.clef)
            if (verifvraie[len(phrase) - 2] + verifvraie[len(phrase) - 1] == 'T2'): # verification commande de modification de clé bien exécuté
                client.clef = client.clefTemporaire
                print("modification de la clef avec succès")
            elif (veriffaux[len(phrase) - 2] + veriffaux[len(phrase) - 1] == 'T2'): 
                print ("echec de la modification de la clé")
        

        verif = cryptage.decrypter(phrase,client.clefTemporaire)
        if (verif[len(phrase) - 2] + verif[len(phrase) - 1] == 'T3'): # verification commande de supression de clef bien exécuté
            client.clef = None
            print("suppression de le clef avec succès")
        elif (verif[len(phrase) - len(client.nomArbitre) : len(phrase) - 1] == client.nomArbitre):
            print("echec de la supression de la clef")
        
        if (client.clef != None):
            veirf = cryptage.decrypter(phrase,client.clef)
        tabPartieA = verif.split(',')
        if (len(tabPartieA) > 3 and tabPartieA[2] == 'T4'): # verification reception de la clef de session
            try:
                client.ks = tabPartieA[3]
                longeurPartieA = len(tabPartieA[0]) + len(tabPartieA[1]) + len(tabPartieA[2]) + len(tabPartieA[3]) + 4 # recuperation de la longeur de la partie coder avec la clef de A
                s.sendto(verif[longeurPartieA:len(verif)].encode(),client.coord_Serveur)
            except Exception as e:
                raise e

        if (client.clef != None):
            verif = cryptage.decrypter(phrase, client.clef)
        tableau = verif.split(',')
        if (len(tableau) == 4 and tableau[2] == client.nom.upper()):
            print ('Vous avez une nouvelle demande de connexion en attente, tapez un caractere quelconque pour la consulter')
            reponse = input("     **********************************************\n"
                           +"     *                                            *\n"
                           +"     *            DEMANDE DE CONNEXION            *\n"
                           +"     *                                            *\n"
                           +"     **********************************************\n\n"
                           +"         Vous avez une demande de connexion de \n"
                           +"                       " + tableau[1] + "\n\n"
                           +"         - Entrez 'oui' pour accepter\n"
                           +"         - Entrez autre chose pour refuser\n ")

            if (reponse == 'oui'):
                client.ks = tableau[3]
                client.nomConnection = tableau[1]
                confirmation = cryptage.crypter(client.nom + ',' + tableau[1] + ',T5',client.ks) # codage du message d'aceptation de communication
                s.sendto(confirmation.encode(),client.coord_Serveur)
            else:
                client.ks = None
                client.nomConnection = None
                confirmation = cryptage.crypter('T0',tableau[3]) #codage du message de refus de communicaton
                s.sendto(confirmation.encode(),client.coord_Serveur)

def t1(client):
    global s
    if (client.clef == None):
        nouvelleClef = input('entrez la clef: ')
        if (not cryptage.cleOk(nouvelleClef)):
            print ('la cle contient un caractere speciale non autorise')
        else:
            message = client.nom + ',' + client.nomArbitre + ',T1,' + nouvelleClef # creation du message de création d'une clé
            client.clefTemporaire = nouvelleClef

            s.sendto(message.encode(), client.coord_Serveur) # envoie du message au serveur

            print("En attente de verification .....")

    else:
        print("vous possedez deja une clef privee")


def t2(client):
    global s
    if (client.clef != None):
        nouvelleClef = input('entrez la nouvelle clef: ')
        client.clefTemporaire = nouvelleClef
        message = client.nom + ',' + client.nomArbitre + ',' + cryptage.crypter("T2," + client.clef + "," + nouvelleClef,client.clef) # creation du message de modification de la clé
        s.sendto(message.encode(), client.coord_Serveur) # envoie du message au serveur

        print("En attente de verification .....")

    else:
        print("votre clef n'est pas initialisée")



def t3(client):
    global s
    if (client.clef != None):
        message = client.nom + ',' + client.nomArbitre + ',' + cryptage.crypter('T3,' + client.clef, client.clef) # creation du message de suppression de la clé
        s.sendto(message.encode(),client.coord_Serveur) # envoie du message au serveur

        print("En attente de verification .....")
        
    else:
        print("votre clef n'est pas initialisé")


def t4(client):
    global s
    if (client.clef != None):
        if (client.nomConnection == None):
            utilisateurB = input('entrez le nom de l\'utilisateur avec qui comuniquer: ')
            message = cryptage.crypter(client.nom + ',' + client.nomArbitre + ',' + utilisateurB + ',T4',client.clef) #creation du message de demande de communication avec un utilisateur
            s.sendto(message.encode(),client.coord_Serveur) # envoie du message au serveur
            client.nomConnection = utilisateurB

            print("En attente de verification .....")
        else:
            message = input('entrez le message que vous souhaitez envoyé a votre correspondant (entrez \'fin\' pour mettre fin a la communication) : \n')
            if (cryptage.messageOk(message)):
                message = cryptage.crypter(message + 'T6',client.ks)
                s.sendto(message.encode(),client.coord_Serveur)
                print ('Message envoyé !!')
            else:
                print('Votre message contient des caractere speciaux non traités, il n\'as pas été envoyé')
    else: 
        print ("votre clef n'est pas initialisé")