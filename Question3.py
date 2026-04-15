import copy
import time
from collections import deque
import os

easy_board = """004030050
609400000
005100489
000060930
300807002
026040000
453009600
000004705
090050200"""

medium_board = """000030040
109700000
000851070
002607830
906010207
031502900
010369000
000005703
090070000"""

hard_board = """102040007
000080000
009500304
000607900
540000026
006405000
708003400
000010000
200060509"""

veryhard_board = """001007000
600400300
000030064
380076000
000000036
270015000
000020051
700100200
008009000"""

files = {
    "easy.txt": easy_board,
    "medium.txt": medium_board,
    "hard.txt": hard_board,
    "veryhard.txt": veryhard_board
}

for filename, content in files.items():
    with open(filename, "w") as f:
        f.write(content.strip())
    print(f"Created {filename}")



class SudokuCSP:
    def __init__(self, board):
        self.variables = [(r, c) for r in range(9) for c in range(9)]
        self.domains = {}
        self.board = board
        
        self.backtrack_calls = 0
        self.backtrack_failures = 0
        
        for var in self.variables:
            r, c = var
            if board[r][c] != 0:
                self.domains[var] = [board[r][c]]
            else:
                self.domains[var] = list(range(1, 10))
                
        self.neighbors = {var: self.get_neighbors(var) for var in self.variables}

    def get_neighbors(self, var):
        r, c = var
        neighbors = set()
        for i in range(9):
            if i != c: neighbors.add((r, i))
        for i in range(9):
            if i != r: neighbors.add((i, c))
        box_r, box_c = 3 * (r // 3), 3 * (c // 3)
        for i in range(box_r, box_r + 3):
            for j in range(box_c, box_c + 3):
                if (i, j) != var: neighbors.add((i, j))
        return list(neighbors)

    def ac3(self, queue=None):

        if queue is None:
            queue = deque([(xi, xj) for xi in self.variables for xj in self.neighbors[xi]])
        else:
            queue = deque(queue)
            
        while queue:
            xi, xj = queue.popleft()
            if self.revise(xi, xj):
                if not self.domains[xi]:
                    return False
                for xk in self.neighbors[xi]:
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def revise(self, xi, xj):
        revised = False
        for x in self.domains[xi][:]:
            if len(self.domains[xj]) == 1 and self.domains[xj][0] == x:
                self.domains[xi].remove(x)
                revised = True
        return revised

    def select_unassigned_variable(self, assignment):
        unassigned = [v for v in self.variables if v not in assignment]
        return min(unassigned, key=lambda var: len(self.domains[var]))

    def is_consistent(self, var, value, assignment):
        for neighbor in self.neighbors[var]:
            if neighbor in assignment and assignment[neighbor] == value:
                return False
        return True

    def backtrack(self, assignment):
        self.backtrack_calls += 1
        
        if len(assignment) == len(self.variables):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.domains[var]:
            if self.is_consistent(var, value, assignment):
                assignment[var] = value
                
                domains_copy = copy.deepcopy(self.domains)
                self.domains[var] = [value]
                
                initial_queue = [(xk, var) for xk in self.neighbors[var]]
                
                if self.ac3(initial_queue):
                    result = self.backtrack(assignment)
                    if result:
                        return result
                
                self.backtrack_failures += 1
                del assignment[var]
                self.domains = domains_copy

        return None

    def solve(self):
        if not self.ac3():
            return None
            
        assignment = {}
        for var in self.variables:
            if len(self.domains[var]) == 1:
                assignment[var] = self.domains[var][0]
                
        return self.backtrack(assignment)


def read_board_from_file(filename):

    board = []
    with open(filename, 'r') as f:
        for line in f:
            if line.strip():
                row = [int(char) for char in line.strip()]
                board.append(row)
    return board

def print_board(assignment):
    if not assignment:
        print("No solution found.")
        return
    for r in range(9):
        row = ""
        for c in range(9):
            row += str(assignment[(r, c)]) + " "
        print(row)

filenames = ["easy.txt", "medium.txt", "hard.txt", "veryhard.txt"]

print("\nStarting solver...\n" + "="*40)

for filename in filenames:
    print(f"\n--- Solving {filename} ---")
    board_data = read_board_from_file(filename)
    
    csp = SudokuCSP(board_data)
    
    start_time = time.time()
    solution = csp.solve()
    end_time = time.time()
    
    if solution:
        print_board(solution)
        print(f"\nStats for {filename}:")
        print(f"Time Taken: {end_time - start_time:.4f} seconds")
        print(f"BACKTRACK Calls: {csp.backtrack_calls}")
        print(f"BACKTRACK Failures: {csp.backtrack_failures}")
    else:
        print(f"Could not solve {filename}")
    print("="*40)