from lexer import Lexer
from lexer import tableOfSymb


class Syntax:
    def __init__(self):
        pass

    def parseProgram(self):
        try:
            self.parseToken('program', 'keyword', '')
            self.parseStatementList()
            self.parseToken('end', 'keyword', '')

            print('Parser: Синтаксичний аналіз завершився успішно')
            return True
        except SystemExit as e:
            print(f'Parser: Аварійне завершення програми з кодом {e}')

    def parseToken(self, lexeme, token, indent):
        global numRow

        if numRow > len_tableOfSymb:
            self.failParse('неочікуваний кінець програми', (lexeme, token, numRow))

        numLine, lex, tok = self.getSymb()
        numRow += 1

        if (lex, tok) == (lexeme, token):
            print(indent + f'parseToken: В рядку {numLine} токен {(lexeme, token)}')
            return True
        else:
            self.failParse('невідповідність токенів', (numLine, lex, tok, lexeme, token))
            return False

    def getSymb(self):
        if numRow > len_tableOfSymb:
            self.failParse('getSymb(): неочікуваний кінець програми', numRow)
        numLine, lexeme, token, _ = tableOfSymb[numRow]
        return numLine, lexeme, token

    def failParse(self, s, t):
        if s == 'неочікуваний кінець програми':
            (lexeme, token, numRow) = t
            print(
                f'Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером {numRow}. '
                f'\n\t Очікувалось - {(lexeme, token)}')
            exit(1001)
        if s == 'getSymb(): неочікуваний кінець програми':
            numRow = t
            print(
                f'Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером {numRow}.'
                f' \n\t Останній запис - {tableOfSymb[numRow - 1]}')
            exit(1002)
        elif s == 'невідповідність токенів':
            (numLine, lexeme, token, lex, tok) = t
            print(
                f'Parser ERROR: \n\t В рядку {numLine} неочікуваний елемент ({lexeme},{token}). \n\t Очікувався - ({lex},{tok}).')
            exit(1)
        elif s == 'невідповідність інструкцій':
            (numLine, lex, tok, expected) = t
            print(
                f'Parser ERROR: \n\t В рядку {numLine} неочікуваний елемент ({lex},{tok}). \n\t Очікувався - {expected}.')
            exit(2)
        elif s == 'невідповідність у Expression.Factor':
            (numLine, lex, tok, expected) = t
            print(
                f'Parser ERROR: \n\t В рядку {numLine} неочікуваний елемент ({lex},{tok}). \n\t Очікувався - {expected}.')
            exit(3)


    def parseStatementList(self):
        print('\t parseStatementList():')
        while self.parseStatement():
            pass
        return True


    def parseStatement(self):
        print('\t\t parseStatement():')
        numLine, lex, tok = self.getSymb()

        #print(tok, lex)

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
            self.failParse('невідповідність інструкцій', (numLine, lex, tok, 'ident'))
            return False

    def parseAssign(self):
        global numRow
        print('\t' * 4 + 'parseAssign():')
        numLine, lex, tok = self.getSymb()
        numRow += 1

        print('\t' * 5 + f'в рядку {numLine} - {(lex, tok)}')
        if self.parseToken('=', 'assign_op', '\t\t\t\t\t'):
            self.parseExpression()
            return True
        else:
            return False

    def parseExpression(self):
        global numRow
        print('\t' * 5 + 'parseExpression():')
        self.parseTerm()
        f = True

        while f:
            numLine, lex, tok = self.getSymb()
            if tok in 'add_op':
                numRow += 1
                print('\t' * 6 + f'в рядку {numLine} - {(lex, tok)}')
                self.parseTerm()
            else:
                f = False
        return True

    def parseTerm(self):
        global numRow
        print('\t' * 6 + 'parseTerm():')
        self.parseFactor()
        F = True

        while F:
            numLine, lex, tok = self.getSymb()
            if tok in 'mult_op':
                numRow += 1
                print('\t' * 6 + f'в рядку {numLine} - {(lex, tok)}')
                self.parseFactor()
            else:
                F = False
        return True

    def parseFactor(self):
        global numRow
        print('\t' * 7 + 'parseFactor():')
        numLine, lex, tok = self.getSymb()
        print('\t' * 7 + f'parseFactor():=============рядок: {numLine}\t (lex, tok):{(lex, tok)}')

        if tok in ('int', 'float', 'ident'):
            numRow += 1
            print('\t' * 7 + f'в рядку {numLine} - {(lex, tok)}')

        elif lex == '(':
            numRow += 1
            self.parseExpression()
            self.parseToken(')', 'bracket_op', '\t' * 7)
            print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
        else:
            self.failParse('невідповідність у Expression.Factor',
                      (numLine, lex, tok, 'bracket_op, int, float, ident або \'(\' Expression \')\''))
        return True

    def parseWrite(self):
        global numRow
        _, lex, tok = self.getSymb()
        if lex == 'write' and tok == 'keyword':
            numRow += 1
            self.parseFactor()
            return True
        else:
            return False

    def parseRead(self):
        global numRow
        _, lex, tok = self.getSymb()
        if lex == 'read' and tok == 'keyword':
            numRow += 1
            self.parseFactor()
            return True
        else:
            return False

    def parseIf(self):
        global numRow
        _, lex, tok = self.getSymb()
        if lex == 'if' and tok == 'keyword':
            numRow += 1
            self.parseBoolExpr()
            self.parseToken('then', 'keyword', '\t' * 5)
            self.parseStatement()
            self.parseToken('else', 'keyword', '\t' * 5)
            self.parseStatement()
            self.parseToken('fi', 'keyword', '\t' * 5)
            return True
        else:
            return False

    def parseFor(self):
        global numRow
        _, lex, tok = self.getSymb()
        if lex == 'for' and tok == 'keyword':
            numRow += 1
            self.parseAssign()
            self.parseToken('to', 'keyword', '\t' * 5)
            self.parseFactor()
            self.parseToken('step', 'keyword', '\t' * 5)
            self.parseFactor()
            self.parseToken('do', 'keyword', '\t' * 5)
            self.parseStatement()
            self.parseToken('next', 'keyword', '\t' * 5)
            return True
        else:
            return False

    def parseBoolExpr(self):
        global numRow
        self.parseExpression()
        numLine, lex, tok = self.getSymb()
        if tok in 'rel_op':
            numRow += 1
            print('\t' * 5 + f'в рядку {numLine} - {(lex, tok)}')
        else:
            self.failParse('mismatch in BoolExpr', (numLine, lex, tok, 'rel_op'))
        self.parseExpression()
        return True


if __name__ == '__main__':
    lex = Lexer()
    lex.lex()
    print('-' * 30)
    print(f'tableOfSymb:{tableOfSymb}')
    print('-' * 30)

    numRow = 1

    len_tableOfSymb = len(tableOfSymb)
    print(f'len_tableOfSymb: {len_tableOfSymb}')
    syn = Syntax()
    syn.parseProgram()
