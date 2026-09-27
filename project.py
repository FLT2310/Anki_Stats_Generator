import sys
import zipfile
import zstandard as zstd
import sqlite3
import plotly.express as px
import os
import shutil
import re

TEMPORARY_DIR = "tempki"


def main():

    if not len(sys.argv) == 2:
        print("Usage: project.py <path of anki.apkg file>")
        sys.exit("Error: No input file provided")

    if not is_anki_package(sys.argv[1]):
        sys.exit("File name provided does not end in '.apkg'")

    try:
        extract_db(sys.argv[1])

        db_compressed_path = os.path.join(TEMPORARY_DIR, "collection.anki21b")
        db_decompressed_path = os.path.join(TEMPORARY_DIR, "db")

        decompress_file(db_compressed_path, db_decompressed_path)

        stats = extract_data(db_decompressed_path)

        html_content = assemble_html(
            generate_card_types_graph(stats.get("cards")),
            generate_buttons_pressed_graph(
                stats.get("buttons_pressed"), "Button Breakdown"
            ),
            generate_graph_horizontal_bars(stats.get("leech_rows"), "Top 10 Leeches"),
            generate_graph_horizontal_bars(
                stats.get("mastered_rows"), "Top 10 Mastered Cards (Interval in Days)"
            ),
            generate_retention_rate_graph(stats.get("passed"), stats.get("failed")),
        )

        with open("data/output/Anki_stats.html", "w", encoding="utf-8") as f:
            f.write(html_content)

    finally:
        if os.path.exists(TEMPORARY_DIR):
            shutil.rmtree(TEMPORARY_DIR)

    print("The statistics for your Anki cards are ready!")


def extract_db(file):
    """This function unzips the anki "*.apkg" file"""
    try:

        with zipfile.ZipFile(file) as anki_zip:
            anki_zip.extractall(TEMPORARY_DIR)

    except (zipfile.BadZipFile, FileNotFoundError, zstd.ZstdError):
        sys.exit("Error: Corrupted or non-existent anki package")


def decompress_file(input_name, output_name):
    """This function decompresses a file using the zstandard algorithm"""

    try:
        with open(input_name, "rb") as compressed_file, open(
            output_name, "wb"
        ) as decompressed_file:
            dctx = zstd.ZstdDecompressor()
            dctx.copy_stream(compressed_file, decompressed_file)

    except FileNotFoundError:
        sys.exit("Error: Requested database file was not found.")


def extract_data(anki_db):
    """This function extracts specific data from the anki database and returns it."""

    con = sqlite3.connect(anki_db)
    try:
        cursor = con.cursor()

        return {
            "cards": get_number_of_cards(cursor),
            "buttons_pressed": get_buttons_pressed(cursor),
            "mastered_rows": get_most_known_cards(cursor),
            "leech_rows": get_most_difficult_cards(cursor),
            "passed": get_passed_cards(cursor),
            "failed": get_failed_cards(cursor),
        }

    finally:
        con.close()


def generate_card_types_graph(cards):
    """This function generates a pie chart with all card types"""

    categories = []
    counts = []

    for key in cards.keys():
        categories.append(key.capitalize())

    for key in categories:
        counts.append(cards[key.lower()])

    fig = px.pie(
        names=categories,
        values=counts,
        title="Card Counts",
    )

    fig.update_traces(textposition="inside", textinfo="percent+label")

    return fig


def generate_buttons_pressed_graph(buttons_pressed, title):
    """This function creates a bar chart with the number of times each button was pressed"""

    LABELS = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}
    y = []

    for _, times in buttons_pressed:
        y.append(times)

    fig2 = px.bar(x=LABELS, y=y, title=title)

    return fig2


def generate_graph_horizontal_bars(data, title):
    """This function generates an horizontal bar chart"""

    x = []
    y = []

    for text, times in data:
        x.append(times)
        y.append(clean_anki_text(text))

    return px.bar(x=x, y=y, orientation="h", title=title)


def generate_retention_rate_graph(passed, failed):
    """This function generates a pie chart indicating the retention in percentages (how many times passed and failed were pressed)"""

    retention_rate = calculate_retention_rate(passed, failed)

    fig = px.pie(
        names=["Passed", "Failed"],
        values=[passed, failed],
        title=f"Overall Retention Rate ({retention_rate}%)",
        color=["Passed", "Failed"],
        color_discrete_map={"Passed": "#10B981", "Failed": "#EF4444"},
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")

    return fig


def assemble_html(fig1, fig2, fig3, fig4, fig5):
    """This function adds all the graphs into one big html file and returns it"""

    html_content = (
        fig1.to_html(full_html=False, include_plotlyjs=True)
        + fig2.to_html(full_html=False, include_plotlyjs=False)
        + fig3.to_html(full_html=False, include_plotlyjs=False)
        + fig4.to_html(full_html=False, include_plotlyjs=False)
        + fig5.to_html(full_html=False, include_plotlyjs=False)
    )

    return html_content


"""Helper functions"""


def clean_anki_text(text):
    """This function selects the text before the separator character and removes sound tags from Anki field text."""

    first_field = text.split("\x1f")[0]
    pattern = r"\[sound:.*?\]"
    clean_text = re.sub(pattern, "", first_field).strip()

    return clean_text


def is_anki_package(filename):
    """This function checks whether the filename provided is a string and ends with '.apkg'"""

    try:
        if filename.lower().endswith(".apkg"):
            return True

        return False

    except:
        return False


def calculate_retention_rate(passed, failed):
    """This function calculates the retention rate of the deck"""

    total = passed + failed

    if total == 0 or passed == 0:
        return 0.00

    if total < 0:
        raise ValueError

    retention = round((passed / total * 100), ndigits=2)

    return retention


def get_number_of_cards(cursor):
    """This function queries the db for all the cards and their type"""

    cards = {
        "new": cursor.execute("SELECT COUNT(*) FROM cards WHERE queue = 0").fetchone()[
            0
        ],
        "learning": cursor.execute(
            "SELECT COUNT(*) FROM cards WHERE queue = 1"
        ).fetchone()[0],
        "relearning": cursor.execute(
            "SELECT COUNT(*) FROM cards WHERE queue = 3"
        ).fetchone()[0],
        "young": cursor.execute(
            "SELECT COUNT(*) FROM cards WHERE queue = 2 AND ivl < 21"
        ).fetchone()[0],
        "mature": cursor.execute(
            "SELECT COUNT(*) FROM cards WHERE queue = 2 AND ivl >= 21"
        ).fetchone()[0],
        "suspended": cursor.execute(
            "SELECT COUNT(*) FROM cards WHERE queue = -1"
        ).fetchone()[0],
        "buried": cursor.execute(
            "SELECT COUNT(*) FROM cards WHERE queue = -2 OR queue = -3"
        ).fetchone()[0],
    }

    return cards


def get_buttons_pressed(cursor):
    """This function returns the number of times each button has been pressed"""

    buttons_pressed = cursor.execute(
        "SELECT ease, COUNT(*) FROM revlog WHERE ease BETWEEN 1 AND 4 GROUP BY ease"
    ).fetchall()

    return buttons_pressed


def get_most_known_cards(cursor):
    """This function returns top 10 most known cards"""

    mastered_rows = cursor.execute(
        "SELECT notes.flds, cards.ivl FROM cards JOIN notes ON cards.nid = notes.id ORDER BY cards.ivl DESC LIMIT 10"
    ).fetchall()

    return mastered_rows


def get_most_difficult_cards(cursor):
    """This function returns top 10 most failed cards (called leeches)"""

    leech_rows = cursor.execute(
        "SELECT notes.flds, cards.lapses FROM cards JOIN notes ON cards.nid = notes.id WHERE cards.lapses > 0 ORDER BY cards.lapses DESC LIMIT 10"
    ).fetchall()

    return leech_rows


def get_passed_cards(cursor):
    """This function returns the number of times the user answered correctly to a card (hard, good, easy)"""

    passed = cursor.execute("SELECT COUNT(*) FROM revlog WHERE ease > 1").fetchone()[0]

    return passed


def get_failed_cards(cursor):
    """This function returns the number of times the user answered wrongly to a card (again)"""

    failed = cursor.execute("SELECT COUNT(*) FROM revlog WHERE ease = 1").fetchone()[0]

    return failed


if __name__ == "__main__":
    main()
