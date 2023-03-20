import sys
import argparse

from IPython.utils.process import arg_split
from IPython.core.magic import (
    Magics,
    line_magic,
    magics_class,
)
from IPython.core.magic_arguments import argument, magic_arguments
from IPython.core.error import UsageError


try:
    from traitlets.config.configurable import Configurable
except ImportError:
    from IPython.config.configurable import Configurable


from sql import inspect


class CmdParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)

    def error(self, message):
        raise UsageError(message)


@magics_class
class SqlCmdMagic(Magics, Configurable):
    """%sqlcmd magic"""

    @line_magic("sqlcmd")
    @magic_arguments()
    @argument("line", default="", type=str, help="Command name")
    def _validate_inputs(self, line=""):
        """
        Command
        """

        if line == "":
            raise UsageError(
                "Missing argument for %sqlcmd"
                "\nValid commands are: 'tables', 'columns'"
            )
        else:
            split = arg_split(line)
            command, others = split[0].strip(), split[1:]

            if command == "tables" or command == "columns":
                return self.execute(command, others)
            else:
                raise UsageError(
                    f"{command!r} is not a valid argument for %sqlcmd"
                    "\nValid commands are: 'tables', 'columns'"
                )

    
    @argument("cmd_name", default="", type=str, help="Command name")
    @argument("others", default="", type=str, help="Other tags")
    def execute(self, cmd_name="", others="", cell="", local_ns=None):
        """
        Command
        """

        if cmd_name == "tables":
            parser = CmdParser()

            parser.add_argument(
                "-s", "--schema", type=str, help="Schema name", required=False
            )

            args = parser.parse_args(others)

            return inspect.get_table_names(schema=args.schema)
        else:
            parser = CmdParser()

            parser.add_argument(
                "-t", "--table", type=str, help="Table name", required=True
            )
            parser.add_argument(
                "-s", "--schema", type=str, help="Schema name", required=False
            )

            args = parser.parse_args(others)
            return inspect.get_columns(name=args.table, schema=args.schema)
