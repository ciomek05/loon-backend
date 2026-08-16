import argparse
import uvicorn
from pathlib import Path

from loon.web import app

LOG_CONFIG = Path(__file__).with_name("logging.ini")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--choose-admin",
        metavar="USERNAME",
        help="Promote a user to admin",
    )
    args = parser.parse_args()

    if args.choose_admin is not None:
        from loon.web.admin.cli import choose_admin

        choose_admin(args.choose_admin)
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_config=str(LOG_CONFIG))
