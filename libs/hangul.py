hangul_ranges = (
    [0xAC00, 0xD7A4],  # Hangul Syllables (AC00–D7A3)
    [0x1100, 0x1200],  # Hangul Jamo (1100–11FF)
    [0x3130, 0x3190],  # Hangul Compatibility Jamo (3130-318F)
    [0xA960, 0xA980],  # Hangul Jamo Extended-A (A960-A97F)
    [0xD7B0, 0xD800],  # Hangul Jamo Extended-B (D7B0-D7FF)
)

def is_hangul(ch):
    val = ord(ch)
    for r in hangul_ranges:
        if val >= r[0] and val <= r[1]:
            return True
    return False

def count_hangul(string):
    count = 0
    for ch in string:
        if is_hangul(ch):
            count += 1
    return count