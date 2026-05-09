import sys


def main():
    if len(sys.argv) < 3:
        print("Usage: python pitwall.py <year> <race>")
        sys.exit(1)

    year = int(sys.argv[1])
    race = " ".join(sys.argv[2:])

    print(f"year: {year}, race: {race}")


if __name__ == "__main__":
    main()
