from lexer import Lexer
from lexer import tableOfSymb, tableOfId, tableOfConst, tableOfLabel, tableOfWrite, sourceCode, FSuccess
from translator import Translator

# a = 12
# b = 0.05^E1
# f = b + a
# if a > 14 then
#     c = b - 2
#     write(c)
# else
#     write(f)
# fi
#
# for x = 1 to 5 step 1 do
#     write(x)
# next


class Interpreter:
    def __init__(self, postfixCode):
        self.stack = []
        self.value = 0
        self.valL = 0
        self.valR = 0
        self.toView = True
        self.lexer = Lexer()
        self.postfixCode = postfixCode
        self.n = 0
        self.instrNum = 0
        self.cyclesNumb = 0

    def postfixInterpreter(self, translator, fsuccess):
        FSuccess = fsuccess
        if (True, 'Translator') == FSuccess:
            print('\nПостфіксний код: \n{0}'.format(translator.getPostfixCode()))
            return self.postfixProcessing(translator)
        else:
            print('Interpreter: Translator завершив роботу аварійно')
            return False

    def postfixProcessing(self, translator):
        self.postfixCode = translator.getPostfixCode()
        maxNumb = len(self.postfixCode)
        try:
            while self.instrNum < maxNumb and self.cyclesNumb < 1000:
                self.cyclesNumb += 1
                lex, tok = self.postfixCode[self.instrNum]
                if tok in ('int', 'float', 'ident', 'label'):
                    self.stack.append((lex, tok))
                    nextInstr = self.instrNum + 1
                elif tok in ('jump', 'jf', 'colon'):
                    nextInstr = self.doJumps(tok)
                elif tok == 'read':
                    self.doRead()
                    nextInstr = self.instrNum + 1
                elif tok == 'write':
                    self.doWrite()
                    nextInstr = self.instrNum + 1
                else:
                    self.doIt(lex, tok)
                    # print(lex, tok)
                    nextInstr = self.instrNum + 1
                # if self.toView:
                #     self.configToPrint(self.cyclesNumb, lex, tok, maxNumb)
                self.instrNum = nextInstr
            for Tbl in ('Id', 'Const', 'Label', 'Write'):
                self.lexer.tableToPrint(Tbl)
            print('Загальна кiлькiсть крокiв: {0}'.format(self.cyclesNumb))
            return True
        except SystemExit as e:
            # Повідомити про факт виявлення помилки
            print('RunTime: Аварійне завершення програми з кодом {0}'.format(e))
        return True

    def doRead(self):
        (lex, tok) = self.stack.pop()
        print('Очікується введення даних в програму для змінної ' + lex + ': ')
        try:
            val = float(input())
        except:
            self.failRunTime('неправильний тип введених даних', None)
        if type(val) != float:
            self.failRunTime('неправильний тип введених даних', None)
        if val.is_integer():
            val = int(val)
            tableOfId[lex] = (tableOfId[lex][0], 'int', val)
        else:
            tableOfId[lex] = (tableOfId[lex][0], 'float', val)

    def doWrite(self):
        lex, tok = self.stack.pop()
        val = tableOfId[lex][2]
        tableOfWrite[self.n] = (lex, val)
        self.n += 1

    def doJumps(self, tok):
        if tok == 'jump':
            next = self.processing_JUMP()
        elif tok == 'colon':
            next = self.processing_colon()
        elif tok == 'jf':
            next = self.processing_JF()
        return next

    def processing_JUMP(self):
        (label, tok) = self.stack.pop()
        val = tableOfLabel[label]
        return val

    def processing_colon(self):
        if self.stack:
            self.stack.pop()
        val = self.instrNum + 1
        return val

    def processing_JF(self):
        (label, tok) = self.stack.pop()
        val = tableOfLabel[label]
        (boolVal, arg) = self.stack.pop()
        if boolVal == 'true':
            val = self.instrNum + 1
        else:
            val += 1
        return val

    def configToPrint(self, step, lex, tok, maxN):
        if step == 1:
            print('=' * 30 + '\nInterpreter run\n')
            self.lexer.tableToPrint('All')
        print('\nКрок інтерпретації: {0}'.format(step))
        if tok in ('int', 'float'):
            print('Лексема: {0} у таблиці констант: {1}'.format((lex, tok), lex + ':' + str(tableOfConst[lex])))
        elif tok in 'ident':
            print('Лексема: {0} у таблиці ідентифікаторів: {1}'.format((lex, tok), lex + ':' + str(tableOfId[lex])))
        else:
            print('Лексема: {0}'.format((lex, tok)))

        print('postfixCode={0}'.format(self.postfixCode))
        # print(self.stack)

        return True

    def doIt(self, lex, tok):
        if (lex, tok) == ('=', 'assign_op'):
            (lexL, tokL) = self.stack.pop()
            (lexR, tokR) = self.stack.pop()
            tableOfId[lexR] = (tableOfId[lexR][0], tableOfConst[lexL][1], tableOfConst[lexL][2])
        elif tok == 'neg_val':
            (lexR, tokR) = self.stack.pop()
            self.valR = tableOfConst[lexR][2]
            self.getValue((0, '0', 'int'), lex, (self.valR, lexR, tokR))
        else:
            (lexL, tokL) = self.stack.pop()
            (lexR, tokR) = self.stack.pop()
            self.processing_add_mult_op_rel_op((lexL, tokL), lex, (lexR, tokR))
            pass
        return True

    def processing_add_mult_op_rel_op(self, ltL, lex, ltR):
        lexL, tokL = ltL
        lexR, tokR = ltR

        if tokL == 'ident':
            if tableOfId[lexL][1] == 'type_undef':
                self.failRunTime('неініціалізована змінна', (lexL, tableOfId[lexL], (lexL, tokL), lex, (lexR, tokR)))
            else:
                self.valL, tokL = (tableOfId[lexL][2], tableOfId[lexL][1])
        else:
            self.valL = tableOfConst[lexL][2]

        if tokR == 'ident':
            if tableOfId[lexR][1] == 'type_undef':
                self.failRunTime('неініціалізована змінна', (lexR, tableOfId[lexR], (lexL, tokL), lex, (lexR, tokR)))
            else:
                self.valR, tokR = (tableOfId[lexR][2], tableOfId[lexR][1])
        else:
            self.valR = tableOfConst[lexR][2]

        self.getValue((self.valL, lexL, tokL), lex, (self.valR, lexR, tokR))

    def getValue(self, vtL, lex, vtR):
        global value
        # print("LEX = " + str(lex))
        self.valL, lexL, tokL = vtL
        self.valR, lexR, tokR = vtR
        if lex == '+':
            value = self.valL + self.valR
        elif lex == '-':
            value = self.valR - self.valL
        elif lex == '*' and tokL == tokR == 'int':
            value = int(self.valL * self.valR)
            tokL = 'int'
        elif lex == '*' and tokL == tokR == 'float':
            value = float('{:.3f}'.format(self.valL * self.valR))
            tokL = 'float'
        elif lex == '*' and tokL != tokR:
            value = float('{:.3f}'.format(self.valL * self.valR))
            tokL = 'float'
        elif lex == '^':
            value = round(pow(self.valR, self.valL), 3)
            tokL = 'float'
        elif lex == '/' and self.valL == 0:
            self.failRunTime('ділення на нуль', ((lexL, tokL), lex, (lexR, tokR)))
        elif lex == '/' and (tokL == 'float' or tokR == 'float'):
            value = float('{:.3f}'.format(self.valR / self.valL))
        elif lex == '/' and tokL == 'int' and tokR == "int":
            value = float('{:.3f}'.format(self.valR / self.valL))
            tokL = 'float'
        elif lex == 'NEG':
            value = - self.valR
            tokL = tokR
        elif lex == 'E':
            value = round(self.valR * pow(10, self.valL), 3)
            tokL = 'float'
        elif lex == '>':
            if lex == '=':
                if self.valL <= self.valR:
                    value = 'true'
            elif self.valL < self.valR:
                value = 'true'
            else:
                value = 'false'
            tokL = 'bool'
        elif lex == '<':
            if lex == '=':
                if self.valL >= self.valR:
                    value = 'true'
            elif self.valL > self.valR:
                value = 'true'
            else:
                value = 'false'
            tokL = 'bool'
        elif lex == '>=':
            if self.valL <= self.valR:
                value = 'true'
            else:
                value = 'false'
            tokL = 'bool'
        elif lex == '<=':
            if self.valL >= self.valR:
                value = 'true'
            else:
                value = 'false'
            tokL = 'bool'
        elif lex == '==':
            if self.valL == self.valR:
                value = 'true'
            else:
                value = 'false'
            tokL = 'bool'
        elif lex == '!=':
            if self.valL != self.valR:
                value = 'true'
            else:
                value = 'false'
            tokL = 'bool'
        elif lex == '&&':
            if self.valR == self.valL == 'true':
                value = 'true'
            else:
                value = 'false'
            tokL = 'bool'
        elif lex == '||':
            if self.valL == self.valR == 'false':
                value = 'false'
            else:
                value = 'true'
            tokL = 'bool'
        else:
            pass
        self.stack.append((str(value), tokL))
        self.toTableOfConst(value, tokL)

        # tableOfId[lexR] = (tableOfId[lexR][0],  tableOfConst[lexL][1], tableOfConst[lexL][2])

    def toTableOfConst(self, val, tok):
        lexeme = str(val)
        indx1 = tableOfConst.get(lexeme)
        if indx1 is None:
            indx = len(tableOfConst) + 1
            tableOfConst[lexeme] = (indx, tok, val)

    def failRunTime(self, str, tuple):
        if str == 'невідповідність типів':
            ((lexL, tokL), lex, (lexR, tokR)) = tuple
            print('RunTime ERROR: \n\t Типи операндів відрізняються у {0} {1} {2}'.format((lexL, tokL), lex,
                                                                                          (lexR, tokR)))
            exit(1)
        elif str == 'неініціалізована змінна':
            (lx, rec, (lexL, tokL), lex, (lexR, tokR)) = tuple
            print('RunTime ERROR: \n\t Значення змінної {0}:{1} не визначене. Зустрілось у {2} {3} {4}'
                  .format(lx, rec, (lexL, tokL), lex, (lexR, tokR)))
            exit(2)
        elif str == 'ділення на нуль':
            ((lexL, tokL), lex, (lexR, tokR)) = tuple
            print('RunTime ERROR: \n\t Ділення на нуль у {0} {1} {2}. '.format((lexL, tokL), lex, (lexR, tokR)))
            exit(3)


if __name__ == '__main__':
    lexer = Lexer()
    lexer.lex()
    translator = Translator()
    fsuccess = translator.postfixTranslator()
    print(fsuccess)
    interpreter = Interpreter(translator.postfixCode)
    interpreter.postfixInterpreter(translator, fsuccess)
