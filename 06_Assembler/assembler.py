
class Parser:
    """
    Parse one line of instruction into 3 different parts.
    DEST=OPT;JMP
    And deals with white spaces and comments.

    instruction_type: [comment, label, a, c]
    """
    def __init__(self):
        self.instruction_type = None
        self.label = None
        self.value = None
        self.dest = None
        self.comp = None
        self.jmp = None

    def _reset_codes(self):
        self.instruction_type = None
        self.label = None
        self.value = None
        self.dest = None
        self.comp = None
        self.jmp = None

    @staticmethod
    def _remove_comments(line):
        return line.split('/')[0]

    @staticmethod
    def _remove_white_spaces(line):
        line = line.replace('\n', '')
        return line.replace(' ', '')

    def _preprocess_line(self, line):
        line = self._remove_comments(line)
        line = self._remove_white_spaces(line)
        return line

    def parse_line(self, line):
        self._reset_codes()
        line = self._preprocess_line(line)
        if len(line) == 0:
            self.instruction_type = 'comment'
            return

        if line[0] == '(':  # label
            self.instruction_type = 'label'
            self.label = line
        elif line[0] == '@':  # a_instruction
            self.instruction_type = 'a'
            self.value = line[1:]
        else:  # c_instruction
            if '=' in line:
                self.instruction_type = 'c'
                self.dest, others = line.split('=')
                if ';' in others:
                    self.comp, self.jmp = others.split(';')
                else:
                    self.comp = others
            else:
                if ';' in line:
                    self.instruction_type = 'c'
                    self.comp, self.jmp = line.split(';')


class Translator:
    """
    Translate one assembly line into (mostly one line of) binary code.
    """
    @staticmethod
    def _convert_to_binary(dec_val):
        return bin(int(dec_val))[2:]

    @staticmethod
    def _translate_dest(dest):
        if dest is None:
            return '000'
        elif dest == 'M':
            return '001'
        elif dest == 'D':
            return '010'
        elif dest == 'MD' or dest == 'DM':
            return '011'
        elif dest == 'A':
            return '100'
        elif dest == 'AM' or dest == 'MA':
            return '101'
        elif dest == 'AD' or dest == 'DA':
            return '110'
        else:  # dest == 'AMD"
            return '111'

    @staticmethod
    def _translate_comp(comp):
        output = ''
        if 'M' in comp:
            output += '1'
            comp = comp.replace('M', 'A')
        else:
            output += '0'

        if comp == '0':
            output += '101010'
        elif comp == '1':
            output += '111111'
        elif comp == '-1':
            output += '111010'
        elif comp == 'D':
            output += '001100'
        elif comp == 'A':
            output += '110000'
        elif comp == '!D':
            output += '001101'
        elif comp == '!A':
            output += '110001'
        elif comp == '-D':
            output += '001111'
        elif comp == '-A':
            output += '110011'
        elif comp == 'D+1':
            output += '011111'
        elif comp == 'A+1':
            output += '110111'
        elif comp == 'D-1':
            output += '001110'
        elif comp == 'A-1':
            output += '110010'
        elif comp == 'D+A' or comp == 'A+D':
            output += '000010'
        elif comp == 'D-A':
            output += '010011'
        elif comp == 'A-D':
            output += '000111'
        elif comp == 'D&A':
            output += '000000'
        elif comp == 'D|A':
            output += '010101'
        else:
            raise NotImplementedError('Comp command not implemented.')
        return output

    @staticmethod
    def _translate_jmp(jmp):
        if jmp is None:
            return '000'
        elif jmp == 'JGT':
            return '001'
        elif jmp == 'JEQ':
            return '010'
        elif jmp == 'JGE':
            return '011'
        elif jmp == 'JLT':
            return '100'
        elif jmp == 'JNE':
            return '101'
        elif jmp == 'JLE':
            return '110'
        elif jmp == 'JMP':
            return '111'
        else:
            raise NotImplementedError('JMP command not implemented.')

    def translate_a_instruction(self, value):
        output = ''
        bin_val = self._convert_to_binary(value)
        bin_len = len(bin_val)
        assert bin_len <= 15
        output += '0' * (16 - bin_len) + bin_val
        return output

    def translate_c_intruction(self, dest, comp, jmp):
        output = '111'
        output += self._translate_comp(comp)
        output += self._translate_dest(dest)
        output += self._translate_jmp(jmp)
        return output

    def translate_parsed_line(self, instruction_type, value, dest, comp, jmp):
        if instruction_type == 'a':
            return self.translate_a_instruction(value)
        return self.translate_c_intruction(dest, comp, jmp)


class SymbolManager:
    """
    Deal with natural language symbols: Variables and Labels.
    Makes table, map each symbol to RAM address.
    At first cycle, only care about Labels.
    Second cycle, unidentified symbols are all variables.
    """
    def __init__(self):
        self.symbol_table = {}
        self.available_address = 0
        self._set_predefined_symbols()

    @staticmethod
    def is_int(n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    def _set_predefined_symbols(self):
        predefined = {
            'SCREEN': '16384',
            'KBD': '24576',
            'SP': '0',
            'LCL': '1',
            'ARG': '2',
            'THIS': '3',
            'THAT': '4'
        }
        # registers
        for i in range(16):
            predefined[f'R{i}'] = str(i)

        self.symbol_table.update(predefined)
        self.available_address += 16

    def map_variable_to_available_address(self, variable):
        self.symbol_table[variable] = self.available_address
        self.available_address += 1

    def map_label_to_instruction_address(self, label, current_address):
        label = label.strip('()')
        self.symbol_table[label] = current_address

    def convert_symbol(self, symbol):
        if symbol is None or self.is_int(symbol):
            return symbol
        if symbol not in self.symbol_table:
            self.map_variable_to_available_address(symbol)
        return self.symbol_table[symbol]


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
    def __init__(self):
        self.current_address = 0

    def _reset_current_line(self):
        self.current_address = 0

    def translate(self, input_path, output_path):
        parser = Parser()
        symbol_manager = SymbolManager()
        translator = Translator()

        # first path: deal with labels first.
        with open(input_path, 'r') as rf:
            for line in rf:
                parser.parse_line(line)
                if parser.instruction_type == 'label':
                    symbol_manager.map_label_to_instruction_address(parser.label, self.current_address)
                if parser.instruction_type != 'comment':
                    self.current_address += 1

        # second path: deal with variable, and translate one by one.
        self._reset_current_line()
        with open(input_path, 'r') as rf:
            with open(output_path, 'w') as wf:
                for line in rf:
                    parser.parse_line(line)
                    if parser.instruction_type not in ('label', 'comment'):
                        parser.label = symbol_manager.convert_symbol(parser.label)
                        parser.value = symbol_manager.convert_symbol(parser.value)
                        translated = translator.translate_parsed_line(
                            parser.instruction_type, parser.value, parser.dest, parser.comp, parser.jmp
                        )
                        wf.write(translated + '\n')
