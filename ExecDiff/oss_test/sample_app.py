# sample_app.py
"""
A minimal independent sample app for testing purposes.
This script does not depend on execdiff or any external package.
"""

import math
import pandas as pd

def add(a, b):
    return a + b

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def get_first_n_primes(n):
    primes = []
    num = 2
    while len(primes) < n:
        if is_prime(num):
            primes.append(num)
        num += 1
    return primes

def circle_area(radius):
    return math.pi * radius ** 2

def fibonacci(n):
    """Generate first n Fibonacci numbers"""
    if n <= 0:
        return []
    fib = [0, 1]
    for _ in range(n - 2):
        fib.append(fib[-1] + fib[-2])
    return fib[:n]

def main():
    x = 5
    y = 7
    result = add(x, y)
    print(f"{x} + {y} = {result}")
    
    # Get first 5 primes and calculate circle areas
    primes = get_first_n_primes(5)
    areas = [circle_area(r) for r in primes]
    
    # Create DataFrame
    df = pd.DataFrame({
        'radius': primes,
        'area': areas
    })
    
    print("\nCircle Areas with Prime Radii:")
    print(df)
    
    # New: Show Fibonacci sequence
    fib = fibonacci(5)
    print(f"\nFirst 5 Fibonacci numbers: {fib}")
    
    return df

if __name__ == "__main__":
    main()
