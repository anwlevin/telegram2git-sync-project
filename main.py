#!/usr/bin/python
import posixpath

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telegram2git
import os
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Telegram to Git (telegram2git).')

    parser.add_argument('--tokenpath', dest='tokenpath',
                        type=str,
                        required=True,
                        help='token set')

    args = parser.parse_args()

    token_path = os.path.expanduser(args.tokenpath)
    token = telegram2git.token_read(token_path)

    telegram2git.run(token)
