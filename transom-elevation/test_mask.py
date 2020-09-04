
from elevations_utils import test_mask

if __name__ == "__main__":
    for i in range(700):
        test_mask(400 + i)
        if 400 + i % 100 == 0:
            print(400 + i)
