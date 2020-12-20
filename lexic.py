###
# Внутренне пердставелние лексем - пара(название класса, номер в классе).
# Номер в классе == номер строки в таблице лексем соответствующего класса.
###


class LexicalAnalyzer:  # класс лексического анализатора Pascal кода
    def __init__(self, program_filename):
        self.ch = ''  # "ячейка" под символ
        self.buf = ''  # инициализируем пустой буфер
        self.state = ['H', 'ID', 'NUM', 'COM', 'ASGN', 'DLM', 'FINE', 'ER']  # инициализируем список состояний
        self.TW = ['program', 'var', 'integer', 'real', 'bool', 'begin', 'end',
                   'if', 'then', 'else', 'while', 'do', 'read', 'write', 'true',
                   'false', 'println', 'writeln']  # №1 таблица служебных слов Pascal
        self.TD = ['.', ';', ',', ':', ':=', '(', ')', '+', '-', '*', '/', '=', '>', '<']  # №2 таблица ограничителей
        self.T_NUM = []  # №3 таблица чисел констант, используемых в коде Pascal
        self.TID = []  # №4 таблица идентификаторов
        self.dt = 0  # объект(переменная) под числовое значение константы
        self.current_state = 'H'  # изначальное состояние
        self.program_filename = program_filename
        self.file = None
        self.lexeme_list = []
        self.token_list = []

    def get_next(self):  # переход к следующему символу из строки(файла) вхождения
        self.ch = self.file.read(1)

    def clear(self):  # очистка буфера
        self.buf = ''

    def add(self):  # добавление символа в конец буфера
        self.buf += self.ch

    def look(self, cls):  # поиск по таблицам лексемы из буфера
        if self.buf in cls:
            self.token_list.append('<' + self.buf + '>')
            return cls.index(self.buf)  # нашли - вернули индекс
        else:
            return -1  # не нашли - вернули -1

    def put(self, cls):  # запись в таблицу лексемы из буфера
        if self.buf not in cls:
            cls.append(self.buf)  # если не нашли - запишем
            self.token_list.append('<' + self.buf + '>')
        else:
            self.token_list.append('<' + self.buf + '>') ########################
        return cls.index(self.buf)  # если нашли - вернули индекс

    def putNum(self, cls):  # запись в таблицу константы из d
        if self.dt not in cls:
            cls.append(self.dt)  # если не нашли - запишем
            self.token_list.append('<' + str(self.dt) + '>')
        else:
            self.token_list.append('<' + str(self.dt) + '>') ######################
        return cls.index(self.dt)  # если нашли - вернули индекс

    def make_lex(self, cls, num):  # создание лексеме в виде пары(номер класса, номер в классе)
        localize = [[1, 'Служебное слово'],
                    [2, 'Знак или ограничитель'],
                    [3, 'Константа'],
                    [4, 'Идентификатор']]
        for case in localize:
            if cls == case[0]:
                cls = case[1]
        self.lexeme_list.append([cls, num])

    def run_analysis(self):
        self.file = open(self.program_filename, 'r')
        self.get_next()
        while True:
            if self.current_state == 'H':
                if self.ch == ' ' or self.ch == '\n' or self.ch == '\t':  # пропускаем пробел, переход, табуляцию
                    self.get_next()
                elif self.ch.isalpha():  # если буква
                    self.clear()
                    self.add()
                    self.get_next()
                    self.current_state = 'ID'
                elif self.ch.isdigit():  # число
                    self.dt = int(self.ch)
                    self.get_next()
                    self.current_state = 'NUM'
                elif self.ch == '{':  # комент
                    self.get_next()
                    self.current_state = 'COM'
                    self.token_list.append('<' + self.ch + '>')  #####################
                elif self.ch == ':':  # присвоение
                    self.get_next()
                    self.current_state = 'ASGN'
                    self.token_list.append('<:>')
                elif self.ch == '.':  # конец
                    self.make_lex(2, 0)
                    self.current_state = 'FIN'
                    self.token_list.append('<' + self.ch + '>')
                else:
                    self.current_state = 'DLM'
            elif self.current_state == 'ID':
                if self.ch.isalpha() or self.ch.isdigit():
                    self.add()
                    self.get_next()
                else:
                    j = self.look(self.TW)
                    if j != -1:
                        self.make_lex(1, j)
                    else:
                        j = self.put(self.TID)
                        self.make_lex(4, j)
                    self.current_state = 'H'
            elif self.current_state == 'NUM':
                if self.ch.isdigit():
                    self.dt = self.dt * 10 + int(self.ch)
                    self.get_next()
                else:
                    j = self.putNum(self.T_NUM)
                    self.make_lex(3, j)
                    self.current_state = 'H'
            elif self.current_state == 'DLM':   # ограничитель
                self.clear()
                self.add()
                j = self.look(self.TD)  # поиск в таблице ТD лексемы из буфера (0 если такой лексемы нет)
                if j != -1:
                    self.get_next()
                    self.make_lex(2, j)
                    self.current_state = 'H'
                else:
                    self.lexeme_list.append(['<ERROR>', '<ERROR>'])
                    self.token_list.append('<!!!ERROR!!!>')
                    self.current_state = 'ER'   # состояние ошибки
            elif self.current_state == 'ASGN':
                if self.ch == '=':
                    self.make_lex(2, 4)
                else:
                    self.make_lex(2, 3)
                self.get_next()
                self.current_state = 'H'
            if self.current_state == 'FIN' or self.current_state == 'ER':
                break
        if self.current_state == 'ER':
            print('Ошибка! Проверьте файл с кодом паскаль на ошибки.')
        if self.current_state == 'FIN':
            print('Лексический анализ выполнен.')
        self.file.close()
        return self.lexeme_list, self.token_list


if __name__ == '__main__':
    way = './programs/example3.pas'
    lexeme_list = LexicalAnalyzer(way).run_analysis()
    container = []
    k = -1
    for lex in lexeme_list[0]:
        k = k+1
        container.append(str(lex)+' '+str(lexeme_list[1][k]))
    with open(f'{way.replace(".pas", "", 1)}-result.txt', "w") as file:
        for rows in container:
            file.write(rows + '\n')
    print(f'Результат записан в файл {way.replace(".pas", "", 1)}-result.txt')
