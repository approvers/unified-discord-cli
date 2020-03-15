import asyncio as ochinko
import atexit

import discord

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

        atexit.register(self.terminate)

    async def launch(self):
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
        await self.connect()
        self.__connected = True

        await self.mainloop()

    def terminate(self):
        if self.__logged:
            self.logout()

        if self.__connected:
            self.close()

        atexit.unregister(self.terminate)

    async def mainloop():
        while True:
            await ochinko.sleep(0.1)

    async def on_ready(self):
        self.screen.clear()
        self.screen.put_str((2, 1), "Discord is ready now.")
