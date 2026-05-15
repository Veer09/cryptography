import time
from utils.crypto import untemper_rand
from utils.crypto import MT19937


def solve():
    ts = int(time.time())
    original_generator = MT19937(ts)
    rand_ouputs = []
    for i in range(624):
        rand_ouputs.append(original_generator.generate_number())

    state = []
    for rand in rand_ouputs:
        state.append(untemper_rand(rand))

    ts_new = int(time.time())
    crack_generator = MT19937(ts_new)
    crack_generator.mt_state = state

    for i in range(100):
        orignal = original_generator.generate_number()
        cracked = crack_generator.generate_number()
        if orignal != cracked:
            print("Wrong Cracked number")
            break
        print("Original Random Number: " + str(orignal))
        print("Cracked Random Number: " + str(cracked))


if __name__ == "__main__":
    solve()
