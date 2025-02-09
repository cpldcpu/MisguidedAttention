import sys
import os
from pathlib import Path

def xor_bytes(data: bytes, key: bytes) -> bytes:
    """XOR the data with the key, repeating the key as needed."""
    key_len = len(key)
    return bytes(data[i] ^ key[i % key_len] for i in range(len(data)))

def process_file(input_path: str, output_path: str, key: bytes, operation: str):
    """Process (scramble/descramble) the input file."""
    with open(input_path, 'rb') as f:
        data = f.read()
    
    processed = xor_bytes(data, key)
    
    with open(output_path, 'wb') as f:
        f.write(processed)

def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ['-s', '-d']:
        print("Usage: python scrambler.py -s|-d <filename>")
        print("  -s: scramble")
        print("  -d: descramble")
        sys.exit(1)

    operation = sys.argv[1]
    filepath = sys.argv[2]
    path = Path(filepath)

    # Secret key - you should change this and keep it secure
    key = b'MisguidedAttention2025'

    if operation == '-s':
        if not path.exists():
            print(f"Error: {filepath} not found")
            sys.exit(1)
        output = path.with_suffix('.scr')
        process_file(filepath, output, key, 'scramble')
        print(f"File scrambled to {output}")

    else:  # -d
        if not path.suffix == '.scr':
            print("Error: Can only descramble .scr files")
            sys.exit(1)
        if not path.exists():
            print(f"Error: {filepath} not found")
            sys.exit(1)
        output = path.with_suffix('.json')
        process_file(filepath, output, key, 'descramble')
        print(f"File descrambled to {output}")

if __name__ == "__main__":
    main()
