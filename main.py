import argparse
import random
import sys


# Generate Polybius square by seed
def generate_square(size: int = 16, seed: str = "seed") -> list[list[int]]:
    indexes = [index for index in range(size * size)]
    random.Random(seed).shuffle(indexes)
    return [list(indexes[row * size:row * size + size]) for row in range(size)]


# Mapper from character to coordinates in Polybius square
def square_coordinates_mapper(square: list[list[int]]) -> dict[int, tuple[int, int]]:
    mapper = {}
    for row in range(len(square)):
        for column in range(len(square[row])):
            mapper[square[row][column]] = (row, column)
    return mapper


def encrypt(text: bytes, square: list[list[int]]) -> str:
    # Convert int ot string with 0 at the beginning if needed for fixed size
    def int_to_str(value: int, size: int = 2) -> str:
        result = str(value)
        return result[:size] if len(result) >= size else ('0' * (size - len(result))) + result

    mapper = square_coordinates_mapper(square)
    encrypted = []
    for c in text:
        if c not in mapper:
            raise Exception(f"Unknown character {c}")
        encrypted.append(int_to_str(mapper[c][0]))
        encrypted.append(int_to_str(mapper[c][1]))
    return "".join(encrypted)


def decrypt(text: str, square: list[list[int]], coordinate_size: int = 2) -> bytes:
    def str_to_int(value: str) -> int:
        try:
            return int(value)
        except:
            raise Exception(f"Parsing coordinate error for text {value}")

    if len(text) % (coordinate_size * 2) != 0:
        raise Exception(f"Encrypted string size must be divisible by {coordinate_size * 2}")
    decrypted = []
    for i in range(0, len(text), coordinate_size * 2):
        row = str_to_int(text[i:i + coordinate_size])
        column = str_to_int(text[i + coordinate_size:i + coordinate_size * 2])

        if row >= len(square) or row < 0 or column >= len(square[0]) or column < 0:
            raise Exception(f"Row {row} or column {column} out of range")

        decrypted.append(square[row][column].to_bytes(1, 'big'))
    return b"".join(decrypted)


def solve(input_path: str, output_path: str, seed_path: str, mode: str) -> None:
    seed: str = 'seed'
    try:
        with open(seed_path, 'r') as f:
            seed = f.read()
    except:
        raise Exception(f"Cannot open {seed_path}")

    square = generate_square(seed=seed)

    if mode == "encrypt":
        with open(input_path, "rb") as file:
            input_bytes = file.read()
        encrypted_text = encrypt(input_bytes, square)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(encrypted_text)

    elif mode == "decrypt":
        with open(input_path, "r", encoding="utf-8") as file:
            input_text = file.read()
        decrypted_bytes = decrypt(input_text, square)
        with open(output_path, "wb") as file:
            file.write(decrypted_bytes)

    else:
        raise Exception(f"Unknown mode {mode}")


def create_arguments_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Encryption and decryption file by Polybius square algorythm.")
    parser.add_argument(
        "--mode",
        default="encrypt",
        help="working mode encrypt(default)/decrypt",
    )
    parser.add_argument(
        "--input",
        default="input.txt",
        help="input file path"
    )
    parser.add_argument(
        "--output",
        default="output.txt",
        help="output file path"
    )
    parser.add_argument(
        "--seed-file",
        default="seed.txt",
        help="seed file path for square generation"
    )
    return parser


if __name__ == "__main__":
    arguments_parser = create_arguments_parser().parse_args()
    try:
        solve(arguments_parser.input, arguments_parser.output, arguments_parser.seed_file, arguments_parser.mode)
    except Exception as e:
        print(e, file=sys.stderr)
