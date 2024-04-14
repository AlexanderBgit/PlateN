import time
import argparse
import platform


from telegram_api import crone_pool, send_message_news
from communications.send_news import send_news_to_telegram


def handler_telegram_pool(print_log: bool = False):
    if print_log:
        print("- handler_telegram_pool")
    crone_pool()


def handler_limit_check(print_log: bool = False):
    if print_log:
        print("- handler_limit_check")


def handler_news_check(print_log: bool = False):
    if print_log:
        print("- handler_news_check")
    send_news_to_telegram()
    # send_message_news(
    #     "Simulation news sending, every 15 mins since start app: <datetime>"
    # )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Infinite loop of service app events")
    parser.add_argument("--loop", action="store_true")
    parser.add_argument(
        "--delay", type=int, default=1, help="loop delay in seconds, default 1 sec"
    )
    parser.add_argument(
        "-t",
        "--telegram_period",
        type=int,
        default=2,
        help="Telegram bot pool period in seconds, default 2 sec",
    )
    parser.add_argument(
        "-l",
        "--limit_period",
        type=int,
        default=300,
        help="Limit Check period in seconds, default 300 sec",
    )
    parser.add_argument(
        "-n",
        "--news_period",
        type=int,
        default=60 * 15,
        help="Limit Check period in seconds, default 900 sec (15 mins)",
    )
    parser.add_argument(
        "--sent_hello",
        action="store_true",
        help="hello message on boot",
    )
    parser.add_argument("-q", "--quite", action="store_true", help="Quite")
    args = parser.parse_args()
    if args.sent_hello:
        if platform.system() != "Linux":
            text = "Local developer run 'sheduler.py' at: <datetime>"
        else:
            text = (
                "Hosting server just applied new changes of git branch at: <datetime>"
            )
        result = send_message_news(text)
    # print(f"{result=}")
    if args.loop:
        loop_delay = args.delay
        time_now = time.time()
        periods = {
            "telegram_pool": args.telegram_period,
            "limit_check": args.limit_period,
            "news_check": args.news_period,
        }
        actions = {
            "telegram_pool": handler_telegram_pool,
            "limit_check": handler_limit_check,
            "news_check": handler_news_check,
        }

        times = {period_name: time_now for period_name in periods.keys()}
        print_log = not args.quite
        try:
            while True:
                time_now = time.time()

                deltas: dict = {
                    period_name: time_now - times[period_name]
                    for period_name in periods.keys()
                }
                for period_name in periods.keys():
                    if deltas[period_name] > periods[period_name]:
                        times[period_name] = time_now
                        actions[period_name](print_log)
                if print_log:
                    print(f"Loop... {loop_delay}")
                time.sleep(loop_delay)
        except KeyboardInterrupt:
            print("*** Terminated by user pressing: Ctrl-C")
