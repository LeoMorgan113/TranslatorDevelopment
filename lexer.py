FSuccess = (True, 'Lexer')
tableOfLanguageTokens = {'program': 'keyword', 'end': 'keyword', 'read': 'keyword',
                         'for': 'keyword', 'do': 'keyword',
                         'write': 'keyword', 'to': 'keyword', 'step': 'keyword', 'next': 'keyword', 'if': 'keyword',
                         'fi': 'keyword', 'then': 'keyword', 'else': 'keyword',
                         '=': 'assign_op',
                         '<': 'rel_op', '>': 'rel_op', '<=': 'rel_op', '>=': 'rel_op', '!=': 'rel_op', '==': 'rel_op',
                         ' ': 'ws', '\t': 'ws', '\32': 'ws', '\n': 'eol', '\0': 'eof',
                         ',': 'punct', ';': 'punct', ':': 'colon', '?': 'punct', '.': 'dot',
                         '-': 'add_op', '+': 'add_op', '&&': 'and', '||': 'or',
                         '*': 'mult_op', '/': 'mult_op', '^': 'mult_op', 'E': 'exponent',
                         '(': 'bracket_op', ')': 'bracket_op', '\'': 'bracket_op', 'true': 'boolean', 'false': 'boolean'
                         }
tableIdentFloatInt = {2: 'ident', 4: 'int', 6: 'float'}

stf = {(0, 'ws'): 0,
       # ident
       (0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, 'other'): 2,
       # digit real/int
       (0, 'Digit'): 3, (3, 'Digit'): 3, (3, 'dot'): 5, (3, 'other'): 4, (5, 'Digit'): 5, (5, 'other'): 6,

       (0, ':'): 11, (0, ';'): 11, (0, 'dot'): 11, (0, '('): 11, (0, ')'): 11,

       # assign and equival operator - final 13, 14
       (0, '='): 12, (12, '='): 14,
       (12, 'other'): 13,

        # rel_op final state - 16
       (0, '<'): 15, (0, '>'): 15, (0, '!'): 15,
       (15, '='): 15,
       (15, 'other'): 16,

       (0, 'eol'): 18,  (0, 'eof'): 20,

       (0, '+'): 22, (0, '-'): 22, (0, '*'): 22, (0, '/'): 22, (0, '^'): 22,
       (0, 'E'): 23, (23, '+'): 23, (23, '-'): 23, (23, 'other'): 25,
       (0, 'other'): 105
       }

F = {2, 4, 6, 11, 13, 14, 16, 18, 20, 22, 25, 105}
Fstar = {2, 4, 6, 25}  # зірочка
Ferror = {101, 102, 105}  # обробка помилок

tableOfId = {'r1': (1, 'type_undef', 'val_undef'), 'r2': (2, 'type_undef', 'val_undef')}  # Таблиця ідентифікаторів
tableOfConst = {'0': (1, 'int', 0), '1': (2, 'int', 1)}  # Таблиць констант
tableOfLabel = {}  # Таблиця символів міток програми
tableOfSymb = {}  # Таблиця символів програми (таблиця розбору)
tableOfWrite = {}


f = open('test.lm113', 'r')
sourceCode = f.read()
f.close()


class Lexer:
    def __init__(self):
        self.state = 0
        self.lenCode = len(sourceCode) - 1
        self.numLine = 1
        self.numChar = -1
        self.char = ''
        self.lexeme = ''

    def lex(self):
        try:
            while self.numChar < self.lenCode:
                self.char = self.nextChar()
                classCh = self.classOfChar(self.char)
                self.state = self.nextState(classCh)
                if self.is_final():
                    self.processing()
                elif self.state == 0:
                    self.lexeme = ''
                else:
                    self.lexeme += self.char
        except SystemExit as e:
            FSuccess = (False, 'Lexer')
            print('Lexer: Аварійне завершення програми з кодом {0}'.format(e))

    def proc_token(self):
        self.lexeme += self.char
        token = self.getToken(self.lexeme)

        if self.state != 18:
            print('{0:<3d} {1:<10s} {2:<10s} '.format(self.numLine, self.lexeme, token))
            tableOfSymb[len(tableOfSymb) + 1] = (self.numLine, self.lexeme, token, '')
        self.lexeme = ''
        self.state = 0


    def processing(self):
        if self.state == 20:  # eof
            self.is_final()
        if self.state in (2, 4, 6, 13, 16, 24):  # keyword, ident, int, float
            token = self.getToken(self.lexeme)
            if token != 'keyword':  # не keyword
                index = self.indexIdConst(self.lexeme, token)
                print('{0:<3d} {1:<10s} {2:<10s} {3:<2d} '.format(self.numLine, self.lexeme, token, index))
                tableOfSymb[len(tableOfSymb) + 1] = (self.numLine, self.lexeme, token, index)
            else:  # якщо keyword
                print('{0:<3d} {1:<10s} {2:<10s} '.format(self.numLine, self.lexeme,
                                                          token))  # print(numLine,lexeme,token)
                tableOfSymb[len(tableOfSymb) + 1] = (self.numLine, self.lexeme, token, '')
            self.lexeme = ''
            self.numChar = self.putCharBack(self.numChar)  # зірочка
            self.state = 0
        if self.state in (8, 9, 11, 14, 18, 22):
            self.proc_token()
        if self.state == 25:
            self.proc_token()
            self.numChar = self.putCharBack(self.numChar)
        if self.state in (101, 102, 105):  # ERROR
            self.fail()

    def fail(self):
        print(self.numLine)
        if self.state == 101:
            print('У рядку: ', self.numLine, ' неочікуваний символ після & ' + self.char)
        if self.state == 102:
            print('У рядку: ', self.numLine, ' очікувався символ після |' + self.char)
        if self.state == 103:
            print('У рядку: ', self.numLine, ' очікувався символ після ! ' + self.char)
        if self.state == 105:
            print('у рядку ', self.numLine, ' неочікуваний символ ' + self.char)
            exit(111)



    def is_final(self):
        if self.state in F:
            return True
        else:
            return False

    def nextState(self, classCh):
        try:
            return stf[(self.state, classCh)]
        except KeyError:
            return stf[(self.state, 'other')]

    def nextChar(self):
        self.numChar += 1
        return sourceCode[self.numChar]

    def putCharBack(self, numChar):
        return numChar - 1

    def classOfChar(self, char):
        res = ''
        #print(char)
        if char in '.':
            res = "dot"
        elif char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            res = "Letter"
        elif char in "0123456789":
            res = "Digit"
        elif char in " \t":
            res = "ws"
        elif char in "\n":
            res = "eol"
        elif char in "+-:<>=()&|*/{}!,;.^":
            res = char
        return res

    def getToken(self, lexeme):
        try:
            return tableOfLanguageTokens[lexeme]
        except KeyError:
            return tableIdentFloatInt[self.state]

    def indexIdConst(self, lexeme, token):
        indx = 0
        if self.state == 2:
            indx1 = tableOfId.get(lexeme)
            if indx1 is None:
                indx = len(tableOfId) + 1
                tableOfId[lexeme] = (indx, 'type_undef', 'val_undef')
        elif self.state in (4, 6):
            indx1 = tableOfConst.get(lexeme)
            if indx1 is None:
                indx = len(tableOfConst) + 1
                if self.state == 6:
                    val = float(lexeme)
                elif self.state == 4:
                    val = int(lexeme)
                tableOfConst[lexeme] = (indx, token, val)
        return indx

    def tableToPrint(self, Tbl):
        if Tbl == "Symb":
            self.tableOfSymbToPrint()
        elif Tbl == "Ident":
            self.tableOfIdToPrint()
        elif Tbl == "Const":
            self.tableOfConstToPrint()
        elif Tbl == "Label":
            self.tableOfLabelToPrint()
        elif Tbl == "Write":
            self.tableOfLabelToPrint()
        else:
            self.tableOfSymbToPrint()
            self.tableOfIdToPrint()
            self.tableOfConstToPrint()
            self.tableOfLabelToPrint()
            self.tableOfWritePrint()
        return True

    def tableOfWritePrint(self):
        print("\n Таблиця виведених значень")
        if len(tableOfWrite) == 0:
            print("\n Таблиця виводу - порожня")
        else:
            s1 = '{0:<10s} {1:<15s} '
            print(s1.format("Змінна", "Значення"))
            s2 = '{0:<10s} {1:<10s} '
        for id in tableOfWrite:
            (lex, val) = tableOfWrite[id]
            print(s2.format(lex, str(val)))

    def tableOfSymbToPrint(self):
        print("\n Таблиця символів")
        s1 = '{0:<10s} {1:<10s} {2:<10s} {3:<10s} {4:<5s} '
        s2 = '{0:<10d} {1:<10d} {2:<10s} {3:<10s} {4:<5s} '
        print(s1.format("numRec", "numLine", "lexeme", "token", "index"))
        for numRec in tableOfSymb:  # range(1,lns+1):
            self.numLine, self.lexeme, token, index = tableOfSymb[numRec]
            print(s2.format(numRec, self.numLine, self.lexeme, token, str(index)))

    def tableOfIdToPrint(self):
        print("\n Таблиця ідентифікаторів")
        s1 = '{0:<10s} {1:<15s} {2:<15s} {3:<10s} '
        print(s1.format("Ident", "Type", "Value", "Index"))
        s2 = '{0:<10s} {2:<15s} {3:<15s} {1:<10d} '
        for id in tableOfId:
            index, type, val = tableOfId[id]
            print(s2.format(id, index, type, str(val)))

    def tableOfConstToPrint(self):
        print("\n Таблиця констант")
        s1 = '{0:<10s} {1:<10s} {2:<10s} {3:<10s} '
        print(s1.format("Const", "Type", "Value", "Index"))
        s2 = '{0:<10s} {2:<10s} {3:<10} {1:<10d} '
        for cnst in tableOfConst:
            index, type, val = tableOfConst[cnst]
            print(s2.format(str(cnst), index, type, val))

    def tableOfLabelToPrint(self):
        if len(tableOfLabel) == 0:
            print("\n Таблиця міток - порожня")
        else:
            s1 = '{0:<10s} {1:<10s} '
            print("\n Таблиця міток")
            print(s1.format("Label", "Value"))
            s2 = '{0:<10} {1:<10} '
            for lbl in tableOfLabel:
                val = tableOfLabel[lbl]
                print(s2.format(lbl, val))


if __name__ == '__main__':
    # запуск лексичного аналізатора
    lex = Lexer()
    lex.lex()

    print('-' * 30)
    print('Таблиця розбору tableOfSymb:{0}'.format(tableOfSymb))
    print('-' * 30)
    print('таблиця констант tableOfConst:{0}'.format(tableOfConst))
    print('-' * 30)
    print('таблиця констант tableOfIdent:{0}'.format(tableOfId))
