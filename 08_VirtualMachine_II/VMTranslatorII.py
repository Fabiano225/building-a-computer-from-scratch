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
        elif cmd == 'label':
            return 'C_LABEL'
        elif cmd == 'goto':
            return 'C_GOTO'
        elif cmd == 'if-goto':
            return 'C_IF'
        elif cmd == 'function':
            return 'C_FUNCTION'
        elif cmd == 'call':
            return 'C_CALL'
        elif cmd == 'return':
            return 'C_RETURN'
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
        self.call_count = 0
        self.current_function = ""

    def set_filename(self, filename):
        self.filename = os.path.basename(filename).replace('.vm', '')

    def write_init(self):
        self.file.write("// Bootstrap code\n")
        self.file.write("@256\nD=A\n@SP\nM=D\n")
        self.write_call("Sys.init", 0)

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
        segment_map = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}

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

    # --- NEUE METHODEN FÜR PROJECT 8 ---

    def format_label(self, label):
        if self.current_function:
            return f"{self.current_function}${label}"
        return label

    def write_label(self, label):
        self.file.write(f"({self.format_label(label)})\n")

    def write_goto(self, label):
        self.file.write(f"@{self.format_label(label)}\n0;JMP\n")

    def write_if(self, label):
        self.file.write("@SP\nAM=M-1\nD=M\n")
        self.file.write(f"@{self.format_label(label)}\nD;JNE\n")

    def write_function(self, function_name, num_locals):
        self.current_function = function_name
        self.file.write(f"({function_name})\n")
        # Initialize local variables with 0
        for _ in range(num_locals):
            self.write_push_pop('C_PUSH', 'constant', 0)

    def write_call(self, function_name, num_args):
        return_label = f"{self.current_function}$ret.{self.call_count}"
        self.call_count += 1
        self.file.write(f"// call {function_name} {num_args}\n")

        # 1. push return-address
        self.file.write(f"@{return_label}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        # 2. push LCL, ARG, THIS, THAT
        for reg in ['LCL', 'ARG', 'THIS', 'THAT']:
            self.file.write(f"@{reg}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        # 3. ARG = SP - num_args - 5
        self.file.write(f"@SP\nD=M\n@{num_args}\nD=D-A\n@5\nD=D-A\n@ARG\nM=D\n")
        # 4. LCL = SP
        self.file.write("@SP\nD=M\n@LCL\nM=D\n")
        # 5. goto f
        self.file.write(f"@{function_name}\n0;JMP\n")
        # 6. (return-address)
        self.file.write(f"({return_label})\n")

    def write_return(self):
        self.file.write("// return\n")
        # FRAME = LCL (wir nutzen R14 als temporären Speicher für FRAME)
        self.file.write("@LCL\nD=M\n@R14\nM=D\n")
        # RET = *(FRAME-5) (wir nutzen R15 als temporären Speicher für RET)
        self.file.write("@5\nA=D-A\nD=M\n@R15\nM=D\n")
        # *ARG = pop() (Rückgabewert der Funktion an die Stelle von ARG legen)
        self.file.write("@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n")
        # SP = ARG+1
        self.file.write("@ARG\nD=M+1\n@SP\nM=D\n")
        # THAT, THIS, ARG, LCL wiederherstellen (Rückwärts auslesen: FRAME-1 bis FRAME-4)
        for i, reg in enumerate(['THAT', 'THIS', 'ARG', 'LCL'], start=1):
            self.file.write(f"@R14\nD=M\n@{i}\nA=D-A\nD=M\n@{reg}\nM=D\n")
        # goto RET
        self.file.write("@R15\nA=M\n0;JMP\n")

    def close(self):
        self.file.close()


def main():
    if len(sys.argv) != 2:
        print("Usage: python VMTranslator.py <input.vm oder Verzeichnis>")
        sys.exit(1)

    input_path = sys.argv[1]

    # Check ob es eine Datei oder ein Ordner ist
    if os.path.isdir(input_path):
        vm_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith('.vm')]
        output_path = os.path.join(input_path, f"{os.path.basename(os.path.normpath(input_path))}.asm")
        write_bootstrap = True
    else:
        vm_files = [input_path]
        output_path = input_path.replace('.vm', '.asm')
        write_bootstrap = False

    writer = CodeWriter(output_path)

    # Bootstrap-Code nur einfügen, wenn wir ein ganzes Verzeichnis kompilieren
    if write_bootstrap:
        writer.write_init()

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
            elif cmd_type == 'C_LABEL':
                writer.write_label(parser.arg1())
            elif cmd_type == 'C_GOTO':
                writer.write_goto(parser.arg1())
            elif cmd_type == 'C_IF':
                writer.write_if(parser.arg1())
            elif cmd_type == 'C_FUNCTION':
                writer.write_function(parser.arg1(), parser.arg2())
            elif cmd_type == 'C_CALL':
                writer.write_call(parser.arg1(), parser.arg2())
            elif cmd_type == 'C_RETURN':
                writer.write_return()

    writer.close()
    print(f"Compilation successful. Output written to {output_path}")


if __name__ == "__main__":
    main()