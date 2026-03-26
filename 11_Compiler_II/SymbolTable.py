class SymbolTable:
    def __init__(self):
        self.class_scope = {}
        self.subroutine_scope = {}
        self.counts = {'STATIC': 0, 'FIELD': 0, 'ARG': 0, 'VAR': 0}

    def startSubroutine(self):
        self.subroutine_scope.clear()
        self.counts['ARG'] = 0
        self.counts['VAR'] = 0

    def define(self, name, type_name, kind):
        kind = kind.upper()
        if kind in ['STATIC', 'FIELD']:
            self.class_scope[name] = {'type': type_name, 'kind': kind, 'index': self.counts[kind]}
        else:
            self.subroutine_scope[name] = {'type': type_name, 'kind': kind, 'index': self.counts[kind]}
        self.counts[kind] += 1

    def varCount(self, kind):
        return self.counts[kind.upper()]

    def kindOf(self, name):
        if name in self.subroutine_scope: return self.subroutine_scope[name]['kind']
        if name in self.class_scope: return self.class_scope[name]['kind']
        return None

    def typeOf(self, name):
        if name in self.subroutine_scope: return self.subroutine_scope[name]['type']
        if name in self.class_scope: return self.class_scope[name]['type']
        return None

    def indexOf(self, name):
        if name in self.subroutine_scope: return self.subroutine_scope[name]['index']
        if name in self.class_scope: return self.class_scope[name]['index']
        return None