import sys
import click
from dotenv import load_dotenv

load_dotenv()

from .run import run_council


@click.command()
@click.argument("hypothesis", nargs=-1, required=True)
def main(hypothesis: tuple[str, ...]) -> None:
    """Submit a hypothesis to the council."""
    h = " ".join(hypothesis).strip()
    if not h:
        click.echo("empty hypothesis", err=True)
        sys.exit(1)
    run_council(h)


if __name__ == "__main__":
    main()
