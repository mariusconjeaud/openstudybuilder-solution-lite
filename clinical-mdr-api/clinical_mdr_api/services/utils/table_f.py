from typing import Any, Mapping

import yattag
from docx.shared import Inches
from opencensus.trace import execution_context
from pydantic import BaseModel, Field

from clinical_mdr_api.services.utils.docx_builder import DocxBuilder


class Ref(BaseModel):
    type: str | None = Field(..., title="Referenced item type")
    uid: str | None = Field(..., title="Referenced item uid")

    def __init__(self, type_=None, uid=None, **kwargs):
        if type_ is not None:
            kwargs["type"] = type_
        if uid is not None:
            kwargs["uid"] = uid
        super().__init__(**kwargs)


class TableCell(BaseModel):
    text: str = Field("", title="Text contents of cell")
    span: int = Field(1, title="Horizontal spanning of cell, 1 by default")
    style: str | None = Field(None, title="Associated style to cell")
    ref: Ref | None = Field(None, title="Reference to item")
    footnotes: list[str] | None = Field(None, title="Referenced footnotes")
    vertical: bool | None = Field(None, title="Text text direction")

    def __init__(self, text=None, **kwargs):
        if text is not None:
            kwargs["text"] = text
        super().__init__(**kwargs)


class TableRow(BaseModel):
    cells: list[TableCell] = Field(default_factory=list, title="Table cells in the row")
    hide: bool = Field(False, title="Hide row from display")

    def __init__(self, cells=None, **kwargs):
        if cells is not None:
            kwargs["cells"] = cells
        super().__init__(**kwargs)


class SimpleFootnote(BaseModel):
    uid: str = Field(..., title="Unique id of footnote")  # TODO? Use Ref here?
    text_html: str = Field(..., title="HTML text of footnote")
    text_plain: str = Field(..., title="Plain text of footnote")


class TableWithFootnotes(BaseModel):
    rows: list[TableRow] = Field(default_factory=list, title="List of table rows")
    footnotes: dict[str, SimpleFootnote] = Field(
        default_factory=list, title="Mapping of symbols and table footnotes"
    )
    num_header_rows: int = Field(0, title="Number of header rows")
    num_header_cols: int = Field(0, title="Number of header columns")
    title: str | None = Field(None, title="Table title")


def table_to_docx(
    table: TableWithFootnotes, styles: Mapping[str, tuple[str, Any]] = None
) -> DocxBuilder:
    num_columns = sum((c.span for c in table.rows[0].cells))

    tracer = execution_context.get_opencensus_tracer()
    with tracer.span("table_to_docx"):
        docx = DocxBuilder(styles=styles, landscape=True, margins=[0.5, 0.5, 0.5, 0.5])

        # Table has to be created with number of columns set. Also creates first row.
        tablex = docx.create_table(
            num_rows=1,
            num_columns=num_columns,
        )

        # Set width of first column
        tablex.columns[0].width = Inches(4)

        # Update header rows
        for row_idx, row in enumerate((row for row in table.rows if not row.hide)):
            if row_idx:
                rowx = tablex.add_row()
            else:
                rowx = tablex.rows[row_idx]

            for cell_idx, cell in enumerate(row.cells):
                cellx = rowx.cells[cell_idx]
                para = cellx.paragraphs[0]

                if cell.span == 0:
                    continue

                if cell.span > 1:
                    # Merge cells
                    for i in range(1, min(len(rowx.cells), cell.span)):
                        cellx.merge(rowx.cells[cell_idx + i])

                if cell.text:
                    para.text = cell.text

                style_name = styles.get(cell.style, [None])[0] if styles else None
                if style_name:
                    para.style = style_name

                if cell.vertical:
                    docx.set_vertical_cell_direction(cellx, "btLr")

                for symbol in cell.footnotes or []:
                    run = para.add_run(f" {symbol}")
                    run.font.superscript = True

            # Set header row to repeat after page breaks
            if row_idx < table.num_header_rows:
                docx.repeat_table_header(rowx)

        # add footnotes
        style_name = styles.get("footnote", [None])[0] if styles else None
        for symbol, footnote in table.footnotes.items():
            para = docx.document.add_paragraph(style=style_name)
            run = para.add_run(f" {symbol}")
            run.font.superscript = True
            para.add_run(f": {footnote.text_plain}")

        return docx


def table_to_html(table: TableWithFootnotes) -> str:
    tracer = execution_context.get_opencensus_tracer()
    with tracer.span("table_to_html"):
        doc, tag, text, line = yattag.Doc().ttl()
        doc.asis("<!DOCTYPE html>")

        with tag("html", lang="en"):
            with tag("head"):
                if table.title:
                    line("title", table.title)

            with tag("body"):
                with tag("table"):
                    with tag("thead"):
                        for row in table.rows[: table.num_header_rows]:
                            if row.hide:
                                continue

                            with tag("tr"):
                                for cell in row.cells:
                                    if cell.span == 0:
                                        continue

                                    with tag("th", **_cell_to_attrs(cell)):
                                        text(cell.text)
                                        for symbol in cell.footnotes or []:
                                            doc.asis("&nbsp;")
                                            line("sup", symbol)

                    with tag("tbody"):
                        for row in table.rows[table.num_header_rows :]:
                            if row.hide:
                                continue

                            with tag("tr"):
                                for i, cell in enumerate(row.cells):
                                    if cell.span == 0:
                                        continue

                                    with tag(
                                        ("th" if i < table.num_header_cols else "td"),
                                        **_cell_to_attrs(cell),
                                    ):
                                        text(cell.text)
                                        for symbol in cell.footnotes or []:
                                            doc.asis("&nbsp;")
                                            line("sup", symbol)

                with tag("dl", klass="footnotes"):
                    for symbol, footnote in table.footnotes.items():
                        line("dt", symbol)
                        with tag("dd"):
                            doc.asis(footnote.text_plain)

        return yattag.indent(doc.getvalue())


def _cell_to_attrs(cell):
    attrs = {}

    if cell.style:
        attrs["klass"] = cell.style

    if cell.span > 1:
        attrs["colspan"] = cell.span

    return attrs
