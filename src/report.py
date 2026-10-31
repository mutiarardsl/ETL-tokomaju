from pathlib import Path


class Report:
    """Mencetak ke layar sekaligus menyimpan teks yang sama ke file (bukti untuk laporan)."""

    def __init__(self):
        self.lines: list[str] = []

    def add(self, text: str = "") -> None:
        print(text)
        self.lines.append(str(text))

    def save(self, path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")
        return path
