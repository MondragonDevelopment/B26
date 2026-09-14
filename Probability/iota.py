import sys
import os
from gmpy2 import get_context, exp, const_pi


def calculateIota(output_file="iot.txt", chunk_size=5_000_000):
    """
    Calculates 100 MB  of i^i = exp(- pi/2) using gmpy2
    """
    target_digits = 100000000

    # Log2(10)  3.321928 bits per decimal digit. Added bits to avoid rounding
    bits_precision = int((target_digits + 50) * 3.321928)
    get_context().precision = bits_precision
    print("I'll calculate...")
    exponent = -const_pi() / 2
    result = exp(exponent)

    # '0.1000' format string specifies the exact number of significant digits
    val_str = format(result, f".{target_digits}f")
    
    if val_str.startswith("0."):
        digits_stream = val_str[2:]
    else:
        digits_stream = val_str
    
    total_written = 0
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("0.")
        
        # Stream the massive string in 5MB blocks to minimize I/O overhead
        for i in range(0, target_digits, chunk_size):
            chunk = digits_stream[i:i+chunk_size]
            f.write(chunk)
            total_written += len(chunk)
            
            if total_written % 50_000_000 == 0 or total_written == target_digits:
                sys.stdout.flush()
    
    print(f"Final file size: {os.path.getsize(output_file) / (1024**2):.4f} MB")


if __name__ == "__main__":
    calculateIota()
