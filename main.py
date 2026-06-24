import numpy as np
import random

rng = np.random.default_rng()

class RandomizedSet:   # O(1) implementation for a random set

    def __init__(self):
        self.lst = []
        self.idx_map = {}
    
    def __str__(self):
        return "{" + ", ".join(str(i) for i in self.lst) + "}"

    def search(self, val):
        return val in self.idx_map

    def insert(self, val):
        if self.search(val):
            return False

        self.lst.append(val)
        self.idx_map[val] = len(self.lst) - 1
        return True

    def remove(self, val):
        if not self.search(val):
            return False

        idx = self.idx_map[val]
        self.lst[idx] = self.lst[-1]
        self.idx_map[self.lst[-1]] = idx
        self.lst.pop()
        del self.idx_map[val]
        return True

    def getRandom(self):
        return tuple(rng.choice(self.lst))


class Ferromagnet():

    def __init__(self, shape):
        self.shape = shape    # shape should be a tuple: (N, M)
        self._iters = 0       # keeps track of update iterations
        self._lattice = self._fill_lattice()    # numpy array N x M, with random spin configuration
        self._energetic_cells = self._init_energetic_cells()   # RandomizedSet with energetically unfavourable spin coordinates

    def _fill_lattice(self):
        A = np.zeros(self.shape)
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                r = rng.random()
                if r < 0.5:
                    spin = 1
                else:
                    spin = -1
                A[i, j] = spin
        return A
    
    def _locally_favourable(self, coord):
        check_coords = set()

        # adding top and bottom first
        if coord[0] == 0:                     # if its on top edge
            check_coords.add((coord[0] + 1, coord[1]))
        elif coord[0] == self.shape[0] - 1:   # if its on bottom edge
            check_coords.add((coord[0] - 1, coord[1]))
        else:                                 # if its somewhere in between
            check_coords.add((coord[0] - 1, coord[1]))
            check_coords.add((coord[0] + 1, coord[1]))
        
        # adding left and right second
        if coord[1] == 0:                     # if its on top edge
            check_coords.add((coord[0], coord[1] + 1))
        elif coord[1] == self.shape[1] - 1:   # if its on bottom edge
            check_coords.add((coord[0], coord[1] - 1))
        else:                                 # if its somewhere in between
            check_coords.add((coord[0], coord[1] - 1))
            check_coords.add((coord[0], coord[1] + 1))

        # computing energy favourability
        local_field = 0
        for check_coord in check_coords:
            local_field += self._lattice[check_coord]
        # energy favourability is purely dependend on local alignment
        if self._lattice[coord] * local_field >= 0:
            return True       # spin is aligned with local field
        return False          # spin not aligned with local field

    def _init_energetic_cells(self):
        C = RandomizedSet()
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if not self._locally_favourable((i, j)):
                    C.insert((i, j))
        return C
    
