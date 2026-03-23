from JackTokenizer import JackTokenizer

class CompilationEngine:
    def __init__(self, input_file, output_file):
        self.tokenizer = JackTokenizer(input_file)
        self.out = open(output_file, 'w')
        self.indent = 0
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()

    def close(self):
        self.out.close()

    def write_line(self, text):
        self.out.write("  " * self.indent + text + "\n")

    def start_block(self, tag):
        self.write_line(f"<{tag}>")
        self.indent += 1

    def end_block(self, tag):
        self.indent -= 1
        self.write_line(f"</{tag}>")

    def escape_xml(self, text):
        return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

    def process(self):
        t_type = self.tokenizer.tokenType()
        tag, val = "", ""

        if t_type == "KEYWORD": val, tag = self.tokenizer.keyword(), "keyword"
        elif t_type == "SYMBOL": val, tag = self.tokenizer.symbol(), "symbol"
        elif t_type == "IDENTIFIER": val, tag = self.tokenizer.identifier(), "identifier"
        elif t_type == "INT_CONST": val, tag = str(self.tokenizer.intVal()), "integerConstant"
        elif t_type == "STRING_CONST": val, tag = self.tokenizer.stringVal(), "stringConstant"

        self.write_line(f"<{tag}> {self.escape_xml(val)} </{tag}>")
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()

    def compileClass(self):
        self.start_block("class")
        self.process() # 'class'
        self.process() # className
        self.process() # '{'
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ['static', 'field']:
            self.compileClassVarDec()
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ['constructor', 'function', 'method']:
            self.compileSubroutine()
        self.process() # '}'
        self.end_block("class")

    def compileClassVarDec(self):
        self.start_block("classVarDec")
        self.process() # 'static' / 'field'
        self.process() # type
        self.process() # varName
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ',':
            self.process() # ','
            self.process() # varName
        self.process() # ';'
        self.end_block("classVarDec")

    def compileSubroutine(self):
        self.start_block("subroutineDec")
        self.process() # 'constructor'/'function'/'method'
        self.process() # 'void' / type
        self.process() # subroutineName
        self.process() # '('
        self.compileParameterList()
        self.process() # ')'
        self.compileSubroutineBody()
        self.end_block("subroutineDec")

    def compileParameterList(self):
        self.start_block("parameterList")
        if not (self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ')'):
            self.process() # type
            self.process() # varName
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ',':
                self.process() # ','
                self.process() # type
                self.process() # varName
        self.end_block("parameterList")

    def compileSubroutineBody(self):
        self.start_block("subroutineBody")
        self.process() # '{'
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == 'var':
            self.compileVarDec()
        self.compileStatements()
        self.process() # '}'
        self.end_block("subroutineBody")

    def compileVarDec(self):
        self.start_block("varDec")
        self.process() # 'var'
        self.process() # type
        self.process() # varName
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ',':
            self.process() # ','
            self.process() # varName
        self.process() # ';'
        self.end_block("varDec")

    def compileStatements(self):
        self.start_block("statements")
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ['let', 'if', 'while', 'do', 'return']:
            kw = self.tokenizer.keyword()
            if kw == 'let': self.compileLet()
            elif kw == 'if': self.compileIf()
            elif kw == 'while': self.compileWhile()
            elif kw == 'do': self.compileDo()
            elif kw == 'return': self.compileReturn()
        self.end_block("statements")

    def compileDo(self):
        self.start_block("doStatement")
        self.process() # 'do'
        self.process() # identifier (subroutineName or className or varName)
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == '.':
            self.process() # '.'
            self.process() # subroutineName
        self.process() # '('
        self.compileExpressionList()
        self.process() # ')'
        self.process() # ';'
        self.end_block("doStatement")

    def compileLet(self):
        self.start_block("letStatement")
        self.process() # 'let'
        self.process() # varName
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == '[':
            self.process() # '['
            self.compileExpression()
            self.process() # ']'
        self.process() # '='
        self.compileExpression()
        self.process() # ';'
        self.end_block("letStatement")

    def compileWhile(self):
        self.start_block("whileStatement")
        self.process() # 'while'
        self.process() # '('
        self.compileExpression()
        self.process() # ')'
        self.process() # '{'
        self.compileStatements()
        self.process() # '}'
        self.end_block("whileStatement")

    def compileReturn(self):
        self.start_block("returnStatement")
        self.process() # 'return'
        if not (self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ';'):
            self.compileExpression()
        self.process() # ';'
        self.end_block("returnStatement")

    def compileIf(self):
        self.start_block("ifStatement")
        self.process() # 'if'
        self.process() # '('
        self.compileExpression()
        self.process() # ')'
        self.process() # '{'
        self.compileStatements()
        self.process() # '}'
        if self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == 'else':
            self.process() # 'else'
            self.process() # '{'
            self.compileStatements()
            self.process() # '}'
        self.end_block("ifStatement")

    def compileExpression(self):
        self.start_block("expression")
        self.compileTerm()
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in '+-*/&|<>=':
            self.process() # op
            self.compileTerm()
        self.end_block("expression")

    def compileTerm(self):
        self.start_block("term")
        t_type = self.tokenizer.tokenType()

        if t_type in ["INT_CONST", "STRING_CONST"]:
            self.process()
        elif t_type == "KEYWORD": # true, false, null, this
            self.process()
        elif t_type == "SYMBOL":
            if self.tokenizer.symbol() == '(':
                self.process() # '('
                self.compileExpression()
                self.process() # ')'
            elif self.tokenizer.symbol() in '-~': # unaryOp
                self.process()
                self.compileTerm()
        elif t_type == "IDENTIFIER":
            next_token = self.tokenizer.peekNextToken()
            if next_token == '[':
                self.process() # varName
                self.process() # '['
                self.compileExpression()
                self.process() # ']'
            elif next_token == '(':
                self.process() # subroutineName
                self.process() # '('
                self.compileExpressionList()
                self.process() # ')'
            elif next_token == '.':
                self.process() # className / varName
                self.process() # '.'
                self.process() # subroutineName
                self.process() # '('
                self.compileExpressionList()
                self.process() # ')'
            else:
                self.process() # varName
        self.end_block("term")

    def compileExpressionList(self):
        self.start_block("expressionList")
        if not (self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ')'):
            self.compileExpression()
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ',':
                self.process() # ','
                self.compileExpression()
        self.end_block("expressionList")