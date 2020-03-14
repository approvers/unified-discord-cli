from client import UnifiedCLIClient


def main():
    try:
        with open("token", mode="r") as f:
            TOKEN = f.read()

        client = UnifiedCLIClient(TOKEN)
        client.launch()
        client.screen.terminate()

        print("123")
    except Exception:
        import traceback

        client.screen.terminate()
        traceback.print_exc()


if __name__ == '__main__':
    main()
