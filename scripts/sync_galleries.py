#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add the project root to sys.path so we can import gallery_plugin
sys.path.append(str(Path(__file__).resolve().parent.parent))

from gallery_plugin.plugin import main

if __name__ == "__main__":
    main()
