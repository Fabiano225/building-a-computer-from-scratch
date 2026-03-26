import sys
import os
from CompilationEngine import CompilationEngine


def main():
    if len(sys.argv) != 2:
        print("Usage: python JackCompiler.py <file.jack or directory>")
        sys.exit(1)

    path = sys.argv[1]
    files_to_process = []

    if os.path.isfile(path) and path.endswith('.jack'):
        files_to_process.append(path)
    elif os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith('.jack'):
                files_to_process.append(os.path.join(path, filename))
    else:
        print("Invalid path or not a .jack file.")
        sys.exit(1)

    for input_file in files_to_process:
        output_file = input_file.replace('.jack', '.vm')
        print(f"Compiling {input_file} -> {output_file}")

        engine = CompilationEngine(input_file, output_file)
        if engine.tokenizer.hasMoreTokens() and engine.tokenizer.keyword() == 'class':
            engine.compileClass()
        engine.close()


if __name__ == '__main__':
    main()