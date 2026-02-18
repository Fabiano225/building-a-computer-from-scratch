import sys
import os

dest_table = {
    "null": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111"
}

jump_table = {
    "null": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
}

comp_table = {
    "0":   "0101010", "1":   "0111111", "-1":  "0111010",
    "D":   "0001100", "A":   "0110000", "M":   "1110000",
    "!D":  "0001101", "!A":  "0110001", "!M":  "1110001",
    "-D":  "0001111", "-A":  "0110011", "-M":  "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010", "D-A": "0010011",
    "D-M": "1010011", "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000", "D|A": "0010101", "D|M": "1010101"
}

symbol_table = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6, "R7": 7,
    "R8": 8, "R9": 9, "R10": 10, "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15,
    "SCREEN": 16384, "KBD": 24576
}

file = sys.argv[1]
output_lines = []
rom_address = 0
instructions_only = []
next_variable_address = 16
base_name = os.path.splitext(file)[0]
output_filename = base_name + ".hack"

with (open(file, "r") as f):
    for line in f:
        clean_line = line.split("//")[0].strip()
        if not clean_line:
            continue

        if clean_line.startswith("(") and clean_line.endswith(")"):
            label = clean_line[1:-1].strip()
            symbol_table[label] = rom_address
        else:
            instructions_only.append(clean_line)
            rom_address += 1

for line in instructions_only:
    if line.startswith("@"):
        symbol = line[1:].strip()

        if symbol.isdigit():
            value = int(symbol)
        elif symbol in symbol_table:
            value = symbol_table[symbol]
        else:
            symbol_table[symbol] = next_variable_address
            value = next_variable_address
            next_variable_address += 1

        binary_a = format(value, "016b")
        output_lines.append(binary_a)

    else:
        dest_part = "null"
        jump_part = "null"

        if "=" in line:
            dest_part, rest = line.split("=")
        else:
            rest = line

        if ";" in rest:
            comp_part, jump_part = rest.split(";")
        else:
            comp_part = rest

        c_bits = comp_table[comp_part]
        d_bits = dest_table[dest_part]
        j_bits = jump_table[jump_part]

        binary_c = "111" + c_bits + d_bits + j_bits
        output_lines.append(binary_c)

with open(output_filename, "w") as f:
    f.write("\n".join(output_lines))