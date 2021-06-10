from lexer import Lexer
from lexer import tableOfSymb, tableOfConst, tableOfLabel, FSuccess


class Translator:
    def __init__(self):
        self.postfixCode = []

        self.numRow = 1
        self.len_tableOfSymb = len(tableOfSymb)

        self.toView = True

    def postfixTranslator(self):
        if (True, 'Lexer') == FSuccess:
            # print(self.parseProgram())
            return self.parseProgram()

    def parseProgram(self):
        try:
            self.parseToken('program', 'keyword', '')
            self.parseStatementList()
            self.parseToken('end', 'keyword', '')

            print('Translator: Переклад у ПОЛІЗ та синтаксичний аналіз завершились успішно')
            FSuccess = (True, 'Translator')
            return FSuccess
        except SystemExit as e:
            print('Parser: Аварійне завершення програми з кодом {0}'.format(e))

    def parseToken(self, lexeme, token, ident):
        if self.numRow > self.len_tableOfSymb:
            self.failParse('неочікуваний кінець програми', (lexeme, token, self.numRow))

        numLine, lex, tok = self.getSymb()
        self.numRow += 1

        if (lex, tok) == (lexeme, token):
            print(ident + 'parseToken: В рядку {0} токен {1}'.format(numLine, (lexeme, token)))
            return True
        else:
            self.failParse('невідповідність токенів', (numLine, lex, tok, lexeme, token))
            return False

    def getSymb(self):
        if self.numRow > self.len_tableOfSymb:
            self.failParse('getSymb(): неочікуваний кінець програми', self.numRow)
        self.numLine, lexeme, token, _ = tableOfSymb[self.numRow]
        return self.numLine, lexeme, token

    def failParse(self, str, tuple):
        if str == 'неочікуваний кінець програми':
            (lexeme, token, self.numRow) = tuple
            print(
                'Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з '
                'номером {1}. \n\t Очікувалось - {0}'.format(
                    (lexeme, token), self.numRow))
            exit(1001)
        if str == 'getSymb(): неочікуваний кінець програми':
            self.numRow = tuple
            print(
                'Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з '
                'номером {0}. \n\t Останній запис - {1}'.format(
                    self.numRow, tableOfSymb[self.numRow - 1]))
            exit(1002)
        elif str == 'невідповідність токенів':
            (numLine, lexeme, token, lex, tok) = tuple
            print('Parser ERROR1: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - ({3},{4}).'.format(
                numLine, lexeme, token, lex, tok))
            exit(1)
        elif str == 'невідповідність інструкцій':
            (numLine, lex, tok, expected) = tuple
            print(
                'Parser ERROR2: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(
                    numLine, lex, tok, expected))
            exit(2)
        elif str == 'невідповідність у Expression.Factor':
            (numLine, lex, tok, expected) = tuple
            print(
                'Parser ERROR3: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(
                    numLine, lex, tok, expected))
            exit(3)

    def parseStatementList(self):
        while self.parseStatement():
            pass
        return True

    def parseStatement(self):
        numLine, lex, tok = self.getSymb()

        if tok == 'ident':
            self.parseAssign()
            return True

        elif (lex, tok) == ('if', 'keyword'):
            self.parseIf()
            return True

        elif (lex, tok) == ('for', 'keyword'):
            self.parseFor()
            return True

        elif (lex, tok) == ('write', 'keyword'):
            self.parseWrite()
            return True

        elif (lex, tok) == ('read', 'keyword'):
            self.parseRead()
            return True

        elif (lex, tok) == ('end', 'keyword'):
            return False
        else:
            self.failParse('невідповідність інструкцій', (numLine, lex, tok, 'ident або if'))
            return False

    def configToPrint(self, lex):
        stage = '\nКрок трансляції\n'
        stage += 'лексема: \'{0}\'\n'
        stage += 'tableOfSymb[{1}] = {2}\n'
        stage += 'postfixCode = {3}\n'
        print(stage.format(lex, self.numRow, str(tableOfSymb[self.numRow]), str(self.postfixCode)))

    def parseAssign(self):
        _numLine, lex, tok = self.getSymb()
        self.postfixCode.append((lex, tok))
        if self.toView:
            self.configToPrint(lex)
        self.numRow += 1

        if self.parseToken('=', 'assign_op', '\t\t\t\t\t'):
            self.parseExpression()

            self.postfixCode.append(('=', 'assign_op'))
            if self.toView:
                self.configToPrint('=')
            return True
        else:
            return False

    def parseExpression(self):
        _numLine, lex, tok = self.getSymb()
        self.parseTerm()
        F = True
        while F:
            _numLine, lex, tok = self.getSymb()
            if tok in 'add_op':
                self.numRow += 1
                self.parseTerm()
                self.postfixCode.append((lex, tok))
                if self.toView:
                    self.configToPrint(lex)
            else:
                F = False
        return True

    def parseTerm(self):
        self.parseFactor()
        F = True
        while F:
            _numLine, lex, tok = self.getSymb()
            if tok in ('mult_op', 'exponent'):
                self.numRow += 1
                self.parseFactor()

                self.postfixCode.append((lex, tok))
                if self.toView:
                    self.configToPrint(lex)
            else:
                F = False
        return True

    def parseFactor(self):
        numLine, lex, tok = self.getSymb()
        if tok in ('int', 'float', 'ident'):
            self.postfixCode.append((lex, tok))
            if self.toView:
                self.configToPrint(lex)

            self.numRow += 1
        elif lex == '(':
            self.numRow += 1
            self.parseExpression()
            self.parseToken(')', 'bracket_op', '\t' * 7)
        elif lex == '-':
            self.numRow += 1
            numLine, lex, tok = self.getSymb()
            self.postfixCode.append((lex, tok))
            if self.toView:
                self.configToPrint(lex)
            self.postfixCode.append(('NEG', 'neg_val'))
            self.numRow += 1
        elif lex == '+':
            self.numRow += 1
            self.parseExpression()
        else:
            self.failParse('невідповідність у Expression.Factor',
                      (numLine, lex, tok, 'bracket_op, int, float, ident або \'(\' Expression \')\''))
        return True

    def parseWrite(self):
        _, lex, tok = self.getSymb()
        print('\t' * 7 + 'в рядку {0} - {1}'.format(self.numLine, (lex, tok)))
        self.numRow += 1
        self.parseExpression()
        self.postfixCode.append(('write', 'write'))
        return True

    def parseRead(self):
        _, lex, tok = self.getSymb()
        print('\t' * 7 + 'в рядку {0} - {1}'.format(self.numLine, (lex, tok)))
        self.numRow += 1
        self.parseFactor()
        self.postfixCode.append(('read', 'read'))
        return True

    def readWriteMany(self):
        _, lex, tok = self.getSymb()
        if lex == ',':
            self.numRow += 1
            self.parseFactor()
            return True
        else:
            return False

    def parseIf(self):
        _, lex, tok = self.getSymb()
        if lex == 'if' and tok == 'keyword':
            self.numRow += 1
            self.parseBoolExpr()
            self.parseToken('then', 'keyword', '\t' * 5)
            m1 = self.createLabel()
            self.postfixCode.append(m1)  # Трансляція
            self.postfixCode.append(('JF', 'jf'))
            self.parseStatement()
            k = True
            while k:
                k = self.exprMany()
            m2 = self.createLabel()
            lexElse = False
            _, lexE, tokE = self.getSymb()
            if lexE == 'else' and tokE == 'keyword':
                self.parseToken('else', 'keyword', '\t' * 5)
                self.postfixCode.append(m2)  # Трансляція
                self.postfixCode.append(('JUMP', 'jump'))
                self.setValLabel(m1)  # в табл. міток
                self.postfixCode.append(m1)
                self.postfixCode.append((':', 'colon'))
                self.parseStatement()
                k = True
                while k:
                    k = self.exprMany()
                lexElse = True
            else:
                self.setValLabel(m1)  # в табл. міток
                self.postfixCode.append(m1)
                self.postfixCode.append((':', 'colon'))
            self.parseToken('fi', 'keyword', '\t' * 5)
            if lexElse:
                self.setValLabel(m2)  # в табл. міток
                self.postfixCode.append(m2)  # Трансляція
                self.postfixCode.append((':', 'colon'))
            return True
        else:
            return False

    def parseFor(self):
        global numRow, postfixCode
        stepExpr = 1
        _, lexem, token = self.getSymb()
        self.numRow += 1
        _numLine, lexPrm, tokPrm = self.getSymb()
        self.postfixCode.append((lexPrm, tokPrm))  # Трансляція
        self.numRow += 1
        if self.parseToken('=', 'assign_op', '\t\t\t\t\t'):
            self.parseExpression()  # get value from expression
            self.postfixCode.append(('=', 'assign_op'))  # assign to parameter
        m1 = self.createLabel()
        self.parseToken('to', 'keyword', '\t' * 7)
        self.postfixCode.append(('r1', 'ident'))
        self.postfixCode.append(('1', 'int'))
        self.postfixCode.append(('=', 'assign_op'))
        self.setValLabel(m1)
        self.postfixCode.append(m1)
        self.postfixCode.append((':', 'colon'))
        self.postfixCode.append(('r2', 'ident'))
        _numLine, lexTarget, tokTarget = self.getSymb()
        self.numRow += 1
        self.parseToken('step', 'keyword', '\t' * 7)
        _numLine, lexStep, tokStep = self.getSymb()
        self.postfixCode.append((lexStep, tokStep))
        self.numRow += 1
        m2 = self.createLabel()
        self.postfixCode.append(('=', 'assign_op'))
        self.postfixCode.append(('r1', 'ident'))
        self.postfixCode.append(('0', 'int'))
        self.postfixCode.append(('==', 'rel_op'))
        self.postfixCode.append(m2)
        self.postfixCode.append(('JF', 'jf'))
        self.setValLabel(m2)
        self.postfixCode.append(m2)
        self.postfixCode.append((':', 'colon'))
        self.postfixCode.append((lexPrm, tokPrm))
        self.postfixCode.append((lexPrm, tokPrm))
        self.postfixCode.append(('r2', 'ident'))
        self.postfixCode.append(('+', 'add_op'))
        self.postfixCode.append(('=', 'assign_op'))
        self.postfixCode.append(('r1', 'ident'))
        self.postfixCode.append(('0', 'int'))
        self.postfixCode.append(('=', 'assign_op'))
        self.postfixCode.append((lexTarget, tokTarget))
        self.postfixCode.append((lexPrm, tokPrm))

        self.parseToken('do', 'keyword', '\t' * 7)
        m3 = self.createLabel()
        self.postfixCode.append(('-', 'add_op'))
        self.postfixCode.append(('r2', 'ident'))
        self.postfixCode.append(('*', 'mult_op'))
        self.postfixCode.append(('0', 'int'))
        self.postfixCode.append(('>=', 'rel_op'))
        self.postfixCode.append(m3)
        self.postfixCode.append(('JF', 'jf'))
        self.parseStatement()
        self.parseToken('next', 'keyword', '\t' * 7)
        self.postfixCode.append(m1)
        self.postfixCode.append(('JUMP', 'jump'))
        self.setValLabel(m3)
        self.postfixCode.append(m3)
        self.postfixCode.append((':', 'colon'))

        return True

    def exprMany(self):
        _numLine, lex, tok = self.getSymb()
        if lex == 'if':
            print('parseIf')
            self.parseIf()
            return True
        elif lex == 'for':
            self.parseFor()
            return True
        elif lex == 'write':
            self.parseWrite()
            return True
        elif lex == 'read':
            self.parseRead()
            return True
        elif lex == 'ident':
            self.parseFactor()
            return True
        else:
            return False

    def createLabel(self):
        nmb = len(tableOfLabel) + 1
        lexeme = "m" + str(nmb)
        val = tableOfLabel.get(lexeme)
        if val is None:
            tableOfLabel[lexeme] = 'val_undef'
            tok = 'label'  # # #
        else:
            tok = 'Конфлікт міток'
            print(tok)
            exit(1003)
        return (lexeme, tok)

    def setValLabel(self, lbl):
        lex, _tok = lbl
        tableOfLabel[lex] = len(self.postfixCode)
        return True

    def parseBoolExpr(self):
        self.parseExpression()
        _numLine, lex, tok = self.getSymb()
        if lex == 'true' or lex == 'false':
            self.numRow += 1
            self.postfixCode.append((lex, tok))
            return True
        elif tok in 'rel_op':
            self.numRow += 1
            if lex == '=' and tok in 'assign_op':
                self.numRow += 1
                self.parseExpression()
                self.postfixCode.append((lex, tok))
            else:
                self.parseExpression()
                self.postfixCode.append((lex, tok))
        else:
            self.failParse('mismatch in BoolExpr', (self.numLine, lex, tok, 'rel_op'))
        return True

    def getPostfixCode(self):
        for i in range(len(self.postfixCode)):
            print('{0:<10d} {1:<10s} {2:<10s}'.format(i, self.postfixCode[i][0], self.postfixCode[i][1]))
        return self.postfixCode


if __name__ == '__main__':
    lexer = Lexer()
    lexer.lex()
    poliz = Translator()
    poliz.postfixTranslator()
    poliz.getPostfixCode()

    # lexer.tableToPrint('All')


