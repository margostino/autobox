import logging
import sys
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PrivateAttr


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
    agent_name: str
    verbose: bool = Field(default=False)
    log_path: Optional[str] = None
    log_file: Optional[str] = None
    _logger: logging.Logger = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        if self.log_file is None:
            self.log_file = datetime.now().strftime("%Y%m%d%H%M") + ".log"
        self._logger = logging.getLogger(self.agent_name)
        self._logger.setLevel(logging.DEBUG)

        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        err_handler = logging.FileHandler(f"{self.log_path}/{self.log_file}")
        stdout_handler.setLevel(logging.DEBUG)
        err_handler.setLevel(logging.DEBUG)

        # fmt = logging.Formatter(
        #     "%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s"
        # )
        fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(message)s")
        stdout_handler.setFormatter(fmt)
        err_handler.setFormatter(fmt)
        self._logger.addHandler(stdout_handler)
        self._logger.addHandler(err_handler)

    def info(self, message: str):
        if self.verbose:
            print(message)

        self._logger.info(message)
