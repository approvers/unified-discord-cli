import atexit
import curses
import curses.ascii
import locale


# noinspection PyMethodMayBeStatic
class Screen:
    """
    スクリーン関連の処理を楽にするためのクラス
    """

    def __init__(self):
        self.terminated = False
        self.console = None

    def initialize(self, term_at_exit=True):
        """
        Cursesライブラリの初期化を行い、
        アプリケーション終了時の非初期化をスケジュールする。

        :param term_at_exit: 終了時の非初期化をスケジュールするかどうか。Falseは非推奨。
        """

        self.console = curses.initscr()

        curses.noecho()
        curses.raw()
        curses.cbreak()

        self.console.keypad(True)

        curses.start_color()

        color_pairs = [
            (curses.COLOR_WHITE, curses.COLOR_BLUE)
        ]

        for i in range(len(color_pairs)):
            curses.init_pair(i + 1, color_pairs[i][0], color_pairs[i][1])

        if term_at_exit:
            atexit.register(self.terminate)
            locale.setlocale(locale.LC_ALL, "")

    def terminate(self):
        """
        Cursesライブラリの非初期化を行う。
        終了するときには呼び出さなくてはいけない。
        というかそうしないとまずくなる。
        """

        if self.terminated:
            return
        self.terminated = True

        self.console.keypad(0)
        curses.nocbreak()
        curses.noraw()
        curses.echo()
        curses.endwin()

        atexit.unregister(self.terminate)

    def __del__(self):
        atexit.unregister(self.terminate)
        self.terminate()

    def get_size(self):
        """
        (w, h)でコンソールの大きさを返す。
        """
        return self.console.getmaxyx()[::-1]

    def get_cursor_pos(self):
        """
        (x, y)で現在のカーソル――マウスカーソルではない――を返す。
        """
        return self.console.getyx()[::-1]

    def set_cursor_pos(self, pos):
        """
        カーソル位置を変更する。
        :param pos: (x, y)で新しいカーソル位置。
        """
        self.console.move(pos[1], pos[0])

    def put_str(self, pos, string):
        """
        画面に文字を出力する。
        :param pos: (x, y)で、出力するカーソル位置
        :param string: 出力する文字
        """
        self.console.addstr(pos[1], pos[0], string)
        self.console.refresh()

    def put_multiline(self, pos, string):
        """
        複数行の文字列を正しく出力する。具体的には：
        ・ちゃんと改行文字で改行される
        ・行頭のX座標はpos[0]で揃えられる。

        :param pos: (x, y)で、出力を行うカーソル位置
        :param string: 出力する文字
        """
        lines = string.split("\n")
        for i in range(len(lines)):
            self.console.addstr(pos[1] + i, pos[0], lines[i])

        self.console.refresh()

    def put_x_center(self, y, string):
        """
        画面の横中央に文字列を描画する。
        :param y: Y座標。
        :param string: 文字列。
        """
        width, height = self.get_size()
        x = (width - len(string)) // 2

        self.put_str((x, y), string)

    def create_window(self, start_pos, size):
        """
        新しいウィンドウを生成する。
        :param start_pos: ウィンドウの左端。
        :param size: ウィンドウの大きさ。
        """
        return curses.newwin(size[1], size[0], start_pos[1], start_pos[0])

    def get_color_pair(self, number):
        """
        カラーペアを取得する。
        :param number: カラーペアのID。
        """
        return curses.color_pair(number)

    def clear(self):
        self.console.clear()
        self.console.refresh()
