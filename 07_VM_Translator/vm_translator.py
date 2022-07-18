import os
from glob import glob


class Parser:
    """
    operation_type: ['compute', 'memory', 'branching', 'call', 'return']
        - compute: arithmetic, logic operations [add, sub, and, or, eq, gt, lt]
        - memory: push, pop operations [push segment idx, pop segment, idx]
        - branching: [label x, goto x, if-goto x]
        - call: function call [call Cls.method args]
        - return: [return]
    """
    def __init__(self):
        self.line = None
        self.operation_type = None
        self.op_code = None
        self.label = None
        self.memory_segment = None
        self.address = None

    @staticmethod
    def _preprocess_line(line):
        line = line.split('/')[0]
        return line.strip()

    def parse_line(self, line):
        self.line = self._preprocess_line(line)
        op_arr = self.line.split()

        if len(op_arr) == 0:
            self.operation_type = None
        elif len(op_arr) == 1:
            # arithmetic, logic operations: [add, sub, and, or, eq, gt, lt]
            # return: [return]
            op_code = op_arr[0]
            if op_code == 'return':
                self.operation_type = self.op_code = 'return'
            else:
                self.operation_type = 'compute'
                self.op_code = op_code
        elif len(op_arr) == 2:  # branching: [label x, goto x, if-goto x]
            self.operation_type = 'branching'
            self.op_code, self.label = op_arr
        else:
            # push, pop memory operation: [push segment idx, pop segment, idx]
            # function call operation: [call Cls.method args]
            op_code = op_arr[0]
            if op_code in ('push', 'pop'):
                self.operation_type = 'memory'
                self.op_code, self.memory_segment, self.address = op_arr
            else:
                assert op_code == 'call'
                pass


class Translator:
    def __init__(self):
        self.file_name = None
        self.label_counter = 0
        self.segment_symbol_table = {
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT'
        }
        self.asm_output = ''

    def _increment_label_counter(self):
        self.label_counter += 1

    def _write(self, line, is_label=False):
        if is_label:
            indent = ''
        else:
            indent = '    '
        self.asm_output += indent + line + '\n'

    def _op_m_decrement_stack_pointer(self):
        self._write('@SP')
        self._write('M=M-1')

    def _op_m_increment_stack_pointer(self):
        self._write('@SP')
        self._write('M=M+1')

    def _op_m_get_current_stack_value(self):
        self._write('@SP')
        self._write('A=M')

    def _op_d_write_comp_branch(self, comp_type):
        assert comp_type in ('EQ', 'GT', 'LT')

        # compare and branching
        self._write('D=D-A')
        self._write(f'@{comp_type}_{self.label_counter}')
        self._write(f'D;J{comp_type}')

        # set D=false
        self._write('@0')
        self._write('D=A')
        self._write(f'@END_{comp_type}_{self.label_counter}')
        self._write('0;JMP')

        # set D=true
        self._write(f'({comp_type}_{self.label_counter})', is_label=True)
        self._write('@-1')
        self._write('D=A')
        self._write(f'(END_{comp_type}_{self.label_counter})', is_label=True)

        self._increment_label_counter()

    def _op_write_d_to_current_stack_pointer(self):
        self._write('@SP')
        self._write('A=M')
        self._write('M=D')

    def _op_a_get_segment_address(self, segment_symbol, address):
        self._write(f'@{address}')
        self._write('D=A')
        self._write(f'@{segment_symbol}')
        self._write('A=D+M')

    def _op_d_set_value(self, address):
        self._write(f'@{address}')
        self._write('D=A')

    def translate_arithmetic_op(self, operation):
        if operation in ('not', 'neg'):  # one value operation
            if operation == 'not':
                self._op_m_get_current_stack_value()
                self._write('M=!M')
            else:  # == 'neg'
                self._op_m_get_current_stack_value()
                self._write('M=-M')
        else:  # two value operation
            # set target values into D, A
            self._op_m_decrement_stack_pointer()
            self._op_m_get_current_stack_value()
            self._write('D=M')
            self._op_m_decrement_stack_pointer()
            self._op_m_get_current_stack_value()
            self._write('A=M')

            if operation == 'add':
                self._write('D=D+A')
            elif operation == 'sub':
                self._write('D=D-A')
            elif operation == 'and':
                self._write('D=D&A')
            elif operation == 'or':
                self._write('D=D|A')
            elif operation == 'eq':
                self._op_d_write_comp_branch('EQ')
            elif operation == 'gt':
                self._op_d_write_comp_branch('GT')
            elif operation == 'lt':
                self._op_d_write_comp_branch('LT')
            else:
                raise NotImplementedError(f"operation {operation} is not implemented.")

            self._op_write_d_to_current_stack_pointer()
            self._op_m_increment_stack_pointer()
        return self.asm_output

    def translate_memory_op(self, operation, memory_segment, address):
        if operation == 'push':
            # set d as value to insert.
            if memory_segment in self.segment_symbol_table:
                segment_symbol = self.segment_symbol_table[memory_segment]
                self._op_a_get_segment_address(segment_symbol, address)
                self._write('D=M')
            elif memory_segment == 'constant':
                self._op_d_set_value(address)
            elif memory_segment == 'static':
                self._write(f'@{self.file_name}.{address}')
                self._write('D=M')
            elif memory_segment == 'temp':
                self._write(f'@{5 + int(address)}')
                self._write('D=M')
            elif memory_segment == 'pointer':
                symbol = 'THIS' if address == 0 else 'THAT'
                self._write(f'@{symbol}')
                self._write('D=M')
            else:
                raise NotImplementedError(f"memory segment [{memory_segment}] is not defined in PUSH operation.")

            # push to stack
            self._op_write_d_to_current_stack_pointer()
            self._op_m_increment_stack_pointer()
        else:
            assert operation == 'pop'
            assert memory_segment != 'constant'
            self._op_m_decrement_stack_pointer()
            self._op_m_get_current_stack_value()
            self._write('D=M')

            # set address to R13
            if memory_segment in self.segment_symbol_table:
                segment_symbol = self.segment_symbol_table[memory_segment]
                self._op_a_get_segment_address(segment_symbol, address)
                self._write('D=M')
                self._write('@R13')
                self._write('M=D')

                # set top stack value to register
                self._op_m_get_current_stack_value()
                self._write('D=M')
                self._write('@R13')
                self._write('A=M')
                self._write('M=D')
            elif memory_segment == 'static':
                self._write(f'@{self.file_name}.{address}')
                self._write(f'M=D')
            elif memory_segment == 'temp':
                self._write(f'@{5 + int(address)}')
                self._write(f'M=D')
            elif memory_segment == 'pointer':
                symbol = 'THIS' if address == 0 else 'THAT'
                self._write(f'@{symbol}')
                self._write(f'M=D')
            else:
                raise NotImplementedError(f"memory segment [{memory_segment}] is not defined in POP operation.")
        return self.asm_output

    def translate_branching_op(self, operation, label):
        if operation == 'label':
            self._write(f'({label})', is_label=True)
        elif operation == 'goto':
            self._write(f'@{label}')
            self._write(f'0;JMP')
        elif operation == 'if-goto':
            self._op_m_decrement_stack_pointer()
            self._op_m_get_current_stack_value()
            self._write('D=M+1')
            self._write(f'@{label}')
            self._write('D;JEQ')
        else:
            raise NotImplementedError(f'{operation} is not defined on branching operation')
        return self.asm_output

    def translate_line(self, parser):
        if parser.operation_type == 'compute':
            asm_line = self.translate_arithmetic_op(parser.op_code)
        elif parser.operation_type == 'memory':
            asm_line = self.translate_memory_op(
                parser.op_code, parser.memory_segment, parser.address
            )
        elif parser.operation_type == 'branching':
            asm_line = self.translate_branching_op(parser.op_code, parser.label)
        elif parser.operation_type == 'call':
            pass
        elif parser.operation_type == 'return':
            pass
        else:  # == 'comment'
            asm_line = None
        return asm_line

    def set_file_name(self, file_name):
        self.file_name = file_name

    def clear_output(self):
        self.asm_output = ''


class VMtranslator:
    def __init__(self, dir_or_path):
        self.file_paths = self._get_file_paths(dir_or_path)

    @staticmethod
    def _get_file_paths(dir_or_path):
        if os.path.isdir(dir_or_path):
            current_dir = os.path.join(dir_or_path, '*.vm')
            paths = glob(current_dir)
        else:
            paths = [dir_or_path]
        return paths

    @staticmethod
    def _get_file_name(file_path):
        return file_path.split('/')[-1].split('.')[0]

    def translate(self, add_annotation=False):
        save_path = self.file_paths[0].replace('.vm', '.asm')

        parser = Parser()
        translator = Translator()
        for idx, path in enumerate(self.file_paths):
            file_name = self._get_file_name(path)
            translator.file_name = file_name
            with open(path, 'r') as rf:
                write_mode = 'w' if idx == 0 else 'a'
                with open(save_path, write_mode) as wf:
                    for line in rf:
                        parser.parse_line(line)
                        asm_line = translator.translate_line(parser)
                        if asm_line:
                            if add_annotation and parser.op_code:
                                wf.write(f'// {parser.line}\n')
                            wf.write(asm_line)
                        translator.clear_output()

        # print output on console
        with open(save_path, 'r') as f:
            print(f.read())


if __name__ == '__main__':
    test_dir_or_path = '../../projects/08/ProgramFlow/BasicLoop/BasicLoop.vm'
    vm_translator = VMtranslator(test_dir_or_path)
    vm_translator.translate(add_annotation=True)
