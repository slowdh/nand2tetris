
class Parser:
    """
    operation_type: ['compute', 'memory']
        - compute: arithmetic, logic operations
        - memory: push, pop operations
    """
    def __init__(self):
        self.operation_type = None
        self.op_code = None
        self.memory_segment = None
        self.address = None

    @staticmethod
    def _preprocess_line(line):
        line = line.split('/')[0]
        return line.strip()

    def parse_line(self, line):
        line = self._preprocess_line(line)
        op_arr = line.split()
        if len(op_arr) == 0:
            self.operation_type = None
        elif len(op_arr) == 1:  # arithmetic, logic operation
            self.operation_type = 'compute'
            self.op_code = op_arr[0]
        else:  # push, pop memory operation
            assert len(op_arr) == 3
            self.operation_type = 'memory'
            self.op_code, self.memory_segment, self.address = op_arr


class Translator:
    def __init__(self, file_name):
        self.file_name = file_name
        self.label_counter = 0
        self.segment_symbol_table = {
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT'
        }

    def translate_arithmetic_op(self, operation):
        if operation in ('not', 'neg'):  # one value operation
            assembly_output = [
                '@SP',
                'A=M-1'
            ]
            if operation == 'not':
                assembly_output.append('M=!M')
            else:  # operation == 'neg'
                assembly_output.append('M=-M')
        else:  # two value operation
            assembly_output = [
                '@SP',
                'M=M-1',
                'A=M-1',
                'D=M',
                '@SP',
                'A=M'
            ]
            if operation == 'add':
                assembly_output.append('D=D+A')
            elif operation == 'sub':
                assembly_output.append('D=D-A')
            elif operation == 'and':
                assembly_output.append('D=D&A')
            elif operation == 'or':
                assembly_output.append('D=D|A')
            else:
                if operation == 'eq':
                    asm_comp = [
                        'D=D-A',
                        f'@EQ_{self.label_counter}',
                        'D;JEQ',
                        f'@END_{self.label_counter}',
                        '0;JMP',
                        f'(EQ_{self.label_counter})',
                        'D=1',
                        f'(END_{self.label_counter})'
                    ]
                elif operation == 'gt':
                    asm_comp = [
                        'D=D-A',
                        f'@GT_{self.label_counter}',
                        'D;JGT',
                        f'@END_{self.label_counter}',
                        '0;JMP',
                        f'(GT_{self.label_counter})',
                        'D=1',
                        f'(END_{self.label_counter})'
                    ]
                elif operation == 'lt':
                    asm_comp = [
                        'D=D-A',
                        f'@LT_{self.label_counter}',
                        'D;JLT',
                        f'@END_{self.label_counter}',
                        '0;JLT',
                        f'(LT_{self.label_counter})',
                        'D=1',
                        f'(END_{self.label_counter})'
                    ]
                else:
                    raise NotImplementedError(f"operation {operation} is not implemented.")
                assembly_output += asm_comp
                self.label_counter += 1

            assembly_output += [
                '@SP',
                'A=M-1',
                'M=D'
            ]
        return '\n'.join(assembly_output)

    def translate_memory_op(self, operation, memory_segment, address):
        if operation == 'push':
            if memory_segment in self.segment_symbol_table:
                segment = self.segment_symbol_table[memory_segment]
                asm_data = [
                    f'@{address}',
                    'D=A',
                    f'@{segment}',
                    'A=D+M',
                    'D=M'
                ]
            elif memory_segment == 'constant':
                asm_data = [
                    f'@{address}',
                    'D=A'
                ]
            elif memory_segment == 'static':
                asm_data = [
                    f'@{self.file_name}.{address}',
                    'D=M'
                ]
            elif memory_segment == 'temp':
                asm_data = [
                    f'@{5 + int(address)}',
                    'D=M'
                ]
            elif memory_segment == 'pointer':
                if address == 0:
                    symbol = 'THIS'
                else:  # == 1
                    symbol = 'THAT'

                asm_data = [
                    f'@{symbol}',
                    'D=M'
                ]
            else:
                raise NotImplementedError(f"memory segment [{memory_segment}] is not defined in PUSH operation.")

            asm_push = [
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1'
            ]
            asm_output = '\n'.join(asm_data + asm_push)

        else:
            assert operation == 'pop'
            assert memory_segment != 'constant'
            asm_stack = [
                '@SP',
                'M=M-1'
            ]

            # set address to R13
            if memory_segment in self.segment_symbol_table:
                segment = self.segment_symbol_table[memory_segment]
                asm_address = [
                    f'@{address}',
                    'D=A',
                    f'@{segment}',
                    'A=D+M',
                    'D=M',
                    '@R13',
                    'M=D'
                ]
            elif memory_segment == 'static':
                asm_address = [f'@{self.file_name}.{address}']
            elif memory_segment == 'temp':
                asm_address = [f'@{5 + int(address)}']
            elif memory_segment == 'pointer':
                if address == 0:
                    symbol = 'THIS'
                else:  # == 1
                    symbol = 'THAT'
                asm_address = [f'@{symbol}']
            else:
                raise NotImplementedError(f"memory segment [{memory_segment}] is not defined in POP operation.")

            asm_save = [
                '@SP',
                'D=M',
                '@R13',
                'A=M',
                'M=D'
            ]
            asm_output = '\n'.join(asm_stack + asm_address + asm_save)
        return asm_output


class VMtranslator:
    def __init__(self):
        self.file_name = None

    def translate(self, file_path, debug=False):
        self.file_name = file_path.split('/')[-1].split('.')[0]
        parser = Parser()
        translator = Translator(self.file_name)
        save_path = file_path.replace('.vm', '.asm')
        with open(file_path, 'r') as rf:
            with open(save_path, 'w') as wf:
                for line in rf:
                    parser.parse_line(line)
                    if parser.operation_type == 'compute':
                        asm_line = translator.translate_arithmetic_op(parser.op_code)
                    elif parser.operation_type == 'memory':
                        asm_line = translator.translate_memory_op(parser.op_code, parser.memory_segment, parser.address)
                    else:  # == 'comment'
                        continue
                    wf.write(asm_line + '\n')

        if debug:
            with open(save_path, 'r') as f:
                print(f.read())


if __name__ == '__main__':
    path = './test/BasicTest.vm'

    vm_translator = VMtranslator()
    vm_translator.translate(path, debug=True)
