DIRECTIONS = [("N", 0), ("E", 1), ("S", 2), ("W", 3)]


def ascii(val):
    n_wall = "───" if (val & 1) else "   "
    e_wall = "│" if (val & 2) else " "
    s_wall = "───" if (val & 4) else "   "
    w_wall = "│" if (val & 8) else " "

    line1 = f"┼{n_wall}┼"
    line2 = f"{w_wall}   {e_wall}"
    line3 = f"┼{s_wall}┼"
    return line1, line2, line3


def print_all_possibilities() -> None:
    print(f"{'Hex':<4} {'Dec':<4} {'Bin':<12} {'Visual':<12} {'Walls'}")
    print("-" * 50)

    for i in range(16):
        l1, l2, l3 = ascii(i)
        hex_val = f"{i:X}"
        bin_val = f"{i:04b}"

        closed = [name for name, bit in DIRECTIONS if (i >> bit) & 1]
        desc = ", ".join(closed) if closed else "None"

        print(f"{hex_val:<4} {i:<4} {bin_val:<12} {l1:<12} {desc}")
        print(f"{'':<22} {l2}")
        print(f"{'':<22} {l3}")
        print("-" * 50)


if __name__ == "__main__":
    print_all_possibilities()
