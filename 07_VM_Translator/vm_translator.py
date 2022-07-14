
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
    def translate_arithmetic(self, operation):
        if operation == 'add':
            pass
        elif operation == 'sub':
            pass
        elif operation == 'neg':
            pass
        elif operation == 'eq':
            pass
        elif operation == 'gt':
            pass
        elif operation == 'lt':
            pass
        elif operation == 'and':
            pass
        elif operation == 'or':
            pass
        elif operation == 'not':
            pass
        else:
            raise NotImplementedError(f"operation {operation} is not implemented.")


class VMtranslator:
    def __init__(self):
        self.file_name = None

    def read_file(self, file_path):
        self.file_name = file_path.split('/')[-1].split('.')[0]

        with open(file_path, 'r') as rf:
            for line in rf:
                # Parse input
                # Write output
                print(line, end='')


if __name__ == '__main__':
    path = './test/SimpleAdd.vm'

    translator = VMtranslator()
    translator.read_file(path)
