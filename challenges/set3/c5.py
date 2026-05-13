
from utils.crypto import MT19937

def solve():
    generator = MT19937(0)
    print(generator.generate_number())
    print(generator.generate_number())



if __name__ == "__main__":
    solve()