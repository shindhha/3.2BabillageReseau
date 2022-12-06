import cryptage
import commande
import threading

class Client:
    def __init__(self, nom):
        self.nom = nom
        self.nomArbitre = 'C'
        self.clef = None
        self.ks = None
        self.coord_S = ('127.0.0.1', 12345)
        self.coordonee = None
        self.port = None
        self.clefTemporaire = None
        self.recevoir = threading.Thread(target=commande.reception, args = (self,))
        


def creation():
    nom = input("entrez votre nom :")
    user = Client(nom)
    return user

def menu(user):
    ok = True
    while ok:
        demande = input("\nque voulez vous faire ?"
                        + "\n1 - ajouter une clef"
                        + "\n2 - modifier une clef"
                        + "\n3 - suprimer sa clef"
                        + "\n4 - comuniquer avec un utilisteur"
                        + "\n5 - quitter\n")

        if (demande == '1'):
            commande.t1(user)
        elif (demande == '2'):
            commande.t2(user)
        elif (demande == '3'):
            commande.t3(user)
        elif (demande == '4'):
            commande.t4(user)
        elif (demande == '5'):
            print ("Au revoir!")
            ok = False
        else:
            print("veuillez entrez un nombre valide")


if __name__ == "__main__":

    user = creation()
    commande.relierSocket(user)
    user.recevoir.start()
    menu(user)