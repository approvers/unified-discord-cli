import atexit
import curses
import locale

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()
console = None


class ConsoleScreen:
    """
    Cursesを使ってコンソールを管理するのに便利になるクラス
    """

    def __init__(self):
        self.screen = curses.initscr()
        self.__initialize()

        atexit.register(self.terminate)

    def __initialize(self):
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)

    def terminate(self):
        curses.nocbreak()
        self.screen.keypadq(False)
        curses.echo()

    def __del__(self):
        atexit.unregister(self.terminate)
        self.terminate()
