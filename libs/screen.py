import atexit
import curses


class Screen():
    """
    スクリーン関連の処理を楽にするためのクラス
    """

    def __init__(self):
        """
        初期化と合わせて、アプリケーション終了時に
        Cursesライブラリの非初期化を行うように
        スケジュールする。
        """
        self.console = curses.initscr()
        self.terminated = False
        self.__initialize()
        self.console.keypad(True)
        atexit.register(self.terminate)

    def __initialize(self):
        """
        Cursesライブラリの初期化を行う。
        勝手に呼び出されるので人民は呼び出さなくていい
        """
        curses.noecho()
        curses.cbreak()

    def terminate(self):
        """
        Cursesライブラリの非初期化を行う。
        終了するときには呼び出さなくてはいけない。
        というかそうしないとまずくなる。
        """

        if self.terminated:
            return
        self.termnated = True

        self.console.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

        atexit.unregister(self.terminate)
        print("Terminated!")

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

    def clear(self):
        self.console.clear()
