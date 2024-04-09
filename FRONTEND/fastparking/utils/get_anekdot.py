import random
from pathlib import Path

STORE_FILE = Path(__file__).resolve().parent.joinpath("anekdots.txt")


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
    return store


def get_random_block():
    store = read_store()
    len_store = len(store)
    id = random.randint(0, len_store - 1)
    return "\n".join(store[id])


if __name__ == "__main__":
    block = get_random_block()
    print(block)
