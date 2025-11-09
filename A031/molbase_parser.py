import sys
from bs4 import BeautifulSoup

def main():
    if len(sys.argv) < 2:
        print("Usage: python molbase_parser.py <html_file>", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except FileNotFoundError:
        print(f"File not found: {filename}", file=sys.stderr)
        sys.exit(1)

    # Find all <h3> elements and print the value of their "title" attribute
    for h3 in soup.find_all("h3"):
        title = h3.get("title")
        if title:
            print(title.strip())

if __name__ == "__main__":
    main()