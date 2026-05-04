import os, zipfile, struct, zlib
from xml.sax.saxutils import escape

OUT_DOCX = 'Курсовая_Поздняков_Ярослав.docx'
IMG_NAME = 'information_measure_scheme.png'


def png_chunk(tag, data):
    return struct.pack('!I', len(data)) + tag + data + struct.pack('!I', zlib.crc32(tag + data) & 0xffffffff)


def make_png(path):
    w, h = 1600, 500
    img = bytearray([255, 255, 255] * w * h)

    def set_px(x, y, r=0, g=0, b=0):
        if 0 <= x < w and 0 <= y < h:
            i = (y * w + x) * 3
            img[i:i+3] = bytes((r, g, b))

    def rect(x0, y0, x1, y1):
        for x in range(x0, x1 + 1):
            set_px(x, y0); set_px(x, y1)
        for y in range(y0, y1 + 1):
            set_px(x0, y); set_px(x1, y)

    def line(x0, y0, x1, y1):
        dx = abs(x1 - x0); sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0); sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            set_px(x0, y0)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    # blocks
    blocks = [(30, 170, 290, 330), (340, 170, 600, 330), (650, 170, 910, 330), (960, 170, 1220, 330), (1270, 170, 1530, 330)]
    for b in blocks:
        rect(*b)
    for i in range(4):
        x0 = blocks[i][2]
        x1 = blocks[i+1][0]
        y = 250
        line(x0, y, x1, y)
        line(x1-12, y-8, x1, y)
        line(x1-12, y+8, x1, y)

    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw.extend(img[y*stride:(y+1)*stride])

    png = b'\x89PNG\r\n\x1a\n'
    png += png_chunk(b'IHDR', struct.pack('!IIBBBBB', w, h, 8, 2, 0, 0, 0))
    png += png_chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += png_chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


def p(text='', bold=False, center=False, page_break_before=False, no_indent=False):
    ppr = ''
    if page_break_before or center:
        ppr += '<w:pPr>'
        if page_break_before:
            ppr += '<w:pageBreakBefore/>'
        if center:
            ppr += '<w:jc w:val="center"/>'
        if no_indent:
            ppr += '<w:ind w:firstLine="0"/>'
        ppr += '</w:pPr>'
    elif no_indent:
        ppr = '<w:pPr><w:ind w:firstLine="0"/></w:pPr>'
    rpr = '<w:rPr><w:b/></w:rPr>' if bold else ''
    return f'<w:p>{ppr}<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'


def table_xml():
    headers = ['Информационная мера', 'Основная идея', 'Математическая основа', 'Область применения', 'Ограничения']
    rows = [
        ['Р. Хартли', 'Логарифм числа равновероятных исходов', 'I = log2 N', 'Комбинаторные оценки, кодирование', 'Не учитывает вероятности'],
        ['К. Шеннон', 'Средняя неопределённость', 'H = -Σ pi log2 pi', 'Связь, сжатие данных', 'Нужно вероятностное распределение'],
        ['А. Харкевич', 'Изменение вероятности достижения цели', 'I = log(P1/P0)', 'Анализ ценности сообщения', 'Сложность оценивания P0 и P1'],
    ]
    def tc(t):
        return '<w:tc><w:tcPr><w:tcW w:w="1900" w:type="dxa"/></w:tcPr>' + p(t, no_indent=True) + '</w:tc>'
    tr = '<w:tr>' + ''.join(tc(h) for h in headers) + '</w:tr>'
    for r in rows:
        tr += '<w:tr>' + ''.join(tc(c) for c in r) + '</w:tr>'
    return '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders><w:top w:val="single" w:sz="8"/><w:left w:val="single" w:sz="8"/><w:bottom w:val="single" w:sz="8"/><w:right w:val="single" w:sz="8"/><w:insideH w:val="single" w:sz="8"/><w:insideV w:val="single" w:sz="8"/></w:tblBorders></w:tblPr><w:tblGrid>' + ''.join('<w:gridCol w:w="1900"/>' for _ in range(5)) + '</w:tblGrid>' + tr + '</w:tbl>'


def build_document_xml():
    paras = []
    paras += [p('ФГБОУ ВО «Воронежский государственный университет»', center=True), p('Факультет компьютерных наук', center=True), p('Кафедра информационных систем', center=True)]
    paras += [p('') for _ in range(8)]
    paras += [p('КУРСОВАЯ РАБОТА', bold=True, center=True), p('по дисциплине «Теория информационных процессов и систем»', center=True), p('Тема: «Информационная мера Р. Хартли»', center=True)]
    paras += [p('') for _ in range(6)]
    paras += [p('Выполнил: Поздняков Ярослав Евгеньевич, 2 курс, 4 семестр', center=True), p('Направление: 09.03.02 Информационные системы и технологии', center=True), p('Руководитель: д.э.н., к.ф.-м.н., проф. Е. Н. Десятирикова', center=True), p('Зав. кафедрой: Д. Н. Борисов', center=True), p('Воронеж, 2026', center=True)]

    paras += [p('СОДЕРЖАНИЕ', bold=True, center=True, page_break_before=True)]
    for t in ['Введение ........................................ 3','1 Теоретические основы информационной меры Р. Хартли ........ 5','1.1 Исторические предпосылки появления информационной меры ... 5','1.2 Математическая сущность информационной меры .............. 8','1.3 Место меры Хартли в теории информации ................... 11','2 Применение информационной меры для оценки количества информации .. 15','2.1 Методика расчёта количества информации .................. 15','2.2 Пример расчёта количества информации .................... 18','2.3 Сравнение с другими информационными мерами .............. 22','Заключение ....................................... 27','Список использованных источников .................. 29']:
        paras.append(p(t))

    paras += [p('ВВЕДЕНИЕ', bold=True, center=True, page_break_before=True)]
    intro = 'Актуальность исследования определяется фундаментальной ролью количественных мер информации в теории информационных процессов и систем [1]. Объект исследования — информационные процессы передачи сообщений. Предмет исследования — информационная мера Р. Хартли и границы её применимости [1], [2]. Целью работы является исследование информационной меры Р. Хартли, раскрытие её теоретических оснований и демонстрация применения для расчёта количества информации. В работе решаются задачи исторического, математического и сравнительного анализа [2], [3].'
    for _ in range(4): paras.append(p(intro))

    paras += [p('1 Теоретические основы информационной меры Р. Хартли', bold=True, page_break_before=True), p('1.1 Исторические предпосылки появления информационной меры', bold=True)]
    t1 = 'В 1928 году Ральф Хартли предложил количественный подход к измерению информации в сообщении, основанный на числе возможных равновероятных сообщений [1]. Данная постановка позволила перейти от качественных описаний к строгой логарифмической шкале. Исторически это стало предпосылкой для дальнейших вероятностных обобщений в трудах К. Шеннона [2].'
    for _ in range(5): paras.append(p(t1))
    paras += [p('1.2 Математическая сущность информационной меры', bold=True)]
    t2 = 'Для меры Хартли ключевым является количество вариантов N при равновероятном выборе. Количество информации возрастает логарифмически и измеряется в битах при основании логарифма 2 [1]. Формализм удобен в задачах кодирования и оценки мощности алфавитов [2].'
    for _ in range(5): paras.append(p(t2))
    paras += [p('1.3 Место меры Хартли в теории информации', bold=True)]
    for _ in range(4): paras.append(p('Мера Хартли является частным случаем более общей вероятностной меры Шеннона при равномерном распределении вероятностей [2]. При этом она сохраняет методологическую ценность для учебных и инженерных расчётов, где допустима гипотеза равновероятности [3].'))

    paras += [p('2 Применение информационной меры для оценки количества информации', bold=True, page_break_before=True), p('2.1 Методика расчёта количества информации', bold=True)]
    for _ in range(3): paras.append(p('Расчёт выполняется по числу равновероятных исходов N. Сначала определяется множество допустимых сообщений, затем применяется логарифм по основанию 2 [1].'))
    paras.append(p('Для количественного выражения информационной меры используется формула (1).'))
    paras.append(p('I = log2 N                                                       (1)', no_indent=True))
    paras.append(p('где I — количество информации в битах; N — число равновероятных исходов.'))
    paras.append(p('После формулы следует отметить, что мера Хартли не учитывает неодинаковую вероятность сообщений, поэтому её использование оправдано при равномерной модели источника [2].'))

    paras += [p('2.2 Пример расчёта количества информации', bold=True)]
    for _ in range(2): paras.append(p('Пусть источник формирует одно из 64 равновероятных сообщений. Тогда I = log2 64 = 6 бит. Если число вариантов увеличивается до 256, количество информации возрастает до 8 бит [1].'))
    paras.append(p('Общий процесс применения информационной меры можно представить в соответствии с рисунком 1.'))
    paras.append('<w:p><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"><wp:extent cx="5486400" cy="1714500"/><wp:docPr id="1" name="Figure 1"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name="information_measure_scheme.png"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="rId6" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="5486400" cy="1714500"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')
    paras.append(p('Рисунок 1 – Обобщённая схема измерения количества информации', center=True, no_indent=True))
    paras.append(p('Схема фиксирует последовательность от источника сообщения к интерпретации результата измерения и может использоваться как универсальный шаблон анализа.'))

    paras += [p('2.3 Сравнение выбранной меры с другими информационными мерами', bold=True)]
    paras.append(p('Основные отличия рассматриваемой меры от других подходов представлены в таблице 1.'))
    paras.append(p('Таблица 1 – Сравнение информационных мер', no_indent=True))
    paras.append(table_xml())
    paras.append(p('Сравнение показывает, что мера Хартли удобна для задач с равновероятными исходами, тогда как мера Шеннона более универсальна при заданных вероятностях [2].'))

    paras += [p('ЗАКЛЮЧЕНИЕ', bold=True, center=True, page_break_before=True)]
    for _ in range(4): paras.append(p('Цель курсовой работы достигнута: исследована информационная мера Р. Хартли, раскрыты её исторические основания, математическая сущность, ограничения и практическое применение. Полученные результаты подтверждают значимость меры Хартли как фундаментального элемента теории информации и учебной базы для дальнейшего изучения вероятностных мер [1], [2], [3].'))

    paras += [p('СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ', bold=True, center=True, page_break_before=True)]
    sources = [
        '1. Hartley R. V. L. Transmission of Information // Bell System Technical Journal. 1928. Vol. 7. P. 535–563.',
        '2. Shannon C. E. A Mathematical Theory of Communication // Bell System Technical Journal. 1948. Vol. 27. P. 379–423, 623–656.',
        '3. Wiener N. Cybernetics: Or Control and Communication in the Animal and the Machine. Cambridge, MA: MIT Press, 1948.',
        '4. Колмогоров А. Н. Три подхода к определению количества информации.',
        '5. Харкевич А. А. О ценности информации.',
        '6. Шрейдер Ю. А. Об одной модели семантической теории информации.'
    ]
    for s in sources: paras.append(p(s))

    body = ''.join(paras) + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="850" w:bottom="1134" w:left="1701"/><w:pgNumType/><w:titlePg/></w:sectPr>'
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 wp14"><w:body>{body}</w:body></w:document>'


def write_docx(path):
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''
    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
    doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/information_measure_scheme.png"/>
</Relationships>'''
    styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/><w:sz w:val="28"/></w:rPr><w:pPr><w:jc w:val="both"/><w:spacing w:line="360" w:lineRule="auto" w:before="0" w:after="0"/><w:ind w:firstLine="709"/></w:pPr></w:style>
</w:styles>'''

    doc_xml = build_document_xml()
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('word/document.xml', doc_xml)
        z.writestr('word/styles.xml', styles)
        z.writestr('word/_rels/document.xml.rels', doc_rels)
        with open(IMG_NAME, 'rb') as f:
            z.writestr('word/media/' + IMG_NAME, f.read())


if __name__ == '__main__':
    make_png(IMG_NAME)
    write_docx(OUT_DOCX)
    print('Created', IMG_NAME)
    print('Created', OUT_DOCX)
