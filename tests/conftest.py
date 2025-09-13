# Ensure repo root is in sys.path for test discovery
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
