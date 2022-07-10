
class Parser:
    """
    Parse one line of instruction into 3 different parts.
    DEST=OPT;JMP
    And deals with white spaces and comments.
    """
    pass


class Translator:
    """
    Translate one assembly line into (mostly one line of) binary code.
    """
    pass


class SymbolManager:
    """
    Deal with natural language symbols: Variables and Labels.
    Makes table,
    """


class Assembler:
    """
    Read file, translate, save output.

    1. Read file.
        1.1. Also, save file.
    2. Translate line by line.
        2.1. Parse line.
            2.1.1. Deal with parsing.
            2.1.2. Deal with comments.
        2.2. Translate line by line.
        2.3. Deal with symbols.
            2.3.1. Need table. + Save default symbols.
            2.3.2. Variable, labels? -> Implement as 2 way path.
    """
