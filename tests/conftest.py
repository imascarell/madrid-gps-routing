import os
import sys

# Permite importar los módulos del proyecto desde los tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
