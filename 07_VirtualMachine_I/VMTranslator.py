import sys
import os

class Parser:
    def __init__(self, input_file):
        with open(input_file, 'r') as f:
            self.lines = f.readlines()
        self.commands = []
        for line in self.lines:
            line = line.split('//')[0].strip()
            if line:
                self.commands.append(line)
        self.current_command = None
        self.current_index = -1

    def has_more_commands(self):
        return self.current_index + 1 < len(self.commands)

    def advance(self):
        self.current_index += 1
        self.current_command = self.commands[self.current_index]

    def command_type(self):
        cmd = self.current_command.split()[0]
        if cmd in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
            return 'C_ARITHMETIC'
        elif cmd == 'push':
            return 'C_PUSH'
        elif cmd == 'pop':
            return 'C_POP'
        return 'UNKNOWN'

    def arg1(self):
        if self.command_type() == 'C_ARITHMETIC':
            return self.current_command.split()[0]
        return self.current_command.split()[1]

    def arg2(self):
        return int(self.current_command.split()[2])


class CodeWriter:
    def __init__(self, output_file):
        self.file = open(output_file, 'w')
        self.filename = ""
        self.label_count = 0

    def set_filename(self, filename):
        self.filename = os.path.basename(filename).replace('.vm', '')

    def write_arithmetic(self, command):
        self.file.write(f"// {command}\n")
        if command in ['add', 'sub', 'and', 'or']:
            self.file.write("@SP\nAM=M-1\nD=M\nA=A-1\n")
            if command == 'add':
                self.file.write("M=D+M\n")
            elif command == 'sub':
                self.file.write("M=M-D\n")
            elif command == 'and':
                self.file.write("M=D&M\n")
            elif command == 'or':
                self.file.write("M=D|M\n")
        elif command in ['neg', 'not']:
            self.file.write("@SP\nA=M-1\n")
            if command == 'neg':
                self.file.write("M=-M\n")
            elif command == 'not':
                self.file.write("M=!M\n")
        elif command in ['eq', 'gt', 'lt']:
            jump_cmd = {'eq': 'JEQ', 'gt': 'JGT', 'lt': 'JLT'}[command]
            label_true = f"TRUE_{self.label_count}"
            label_end = f"END_{self.label_count}"
            self.label_count += 1

            self.file.write("@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n")
            self.file.write(f"@{label_true}\nD;{jump_cmd}\n")
            self.file.write(f"@SP\nA=M-1\nM=0\n@{label_end}\n0;JMP\n")
            self.file.write(f"({label_true})\n@SP\nA=M-1\nM=-1\n({label_end})\n")

    def write_push_pop(self, command, segment, index):
        self.file.write(f"// {command} {segment} {index}\n")

        segment_map = {
            'local': 'LCL', 'argument': 'ARG',
            'this': 'THIS', 'that': 'THAT'
        }

        if command == 'C_PUSH':
            if segment == 'constant':
                self.file.write(f"@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment in segment_map:
                self.file.write(f"@{index}\nD=A\n@{segment_map[segment]}\nA=D+M\nD=M\n")
                self.file.write("@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == 'temp':
                self.file.write(f"@{5 + index}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == 'pointer':
                self.file.write(f"@{3 + index}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == 'static':
                self.file.write(f"@{self.filename}.{index}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

        elif command == 'C_POP':
            if segment in segment_map:
                self.file.write(f"@{index}\nD=A\n@{segment_map[segment]}\nD=D+M\n@R13\nM=D\n")
                self.file.write("@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")
            elif segment == 'temp':
                self.file.write(f"@{5 + index}\nD=A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")
            elif segment == 'pointer':
                self.file.write(f"@{3 + index}\nD=A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")
            elif segment == 'static':
                self.file.write(f"@SP\nAM=M-1\nD=M\n@{self.filename}.{index}\nM=D\n")

    def close(self):
        self.file.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: python VMTranslator.py <input.vm>")
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        vm_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith('.vm')]
        output_path = os.path.join(input_path, f"{os.path.basename(os.path.normpath(input_path))}.asm")
    else:
        vm_files = [input_path]
        output_path = input_path.replace('.vm', '.asm')

    writer = CodeWriter(output_path)

    for vm_file in vm_files:
        parser = Parser(vm_file)
        writer.set_filename(vm_file)

        while parser.has_more_commands():
            parser.advance()
            cmd_type = parser.command_type()

            if cmd_type == 'C_ARITHMETIC':
                writer.write_arithmetic(parser.arg1())
            elif cmd_type in ['C_PUSH', 'C_POP']:
                writer.write_push_pop(cmd_type, parser.arg1(), parser.arg2())

    writer.close()
    print(f"Compilation successful. Output written to {output_path}")


if __name__ == "__main__":
    main()