# pylint: disable=no-member

from docx.document import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.table import Table

from clinical_mdr_api.services.utils.table_f import (
    SimpleFootnote,
    TableCell,
    TableRow,
    TableWithFootnotes,
    table_to_docx,
    table_to_html,
)


def test_table_to_html():
    html = table_to_html(TABLE)
    assert html == HTML


def test_table_to_docx():
    doc: Document = table_to_docx(TABLE, styles=DOCX_STYLES).document
    rows = 5
    cols = 3

    assert len(doc.tables) == 1, "expected exactly 1 table in DOCX document"

    table: Table = doc.tables[0]
    assert len(table.columns) == cols, f"expected {cols} columns of table"
    assert len(table.rows) == rows, f"expected {rows} rows of table"

    # extract all text from the table
    text = "\n".join([cell.text for row in table.rows for cell in row.cells])

    assert TABLE.rows[3].cells[2].text in text

    assert_table_data_in_str(TABLE, text)

    text = "\n".join([p.text for p in doc.paragraphs])

    assert TABLE.footnotes["hello"].text_plain in text


def assert_table_data_in_str(table, text):
    """ensure that textual contents of table is present in a string"""

    for row in table.rows:
        for cell in row.cells:
            txt = cell.text
            if txt:
                assert txt in text, f'text "{txt}" was not found in document'


TABLE = TableWithFootnotes(
    rows=[
        TableRow(
            hide=False,
            cells=[
                TableCell(text="hi", style="hi hi", vertical=True, footnotes=["a"]),
                TableCell(text="hello", span="2"),
                TableCell(style="foo", span=0),
            ],
        ),
        TableRow(
            hide=False,
            cells=[
                TableCell("some text", style="head", footnotes=["hello", "z13"]),
                TableCell("more head"),
                TableCell("also a head"),
            ],
        ),
        TableRow(
            hide=False,
            cells=[
                TableCell("this goes th", style="head"),
                TableCell("data #1 cell"),
                TableCell("data cell #2", style="data"),
            ],
        ),
        TableRow(
            hide=False,
            cells=[
                TableCell("more data th"),
                TableCell(),
                TableCell("foo", footnotes=["z13", "hello"]),
            ],
        ),
        TableRow(
            hide=False,
            cells=[
                TableCell("even more data th"),
                TableCell("X", style="data", footnotes=["a"]),
                TableCell("data"),
            ],
        ),
    ],
    num_header_rows=2,
    num_header_cols=1,
    title="Hello Table",
    footnotes={
        "a": SimpleFootnote(uid="fn01", text_html="not used", text_plain="Footote ej"),
        "hello": SimpleFootnote(
            uid="foot76",
            text_plain="Hello footnotes here and there",
            text_html="not displayed",
        ),
        "z13": SimpleFootnote(
            uid="foot42",
            text_plain="More footnotes after numbering",
            text_html="not shown",
        ),
    },
)


HTML = """<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Hello Table</title>
  </head>
  <body>
    <table>
      <thead>
        <tr>
          <th class="hi hi">hi&nbsp;<sup>a</sup></th>
          <th colspan="2">hello</th>
        </tr>
        <tr>
          <th class="head">some text&nbsp;<sup>hello</sup>&nbsp;<sup>z13</sup></th>
          <th>more head</th>
          <th>also a head</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th class="head">this goes th</th>
          <td>data #1 cell</td>
          <td class="data">data cell #2</td>
        </tr>
        <tr>
          <th>more data th</th>
          <td></td>
          <td>foo&nbsp;<sup>z13</sup>&nbsp;<sup>hello</sup></td>
        </tr>
        <tr>
          <th>even more data th</th>
          <td class="data">X&nbsp;<sup>a</sup></td>
          <td>data</td>
        </tr>
      </tbody>
    </table>
    <dl class="footnotes">
      <dt>a</dt>
      <dd>Footote ej</dd>
      <dt>hello</dt>
      <dd>Hello footnotes here and there</dd>
      <dt>z13</dt>
      <dd>More footnotes after numbering</dd>
    </dl>
  </body>
</html>"""

DOCX_STYLES = {
    "table": ("My Table Style", WD_STYLE_TYPE.TABLE),
    "head": ("Head Style", WD_STYLE_TYPE.PARAGRAPH),
    "data": ("Data Style", WD_STYLE_TYPE.PARAGRAPH),
}
