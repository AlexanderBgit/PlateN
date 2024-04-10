import time
import datetime
import argparse


from telegram_api import crone_pool


def handler_telegram_pool():
    print("handler_telegram_pool")
    crone_pool()

def handler_limit_check():
    print("handler_limit_check")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Infinite loop of service app events')
    parser.add_argument('--loop', action='store_true')
    parser.add_argument('--delay', type=int,  default=1, help='loop delay in seconds, default 1 sec') 
    args = parser.parse_args()
    if args.loop:
        loop_delay = args.delay
        time_now = time.time()
        periods = {
            "telegram_pool" : 2,
            "limit_check": 15
        }
        actions = {
            "telegram_pool": handler_telegram_pool, 
            "limit_check":  handler_limit_check
        }

        times = { period_name: time_now for period_name in periods.keys()}
        try:
            while True:
                time_now = time.time()

                deltas: dict = { period_name: time_now - times[period_name]  for period_name in periods.keys() }
                for period_name in periods.keys():
                    if deltas[period_name] > periods[period_name]:
                        times[period_name] = time_now
                        actions[period_name]()

                print(f"Loop... {loop_delay}")
                time.sleep(loop_delay)
        except KeyboardInterrupt:
            print("*** Terminated by user pressing: Ctrl-C")




