from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

A = (AKnight, AKnave)
B = (BKnight, BKnave)
C = (CKnight, CKnave)


def says(person, claim):
    Knight, Knave = person
    return And(
        Or(Not(Knight), claim),
        Or(Not(Knave), Not(claim))
    )


def is_person(person):
    Knight, Knave = person
    return And(
        Or(Knight, Knave),
        Not(And(Knight, Knave))
    )


# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    is_person(A),
    says(A, And(AKnight, AKnave))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    is_person(A),
    is_person(B),
    says(A, And(AKnave, BKnave))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    is_person(A),
    is_person(B),
    says(A, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    says(B, Or(And(AKnight, BKnave), And(AKnave, BKnight)))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    is_person(A),
    is_person(B),
    is_person(C),
    says(A, Or(AKnight, AKnave)),
    says(B, says(A, AKnave)),
    says(B, CKnave),
    says(C, AKnight)
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
