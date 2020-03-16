import asyncio

from client import UnifiedCLIClient


def main():
    with open("token", mode="r") as f:
        token = f.read()

    client = UnifiedCLIClient(token)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.launch())

    client.screen.terminate()

    print("123")


if __name__ == '__main__':
    main()
