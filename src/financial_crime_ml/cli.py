"""Command-line entry point for the scaffolded project."""

STATUS_MESSAGE = "GCP Financial Crime ML Intelligence Platform scaffold is ready."


def get_status_message() -> str:
    """Return the current scaffold status message."""
    return STATUS_MESSAGE


def main() -> None:
    """Print the scaffold status message."""
    print(get_status_message())


if __name__ == "__main__":
    main()

