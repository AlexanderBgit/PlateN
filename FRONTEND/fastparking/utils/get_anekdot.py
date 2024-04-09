import random
from pathlib import Path

STORE_FILE = Path(__file__).resolve().parent.joinpath("anekdots.txt")


def read_store():
    store = []
    if STORE_FILE.exists():
        text = STORE_FILE.read_text()
        with STORE_FILE.open("r") as text:
            block = []
            for line in text:
                if line.strip() == "@@@@@":
                    store.append(block)
                    block = []
                    continue
                block.append(line.strip())
    return store


def get_random_block():
    store = read_store()
    len_store = len(store)
    id = random.randint(0, len_store - 1)
    return "\n".join(store[id])


if __name__ == "__main__":
    block = get_random_block()
    print(block)
