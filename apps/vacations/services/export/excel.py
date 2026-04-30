"""Generacion de exportaciones Excel para solicitudes de vacaciones.

No dependemos de librerias externas como `openpyxl` para mantener ligera la
instalacion. Generamos un `.xlsx` minimo con la estructura XML necesaria para
que Excel pueda abrirlo sin problemas.
"""

from datetime import datetime
from decimal import Decimal
from io import BytesIO
from secrets import token_hex
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from django.utils import timezone
from django.utils.translation import gettext_lazy as _


RRHH_EXCEL_COLUMN_WIDTHS = (18, 30, 22, 16, 16, 18, 18)
RRHH_EXPORT_COLUMNS_VERSION = "rrhh_vacation_requests_v1"
RRHH_EXPORT_COLUMNS = (
    ("employee_number", _("Numero empleado")),
    ("last_name", _("Apellidos")),
    ("first_name", _("Nombre")),
    ("start_date", _("Fecha inicio")),
    ("end_date", _("Fecha final")),
    ("phone", _("Telefono")),
    ("requested_days", _("Dias solicitados")),
)


def build_rrhh_vacation_requests_excel(vacation_requests):
    """Devuelve nombre, contenido `.xlsx` y snapshot JSON-safe.

    El Excel replica el listado filtrado con las columnas operativas que RRHH
    necesita para procesar las solicitudes fuera de la aplicacion.
    """

    snapshot_rows = build_rrhh_vacation_requests_snapshot(vacation_requests)
    file_name = build_rrhh_vacation_requests_file_name()
    file_bytes = build_rrhh_vacation_requests_excel_from_snapshot(snapshot_rows)
    return file_name, file_bytes, snapshot_rows


def build_rrhh_vacation_requests_file_name():
    """Construye un nombre unico y legible para la descarga."""

    export_date = timezone.localdate().isoformat()
    return f"vacation_{export_date}_{token_hex(3)}.xlsx"


def build_rrhh_vacation_requests_snapshot(vacation_requests):
    """Serializa las solicitudes exportadas para guardarlas en historial."""

    snapshot_rows = []
    for vacation_request in vacation_requests:
        snapshot_rows.append(
            {
                "employee_number": vacation_request.employee.user.dni,
                "last_name": vacation_request.employee.last_name,
                "first_name": vacation_request.employee.first_name,
                "start_date": vacation_request.start_date.strftime("%d-%m-%Y"),
                "end_date": vacation_request.end_date.strftime("%d-%m-%Y"),
                "phone": vacation_request.employee.phone or "",
                "requested_days": int(vacation_request.requested_days),
            }
        )

    return snapshot_rows


def build_rrhh_vacation_requests_excel_from_snapshot(snapshot_rows):
    """Genera el `.xlsx` a partir del snapshot guardado en historial."""

    rows = [[label for _key, label in RRHH_EXPORT_COLUMNS]]
    for snapshot_row in snapshot_rows or []:
        rows.append([snapshot_row.get(key, "") for key, _label in RRHH_EXPORT_COLUMNS])

    return _build_minimal_xlsx(
        sheet_name=_("Solicitudes"),
        rows=rows,
        column_widths=RRHH_EXCEL_COLUMN_WIDTHS,
    )


def _build_minimal_xlsx(*, sheet_name, rows, column_widths=None):
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
        workbook_zip.writestr(
            "xl/worksheets/sheet1.xml",
            _build_sheet_xml(rows, column_widths=column_widths),
        )

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
    escaped_sheet_name = escape(str(sheet_name))
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
  <fonts count="2">
    <font>
      <sz val="11"/>
      <name val="Calibri"/>
    </font>
    <font>
      <b/>
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
  <cellXfs count="2">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>
  </cellXfs>
  <cellStyles count="1">
    <cellStyle name="Normal" xfId="0" builtinId="0"/>
  </cellStyles>
</styleSheet>"""


def _build_sheet_xml(rows, *, column_widths=None):
    xml_rows = []

    for row_index, row in enumerate(rows, start=1):
        xml_cells = []

        for column_index, value in enumerate(row, start=1):
            cell_reference = f"{_get_excel_column_letter(column_index)}{row_index}"
            style_index = 1 if row_index == 1 else None
            xml_cells.append(_build_cell_xml(cell_reference, value, style_index))

        xml_rows.append(f'<row r="{row_index}">{"".join(xml_cells)}</row>')

    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  {columns}
  <sheetData>{rows}</sheetData>
</worksheet>""".format(
        columns=_build_columns_xml(column_widths or ()),
        rows="".join(xml_rows),
    )


def _build_columns_xml(column_widths):
    if not column_widths:
        return ""

    columns = []
    for column_index, width in enumerate(column_widths, start=1):
        columns.append(
            f'<col min="{column_index}" max="{column_index}" '
            f'width="{width}" customWidth="1"/>'
        )

    return f"<cols>{''.join(columns)}</cols>"


def _build_cell_xml(cell_reference, value, style_index=None):
    style_attribute = f' s="{style_index}"' if style_index is not None else ""

    if isinstance(value, (int, float, Decimal)):
        return f'<c r="{cell_reference}"{style_attribute}><v>{value}</v></c>'

    text = escape("" if value is None else str(value))
    return (
        f'<c r="{cell_reference}"{style_attribute} t="inlineStr">'
        f"<is><t>{text}</t></is>"
        "</c>"
    )


def _get_excel_column_letter(column_index):
    letters = []

    while column_index > 0:
        column_index, remainder = divmod(column_index - 1, 26)
        letters.append(chr(65 + remainder))

    return "".join(reversed(letters))
