"""Generacion de exportaciones Excel para solicitudes de vacaciones.

No dependemos de librerias externas como `openpyxl` para mantener ligera la
instalacion. Generamos un `.xlsx` minimo con la estructura XML necesaria para
que Excel pueda abrirlo sin problemas.
"""

from datetime import datetime
from decimal import Decimal
from io import BytesIO
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from django.utils import timezone


def build_rrhh_vacation_requests_excel(vacation_requests):
    """Devuelve el nombre de archivo y el contenido `.xlsx` en bytes.

    El Excel replica el listado que RRHH ya ve en pantalla: apellidos, nombre,
    fechas, dias y estado. Asi evitamos inconsistencias entre la tabla filtrada
    y el archivo descargado.
    """

    # Usamos una fecha legible en el nombre para que RRHH pueda identificar
    # rapidamente cuando se genero el archivo desde el propio explorador.
    export_date = timezone.localdate().strftime("%d-%m-%Y")
    file_name = f"vacation_{export_date}.xlsx"

    rows = [
        [
            "Apellidos",
            "Nombre",
            "Fecha inicio",
            "Fecha final",
            "Dias seleccionados",
            "Estado",
        ]
    ]

    for vacation_request in vacation_requests:
        rows.append(
            [
                vacation_request.employee.last_name,
                vacation_request.employee.first_name,
                vacation_request.start_date.strftime("%d-%m-%Y"),
                vacation_request.end_date.strftime("%d-%m-%Y"),
                str(vacation_request.requested_days),
                vacation_request.status.name,
            ]
        )

    return file_name, _build_minimal_xlsx(sheet_name="Solicitudes", rows=rows)


def _build_minimal_xlsx(*, sheet_name, rows):
    """Construye un `.xlsx` minimo usando solo librerias de la stdlib.

    El formato XLSX es un zip con varios archivos XML internos. Para esta fase
    necesitamos una sola hoja simple, sin estilos complejos ni formulas.
    """

    workbook_buffer = BytesIO()

    with ZipFile(workbook_buffer, "w", ZIP_DEFLATED) as workbook_zip:
        workbook_zip.writestr("[Content_Types].xml", _build_content_types_xml())
        workbook_zip.writestr("_rels/.rels", _build_root_relationships_xml())
        workbook_zip.writestr("docProps/app.xml", _build_app_xml())
        workbook_zip.writestr("docProps/core.xml", _build_core_xml())
        workbook_zip.writestr("xl/workbook.xml", _build_workbook_xml(sheet_name))
        workbook_zip.writestr(
            "xl/_rels/workbook.xml.rels",
            _build_workbook_relationships_xml(),
        )
        workbook_zip.writestr("xl/styles.xml", _build_styles_xml())
        workbook_zip.writestr("xl/worksheets/sheet1.xml", _build_sheet_xml(rows))

    return workbook_buffer.getvalue()


def _build_content_types_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""


def _build_root_relationships_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def _build_app_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>LR App</Application>
</Properties>"""


def _build_core_xml():
    created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:creator>LR App</dc:creator>
  <cp:lastModifiedBy>LR App</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{created_at}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{created_at}</dcterms:modified>
</cp:coreProperties>"""


def _build_workbook_xml(sheet_name):
    escaped_sheet_name = escape(sheet_name)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="{escaped_sheet_name}" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>"""


def _build_workbook_relationships_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""


def _build_styles_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1">
    <font>
      <sz val="11"/>
      <name val="Calibri"/>
    </font>
  </fonts>
  <fills count="1">
    <fill>
      <patternFill patternType="none"/>
    </fill>
  </fills>
  <borders count="1">
    <border/>
  </borders>
  <cellStyleXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
  </cellStyleXfs>
  <cellXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
  </cellXfs>
  <cellStyles count="1">
    <cellStyle name="Normal" xfId="0" builtinId="0"/>
  </cellStyles>
</styleSheet>"""


def _build_sheet_xml(rows):
    xml_rows = []

    for row_index, row in enumerate(rows, start=1):
        xml_cells = []

        for column_index, value in enumerate(row, start=1):
            cell_reference = f"{_get_excel_column_letter(column_index)}{row_index}"
            xml_cells.append(_build_cell_xml(cell_reference, value))

        xml_rows.append(f'<row r="{row_index}">{"".join(xml_cells)}</row>')

    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>{rows}</sheetData>
</worksheet>""".format(rows="".join(xml_rows))


def _build_cell_xml(cell_reference, value):
    if isinstance(value, (int, float, Decimal)):
        return f'<c r="{cell_reference}"><v>{value}</v></c>'

    text = escape("" if value is None else str(value))
    return (
        f'<c r="{cell_reference}" t="inlineStr">'
        f"<is><t>{text}</t></is>"
        "</c>"
    )


def _get_excel_column_letter(column_index):
    letters = []

    while column_index > 0:
        column_index, remainder = divmod(column_index - 1, 26)
        letters.append(chr(65 + remainder))

    return "".join(reversed(letters))
