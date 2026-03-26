class VMWriter:
    def __init__(self, output_file):
        self.out = open(output_file, 'w')

    def writePush(self, segment, index):
        self.out.write(f"push {segment} {index}\n")

    def writePop(self, segment, index):
        self.out.write(f"pop {segment} {index}\n")

    def writeArithmetic(self, command):
        self.out.write(f"{command}\n")

    def writeLabel(self, label):
        self.out.write(f"label {label}\n")

    def writeGoto(self, label):
        self.out.write(f"goto {label}\n")

    def writeIf(self, label):
        self.out.write(f"if-goto {label}\n")

    def writeCall(self, name, nArgs):
        self.out.write(f"call {name} {nArgs}\n")

    def writeFunction(self, name, nLocals):
        self.out.write(f"function {name} {nLocals}\n")

    def writeReturn(self):
        self.out.write("return\n")

    def close(self):
        self.out.close()