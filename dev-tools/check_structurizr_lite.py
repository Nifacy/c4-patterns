from typing import NoReturn


from _exporters import StructurizrLite
from pathlib import Path


def main() -> NoReturn:
    lite = StructurizrLite(
        structurizr_lite_dir=Path(".bin/structurizr-lite"),
        java_path=Path("D:\\Program Files\\Java\\jdk-17\\bin\\"),
        syntax_plugin_path=Path(".bin/pattern-syntax-plugin-1.0.jar"),
    )

    try:
        result = lite.export_to_json(Path(".bin/examples/databasePerService.dsl"))
        print(f"Result: {result}")
    finally:
        lite.close()


if __name__ == '__main__':
    main()
