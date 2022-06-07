from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from pathlib import Path
from datetime import date


def document_get_folder_path(instance) -> Path:
    """Возвращает путь к каталогу с файлами документа."""
    d = date.today()
    return Path('documents') / str(d.year) / str(d.month) / str(d.day) / str(instance.pk)


def document_get_original_file_path(instance, file_name: str) -> Path:
    """Возвращает путь к файлу документа."""
    return document_get_folder_path(instance) / file_name


def sign_get_file_path(instance, file_name: str) -> Path:
    """Возвращает путь к файлу цифровой печати."""
    p = Path(instance.document.file)
    return p.parent / file_name


def set_cell_border(cell, **kwargs):
    """
    Set cell`s border
    Usage:

    set_cell_border(
        cell,
        top={"sz": 12, "val": "single", "color": "#FF0000", "space": "0"},
        bottom={"sz": 12, "color": "#00FF00", "val": "single"},
        start={"sz": 24, "val": "dashed", "shadow": "true"},
        end={"sz": 12, "val": "dashed"},
    )
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    # check for tag existnace, if none found, then create one
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)

    # list over all available tags
    for edge in ('start', 'top', 'end', 'bottom', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)

            # check for tag existnace, if none found, then create one
            element = tcBorders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                tcBorders.append(element)

            # looks like order of attributes is important
            for key in ["sz", "val", "color", "space", "shadow"]:
                if key in edge_data:
                    element.set(qn('w:{}'.format(key)), str(edge_data[key]))
