from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable, Sequence
import marko
import marko.element
import marko.inline
from _parser import parse_change_log
from _types import ChangeItem, ChangeLog, IssueInfo, VersionChanges
from _markdown import Elements, parse_header, parse_item_list, parse_raw_text, skip_blank_lines, validate_element_type


ast = marko.Markdown().parse(Path("file.md").read_text())
change_log = parse_change_log(ast.children)


print(change_log)