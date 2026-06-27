import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import copy
import csv

rng = np.random.default_rng()


class RandomizedSet:   # O(1) implementation for a random set

    def __init__(self):
        self.lst = []
        self.idx_map = {}
    
    def __str__(self):
        return "{" + ", ".join(str(i) for i in self.lst) + "}"
    
    def __len__(self):
        return len(self.lst)

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
        self.lattice = self._fill_lattice()    # numpy array N x M, with random spin configuration
        self._energetic_cells = self._init_energetic_cells()   # RandomizedSet with energetically unfavourable spin coordinates
        self.stabilized = False    # not true in general, but it is very unlikely it will initiallize in a metastable state


    def __getitem__(self, coords):
        return self.lattice[coords]
    

    def __setitem__(self, coord, value):
        if value not in (1, -1):
            raise TypeError("Spin can only take values +1 and -1")
        self.lattice[coord] = value
        self._update_local_neighbourhood(coord)


    def _get_neighbourhood(self, coord):   # neighbouring sites (excluding itself) 
        neighbour_coords = set()
        # adding top and bottom first
        if coord[0] == 0:                     # if its on top edge
            neighbour_coords.add((coord[0] + 1, coord[1]))
        elif coord[0] == self.shape[0] - 1:   # if its on bottom edge
            neighbour_coords.add((coord[0] - 1, coord[1]))
        else:                                 # if its somewhere in between
            neighbour_coords.add((coord[0] - 1, coord[1]))
            neighbour_coords.add((coord[0] + 1, coord[1]))

        # adding left and right second
        if coord[1] == 0:                     # if its on top edge
            neighbour_coords.add((coord[0], coord[1] + 1))
        elif coord[1] == self.shape[1] - 1:   # if its on bottom edge
            neighbour_coords.add((coord[0], coord[1] - 1))
        else:                                 # if its somewhere in between
            neighbour_coords.add((coord[0], coord[1] - 1))
            neighbour_coords.add((coord[0], coord[1] + 1))
        
        return neighbour_coords
    

    def _update_local_neighbourhood(self, coord):   # updates _energetic_cells by looking at local neigbourhood
        # need to check coord itself, and the other 4 (unless its a corner or edge)
        neighbour_coords = self._get_neighbourhood(coord)
        neighbour_coords.add(coord)    # also adding center site
        for ne_coord in neighbour_coords:
            if self._locally_favourable(ne_coord):
                self._energetic_cells.remove(ne_coord)     # if its not in it, False will simply be returned (RandomSet convention)
            else:
                self._energetic_cells.insert(ne_coord)     # add to energetic cells


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
        check_coords = self._get_neighbourhood(coord)
        # computing energy favourability
        local_field = 0
        for check_coord in check_coords:
            local_field += self.lattice[check_coord]    # adding each local spin
        # energy favourability is purely dependend on local alignment
        if self.lattice[coord] * local_field > 0:
            return True       # spin is aligned with local field
        return False          # spin not aligned with local field or equally in both directions


    def _init_energetic_cells(self):
        C = RandomizedSet()
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if not self._locally_favourable((i, j)):
                    C.insert((i, j))
        return C
    

    def plot(self, save=False, title=""):
        plt.imshow(self.lattice, cmap="plasma")
        plt.colorbar()
        if title:
            plt.title(title)
        if save:
            count = 0    # using this variable to label each image differently
            with open("./images/.image_count.txt", "r") as file:
                content = file.read()
                count = int(content)
            plt.savefig(f"./images/plot_{title}_count_{count}.png")
            count += 1
            with open("./images/.image_count.txt", "w") as file:
                file.write(str(count))
        plt.show()


    def energetic_update(self):
        """flip a random energetic cell and update the energetic cells set"""
        coord = self._energetic_cells.getRandom()
        old_spin = self.__getitem__(coord)
        new_spin = old_spin * -1
        self.__setitem__(coord, new_spin)   # flip, energetic cell update is done automatically
        if len(self._energetic_cells) == 0:
            self.stabilized = True

    def get_energy(self):
        E = 0
        # pairwise along the rows
        for j in range(self.shape[1]):
            for i in range(self.shape[0] - 1):
                E += -1 * self.lattice[i, j] * self.lattice[i + 1, j]
        # pairwise along the columns
        for i in range(self.shape[0]):
            for j in range(self.shape[1] - 1):
                E += -1 * self.lattice[i, j] * self.lattice[i, j + 1]
        return E
    

    def minimize_energy(self):
        """reach a metastable state by flipping spins until energetic_spins set is empty"""
        while len(self._energetic_cells) > 0:
            self.energetic_update()
            print(f"\rNumber of Energetic Cells: {len(self._energetic_cells)} ", end="")   # comment this out when not debugging
        self.stabilized = True

    
    def classify(self):
        if self.stabilized == False:
            return "unstable"
        else:
            # checking for horizontal stripes
            for i in range(self.shape[0] - 1):
                if self.__getitem__((i, 0)) != self.__getitem__((i + 1, 0)):
                    return "horizontal"
            # checking for vertical stripes
            for j in range(self.shape[1] - 1):
                if self.__getitem__((0, j)) != self.__getitem__((0, j + 1)):
                    return "vertical"
            # if neither, then it has to be uniform
            return "uniform"


def sample_metastable_state(shape):
    """Collect 1 sample final state classification from a initially random ferromagnet"""
    A = Ferromagnet(shape)
    A.minimize_energy()
    calssification = A.classify()
    return calssification


def accumulate_stats(shape):
    """sample a metastable state classification from a ferromagnet and write to disk"""
    classification = sample_metastable_state(shape)

    try:
        data = []
        # loading the data into memory
        with open(f"./statistics/metastable_N={shape[0]}_M={shape[1]}.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
        
        # updating the data
        if classification == "uniform":
            data[1][1] = str(int(data[1][1]) + 1)
        elif classification == "horizontal":
            data[2][1] = str(int(data[2][1]) + 1)
        elif classification == "vertical":
            data[3][1] = str(int(data[3][1]) + 1)

        # writing the updated data to disk
        with open(f"./statistics/metastable_N={shape[0]}_M={shape[1]}.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(data)

    except FileNotFoundError:
        # initializing the data
        data = [["metastable state", "count"],
                ["uniform", 0],
                ["horizontal", 0],
                ["vertical", 0]]
        
        # updating the initialized data
        if classification == "uniform":
            data[1][1] += 1
        elif classification == "horizontal":
            data[2][1] += 1
        elif classification == "vertical":
            data[3][1] += 1
        
        # writing the data to disk
        with open(f"./statistics/metastable_N={shape[0]}_M={shape[1]}.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(data)


def make_animation(A, n_updates, save_title="", spacing=1):
    """For title don't specify the file type (it will automatically be .mp4)"""
    states = []
    states.append(copy.deepcopy(A.lattice))
    for i in range(n_updates):
        A.energetic_update()
        if (i + 1) % spacing == 0:
            states.append(copy.deepcopy(A.lattice))
        print(f"\r{i + 1} / {n_updates}", end="", flush=True)   # this is here for sanity

    fig, ax = plt.subplots()

    im = ax.imshow(states[0], cmap="plasma", animated=True)

    def update(i):
        im.set_data(states[i])
        print(f"\rFrame {i+1}/{len(states)}", end="", flush=True)
        return [im]
    
    ani = FuncAnimation(
        fig,
        update,
        frames=len(states),
        interval=0.00001,
        blit=True,
        repeat=False
    )

    if save_title:
        ani.save(
            f"./animations/{save_title}.gif"
            )

    plt.show()


def make_metastable_animation(A, save_title="", spacing=1):
    """For title don't specify the file type (it will automatically be .gif)"""
    states = []
    states.append(copy.deepcopy(A.lattice))
    iter = 0
    while not A.stabilized:
        iter += 1
        A.energetic_update()
        if iter % spacing == 0:    # only add 1 in every spacing to the states
            states.append(copy.deepcopy(A.lattice))
        print(f"\r{len(A._energetic_cells)} ", end="")    # this is here for sanity
    states.append(copy.deepcopy(A.lattice))

    fig, ax = plt.subplots()

    im = ax.imshow(states[0], cmap="plasma", animated=True)

    def update(i):
        im.set_data(states[i])
        print(f"\rFrame {i+1}/{len(states)}", end="", flush=True)
        return [im]
    
    ani = FuncAnimation(
        fig,
        update,
        frames=len(states),
        interval=0.00000001,    # setting it to the minimum
        blit=True,
        repeat=False
    )

    if save_title:
        ani.save(
            f"./animations/{save_title}.gif"
            )

    plt.show()


A = Ferromagnet((120, 120))

# making a line down the middle
for i in range(80, 120):
    for j in range(120):
        A[i, j] = -1

make_metastable_animation(A, save_title="special_200_200_animation", spacing=200)


# A = Ferromagnet((120, 120))
# make_metastable_animation(A, "test_video1", spacing=40)


# for i in range(100):
#     print(f"\n{i + 1} / 100")
#     accumulate_stats((50, 50))
