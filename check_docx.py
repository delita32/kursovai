import zipfile,re
fn='Курсовая_Поздняков_Ярослав.docx'
with zipfile.ZipFile(fn) as z:
    xml=z.read('word/document.xml').decode('utf-8','ignore')
checks={
 'title': 'КУРСОВАЯ РАБОТА' in xml,
 'content': 'СОДЕРЖАНИЕ' in xml,
 'intro': 'ВВЕДЕНИЕ' in xml,
 'chapter1': '1 Теоретические основы' in xml,
 'chapter2': '2 Применение' in xml,
 'conclusion': 'ЗАКЛЮЧЕНИЕ' in xml,
 'sources': 'СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ' in xml,
 'table': '<w:tbl>' in xml,
 'formula': 'I = log2 N' in xml,
 'figure_ref': 'рисунком 1' in xml.lower(),
}
for k,v in checks.items():
    print(k, 'OK' if v else 'FAIL')
print('Approx paragraphs:', xml.count('<w:p'))
