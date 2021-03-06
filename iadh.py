# -*- coding: utf-8 -*-

from parsa import *
from auxiliaire import beauMot, animation
from auxiliaire import choix as chx 

class Joueur:
    # ces attributs n'apparaissent pas dans le diagramme de classe car peu
    # pértinent.
    __MENU1 = {str(i) for i in range(9)}
    __MENU2 = {str(i) for i in range(7)}
    __VIDE = '   '

    def __init__(self, nom):
        self.__defausse = False             # True qd joueur décide défausse
        self.__priorite = False             # True quand une botte est utilisée
        self.__n200, self.__score = 0, 0    # compteur de carte 200 et score
        self.nom = nom                      # nom du joueur

        self.__choix = 99                   # carte choisie
        self.__main = []                    # main du joueur

        # La table est composée de 4 piles :
        # 0: pile de bataille
        # 1: pile de de vitesse
        # 2 et au delà: pile de bottes
        self.__table = [Attaque('feu'), Parade('vitesse')]

    def __str__(self):
        # mise en forme du contenu de la table
        p = ', '.join(beauMot(c.abreviation()) for c in self.__table[:2])
        b = ' '.join(c.abreviation() for c in self.__table[2:]) or self.__VIDE

        return f"{self.nom:4} - {self.score:3} km [ {p:8} | {b} | {self.__n200}*200 ]"

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #

    @property
    def choix(self):
        return self.__choix

    @property
    def priorite(self):
        return self.__priorite

    @property # obligé pour que la main soit visible à l'enregistrement
    def main(self):
        return self.__main

    @property
    def n200(self):
        return self.__n200

    @property
    def score(self):
        return self.__score

    @property
    def table(self):
        return self.__table

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #

    @classmethod
    def rappel(self, seq):
        """Rappelle un joueur par une séquence de caractères `seq` qui le
        caractérise."""

        main, table, nom, score = seq.split(';')

        # traduction des cartes constituant la séquence
        main = [Carte.traduction(mot) for mot in main.split(',')]
        table = [Carte.traduction(mot) for mot in table.split(',')]       

        j = Joueur(nom)

        j.__main, j.__table, j.__score = main, table, int(score)

        return j

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #

    def choisir(self):
        """Ouvre le menu principal du joueur et lui donne le choix de l'action.
        """

        # À ce moment du jeu, le joueur n'a plus à avoir de priorité.
        self.__priorite = False

        print("\n" + f"Au tour de {self} :")

        # Liste la main
        animation(self)
        for i, carte in enumerate(self.__main):
            print(f"{i}: {carte}")
        print("-"*42)

        print('7:Défausser    8:Sauver et quitter')

        choix = input("Que faire [0-8] ? ")

        while choix not in self.__MENU1:
            choix = input("Saisie invalide. Que faire [0-8] ? ")

        # Une redondance mais qui facilite d'autres parties du programme.
        choix = int(choix)
        self.__choix = choix

        return choix

    # ------------------------------------------------------------------ #

    def cibler(self, joueurs):
        # inutile de faire intervenir le joueur quand il n'y en a que deux
        if len(joueurs) == 2:
            return joueurs[1] if joueurs[0] == self else joueurs[0]

        else:
            print()
            # construction de la liste des cibles
            menuCible = []
            for i, j in enumerate(joueurs):
                if j is not self:
                    menuCible.append(i)
                    print(f"{i}: {j}")

            # choix de la cible
            print(f"Qui attaquer {menuCible} ? ", flush=True, end='')

            choixCible = chx(menuCible)

        return joueurs[choixCible]

    # ------------------------------------------------------------------ #

    def defausser(self):
        choix = input("Quelle carte défausser [0-6] ? ")

        while choix not in self.__MENU2:
            choix = input("Saisie invalide. Quelle carte défausser [0-6] ? ")

        return self.__main.pop(int(choix))

    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #

    def jouerCarte(self, joueurs):
        """Interaction carte à table et carte à main."""

        carte = self.__main[self.__choix]

        if type(carte) is Attaque:
            cible = self.cibler(joueurs)
            cible.__priorite = carte.interagir(cible.__table, cible.__main)

        else:
            self.__priorite = carte.interagir(self.__table)

    # ------------------------------------------------------------------ #

        if type(carte) is Distance and carte.valide:
            # Validation finale si
            # 1. moins de 2 cartes 200 bornes jouées
            # 2. score inférieur à 1000 bornes

            if ((carte.famille < 200 or self.__n200 < 2) and    # 1
                carte.famille + self.__score <= 1000):          # 2

                self.__n200 += (carte.famille == 200)
                self.__score += carte.famille

            else:               # La vérification finale aboutit à un refus.
                return False    # not carte.valide
        
    # ------------------------------------------------------------------ #

        # si la carte est valide, on l'enlève de la main
        if carte.valide:
            self.__main.pop(self.__choix)

        # on renvoie la validité de l'action
        return carte.valide

    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #

    def piocher(self, partie, nbrCartes=7):
        while len(self.__main) < nbrCartes and partie.pioche:
            self.__main.append(partie.pioche.pop(0))

    # ------------------------------------------------------------------ #
