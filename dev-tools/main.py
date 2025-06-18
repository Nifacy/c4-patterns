from pathlib import Path
import marko
from change_log import parse_change_log


ast = marko.Markdown().parse(Path("file.md").read_text())
change_log = parse_change_log(ast.children)


print(change_log)
