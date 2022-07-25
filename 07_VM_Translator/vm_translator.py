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
        self.function_name = None
        self.n_args = None
        self.n_lcls = None

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
            elif op_code == 'call':
                self.operation_type = 'call'
                self.op_code, self.function_name = op_arr[:2]
                self.n_args = int(op_arr[2])
            elif op_code == 'function':
                self.operation_type = 'function'
                self.op_code, self.function_name = op_arr[:2]
                self.n_lcls = int(op_arr[2])
            else:
                raise NotImplementedError(f'op_code {op_code} is not implemented')


class Translator:
    def __init__(self, add_annotation, include_bootstrapping=True):
        self.add_annotation = add_annotation
        self.file_name = None
        self.label_counter = 0
        self.segment_symbol_table = {
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT'
        }
        self.asm_output = ''
        if include_bootstrapping:
            self._initialize_program()
        else:
            self._initialize_pointers()

    def _initialize_program(self):
        # init SP
        if self.add_annotation:
            self._write('//initialize pointers and call sys.init', indent=False)
        self._op_d_set_value(256)
        self._write(f'@SP')
        self._write('M=D')

        # run sys.init 0
        self._translate_call('Sys.init', 0)

    def _initialize_pointers(self):
        self._op_d_set_value(256)
        self._write(f'@SP')
        self._write('M=D')

        self._op_d_set_value(300)
        self._write(f'@LCL')
        self._write('M=D')

        self._op_d_set_value(400)
        self._write(f'@ARG')
        self._write('M=D')

        self._op_d_set_value(3000)
        self._write(f'@THIS')
        self._write('M=D')

        self._op_d_set_value(3010)
        self._write(f'@THAT')
        self._write('M=D')

    def _increment_label_counter(self):
        self.label_counter += 1

    def _write(self, line, indent=True):
        if indent:
            indent = '    '
        else:
            indent = ''
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
        self._write('D=0')
        self._write(f'@END_{comp_type}_{self.label_counter}')
        self._write('0;JMP')

        # set D=true
        self._write(f'({comp_type}_{self.label_counter})', indent=False)
        self._write('D=-1')
        self._write(f'(END_{comp_type}_{self.label_counter})', indent=False)

        self._increment_label_counter()

    def _op_write_d_to_current_stack_pointer(self):
        self._write('@SP')
        self._write('A=M')
        self._write('M=D')

    def _op_write_d_to_symbol_pointer(self, symbol):
        self._write(f'@{symbol}')
        self._write('M=D')

    def _op_a_get_segment_address(self, segment_symbol, address):
        self._write(f'@{address}')
        self._write('D=A')
        self._write(f'@{segment_symbol}')
        self._write('A=D+M')

    def _op_d_set_value(self, address):
        self._write(f'@{address}')
        self._write('D=A')

    def _op_m_get_symbol_n_prev_value(self, symbol, n):
        self._write(f'@{n}')
        self._write('D=A')
        self._write(f'@{symbol}')
        self._write('A=M-D')

    def _op_a_get_memory_segment_address(self, memory_segment, address):
        # get memory address to store data
        if memory_segment in self.segment_symbol_table:
            segment_symbol = self.segment_symbol_table[memory_segment]
            self._op_a_get_segment_address(segment_symbol, address)
        elif memory_segment == 'static':
            self._write(f'@{self.file_name}.{address}')
        elif memory_segment == 'temp':
            self._write(f'@{5 + int(address)}')
        elif memory_segment == 'pointer':
            symbol = 'THIS' if address == '0' else 'THAT'
            self._write(f'@{symbol}')
        else:
            raise NotImplementedError(f"memory segment [{memory_segment}] is not defined in memory operation.")

    def _save_pointer(self, pointer):
        # push onto global stack: [LCL, ARG, THIS, THAT]
        self._write(f'@{pointer}')
        self._write(f'D=M')
        self._op_write_d_to_current_stack_pointer()
        self._op_m_increment_stack_pointer()

    def _save_return_address(self, return_label):
        self._write(f'@{return_label}')
        self._write('D=M')
        self._op_write_d_to_current_stack_pointer()
        self._op_m_increment_stack_pointer()

    def _save_pointers(self):
        for p in ('LCL', 'ARG', 'THIS', 'THAT'):
            self._save_pointer(p)

    def _set_arg_pointer(self, n_args):
        # set ARG (SP - 5 - n_args)
        self._write('@5')
        self._write('D=A')
        self._write(f'@{n_args}')
        self._write('D=D+A')

        self._write('@SP')
        self._write('D=M-D')

        self._op_write_d_to_symbol_pointer('ARG')

    def _set_lcl_pointer(self):
        self._write('@SP')
        self._write('D=M')
        self._write('@LCL')
        self._write('M=D')

    def _jump_to_label(self, label):
        self._write(f'@{label}')
        self._write('0;JMP')

    def _set_return_value(self):
        self._op_m_decrement_stack_pointer()
        self._op_m_get_current_stack_value()
        self._write('D=M')
        self._write('@ARG')
        self._write('A=M')
        self._write('M=D')

    def _reset_stack_pointer(self):
        self._write('@ARG')
        self._write('D=M+1')
        self._write('@SP')
        self._write('M=D')

    def _retrieve_pointer(self, symbol, endframe):
        # push onto global stack: [LCL, ARG, THIS, THAT]
        if symbol == 'THAT':
            n_prev = 1
        elif symbol == 'THIS':
            n_prev = 2
        elif symbol == 'ARG':
            n_prev = 3
        elif symbol == 'LCL':
            n_prev = 4
        else:
            raise NotImplementedError

        self._op_m_get_symbol_n_prev_value(endframe, n_prev)
        self._write('D=M')
        self._write(f'@{endframe}')
        self._write('M=D')

    def _save_endframe_to_r13(self):
        # endframe == LCL
        self._write('@LCL')
        self._write('D=M')
        self._write('@R13')
        self._write('M=D')

    def _save_return_address_to_r14(self):
        # return_address = *(end_frame - 5)
        self._op_m_get_symbol_n_prev_value('LCL', 5)
        self._write('D=M')
        self._write('@R14')
        self._write('M=D')

    def _op_d_pop_value(self):
        self._op_m_decrement_stack_pointer()
        self._op_m_get_current_stack_value()
        self._write('D=M')

    def _translate_call(self, fn_name, n_args):
        return_label = f'{fn_name}.{self.label_counter}'
        self._save_return_address(return_label)
        self._save_pointers()
        self._set_arg_pointer(n_args)
        self._set_lcl_pointer()
        self._jump_to_label(fn_name)

        self._write(f'({return_label})', indent=False)
        self._increment_label_counter()

    def _translate_function_definition(self, fn_name, n_lcls):
        self._write(f'({fn_name})', indent=False)
        # set local variable placeholders
        self._write('D=0')
        for _ in range(n_lcls):
            self._op_write_d_to_current_stack_pointer()
            self._op_m_increment_stack_pointer()

    def _translate_return(self):
        # return value should be at top of the stack.
        # R13 = frame, R14 = return_address
        self._save_endframe_to_r13()
        self._save_return_address_to_r14()
        self._set_return_value()
        self._reset_stack_pointer()
        for p in ('LCL', 'ARG', 'THIS', 'THAT'):
            self._retrieve_pointer(p, 'R13')
        self._jump_to_label('R14')

    def _translate_arithmetic_op(self, operation):
        if operation in ('not', 'neg'):  # one value operation
            self._op_m_decrement_stack_pointer()
            if operation == 'not':
                self._op_m_get_current_stack_value()
                self._write('M=!M')
            else:  # == 'neg'
                self._op_m_get_current_stack_value()
                self._write('M=-M')
            self._op_m_increment_stack_pointer()
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
                self._write('D=A-D')
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

    def _translate_memory_op(self, operation, memory_segment, address):
        if operation == 'push':
            # set d as value to insert.
            if memory_segment == 'constant':
                self._write(f'@{address}')
                self._write('D=A')
            else:
                self._op_a_get_memory_segment_address(memory_segment, address)
                self._write('D=M')

            # push to stack
            self._op_write_d_to_current_stack_pointer()
            self._op_m_increment_stack_pointer()
        else:
            assert operation == 'pop'
            assert memory_segment != 'constant'
            # get memory address to store data
            self._op_a_get_memory_segment_address(memory_segment, address)

            # put address into R13
            self._write('D=A')
            self._write('@R13')
            self._write('M=D')

            # set top stack value to register
            self._op_d_pop_value()
            self._write('@R13')
            self._write('A=M')
            self._write('M=D')

    def _translate_branching_op(self, operation, label):
        if operation == 'label':
            self._write(f'({label})', indent=False)
        elif operation == 'goto':
            self._write(f'@{label}')
            self._write(f'0;JMP')
        elif operation == 'if-goto':
            self._op_m_decrement_stack_pointer()
            self._op_m_get_current_stack_value()
            self._write('D=M')
            self._write(f'@{label}')
            self._write('D;JNE')
        else:
            raise NotImplementedError(f'{operation} is not defined on branching operation')

    def translate_line(self, parser):
        if parser.operation_type == 'compute':
            self._translate_arithmetic_op(parser.op_code)
        elif parser.operation_type == 'memory':
            self._translate_memory_op(
                parser.op_code, parser.memory_segment, parser.address
            )
        elif parser.operation_type == 'branching':
            self._translate_branching_op(parser.op_code, parser.label)
        elif parser.operation_type == 'call':
            self._translate_call(parser.function_name, parser.n_args)
        elif parser.operation_type == 'function':
            self._translate_function_definition(parser.function_name, parser.n_lcls)
        elif parser.operation_type == 'return':
            self._translate_return()
        return self.asm_output

    def set_file_name(self, file_name):
        self.file_name = file_name

    def clear_output(self):
        self.asm_output = ''


class VMtranslator:
    def __init__(self, dir_or_path, include_bootstrapping=True):
        self.file_paths = self._get_file_paths(dir_or_path)
        self.save_path = self._get_save_path(dir_or_path)
        self.include_bootstrapping = include_bootstrapping

    @staticmethod
    def _get_file_paths(dir_or_path):
        if os.path.isdir(dir_or_path):
            current_dir = os.path.join(dir_or_path, '*.vm')
            paths = glob(current_dir)
        else:
            paths = [dir_or_path]
        return paths

    @staticmethod
    def _get_save_path(dir_or_path):
        if os.path.isdir(dir_or_path):
            file_name = dir_or_path.split('/')[-1]
            file_name += '.asm'
            save_path = os.path.join(dir_or_path, file_name)
        else:
            save_path = dir_or_path.replace('vm', 'asm')
        return save_path

    @staticmethod
    def _get_file_name(file_path):
        return file_path.split('/')[-1].split('.')[0]

    def translate(self, add_annotation=False):
        parser = Parser()
        translator = Translator(add_annotation, self.include_bootstrapping)
        for idx, path in enumerate(self.file_paths):
            file_name = self._get_file_name(path)
            translator.file_name = file_name
            with open(path, 'r') as rf:
                write_mode = 'w' if idx == 0 else 'a'
                with open(self.save_path, write_mode) as wf:
                    for line in rf:
                        parser.parse_line(line)
                        asm_line = translator.translate_line(parser)
                        if len(asm_line) != 0:
                            if add_annotation and parser.op_code:
                                annotation = f'  // {parser.line}'
                                line_split = asm_line.split('\n')
                                line_split[0] += annotation
                                asm_line = '\n'.join(line_split)
                            wf.write(asm_line)
                        translator.clear_output()

        # print output on console
        with open(self.save_path, 'r') as f:
            print(f.read())


if __name__ == '__main__':
    test_dir_or_path = '/Users/leo/Desktop/fun/programming/nand2tetris/projects/08/ProgramFlow/FibonacciSeries/FibonacciSeries.vm'
    vm_translator = VMtranslator(test_dir_or_path, include_bootstrapping=False)
    vm_translator.translate(add_annotation=True)
