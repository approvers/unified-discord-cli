import asyncio as ochinko
import atexit
import curses
import locale
import sys
import unicodedata

import discord

import libs.charutil as charutil
from libs.screen import Screen


class UnifiedCLIClient(discord.Client):
    """
    Discordのクライアント。
    """

    def __init__(self, token):
        super(UnifiedCLIClient, self).__init__()
        self.token = token
        self.screen = Screen()

        self.__connected = False
        self.__logged = False

        self.loop = ochinko.get_event_loop()

        atexit.register(self.terminate)

    async def launch(self):
        self.screen.initialize()

        greetings = \
            "   U n i f i e d   C L I   \n" + \
            "D i s c o r d   V i e w e r\n"
        grt_max_width = max([len(x) for x in greetings.split("\n")])
        width, height = self.screen.get_size()
        self.screen.put_multiline(
            (width // 2 - grt_max_width // 2, 3), greetings)

        self.screen.put_x_center(6, "Logging in to Discord...")
        await self.login(self.token)
        self.__logged = True

        self.screen.put_x_center(6, "Connecting to the Server...")
        ochinko.ensure_future(self.connect())

        # on_ready() 関数でこのフラグの値が変わります
        while not self.__connected:
            await ochinko.sleep(0.2)

        self.screen.console.clear()

        await self.mainloop()

    def terminate(self):
        if self.__logged:
            self.loop.run_until_complete(self.logout())

        if self.__connected:
            self.loop.run_until_complete(self.close())

        atexit.unregister(self.terminate)

    async def on_ready(self):
        self.__connected = True

    async def mainloop(self):
        locale.setlocale(locale.LC_ALL, "")

        root_w, root_h = self.screen.get_size()
        header_win = self.screen.create_window((0, 0), (root_w, 1))
        read_win = self.screen.create_window((0, 1), (root_w, root_h - 4))
        write_win = self.screen.create_window((0, root_h - 3), (root_w, 3))

        write_win.nodelay(True)
        write_win.keypad(True)

        self.screen.console.clear()
        self.screen.console.refresh()

        inputted = ""
        input_cursor_x = 0

        channels = self.get_available_channel()
        sel_chn_idx = 0

        i = 0
        while True:

            # -------------------------
            #        Text Input
            # -------------------------

            # ----- Normal Input
            typed = bytearray()
            control_key = False
            while True:
                input_chr = write_win.getch()
                if input_chr == curses.ERR:
                    break

                if not (0 <= input_chr <= 256):
                    control_key = True
                    break
                typed.append(input_chr)

            # ---- Key Binding
            if control_key:
                if input_chr == curses.KEY_UP and sel_chn_idx > 0:
                    sel_chn_idx -= 1
                elif input_chr == curses.KEY_DOWN and sel_chn_idx < len(channels) - 1:
                    sel_chn_idx += 1
                elif input_chr == curses.KEY_BACKSPACE:
                    input_cursor_x -= charutil.get_visible_len(inputted[-1:])
                    inputted = inputted[:-1]
            elif len(typed) > 0:
                if typed[0] in (10, 13):
                    if len(inputted) > 0:
                        ochinko.ensure_future(
                            channels[sel_chn_idx].send(inputted))
                        inputted = ""
                        input_cursor_x = 0
                else:
                    text = typed.decode()
                    inputted += text
                    input_cursor_x += charutil.get_visible_len(text)

            # -------------------------
            #      Screen Update
            # -------------------------

            # ----- Erase
            read_win.erase()
            write_win.erase()
            header_win.erase()

            # ----- Screen Initialize Phase
            write_win.border("|", "|", "-", "-")
            header_win.bkgdset(" ", self.screen.get_color_pair(1))

            # ----- Screen Drawing

            # --- Header
            header_win.addstr(0, 0, self.guilds[0].name)

            # --- Textbox (ish)

            cutted = charutil.right_visibility(root_w - 2, inputted)
            cutted_len = charutil.get_visible_len(
                inputted) - charutil.get_visible_len(cutted)

            write_win.addstr(1, 1, cutted)
            write_win.addstr(
                0, 1, " " + channels[sel_chn_idx].name + " ", curses.A_BOLD)

            if cutted_len > 0:
                write_win.addstr(1, 0, "<")

            write_win.move(1, 1 + input_cursor_x - cutted_len)

            # --- Message
            messages = self.calc_visible_message(root_w - 2, root_h - 4, pad=2)

            y = 1
            for message in messages:
                read_win.addstr(y, 1, message.channel.name)
                lines = charutil.get_wrapped(root_w - 2, message.content)

                read_win.hline(y - 1, 0, "-", root_w)

                read_win.addstr(y, 10, str(len(lines)))

                for i in range(len(lines)):
                    read_win.addstr(y + i + 1, 1, lines[i])

                y += len(lines) + 2

            # ----- Screen Updating

            header_win.refresh()
            read_win.refresh()
            write_win.refresh()

            # ----- Cleaning up
            await ochinko.sleep(1 / 10)

    async def on_error(self, event_method, *args, **kwargs):
        e = sys.exc_info()
        width, height = self.screen.get_size()
        self.screen.put_str((0, height - 1), e[1])

    # ----- Utility Functions -----

    def get_available_channel(self):
        channels = self.get_all_channels()
        availables = filter(lambda x: isinstance(
            x, discord.TextChannel), channels)
        return list(availables)

    def calc_visible_message(self, width, height, pad=1):
        """
        メッセージ表示に必要な行数を計算し、
        画面に収まりきるメッセージの配列を返す。

        :self width: 表示領域の横幅。
        :self height: 表示領域の縦幅。
        :self pad: [デフォ値=1] 計算補正値。
        """

        cached_mes = list(self.cached_messages).copy()
        cached_mes.reverse()
        cached_mes_heights = [len(charutil.get_wrapped(
            width, x.content)) + pad for x in cached_mes]
        height_comsum = [sum(cached_mes_heights[:i+1])
                         for i in range(len(cached_mes_heights))]

        i = 0
        for i in range(len(height_comsum) + 1):
            if len(height_comsum) == i or height_comsum[i] > height:
                break

        return cached_mes[: i][:: -1]
