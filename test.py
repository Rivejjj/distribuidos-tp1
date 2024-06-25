import sys


class EvenDistributionHash:
    def __init__(self, table_size):
        self.table_size = table_size
        self.A = (5 ** 0.5 - 1) / 2  # Knuth's suggestion for A

    def hash(self, key):
        if isinstance(key, str):
            # Convert string to a large integer
            key = sum(ord(char) * (256 ** i) for i, char in enumerate(key))
        elif not isinstance(key, (int, float)):
            raise ValueError("Key must be a string, integer, or float")

        # Use the multiplication method
        return int(self.table_size * ((key * self.A) % 1))


# Example usage
if __name__ == "__main__":
    table_size = 1000
    hasher = EvenDistributionHash(table_size)

    # Test with various inputs
    test_inputs = [
        "hello", "world", "python", "hash",
        42, 3.14, 2718, 31415926535
    ]

    for input_value in test_inputs:
        hash_value = hasher.hash(input_value)
        print(f"Hash of {input_value}: {hash_value}")

    # Optional: Uncomment to test distribution
    distribution = [0] * table_size
    for i in range(100000):
        hash_value = hasher.hash(i)
        distribution[hash_value] += 1
    print(f"Min occurrences: {min(distribution)}")
    print(f"Max occurrences: {max(distribution)}")
    print(f"Average occurrences: {sum(distribution) / len(distribution)}")
