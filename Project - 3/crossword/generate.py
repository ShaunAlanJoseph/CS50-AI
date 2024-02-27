import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
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
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        for var in self.domains:
            remove_these = list()
            for word in self.domains[var]:
                if len(word) != var.length:
                    remove_these.append(word)
            for word in remove_these:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False

        i, j = overlap
        remove_these = list()
        for word in self.domains[x]:
            corresp_val_found = False
            for w in self.domains[y]:
                if word[i] == w[j]:
                    corresp_val_found = True
                    break

            if not corresp_val_found:
                remove_these.append(word)

        for word in remove_these:
            self.domains[x].remove(word)

        return len(remove_these) > 0

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            arcs = list()
            keys = list(self.domains.keys())
            for x in range(len(keys) - 1):
                for y in range(x + 1, len(keys)):
                    arcs.append((keys[x], keys[y]))

        while len(arcs):
            x, y = arcs.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False

                for neighbor in self.crossword.neighbors(x):
                    if neighbor != y:
                        arcs.append((neighbor, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        return len(self.domains) == len(assignment)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # checking length consistency
        for var, word in assignment.items():
            if var.length != len(word):
                return False

        # checking distinct words
        if len(assignment) != len(set(assignment.values())):
            return False

        # checking neighbor conflicts
        for x in assignment.keys():
            for y in self.crossword.neighbors(x):
                if y not in assignment:
                    continue
                i, j = self.crossword.overlaps[x, y]
                if assignment[x][i] != assignment[y][j]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        fixed_vars = set(assignment.keys())
        domain_values = set(self.domains[var])
        neighbors = self.crossword.neighbors(var)
        for fixed_var in fixed_vars:
            if fixed_var not in neighbors:
                continue
            i, j = self.crossword.overlaps[var, fixed_var]
            remove_these = list()
            for word in domain_values:
                if word[i] != assignment[fixed_var][j]:
                    remove_these.append(word)
            for word in remove_these:
                domain_values.remove(word)

        rules_out = list()
        for word in domain_values:
            conflict_count = 0
            for neighbor in neighbors:
                if neighbor in fixed_vars:
                    continue
                i, j = self.crossword.overlaps[var, neighbor]
                for neighbor_word in self.domains[neighbor]:
                    if word[i] != neighbor_word[j]:
                        conflict_count += 1
            rules_out.append((conflict_count, word))

        if len(rules_out) == 0:
            return None

        rules_out = sorted(rules_out, key=lambda item: item[0])
        return [word[1] for word in rules_out]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        not_assigned = list(self.domains.keys())
        for var in assignment:
            not_assigned.remove(var)

        priority = list()
        for var in not_assigned:
            word_count = len(self.domains[var])
            neighbor_count = len(self.crossword.neighbors(var))
            priority.append((word_count, -neighbor_count, var))

        priority = sorted(priority, key=lambda item: (item[0], item[1]))

        return priority[0][2]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if not self.consistent(assignment):
            return None

        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        domain_values = self.order_domain_values(var, assignment)
        if domain_values is None:
            return None

        for word in domain_values:
            assignment[var] = word
            if self.backtrack(assignment) is not None:
                return assignment
        del assignment[var]
        return None


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
