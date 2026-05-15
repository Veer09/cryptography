from utils.crypto import MT19937
from utils.oracles import random_oracle


def solve():
    random_num, ts = random_oracle()
    for i in range(40, 1001):
        ts_test = ts - i
        generator = MT19937(ts_test)
        if random_num == generator.generate_number():
            print("Found Seeded timestamp: " + str(ts_test))
            break
        

if __name__ == "__main__":
    solve()