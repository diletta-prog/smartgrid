from lamp import *
import numpy as np

class City:
    """ matrice sparsa dove alcuni nodi corrispondono a lampioni """

    def __init__(self,m):
        self.lampsCount = 0  # numero i lampioni
        self.lamps = []  # lista dei lampioni
        self.matrixRaw = m  # mi salvo la matrice grezza con 0 e 1
        self.matrix=np.empty(shape=np.shape(m), dtype=object)   # matrice di oggetti che saranno lampioni
        # self.matrix=np.pad(np.empty(shape=np.shape(m), dtype=object)   # matrice di oggetti che saranno lampioni, creo il borso di None
        #     ,pad_width=1,mode='constant', constant_values=None)        # per quando estraggo la submatrix
        pass

    def addLamp(self):
        '''creo la matrice di lampioni partendo da quella di 1 e 0'''
        a,b = np.where(self.matrixRaw == 1) # mi salvo le posizione degli 1
        for i in range(len(a)):
            pos = [a[i],b[i]]
            self.matrix[a[i]][b[i]] = Lamp(id=self.lampsCount, pos=pos) # inserisco oggetto lampione
            self.lamps.append(Lamp(id=self.lampsCount, pos=pos))    # salvo nella lista della città il lampione
            self.lampsCount += 1    # incremento numero lampioni
        pass


    def setLampLevel(self, id, level):  # setto livello lampada
        self.lamps[id].setLevel(level)  # sia nella lista della città
        a,b = self.lamps[id].getPos()
        self.matrix[a][b].setLevel(level)   # sia nella matrice
        pass
    
    def setLampState(self, id, state):  # setto stato lampada
        self.lamps[id].setState(state)  # sia nella lista della città
        a,b = self.lamps[id].getPos()
        self.matrix[a][b].setState(state)   # sia nella matrice
        pass

    def exctSubMatrix(self, pos):   
        '''per estrarre matrice 3x3, l'intorno del lampione, per salvare i vicini'''
        i,j = pos
        maxR, maxC = self.matrix.shape
        if i-1>=0 and j-1>=0 and i+2<=maxR and j+2<=maxC:   # controllo che la cella non sia sul borso (+2 perchè parte da 0)
            return self.matrix[i-1:i+2, j-1:j+2]
        else:
            temp=np.copy(self.matrixRaw)
            i = i+1
            j = j+1
            temp = np.pad(temp,pad_width=1,mode='constant', constant_values=None)
            return 

    def exctNeigh(self, pos):   
        '''per estrarre matrice 3x3, l'intorno del lampione, per salvare i vicini'''
        i,j = pos
        for row in range(i-1,i+2,1):    # giro intorno alla cella (matrice 3x3)
            for col in range(j-1,j+2,1):
                if (row>=0 and col>=0) and (col!=j or row!=i):  # non conto le posizioni negative (bordi) e la cella stessa
                    if self.matrix[row][col] != None:   # se la cella contiene un lampione la salvo
                        self.matrix[i][j].addNeigh(self.matrix[row][col].getID())
                        