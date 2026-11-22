"""Чашки, чеки и виды кофе 3 января."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from lab import connect


def daily_report(cursor, label):
    cursor.execute((HERE / "today.sql").read_text(encoding="utf-8"))
    cups, receipts, types = map(int, cursor.fetchone())
    print(f"{label}: чашек: {cups}, чеков: {receipts}, видов кофе: {types}")
    return cups, receipts, types


def check_receipts(cursor):
    cursor.execute((HERE / "check.sql").read_text(encoding="utf-8"))
    if cursor.fetchone()[0] != 1:
        raise ValueError("Данные отличаются от примера. Восстановите его командой uv run python lab.py setup 01/01.")


def main():
    new_receipt = (HERE / "add_receipt.sql").read_text(encoding="utf-8")
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute("USE course")
        check_receipts(cursor)
        daily_report(cursor, "До добавления чека")
        for label in ("После добавления чека № 104", "Повторная отправка чека № 104"):
            cursor.execute(new_receipt)
            if daily_report(cursor, label) != (8, 4, 2):
                raise ValueError("Ожидался тот же результат: 8 чашек, 4 чека и 2 вида кофе.")
        check_receipts(cursor)
        cursor.execute("SELECT SUM(cups) FROM cafe_sales WHERE sale_day = '2026-01-02'")
        yesterday = int(cursor.fetchone()[0])
        print(f"2 января по-прежнему продано {yesterday} чашки.")
        print("Эспрессо в чеке № 104 учтён один раз.")


if __name__ == "__main__":
    main()
