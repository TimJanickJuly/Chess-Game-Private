import os
import sys

module_path = os.path.abspath("path/to/your/pyd/file")
if module_path not in sys.path:
    sys.path.append(module_path)

import chess_engine
print("succsess")