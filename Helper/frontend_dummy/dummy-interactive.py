import os

# DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DIR = os.path.dirname(os.path.abspath(__file__))
while True:
    command = input("enter command or X to quit: ")
    if command == "X":
        exit(0)
    os.system(f"python3 dummy.py {command}")
