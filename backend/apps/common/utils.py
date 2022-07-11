from django.utils.datastructures import MultiValueDict
from pathlib import Path
import uuid
import tempfile
import base64


def docx_replace(doc, data):
    paragraphs = list(doc.paragraphs)
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraphs.append(paragraph)
    for p in paragraphs:
        for key_name, val in data.items():
            if key_name in p.text:
                inline = p.runs
                # Replace strings and retain the same style.
                # The text to be replaced can be split over several runs so
                # search through, identify which runs need to have text replaced
                # then replace the text in those identified
                started = False
                key_index = 0
                # found_runs is a list of (inline index, index of match, length of match)
                found_runs = list()
                found_all = False
                replace_done = False
                for i in range(len(inline)):

                    # case 1: found in single run so short circuit the replace
                    if key_name in inline[i].text and not started:
                        found_runs.append((i, inline[i].text.find(key_name), len(key_name)))
                        text = inline[i].text.replace(key_name, str(val))
                        inline[i].text = text
                        replace_done = True
                        found_all = True
                        break

                    if key_name[key_index] not in inline[i].text and not started:
                        # keep looking ...
                        continue

                    # case 2: search for partial text, find first run
                    if key_name[key_index] in inline[i].text and inline[i].text[-1] in key_name and not started:
                        # check sequence
                        start_index = inline[i].text.find(key_name[key_index])
                        check_length = len(inline[i].text)
                        for text_index in range(start_index, check_length):
                            if inline[i].text[text_index] != key_name[key_index]:
                                # no match so must be false positive
                                break
                        if key_index == 0:
                            started = True
                        chars_found = check_length - start_index
                        key_index += chars_found
                        found_runs.append((i, start_index, chars_found))
                        if key_index != len(key_name):
                            continue
                        else:
                            # found all chars in key_name
                            found_all = True
                            break

                    # case 2: search for partial text, find subsequent run
                    if key_name[key_index] in inline[i].text and started and not found_all:
                        # check sequence
                        chars_found = 0
                        check_length = len(inline[i].text)
                        for text_index in range(0, check_length):
                            if inline[i].text[text_index] == key_name[key_index]:
                                key_index += 1
                                chars_found += 1
                            else:
                                break
                        # no match so must be end
                        found_runs.append((i, 0, chars_found))
                        if key_index == len(key_name):
                            found_all = True
                            break

                if found_all and not replace_done:
                    for i, item in enumerate(found_runs):
                        index, start, length = [t for t in item]
                        if i == 0:
                            text = inline[index].text.replace(inline[index].text[start:start + length], str(val))
                            inline[index].text = text
                        else:
                            text = inline[index].text.replace(inline[index].text[start:start + length], '')
                            inline[index].text = text
                # print(p.text)


def qdict_to_dict(qdict):
    """Convert a Django QueryDict to a Python dict.

    Single-value fields are put in directly, and for multi-value fields, a list
    of all values is stored at the field's key.

    """
    return {k: v[0] if len(v) == 1 else v for k, v in qdict.lists()}


def files_to_base64(request_files: MultiValueDict) -> dict:
    """Конвертирует request.FILES в строки base64"""
    res = {}
    for key in request_files:
        res[key] = []
        files = request_files.getlist(key)
        for file in files:
            f = file.file
            file_bytes = f.read()
            file_bytes_base64 = base64.b64encode(file_bytes)
            file_bytes_base64_str = file_bytes_base64.decode('utf-8')  # this is a str
            res[key].append({'name': file.name, 'content': file_bytes_base64_str})
    return res


def base64_to_temp_file(base64_str: str) -> Path:
    """Сохраняет файл (строка base64) во временный каталог."""
    file_bytes_base64 = base64_str.encode('utf-8')
    file_bytes = base64.b64decode(file_bytes_base64)

    tmp_dir = tempfile.gettempdir()
    tmp_file_name = str(uuid.uuid4())
    tmp_file_path = Path(tmp_dir) / tmp_file_name
    with open(tmp_file_path, 'wb') as f:
        f.write(file_bytes)
    return tmp_file_path


def base64_to_file(base64_str: str, path: Path) -> None:
    """Сохраняет файл (строка base64) во временный каталог."""
    file_bytes_base64 = base64_str.encode('utf-8')
    file_bytes = base64.b64decode(file_bytes_base64)

    with open(path, 'wb') as f:
        f.write(file_bytes)
