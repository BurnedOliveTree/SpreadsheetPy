import curses


class Complementary():
    def create_y_label(y, name=""):
        name = chr(65 + (y % 26)) + name
        y = y // 26
        if y == 0:
            return name
        else:
            return Complementary.create_y_label(y-1, name)

    def recreate(name, x):
        y = 0
        for i in range(len(name)):
            y = y * 26 + (ord(name[i]) - 65)
        return y, int(x)

    def main(y, x):
        # initiating curses window and all required functions for it
        stdscr = curses.initscr()   # initiate screen
        curses.noecho()   # display keys only when needed
        curses.cbreak()   # keys react without needing Enter
        stdscr.keypad(True)   # direction keys work as they should

        curses.wrapper(Complementary.wrapped, y, x)

        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def wrapped(stdscr, size_x, size_y):
        # size_y = size_y % (((curses.LINES - 2) // 2) % size_y - 1)
        spreadsheet_one = Spreadsheet(size_x, size_y)
        Spreadsheet.actual_main(spreadsheet_one, stdscr)


class Spreadsheet():
    def __init__(self, size_x, size_y):
        self.label = [['' for x in range(size_x)] for y in range(size_y)]
        self.formulas = [['' for x in range(size_x)] for y in range(size_y)]
        self.x_max = size_x
        self.y_max = size_y
        self.x = 0  # current x
        self.y = 0  # current y
        self.cell_size = [1 for y in range(size_y)]
        self.x_labels = [str(x) for x in range(size_x)]
        self.y_labels = [Complementary.create_y_label(y) for y in range(size_y)]
        if len(self.y_labels) > 26:
            self.over_Z = True
        else:
            self.over_Z = False

    def decypher(self, text):
        y, x = "", ""
        for i in range(len(text)):
            temp = text[i]
            if temp.isnumeric():
                x += temp
            elif temp.isupper():
                y += temp
            elif temp.islower():
                y += chr(ord(temp) - 32)
        return y, x

    def calculate(self):
        self.formulas[self.x][self.y] = self.label[self.x][self.y]
        signs = [['^', '*', '/', '+', '-'], [0, 0, 0, 0, 0]]
        temp = self.label[self.x][self.y][1:]
        splited = []
        very_temp = ''
        for i in range(len(temp)):
            if temp[i] in signs[0]:
                if very_temp.isnumeric():
                    splited.append(very_temp)
                else:
                    y, x = (Complementary.recreate(*Spreadsheet.decypher(self, very_temp)))
                    splited.append(self.label[y][x])
                splited.append(temp[i])
                very_temp = ''
            else:
                very_temp += temp[i]
        if very_temp.isnumeric():
            splited.append(very_temp)
        else:
            y, x = (Complementary.recreate(*Spreadsheet.decypher(self, very_temp)))
            splited.append(self.label[y][x])
        for i in range(len(splited)):
            for j in range(len(signs[1])):
                if splited[i] == signs[0][j]:
                    signs[1][j] += 1
        for i in range(len(signs[0])):
            temp = len(splited) - 2
            while signs[1][i] > 0:
                if splited[temp+1] == signs[0][i]:
                    if splited[temp+1] == "^":
                        splited[temp+1] = "**"
                    splited[temp] = str(eval(''.join(splited[temp:temp+3])))
                    del splited[temp+1]
                    del splited[temp+1]
                    signs[1][i] -= 1
                temp -= 1
        self.label[self.x][self.y] = str(splited[0])

    def actual_main(self, stdscr):
        input_key = 'A'
        fn_key = ["KEY_LEFT", "KEY_RIGHT", "KEY_UP", "KEY_DOWN", "\n", chr(27)]
        while ord(input_key) != 27:
            Spreadsheet.print_label(self, stdscr)
            input_key = stdscr.getkey()
            if input_key == fn_key[0]:
                if self.x > 0:
                    self.x -= 1
            elif input_key == fn_key[1]:
                if self.x+1 < self.y_max:
                    self.x += 1
            elif input_key == fn_key[2]:
                if self.y > 0:
                    self.y -= 1
            elif input_key == fn_key[3]:
                if self.y+1 < self.x_max:
                    self.y += 1
            elif input_key == " ":
                pass
            else:
                if self.formulas[self.x][self.y] != '':
                    self.label[self.x][self.y] = self.formulas[self.x][self.y]
                while input_key not in fn_key:
                    if input_key == '\x7f':
                        self.label[self.x][self.y] = self.label[self.x][self.y][:-1] # noqa
                        if self.cell_size[self.x] > 1:
                            self.cell_size[self.x] -= 1
                    else:
                        self.label[self.x][self.y] += input_key
                    Spreadsheet.set_cell_size(self)
                    Spreadsheet.print_label(self, stdscr)
                    input_key = stdscr.getkey()
                if len(self.label[self.x][self.y]) > 0:
                    if self.label[self.x][self.y][0] == "=":
                        Spreadsheet.calculate(self)
                        self.cell_size[self.x] = 1
                        Spreadsheet.set_cell_size(self)
            if input_key in fn_key and input_key != chr(27):
                input_key = 'A'

    def print_label(self, stdscr):
        stdscr.clear()
        lines = "-"+"-"*(sum(self.cell_size)+3*self.y_max)
        x_offset = (self.x_max - 1) // 10 + 3
        y_offset = 3
        prev_y = x_offset
        stdscr.addstr(y_offset-1, x_offset, lines)
        for y in range(self.y_max):
            stdscr.addstr(y_offset-2, prev_y+2-int(self.over_Z), self.y_labels[y])
            for x in range(self.x_max):
                stdscr.addstr(x*2+y_offset, prev_y+2, self.label[y][x])
                stdscr.addstr(x*2+y_offset, prev_y, "|")
            prev_y += self.cell_size[y]+3
        for x in range(self.x_max):
            stdscr.addstr(x*2+y_offset, 1, self.x_labels[x])
            stdscr.addstr(x*2+y_offset+1, x_offset, lines)
            stdscr.addstr(x*2+y_offset, len(lines)-1+x_offset, "|")
        prev_y = 2 + x_offset
        for y in range(self.x):
            prev_y = prev_y + self.cell_size[y] + 3
        stdscr.addstr(self.y*2+y_offset, prev_y+len(self.label[self.x][self.y]), "")

    def set_cell_size(self):
        for x in range(self.x_max):
            for y in range(self.y_max):
                if len(self.label[y][x]) > self.cell_size[y]:
                    self.cell_size[y] = len(self.label[y][x])


if __name__ == "__main__":
    Complementary.main(5, 35)
