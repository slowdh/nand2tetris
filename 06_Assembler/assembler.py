
class Parser:
    """
    Parse one line of instruction into 3 different parts.
    DEST=OPT;JMP
    And deals with white spaces and comments.
    """
    def __init__(self):
        self.dest = None
        self.opt = None
        self.jmp = None

    def _initialize_codes(self):
        self.dest = None
        self.opt = None
        self.jmp = None

    @staticmethod
    def _remove_comments(line):
        return line.split('/')[0]

    @staticmethod
    def _remove_white_spaces(line):
        return line.replace(' ', '')

    def _preprocess_line(self, line):
        line = self._remove_comments(line)
        line = self._remove_white_spaces(line)
        return line

    def parse_line(self, line):
        self._initialize_codes()
        preprocessed_line = self._preprocess_line(line)
        if len(preprocessed_line) == 0:
            return

        if '=' in preprocessed_line:
            self.dest, others = preprocessed_line.split('=')
            if ';' in others:
                self.opt, self.jmp = others.split(';')
            else:
                self.opt = others
        else:
            if ';' in preprocessed_line:
                self.opt, self.jmp = preprocessed_line.split(';')


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

    def translate(self, input_path, output_path):
        # first path: deal with labels first.
        with open(input_path, 'r') as rf:
            pass

        # second path: deal with variable, and translate one by one.
        with open(input_path, 'r') as rf:
            with open(output_path, 'w') as wf:
                # print output
                pass


if __name__ == '__main__':
    def test_parser():
        parser = Parser()
        with open('./test/Add.asm', 'r') as f:
            for line in f:
                print(line, end='')
                parser.parse_line(line)
                if parser.dest is None and parser.opt is None and parser.jmp is None:
                    continue
                else:
                    print(f"===DEST: {parser.dest} OPT:{parser.opt} JMP:{parser.jmp}")


    test_parser()
