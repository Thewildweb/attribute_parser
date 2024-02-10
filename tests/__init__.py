import os
import sys

# Add the parent directory to the path so that we can import the
# module we want to test.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
