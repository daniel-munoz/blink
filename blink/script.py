#!/usr/bin/python3
import os
import sys
import yaml
from blink import Blink


def _main():
    config_fn = os.path.join(os.path.expanduser("~"), '.blinkconfig')
    if os.path.isfile(config_fn):
        with open(config_fn) as f:
            config = yaml.load(f.read())
            if isinstance(config, dict):
                if len(config) == 1:
                    _email, _password = list(config.items())[0]
                if len(config) > 1:
                    raise Exception('Multiple email/passwords found in .blinkconfig. Please specify which ones to use.')
            else:
                raise Exception('File .blinkconfig must be a YAML dictionary. Currently it is a %s.' % type(config))

    args = sys.argv[1:]
    if len(args) > 1 and args[0] == '--archive':
        Blink(_email, _password).archive(args[1])
    else:
        print(f'Usage:\n\t{sys.argv[0]} --archive <dest_dir>')


if __name__ == '__main__':
    _main()
