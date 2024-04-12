from pathlib import Path

STORE_FILE = Path(__file__).resolve().parent.joinpath("news.txt")
TELEGRAM_CHANEL_FILE = 'telegram_channel.txt'


def read_store():
    store = []
    if STORE_FILE.exists():
        with STORE_FILE.open("r") as text:
            block = []
            for line in text:
                line = line.strip()
                if line == "@@@@@":
                    store.append(block)
                    block = []
                    continue
                block.append(line)
            if block:
                store.append(block)
    return store


def get_latest_block():
    store = read_store()
    if store:
        return "\n".join(store[-1])
    else:
        return "Новин немає"


def read_telegram_chanel():
    if Path(TELEGRAM_CHANEL_FILE).exists():
        with open(TELEGRAM_CHANEL_FILE, "r") as file:
            return file.read().strip()
    return None


def write_telegram_chanel(content):
    with open(TELEGRAM_CHANEL_FILE, "w") as file:
        file.write(content)


def publish_latest_news():
    latest_news = get_latest_block()
    last_published_news = read_telegram_chanel()

    if latest_news != last_published_news:
        write_telegram_chanel(latest_news)
        print(latest_news)


if __name__ == "__main__":
    publish_latest_news()
