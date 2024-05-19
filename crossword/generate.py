import sys
import random
from crossword import *
import copy

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

    def enforce_node_consistency(self): #TODO CHECK
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        #make all the word in variable domain fit the variable length

        not_consistent = {x: set() for x,y in self.domains.items()}
        #iterates thorugh the domains checking which words are of different length than length of variable,
        #then adding them do not_consisten dictionary
        for var, words in self.domains.items():
            for word in words:
                if var.length != len(word):
                    not_consistent[var].add(word)

        #iterating through not_consisted dictionary, deleting all the values that doesnt meet unary constraints
        for var, words in not_consistent.items():
            for word in words:
                self.domains[var].remove(word)




    def revise(self, x, y): #DONE (NA PEWNO)
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        #



        change = False
        #lap[x,y] indexes of x and y where they both overlap with each other
        lap = self.crossword.overlaps[x,y]
        #iterating through all the values in x and y domain
        if lap:
            val = []
            for x_val in self.domains[x]: #goes through values of the domain of x
                truth_table = []
                for y_val in self.domains[y]:
                    #if overlapping index of word in x domain is not the same as overlapping index of word in y, append False
                    if x_val[lap[0]] != y_val[lap[1]]:
                        truth_table.append(False)
                    else:
                        truth_table.append(True)

            #truth table contains True if x domain value is consistent with at least one of the y domain value
                if not any(truth_table):
                    val.append(x_val)
                    change = True

            for value in val:
                self.domains[x].remove(value)

            return change

        return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        #function revsie takes only variables names, so queue items should only
        #be variable names
        queue = []
        #apppend all the arc to the queue

        if not arcs:
            for var in self.domains:
                for neighbor in self.crossword.neighbors(var):
                    if self.crossword.overlaps[var,neighbor] is not None:
                        queue.append(var)
                        queue.append(neighbor)


        #self.crossword.neighbour(x) return only names of neighbouring variables without its values
        while queue:
            #get first two value of the queue and check arc consistency between them

            if len(queue) >= 2:
                x,y = queue.pop(0), queue.pop(0)
                if x != y:

                    revised = self.revise(x,y) #returns True if changes were made, False if not
                    if revised:
                        if not self.domains[x]: #if variables have no values, then arc consistency cant be kept, so return False
                            return False
                        #if changes was made, add element neighbours to the queue

                        neighbors = self.crossword.neighbors(x)

                        neighbors.remove(y)
                        for element in neighbors:
                            queue.append(element) #appends only variable name without its values
                            queue.append(x)
                else: #if queue first element is assigment last element then same elements gets added to prevent errors,move values by one element
                    next = queue.pop(0)
                    y_cop = copy.deepcopy(y)
                    x = y_cop
                    y = next

                    revised = self.revise(x, y)  # returns True if changes were made, False if not
                    if revised:
                        if not self.domains[x]:  # if variables have no values, then arc consistency cant be kept, so return False
                            return False
                            # if changes was made, add element neighbours to the queue

                        neighbors = self.crossword.neighbors(x)

                        neighbors.remove(y)
                        for element in neighbors:
                            queue.append(element)  # appends only variable name without its values
                            queue.append(x)


            else: #if queue contains one element,then add x, along with it neighbour(even number)
                neighbors = self.crossword.neighbors(x)
                for element in neighbors:
                    queue.append(element)
                    queue.append(x)
                queue.pop(0) # remove first element(x), to make queue even

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment): #assigment always have full number of variables as they
                                      #are created at the start of the program
                                      #while initializing CrosswordCreator class
                                      #TODO CHECK IF OVERLAPING LETTERS ARE THE SAME FOR EVERY ASSIGNMENT NODE
        """"
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # words = [*assignment.values()]
        # if len(words) != len(set(words)):
        #     return False
        #
        #                               # check if every value is the correct length
        # for variable in assignment:
        #     if variable.length != len(assignment[variable]):
        #         return False
        #
        #                               # check if there are any conflicts between neighbouring variables
        # for variable in assignment:
        #     for neighbour in self.crossword.neighbors(variable):
        #         if neighbour in assignment:
        #             x, y = self.crossword.overlaps[variable, neighbour]
        #             if assignment[variable][x] != assignment[neighbour][y]:
        #                 return False
        #
        #                               # all cases checked, no conflicts, can return True
        # return True



        ac3 = self.ac3() #def ac3(self, arcs = None) #make all the assignment nodes satisfy the arc consistency between each other
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

        num = dict()
        #iterates through neighbours of variable
        for neighbor in self.crossword.neighbors(var):
            #checks if neighbour's values is already assigned
            if neighbor in assignment.items():
                lap = self.crossword.overlaps(var, neighbor)
                for value1 in var.values():
                    if value1 not in num.keys():
                        num[value1] = 0
                    for value2 in neighbor.values():
                        #iterates through the domain of variable and neighbour
                        #and for each value ruled out by domain variable
                        #icreases value of domain key in num dictionary
                        if value1[lap[0]] != value2[lap[1]]:
                            num[value1] += 1

        #sorting the dictionary by values in ascending order
        sort = sorted(num.items(), key=lambda d: d[1])
        domains = [x for (x,y) in sort]

        return domains

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        not_assigned = {element:values for element, values in self.domains.items() if element not in list(assignment)}
        MRV = dict()

        #assaigns every variable length of its domain
        for variable, domain in not_assigned.items():
            MRV[variable] = len(domain)

        #sorting by length of domain
        s_MRV = sorted(MRV.items(), key = lambda d: d[1])
        #if two first elements are the same
        #check is it even possible to search for duplicates in MRV if not return variable of lovest MRV
        if len(s_MRV) >= 2:
            dgr = []
            #get elements that have the same MRV value
            for index,element in enumerate(s_MRV): #MRV = {(val,var) <- element}
                if s_MRV[index][1] == s_MRV[0][1]:
                    dgr.append(element)
            if len(dgr) >= 2:
                #if there are values of same MRV calculate map variable, the number of ith neighbours(degree heuristic)
                dgr = [(dgr[index][0],len(self.crossword.neighbors(dgr[index][0]))) for index, element in enumerate(dgr)]
                dgr = sorted(dgr, key = lambda d: d[1], reverse=True)
                #if it is possible to even look for duplicates in dgr values, else return value of highest degree

                rnd = []
                for index,element in enumerate(dgr):
                    if dgr[index][1] == dgr[0][1]:
                        rnd.append(element)
                    #return random value
                if len(rnd) >=2:
                    ind = random.choice(range(0, len(rnd)))
                    #if rnd is greater or equal than 2 than return random element out of rnd
                    return {rnd[ind][0]: rnd[ind][1]}.items()
                #if length rnd( random value of dgr) is less than 2 then return first element of dgr
                return {dgr[0][0]:dgr[0][1]}.items()
            #if len of MRV is less than 2 then return first element of MRV as it is the same as first elmenet of dgr
            return {s_MRV[0][0]:s_MRV[0][1]}.items()
        #it len or MRV less than 2 then return first element of MRV
        return {s_MRV[0][0]:s_MRV[0][1]}.items()




    def backtrack(self, assignment): #TODO ADD IFRENCE(REMOVE VALUE FROM ONE'S DOMAIN AFTET IT BEING ASSIGNED TO VARIABLE (COULD BE DONE IN CONSISTENT, IDK)
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        """


        if self.assignment_complete(assignment): return assignment
        var = list(self.select_unassigned_variable(assignment))[0][0]
        domain = list(self.domains[var])

        for value in domain:
            check = copy.deepcopy(assignment)
            check[var] = value

            if self.consistent(check):
                assignment[var] = value
                result = self.backtrack(assignment)
                if not (not result): return result
            check.remove(value)
        return False

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
