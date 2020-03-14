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

    def launch(self):
        greetings = \
            "   U n i f i e d   C L I   \n" + \
            "D i s c o r d   V i e w e r\n" + \
            "                           \n" + \
            "  Connecting to Discord..  "
        grt_max_width = max([len(x) for x in greetings.split("\n")])
        width, height = self.screen.get_size()
        self.screen.put_multiline(
            (width // 2 - grt_max_width // 2, 3), greetings)
        self.run(self.token)

    async def on_ready(self):
        self.screen.clear()
        self.screen.put_str((2, 1), "Discord is ready now.")
