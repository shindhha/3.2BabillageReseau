import multiprocessing as mp


class SimpleReceiver(mp.Process):
    """
    SimpleReceiver est un processus qui va écouter le socket et mettre les messages reçus dans une file. L'objectif
    de pouvoir facilement terminer la connexion ainsi que les threads qui s'occupent du traitement des messages grâce
    à la méthode terminate() de multiprocessing.Process (qui n'existe pas pour threading.Thread).

    La file contient toujours le message reçu en première position, et le serveur qui a envoyé le message en deuxième
    """

    def __init__(self, socket):
        super().__init__()
        self.queue_recv = mp.Queue()
        self.socket = socket

        self.start()  # Démarrage automatique du processus lors de la création de l'objet

    def run(self):
        while True:
            msg, server = self.socket.recvfrom(2048)
            self.queue_recv.put(msg.decode())
            self.queue_recv.put(server)

    def terminate(self) -> None:
        self.queue_recv.put('end')  # Message de fin pour les boucles infinies
        self.queue_recv.put('end')  # Message de fin pour les boucles infinies

        super().terminate()
        print('SimpleReceiver terminé')
