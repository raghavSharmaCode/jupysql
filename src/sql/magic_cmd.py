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
from sqlglot import select, condition

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
                "-g",
                "--greater",
                type=str,
                help="Greater than a certain number.",
                required=False,
            )
            parser.add_argument(
                "-goe",
                "--greater-or-equal",
                type=str,
                help="Greater or equal than a certain number.",
                required=False,
            )
            parser.add_argument(
                "-l",
                "--less-than",
                type=str,
                help="Less than a certain number.",
                required=False,
            )
            parser.add_argument(
                "-loe",
                "--less-than-or-equal",
                type=str,
                help="Less than or equal to a certain number.",
                required=False,
            )
            parser.add_argument(
                "-nn",
                "--no-nulls",
                help="Returns rows in specified column that are not null.",
                action="store_true",
            )

            args = parser.parse_args(others)

            if args.greater and args.greater_or_equal:
                return ValueError(
                    "You cannot use both greater and greater than or equal to arguments at the same time."
                )
            elif args.less_than and args.less_than_or_equal:
                return ValueError(
                    "You cannot use both less and less than or equal to arguments at the same time."
                )

            query = construct_string_query(args)
            conn = sql.connection.Connection.current.session
            res = conn.execute(query).fetchall()

            if args.no_nulls and len(res) > 0:
                raise ValueError(
                    "Specified column {} has null values present.".format(args.column)
                )
        else:
            raise UsageError(
                f"%sqlcmd has no command: {cmd_name!r}. "
                "Valid commands are: 'tables', 'columns'"
            )


def construct_string_query(args):
    base_query = select("*").from_(args.table)

    if args.greater:
        where = condition(args.column + ">" + args.greater)
        base_query = base_query.where(where)
    if args.greater_or_equal:
        where = condition(args.column + ">=" + args.greater_or_equal)
        base_query = base_query.where(where)
    if args.less_than:
        where = condition(args.column + "<" + args.less_than)
        base_query = base_query.where(where)
    if args.less_than_or_equal:
        where = condition(args.column + "<=" + args.less_than_or_equal)
        base_query = base_query.where(where)
    base_query = base_query.sql()

    if args.no_nulls:
        not_null = condition(args.column + "=NULL")
        base_query = base_query + " AND " + args.column + " IS NOT NULL"

    return base_query
