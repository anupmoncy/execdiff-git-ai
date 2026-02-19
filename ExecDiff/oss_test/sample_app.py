# sample_app.py
"""
A minimal independent sample app for testing purposes.
This script does not depend on execdiff or any external package.
"""
def add(a, b):
    return a + b

def main():
    x = 5
    y = 7
    result = add(x, y)
    print(f"{x} + {y} = {result}")

if __name__ == "__main__":
    main()
