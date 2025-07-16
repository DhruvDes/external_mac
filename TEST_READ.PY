import time
import struct
import numpy as np

def send_two_matrices(ser, matrix_a, matrix_b, expect_response=True, response_timeout=5, byte_delay=0.000):

    def flatten(matrix):
        return [val for row in matrix for val in row]

    flat_a = flatten(matrix_a)
    flat_b = flatten(matrix_b)

    if len(flat_a) != 16 or len(flat_b) != 16:
        raise ValueError("Each matrix must be 4x4.")

    if any(not (0 <= v <= 255) for v in flat_a + flat_b):
        raise ValueError("All matrix values must be 8-bit integers (0–255).")

    # Combine into 32-byte payload
    payload = bytes(flat_a + flat_b)

    # Print matrix contents
    print("\n🔼 Sending matrices to FPGA:")
    print("Matrix A:")
    for row in matrix_a:
        print("  ", row)
    print("Matrix B:")
    for row in matrix_b:
        print("  ", row)

    # Show raw bytes being sent
    print("\n📤 Bytes being written (hex):")
    print("  ", " ".join(f"{b:02X}" for b in payload))

    # Send each byte with delay
    for b in payload:
        ser.write(bytes([b]))
        time.sleep(byte_delay)

    if not expect_response:
        return None

    # --- RECEIVE SECTION ---
    ser.timeout = 0.1
    buffer = bytearray()
    start = time.time()

    while time.time() - start < response_timeout:
        if ser.in_waiting:
            buffer.extend(ser.read(ser.in_waiting))
            if len(buffer) >= 32:
                break
        time.sleep(0.01)

    if len(buffer) < 32:
        print(f"⚠️ Timeout or incomplete response: received {len(buffer)} of 32 bytes.")
        print("📥 Raw received bytes (hex):", " ".join(f"{b:02X}" for b in buffer))
        return None

    print("\n📥 Raw received bytes (hex):")
    print("  ", " ".join(f"{b:02X}" for b in buffer[:32]))

    # Interpret as 16 unsigned 16-bit ints
    result_values = list(struct.unpack('<16H', buffer[:32]))
    result_matrix = [result_values[i:i+4] for i in range(0, 16, 4)]

    print("\n✅ Received 4x4 matrix from FPGA (uint16 values):")
    for row in result_matrix:
        print("  ", row)

    return result_matrix


import serial
import time

# Setup serial connection
ser = serial.Serial('COM4', 9600, timeout=1)
time.sleep(0.1)  # let the port settle

# Define two 4x4 matrices
A = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 16]
]

B = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 16]
]

c = [
    [41, 42, 43, 44],
    [45, 46, 47, 48],
    [49, 50, 51, 52],
    [53, 54, 55, 56]
]
# Send to FPGA
send_two_matrices(ser, A, B, byte_delay=0.002)  # 2 ms delay between bytes

send_two_matrices(ser, c, B, byte_delay=0.002)  # 2 ms delay between bytes

np.matmul()

ser.close()
