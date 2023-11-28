import yattag

from clinical_mdr_api.models.study_selections.table import Table
from clinical_mdr_api.services.utils.docx_builder import DocxBuilder


def table_to_html(
    table: Table, id_: str | None = None, title: str | None = None
) -> yattag.simpledoc.SimpleDoc:
    doc, tag, _, line = yattag.Doc().ttl()
    doc.asis("<!DOCTYPE html>")

    with tag("html", lang="en"):
        if title:
            with tag("head"):
                line("title", title)

        with tag("body"):
            attrs = [("id", id_)] if id_ else []

            with tag("table", *attrs):
                if table.num_header_rows:
                    with tag("thead"):
                        table_data_cell = "th"

                        for row in range(table.num_header_rows):
                            with tag("tr"):
                                for idx, txt in enumerate(table.data[row]):
                                    meta = table.meta[row][idx]
                                    _html_cell(doc, meta, table_data_cell, txt)

                with tag("tbody"):
                    for row in range(table.num_header_rows, table.data.size):
                        with tag("tr"):
                            for idx, txt in enumerate(table.data[row]):
                                table_data_cell = (
                                    "th" if idx < table.num_header_columns else "td"
                                )

                                meta = table.meta[row][idx]
                                _html_cell(doc, meta, table_data_cell, txt)

    return doc


def _html_cell(doc, meta, tag, txt):
    if not meta.get("merged"):
        attrs = _meta_to_html_attrs(meta)

        if "\n" in txt:
            with doc.tag(tag, *attrs):
                for i, line in enumerate(txt.split("\n")):
                    if i:
                        doc.stag("br")
                    doc.text(line)

        else:
            doc.line(tag, txt, *attrs)


def _meta_to_html_attrs(meta):
    return (
        (a, meta[a]) for a in ("class", "colspan", "rowspan") if meta.get(a) is not None
    )


def table_to_docx(table, styles):
    docx = DocxBuilder(styles=styles, landscape=True, margins=[0.5, 0.5, 0.5, 0.5])
    # Create table with actual number of columns and rows for all headers
    tablex = docx.create_table(
        num_rows=table.num_header_rows, num_columns=table.data[0].size
    )

    # Update header rows
    for header_row in range(table.num_header_rows):
        row = tablex.rows[header_row]

        prev_cell = None
        for idx, txt in enumerate(table.data[header_row].values()):
            cellx = row.cells[idx]
            meta = table.meta[header_row][idx]

            if meta.get("merged") and prev_cell:
                # Merge cell with previous cell, will preserve the paragraph (text) from the previous one
                cellx = prev_cell.merge(cellx)

            else:
                cellx.text = txt

            prev_cell = cellx

        # Apply paragraph styles on all cells, looking up style names
        docx.format_row(
            row,
            [
                docx.styles[table.meta[header_row][idx].get("class")][0]
                for idx in range(table.data[header_row].size)
            ],
        )

        # Set row to repeat after a page break
        docx.repeat_table_header(row)

    # Append data rows
    for header_row in range(table.num_header_rows, table.data.size):
        row = docx.add_row(tablex, table.data[header_row])

        # Apply paragraph styles on all cells, looking up style names
        # Discovering meta by getitem rather than iteration, because lazily populated
        docx.format_row(
            row,
            [
                docx.styles[table.meta[header_row][idx].get("class")][0]
                for idx in range(table.data[header_row].size)
            ],
        )

    return docx
