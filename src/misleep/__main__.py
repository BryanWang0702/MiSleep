# -*- coding: UTF-8 -*-
"""Entry point for ``python -m misleep [data] [anno]`` (launches the GUI)."""

import sys


def main():
    from misleep.gui.app import show
    from misleep.gui.app import _parse_args

    data_path, anno_path = _parse_args(sys.argv[1:])
    show(data_path=data_path, anno_path=anno_path)


if __name__ == "__main__":
    main()
