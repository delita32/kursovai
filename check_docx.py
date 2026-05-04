import zipfile

fn = 'Курсовая_Поздняков_Ярослав.docx'
with zipfile.ZipFile(fn) as z:
    xml = z.read('word/document.xml').decode('utf-8', 'ignore')
    names = set(z.namelist())

checks = {
    'title': 'КУРСОВАЯ РАБОТА' in xml,
    'topic': 'Информационная мера Р. Хартли' in xml,
    'content': 'СОДЕРЖАНИЕ' in xml,
    'intro': 'ВВЕДЕНИЕ' in xml,
    'chapter1': '1 Теоретические основы информационной меры Р. Хартли' in xml,
    'chapter2': '2 Применение информационной меры для оценки количества информации' in xml,
    'conclusion': 'ЗАКЛЮЧЕНИЕ' in xml,
    'sources': 'СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ' in xml,
    'table': '<w:tbl>' in xml,
    'formula': 'I = log2 N' in xml,
    'figure_ref': 'рисунком 1' in xml.lower(),
    'figure_caption': 'Рисунок 1 –' in xml,
    'source_links': '[1]' in xml and '[2]' in xml and '[3]' in xml,
    'image_file': 'word/media/information_measure_scheme.png' in names,
}
for k, v in checks.items():
    print(f'{k}:', 'OK' if v else 'FAIL')
