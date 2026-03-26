from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    OP_MAP = {'+': 'add', '-': 'sub', '*': 'call Math.multiply 2', '/': 'call Math.divide 2',
              '&': 'and', '|': 'or', '<': 'lt', '>': 'gt', '=': 'eq'}
    UNARY_OP_MAP = {'-': 'neg', '~': 'not'}

    def __init__(self, input_file, output_file):
        self.tokenizer = JackTokenizer(input_file)
        self.sym_table = SymbolTable()
        self.vm = VMWriter(output_file)
        self.class_name = ""
        self.label_idx = 0
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()

    def close(self):
        self.vm.close()

    def get_label(self, prefix):
        self.label_idx += 1
        return f"{prefix}{self.label_idx}"

    def process(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()

    def kind_to_segment(self, kind):
        mapping = {'FIELD': 'this', 'STATIC': 'static', 'VAR': 'local', 'ARG': 'argument'}
        return mapping.get(kind, 'NONE')

    def compileClass(self):
        self.process()  # 'class'
        self.class_name = self.tokenizer.identifier()
        self.process()  # className
        self.process()  # '{'
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ['static', 'field']:
            self.compileClassVarDec()
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ['constructor', 'function',
                                                                                       'method']:
            self.compileSubroutine()
        self.process()  # '}'

    def compileClassVarDec(self):
        kind = self.tokenizer.keyword().upper()
        self.process()  # 'static' or 'field'
        type_name = self.tokenizer.keyword() if self.tokenizer.tokenType() == "KEYWORD" else self.tokenizer.identifier()
        self.process()  # type
        var_name = self.tokenizer.identifier()
        self.sym_table.define(var_name, type_name, kind)
        self.process()  # varName
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ',':
            self.process()  # ','
            var_name = self.tokenizer.identifier()
            self.sym_table.define(var_name, type_name, kind)
            self.process()  # varName
        self.process()  # ';'

    def compileSubroutine(self):
        self.sym_table.startSubroutine()
        func_type = self.tokenizer.keyword()  # constructor, function, method
        self.process()
        self.process()  # void or type
        func_name = self.tokenizer.identifier()
        self.process()

        if func_type == 'method':
            self.sym_table.define('this', self.class_name, 'ARG')

        self.process()  # '('
        self.compileParameterList()
        self.process()  # ')'
        self.process()  # '{'

        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == 'var':
            self.compileVarDec()

        n_locals = self.sym_table.varCount('VAR')
        self.vm.writeFunction(f"{self.class_name}.{func_name}", n_locals)

        if func_type == 'method':
            self.vm.writePush('argument', 0)
            self.vm.writePop('pointer', 0)
        elif func_type == 'constructor':
            n_fields = self.sym_table.varCount('FIELD')
            self.vm.writePush('constant', n_fields)
            self.vm.writeCall('Memory.alloc', 1)
            self.vm.writePop('pointer', 0)

        self.compileStatements()
        self.process()  # '}'

    def compileParameterList(self):
        if not (self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ')'):
            type_name = self.tokenizer.keyword() if self.tokenizer.tokenType() == "KEYWORD" else self.tokenizer.identifier()
            self.process()
            var_name = self.tokenizer.identifier()
            self.sym_table.define(var_name, type_name, 'ARG')
            self.process()
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ',':
                self.process()  # ','
                type_name = self.tokenizer.keyword() if self.tokenizer.tokenType() == "KEYWORD" else self.tokenizer.identifier()
                self.process()
                var_name = self.tokenizer.identifier()
                self.sym_table.define(var_name, type_name, 'ARG')
                self.process()

    def compileVarDec(self):
        self.process()  # 'var'
        type_name = self.tokenizer.keyword() if self.tokenizer.tokenType() == "KEYWORD" else self.tokenizer.identifier()
        self.process()
        var_name = self.tokenizer.identifier()
        self.sym_table.define(var_name, type_name, 'VAR')
        self.process()
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ',':
            self.process()  # ','
            var_name = self.tokenizer.identifier()
            self.sym_table.define(var_name, type_name, 'VAR')
            self.process()
        self.process()  # ';'

    def compileStatements(self):
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ['let', 'if', 'while', 'do',
                                                                                       'return']:
            kw = self.tokenizer.keyword()
            if kw == 'let':
                self.compileLet()
            elif kw == 'if':
                self.compileIf()
            elif kw == 'while':
                self.compileWhile()
            elif kw == 'do':
                self.compileDo()
            elif kw == 'return':
                self.compileReturn()

    def compileDo(self):
        self.process()  # 'do'
        self.compileCall()
        self.process()  # ';'
        self.vm.writePop("temp", 0)  # Ignoriere Rückgabewert bei 'do'

    def compileLet(self):
        self.process()  # 'let'
        var_name = self.tokenizer.identifier()
        self.process()
        is_array = False
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == '[':
            is_array = True
            self.process()  # '['
            self.compileExpression()
            self.process()  # ']'
            self.vm.writePush(self.kind_to_segment(self.sym_table.kindOf(var_name)), self.sym_table.indexOf(var_name))
            self.vm.writeArithmetic("add")

        self.process()  # '='
        self.compileExpression()
        self.process()  # ';'

        if is_array:
            self.vm.writePop("temp", 0)
            self.vm.writePop("pointer", 1)
            self.vm.writePush("temp", 0)
            self.vm.writePop("that", 0)
        else:
            self.vm.writePop(self.kind_to_segment(self.sym_table.kindOf(var_name)), self.sym_table.indexOf(var_name))

    def compileWhile(self):
        l_exp = self.get_label("WHILE_EXP")
        l_end = self.get_label("WHILE_END")
        self.vm.writeLabel(l_exp)
        self.process()  # 'while'
        self.process()  # '('
        self.compileExpression()
        self.process()  # ')'
        self.vm.writeArithmetic("not")
        self.vm.writeIf(l_end)
        self.process()  # '{'
        self.compileStatements()
        self.process()  # '}'
        self.vm.writeGoto(l_exp)
        self.vm.writeLabel(l_end)

    def compileReturn(self):
        self.process()  # 'return'
        if not (self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ';'):
            self.compileExpression()
        else:
            self.vm.writePush("constant", 0)  # void returns 0
        self.process()  # ';'
        self.vm.writeReturn()

    def compileIf(self):
        l_true = self.get_label("IF_TRUE")
        l_false = self.get_label("IF_FALSE")
        l_end = self.get_label("IF_END")
        self.process()  # 'if'
        self.process()  # '('
        self.compileExpression()
        self.process()  # ')'
        self.vm.writeIf(l_true)
        self.vm.writeGoto(l_false)
        self.vm.writeLabel(l_true)
        self.process()  # '{'
        self.compileStatements()
        self.process()  # '}'
        if self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == 'else':
            self.vm.writeGoto(l_end)
            self.vm.writeLabel(l_false)
            self.process()  # 'else'
            self.process()  # '{'
            self.compileStatements()
            self.process()  # '}'
            self.vm.writeLabel(l_end)
        else:
            self.vm.writeLabel(l_false)

    def compileExpression(self):
        self.compileTerm()
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in '+-*/&|<>=':
            op = self.tokenizer.symbol()
            self.process()
            self.compileTerm()
            if op in self.OP_MAP:
                if self.OP_MAP[op].startswith('call'):
                    self.vm.writeCall(self.OP_MAP[op].split()[1], 2)
                else:
                    self.vm.writeArithmetic(self.OP_MAP[op])

    def compileTerm(self):
        t_type = self.tokenizer.tokenType()
        if t_type == "INT_CONST":
            self.vm.writePush("constant", self.tokenizer.intVal())
            self.process()
        elif t_type == "STRING_CONST":
            s = self.tokenizer.stringVal()
            self.vm.writePush("constant", len(s))
            self.vm.writeCall("String.new", 1)
            for char in s:
                self.vm.writePush("constant", ord(char))
                self.vm.writeCall("String.appendChar", 2)
            self.process()
        elif t_type == "KEYWORD":
            kw = self.tokenizer.keyword()
            if kw == 'true':
                self.vm.writePush("constant", 0)
                self.vm.writeArithmetic("not")
            elif kw in ['false', 'null']:
                self.vm.writePush("constant", 0)
            elif kw == 'this':
                self.vm.writePush("pointer", 0)
            self.process()
        elif t_type == "SYMBOL":
            sym = self.tokenizer.symbol()
            if sym == '(':
                self.process()
                self.compileExpression()
                self.process()
            elif sym in '-~':
                self.process()
                self.compileTerm()
                self.vm.writeArithmetic(self.UNARY_OP_MAP[sym])
        elif t_type == "IDENTIFIER":
            next_token = self.tokenizer.peekNextToken()
            if next_token == '[':  # Array Access
                var_name = self.tokenizer.identifier()
                self.process()
                self.process()  # '['
                self.compileExpression()
                self.process()  # ']'
                self.vm.writePush(self.kind_to_segment(self.sym_table.kindOf(var_name)),
                                  self.sym_table.indexOf(var_name))
                self.vm.writeArithmetic("add")
                self.vm.writePop("pointer", 1)
                self.vm.writePush("that", 0)
            elif next_token in '(.':  # Call
                self.compileCall()
            else:  # Simple Var
                var_name = self.tokenizer.identifier()
                self.vm.writePush(self.kind_to_segment(self.sym_table.kindOf(var_name)),
                                  self.sym_table.indexOf(var_name))
                self.process()

    def compileCall(self):
        first_id = self.tokenizer.identifier()
        self.process()
        n_args = 0

        if self.tokenizer.symbol() == '.':
            self.process()  # '.'
            func_name = self.tokenizer.identifier()
            self.process()

            kind = self.sym_table.kindOf(first_id)
            if kind:  # Es ist ein Objekt
                self.vm.writePush(self.kind_to_segment(kind), self.sym_table.indexOf(first_id))
                call_name = f"{self.sym_table.typeOf(first_id)}.{func_name}"
                n_args += 1
            else:  # Es ist eine Klasse (Static Function)
                call_name = f"{first_id}.{func_name}"
        else:  # Methode der aktuellen Klasse
            call_name = f"{self.class_name}.{first_id}"
            self.vm.writePush("pointer", 0)
            n_args += 1

        self.process()  # '('
        n_args += self.compileExpressionList()
        self.process()  # ')'
        self.vm.writeCall(call_name, n_args)

    def compileExpressionList(self):
        n_args = 0
        if not (self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ')'):
            self.compileExpression()
            n_args += 1
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ',':
                self.process()
                self.compileExpression()
                n_args += 1
        return n_args