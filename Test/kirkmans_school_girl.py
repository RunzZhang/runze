###############################################################################
#
# https://en.wikipedia.org/wiki/Kirkman's_schoolgirl_problem
# http://gurmeet.net/puzzles/kirkmans-schoolgirl-problem/
#
#
# This solving algorithm is terribly slow on higher numbers...
#
# Some possible ideas to speed this up (and to find only unique solutions):
#
#   http://www.recherche.enac.fr/opti/papers/articles/golf.pdf
#
###############################################################################

import math
import sys

# ------------------------------------------------------------------------------
#
# If we represent the solution in three dimensional matrix?
#
# [
#     [ [1, 2, 3], [4, 5, 6], [7, 8, 9] ],  // 1st day
#     [ [1, 4, 7], [2, 5, 8], [3, 6, 9] ],  // 2nd day
#     ...                                   // ...
# ]
#
# ------------------------------------------------------------------------------

m = 2

girls = range(1, 6 * m + 4)

# ------------------------------------------------------------------------------

COLS = len(girls) / 3
ROWS = 3 * m + 1

print(("Girls..:", girls))
print(("Matrix.:", COLS, "x", ROWS))
print(("--------"))


# print( math.factorial(len(girls)))
# sys.exit(0)

# ------------------------------------------------------------------------------

def C(n, k): return math.factorial(n) / (math.factorial(k) * math.factorial(n - k))


def P(n, k): return math.factorial(n) / (math.factorial(n - k))


# ------------------------------------------------------------------------------

def combine(store, items, length,
            validateitem=None,
            validatecand=None,
            i=0, candidate=[]
            ):
    if len(candidate) == length:
        if validatecand and not validatecand(candidate): return
        store.append(candidate)
    else:
        for j in range(i, len(items)):
            if validateitem and not validateitem(candidate, items[j]): continue
            combine(store,
                    items, length,
                    validateitem,
                    validatecand,
                    j + 1, candidate + [items[j]]
                    )


# ------------------------------------------------------------------------------
# Three girl group combinations
# ------------------------------------------------------------------------------

groups = []

combine(groups, girls, 3)

print(("Groups.: %d (C=%d)" % (len(groups), C(len(girls), 3))))

# sys.exit(0)

# ------------------------------------------------------------------------------
# Row combinations
# ------------------------------------------------------------------------------

rows = []


def checkpartialrow(row, group):
    for girl in group:
        for team in row:
            if girl in team: return False
    return True


def reportrows(candidate):
    global rows
    if (len(rows) % 100) == 0:
        print("Rows...:", len(rows), "\r", )
        sys.stdout.flush()
    return True


combine(rows, groups, COLS,
        validateitem=checkpartialrow,
        validatecand=reportrows
        )

print("Rows...:", len(rows))
print("--------")

# print( groups)
# print( rows)

# ------------------------------------------------------------------------------
# From rows, choose combinations where no girl has grouped with others more
# than once.
# ------------------------------------------------------------------------------

solutions = []


def isUniqueSolution(solution):
    def isSame(solution, stored):
        for row in solution:
            if row not in stored: return False
        return True

    for stored in solutions:
        if isSame(solution, stored): return False

    return True


def solve(rows, solution=[]):
    # --------------------------------------------------------------------------
    # Do we already have solution?
    # --------------------------------------------------------------------------

    if len(solution) == ROWS:
        global solutions

        if isUniqueSolution(solution):
            solutions.append(solution)
            print("Solution %d:" % len(solutions))
            # This prints whats in Solution[] list
            for row in solution:
                print("    ", row)
        return

    # --------------------------------------------------------------------------
    # Who have been paired already?
    # --------------------------------------------------------------------------

    paired = {}
    for girl in girls:
        paired[girl] = {}
        paired[girl][girl] = True

    for row in solution:
        for group in row:
            for girl in group:
                for mate in group:
                    paired[girl][mate] = True

    # --------------------------------------------------------------------------
    # Check valid rows for solution
    # --------------------------------------------------------------------------

    def alreadypaired(group):
        a, b, c = group
        return (a in paired[b]) or (a in paired[c]) or (b in paired[c])

    def validrow(row):
        for group in row:
            if alreadypaired(group): return False
        return True

    # --------------------------------------------------------------------------
    # Pick groups and try them out
    # --------------------------------------------------------------------------

    for row in rows:
        if not validrow(row): continue

        solve(rows, solution + [row])


# ------------------------------------------------------------------------------

solve(rows, [rows[0]])

print(len(solutions))