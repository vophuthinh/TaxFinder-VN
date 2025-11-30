#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Entry point cho CLI tool masothue-cli
Có thể chạy: python masothue_cli.py hoặc python -m masothue.cli
"""

from masothue.cli import main

if __name__ == "__main__":
    import sys
    sys.exit(main())

