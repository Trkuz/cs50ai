import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        #self.domains maps to a variable, all possibles values that variable can take(in the beggining its all varibles,
        #as we didnt include any of the contraints yet)
        self.crossword = crossword #crossword = Crossword(structure, words)
        self.domains = {
            var: self.crossword.words.copy()# var1: {w1,w2,w3,w4}, var2: {w1,w2,w3,w4}, var3: {w1,w2,w3,w4}
            for var in self.crossword.variables# self.domains.var = var1, self.domain.words = {w1,w2,w3,w4}
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        #enfornce node consistency: ensures that all values in variable domain satisfies unary constraints
        self.enforce_node_consistency()
        self.ac3() #ac3 ensures that all values i variable satisfies binary constraints
        return self.backtrack(dict()) #runs backtracking search algorithm on assigment and finds the solution

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        not_consistent = dict()

        #iterates thorugh the domains checking which words are of different length than length of variable,
        #then adding them do not_consisten dictionary
        for var, words in self.domains.items():
            for word in words:
                if var.length() != len(word):
                    not_consistent[var] = word

        #iterating through not_consisted dictionary, deleting all the values that doesnt meet unary constraints
        for var, words in not_consistent.items():
            for word in words:
                self.domains[var].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        change = False
        #lap[x,y] indeces of x and y where they both overlap with each other
        lap = self.crossword.overlaps[x,y]
        #iterating through all the values in x and y domain
        for x_val in self.domains[x]:
            truth_table = []
            for y_val in self.domains[y]:
                #if overlapping index of word in x domain is not the same as overlapping index of word in y, append False
                if x_val[lap[0]] != y_val[lap[1]]:
                    truth_table.append(False)
                #else append True
                else:
                    truth_table.append(True)

            #truth table contains True if x domain value is consistent with at least one of the y domain value
            if not any(truth_table):
                self.domains[x].remove(x_val)
                change = True

        return change

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        #function revie takes only variables names, so queue items should only
        #be varaible names
        queue = []
        #apppend all the arc to the queue
        if not arcs:
            for var, _ in self.domains.items():
                queue.append(var)
        #self.crossword.neighbour(x) return only names of neighbouring variables without its values
        while queue:
            #get first two value of the queue and check arc consistency between them
            x,y = queue.pop(0), queue.pop(1)
            if self.revise(x,y):
                if not self.domains[x]: #if variables have no values, then arc consistency cant be kept, so return False
                    return False
                #if changes was made, add element neighbours to the queue
                for element in [self.crossword.neighbors(x) - y]:
                    queue.append(element) #appends only variable name without its values

        return True



    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        vals = []
        for var, value in assignment.items():
            if len(var[value]):
                vals.append(True)
            else:
                vals.append(False)

        if all(vals):
            return True

        return False

    def consistent(self, assignment): #assigment always have full number of variables as they
                                      #are created at the start of the program
                                      #while initializing CrosswordCreator class
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        ac3 = self.ac3()
        self.enforce_node_consistency()

        if ac3:
            return True

        return False

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """



        #doesn't change the order of variables
        return [var for var, _ in self.domains.items()]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """


        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
