from typing import Optional


class YamlOutputter:
    def __init__(self, outpath: Optional[str] = None):
        self.outpath = outpath

    def write(self, message: bytes) -> None:
        content = message.decode(errors="replace")
        out = f"message: |\n  {content.replace('\n','\n  ')}\n"
        if self.outpath:
            with open(self.outpath, "w", encoding="utf-8") as fh:
                fh.write(out)
        else:
            print(out)
