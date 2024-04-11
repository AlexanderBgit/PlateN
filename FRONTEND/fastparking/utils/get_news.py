from pathlib import Path

STORE_FILE = Path(__file__).resolve().parent.joinpath("news.txt")


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


if __name__ == "__main__":
    block = get_latest_block()
    print(block)
