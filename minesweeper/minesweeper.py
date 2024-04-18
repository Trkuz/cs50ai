import itertools
import random
import copy
from sympy import Eq, solve, symbols
class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=12):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines

    def mines_count(self):
        return len(self.mines)


class Sentence():# DONE
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count


    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __ne__(self, other):
        return self.cells != other.cells

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(list(self.cells)):
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set()


    def mark_mine(self, cell):

        if cell in self.cells:
            self.count -= 1
            self.cells.remove(cell)



        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

    def mark_safe(self, cell): #git
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count): #TODO
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """

        self.moves_made.add(cell)
        self.mark_safe(cell)
        neighbours = set()

        for x in range(cell[0]-1, cell[0]+2):
            for y in range(cell[1]-1,cell[1]+2):
                if x < 0 or x > 7 or y < 0 or y > 7:
                    continue
                else:
                    if (x,y) == cell or (x,y) in self.safes or (x,y) in self.moves_made:
                        continue
                    else:
                        neighbours.add((x,y))

        nbr = copy.deepcopy(neighbours)
        self.knowledge.append(Sentence(nbr,count))
        neighbours.clear()

        for sentence in self.knowledge:
            if len(sentence.cells) == sentence.count:
                snt = copy.deepcopy(sentence.cells)
                for element in snt:
                    self.mark_mine(element)

            if sentence.count == 0:
                snt = copy.deepcopy(sentence.cells)
                for element in snt:
                    self.mark_safe(element)
                self.knowledge.remove(sentence)


        for sentence in self.knowledge:
            for cell in self.mines:
                if cell in sentence.cells:
                    sentence.cells.remove(cell)
                    sentence.count -= 1

            if sentence.count == 0:
                snt = copy.deepcopy(sentence.cells)
                for element in snt:
                    self.mark_safe(element)
                self.knowledge.remove(sentence)

        kwg2 = copy.deepcopy(self.knowledge)

        for sent1 in self.knowledge:
            for sent2 in kwg2:
                if sent2.cells.issubset(sent1.cells) and (len(sent1.cells) > len(sent2.cells)):
                    for cell in sent2.cells:
                        sent1.cells.remove(cell)
                    sent1.count -= sent2.count
                    print(f"po usunieciu: {sent1.cells},   {sent1.count}")

        kwg2 = copy.deepcopy(self.knowledge)


        #find safes and mines from sentences with two common cells and different cell count, sentences must contain at lest 3 cells:
        for sent1 in self.knowledge:
            for sent2 in kwg2:
                #only take equation that differ from each other by 2 elements
                if len(sent1.cells) == len(sent2.cells) and len(set.union(sent1.cells.difference(sent2.cells),
                                                                     sent2.cells.difference(sent1.cells))) == 2\
                                                        and sent2.count != sent1.count\
                                                        and len(sent1.cells) >  2:
                    syms = ["a", "b"]
                    dicttup = {}

                    rside = sent1.count - sent2.count #right side of equation
                    lside = [] #left side of equation

                    lside.append(sent1.cells.difference(sent2.cells)) #list to keep the order
                    lside.append(sent2.cells.difference(sent1.cells))

                    for x in range(len(lside)):
                        dicttup[syms[x]] = val[x] #key: sympy symbol, value: equation left side symbol

                    dictsymb = {element: symbols(element) for element in dicttup}

                    eq = Eq(dictsymb['a'] - dictsymb['b'], rside)
                    a_expr = solve(eq, dictsymb['a'])[0]
                    valid_solution = []
                    for b_val in range(2):
                        a_val = a_expr.subs({dictsymb['b']: b_val})

                        if all(val in [0,1] for val in (a_val, b_val)): #check is all symbols are either 0 or 1
                            valid_solution.append(a_val)
                            valid_solution.append(b_val)

                    for key, value in dictsymb.items():
                        dictsymb[key] = valid_solution[0]
                        valid_solution.pop(0)


                    #dicttup = {'a' : {(4,6), 'b': (3,3)}
                    # dictsymb = {'a': 0, 'b' : 1 }

                    #replace dicttup keys with solutions

                    sol = {dictsymb[key]: value for key, value in dicttup.items()}
                    #sol = {0 : {(4,6)}, 1:{7,6}}

                    #marking safe cell or mine:
                    for key, value in sol.items():
                        if key == 0:
                            self.mark_safe(list(value)[0])
                        else:
                            self.mark_mine(list(value)[0])

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        Return None if there is none safe move to make

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if self.safes:
            (x,y) = random.choice([x for x in self.safes])
            while True:
                if (x,y) in self.moves_made:
                        if len(self.safes) == len(self.moves_made):
                            return None
                        else:
                            (x, y) = (random.choice(list(self.safes)))
                else:
                    return (x,y)
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        (x,y) = (random.choice(range(0,8)), random.choice(range(0,8)))
        while True:
            if 64 - len(self.moves_made) == len(self.mines):
                return None
            if (x,y) in self.moves_made:
                (x, y) = (random.choice(range(0, 8)), random.choice(range(0, 8)))
                continue
            if (x, y) in self.mines:
                (x, y) = (random.choice(range(0, 8)), random.choice(range(0, 8)))
                continue

            else:
                return (x, y)

