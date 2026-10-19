import sys
from ui.app import VocabularyApp


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    app = VocabularyApp()
    app.run()


if __name__ == "__main__":
    main()

