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
from jinja2 import Template
from sqlalchemy.engine import Engine

try:
    from traitlets.config.configurable import Configurable
except ImportError:
    from IPython.config.configurable import Configurable

import sql.connection
from sql import inspect
import sql.run

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
    def execute(self, line="", cell="", local_ns=None):
        """
        Command
        """
        split = arg_split(line)
        cmd_name, others = split[0].strip(), split[1:]

        if cmd_name == "tables":
            parser = CmdParser()

            parser.add_argument(
                "-s", "--schema", type=str, help="Schema name", required=False
            )

            args = parser.parse_args(others)

            return inspect.get_table_names(schema=args.schema)
        elif cmd_name == "columns":
            parser = CmdParser()

            parser.add_argument(
                "-t", "--table", type=str, help="Table name", required=True
            )
            parser.add_argument(
                "-s", "--schema", type=str, help="Schema name", required=False
            )

            args = parser.parse_args(others)
            return inspect.get_columns(name=args.table, schema=args.schema)
        elif cmd_name == "test":
            parser = CmdParser()

            parser.add_argument(
                "-t", "--table", type=str, help="Table name", required=True
            )
            parser.add_argument(
                "-c", "--column", type=str, help="Column name", required=False
            )
            parser.add_argument(
                "-w", "--within", type=str, help="Whether it is within two numbers", required=False
            )
            args = parser.parse_args(others)

            template = Template(
                """
        SELECT *
        FROM "{{table}}"
        WHERE "{{column}}" < {{whislo}}
        OR  "{{column}}" > {{whishi}}
        """)
            bottom, top = args.within.split(",")
            query = template.render(table=args.table, column=args.column, whislo=int(top), whishi=int(bottom))
            print(query)
            conn = sql.connection.Connection.current.session
            res = conn.execute(query).fetchall()
            print(res)

        else:
            raise UsageError(
                f"%sqlcmd has no command: {cmd_name!r}. "
                "Valid commands are: 'tables', 'columns'"
            )
