import logging
import sys
from typing import Optional

from pydantic import BaseModel, Field, PrivateAttr

from autobox.utils.normalization import value_to_id


def print_banner():
    print(
        """\n
 █████╗ ██╗   ██╗████████╗ ██████╗ ██████╗  ██████╗ ██╗  ██╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔══██╗██╔═══██╗╚██╗██╔╝
███████║██║   ██║   ██║   ██║   ██║██████╔╝██║   ██║ ╚███╔╝
██╔══██║██║   ██║   ██║   ██║   ██║██╔══██╗██║   ██║ ██╔██╗
██║  ██║╚██████╔╝   ██║   ╚██████╔╝██████╔╝╚██████╔╝██╔╝ ██╗
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝

"""
    )


class Logger(BaseModel):
    name: str
    verbose: bool = Field(default=False)
    log_path: Optional[str] = None
    log_file: Optional[str] = None
    _logger: logging.Logger = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        if self.log_file is None:
            # self.log_file = datetime.now().strftime("%Y%m%d%H%M") + ".log"
            self.log_file = f"{value_to_id(self.name)}.log"

        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(logging.DEBUG)

        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        err_handler = logging.FileHandler(f"{self.log_path}/{self.log_file}")
        stdout_handler.setLevel(logging.DEBUG)
        err_handler.setLevel(logging.DEBUG)

        # fmt = logging.Formatter(
        #     "%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s"
        # )
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        stdout_handler.setFormatter(fmt)
        err_handler.setFormatter(fmt)
        self._logger.addHandler(stdout_handler)
        self._logger.addHandler(err_handler)

    def info(self, message: str):
        if self.verbose:
            print(message)

        self._logger.info(message)

    def error(self, message: str, exception: Exception = None):
        if self.verbose:
            print(message)

        self._logger.error(message, exc_info=exception)
