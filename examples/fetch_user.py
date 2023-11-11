import sys
import os
sys.path.append(os.getcwd())
from src.user import User

if __name__ == '__main__':
    u = User(sys.argv[1])
    u.fetch_updates()
    pass