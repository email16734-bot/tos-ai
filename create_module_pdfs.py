from pathlib import Path
from shutil import copyfile
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "pdfs"
OUTPUT.mkdir(parents=True, exist_ok=True)

FONT_REGULAR = Path("C:/Windows/Fonts/arial.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/arialbd.ttf")
pdfmetrics.registerFont(TTFont("ModuleSans", str(FONT_REGULAR)))
pdfmetrics.registerFont(TTFont("ModuleSansBold", str(FONT_BOLD)))

PAGE_W, PAGE_H = A4
INK = HexColor("#141815")
MUTED = HexColor("#657069")
LIME = HexColor("#9FC23B")
PALE = HexColor("#EEF2E6")
PAPER = HexColor("#F7F8F4")
LINE = HexColor("#D9DED7")
GRAPHITE = HexColor("#171B19")

MODULES = [
    {
        "id": "tr-01",
        "code": "ТР-01",
        "name": "Тактическая радиостанция ТР-01",
        "category": "Переносная связь",
        "summary": "Учебное руководство по устройству, подготовке и базовому осмотру переносной радиостанции.",
        "parts": ["Антенна", "Дисплей", "Органы управления", "Аккумулятор", "Корпус и разъемы"],
    },
    {
        "id": "rp-4",
        "code": "РП-4",
        "name": "Полевой ретранслятор РП-4",
        "category": "Ретрансляция",
        "summary": "Учебное руководство по составу ретрансляционного комплекта и последовательности его развертывания.",
        "parts": ["Панель разъемов", "Блок охлаждения", "Узел питания", "Защитный корпус", "Световая индикация"],
    },
    {
        "id": "st-5",
        "code": "СТ-5",
        "name": "Спутниковый терминал СТ-5",
        "category": "Спутниковая связь",
        "summary": "Учебное руководство по устройству переносного терминала, сборке и контролю его основных узлов.",
        "parts": ["Антенный рефлектор", "Облучатель", "Опорно-поворотный узел", "Транспортный кейс", "Соединительные линии"],
    },
    {
        "id": "as-12",
        "code": "АС-12",
        "name": "Аппаратная связи АС-12",
        "category": "Пункт управления",
        "summary": "Учебное руководство по организации рабочего места и контролю элементов аппаратной связи.",
        "parts": ["Панель отображения", "Панель управления", "Интерфейсный блок", "Рабочая поверхность", "Защитный корпус"],
    },
]


def wrap_text(text, font_name, font_size, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(pdf, text, x, y, max_width, font="ModuleSans", size=11, leading=16, color=INK):
    pdf.setFillColor(color)
    pdf.setFont(font, size)
    for line in wrap_text(text, font, size, max_width):
        pdf.drawString(x, y, line)
        y -= leading
    return y


def page_frame(pdf, module, page_number, section):
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    pdf.setStrokeColor(LINE)
    pdf.line(48, PAGE_H - 54, PAGE_W - 48, PAGE_H - 54)
    pdf.setFont("ModuleSansBold", 8)
    pdf.setFillColor(LIME)
    pdf.drawString(48, PAGE_H - 40, module["code"])
    pdf.setFillColor(MUTED)
    pdf.drawRightString(PAGE_W - 48, PAGE_H - 40, section.upper())
    pdf.line(48, 46, PAGE_W - 48, 46)
    pdf.setFont("ModuleSans", 8)
    pdf.drawString(48, 30, "Демонстрационный учебный материал")
    pdf.drawRightString(PAGE_W - 48, 30, f"{page_number:02d}")


def section_title(pdf, index, title, subtitle=None):
    pdf.setFillColor(LIME)
    pdf.setFont("ModuleSansBold", 9)
    pdf.drawString(48, PAGE_H - 92, index)
    pdf.setFillColor(INK)
    pdf.setFont("ModuleSansBold", 25)
    pdf.drawString(48, PAGE_H - 126, title)
    if subtitle:
        draw_wrapped(pdf, subtitle, 48, PAGE_H - 151, PAGE_W - 96, size=10, leading=14, color=MUTED)


def make_pdf(module, path):
    pdf = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
    pdf.setTitle(f"{module['name']} - учебное руководство")
    pdf.setAuthor("Обучающий модуль связи")

    pdf.setFillColor(GRAPHITE)
    pdf.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    pdf.setFillColor(LIME)
    pdf.rect(48, PAGE_H - 80, 64, 4, fill=1, stroke=0)
    pdf.setFont("ModuleSansBold", 10)
    pdf.drawString(48, PAGE_H - 112, module["category"].upper())
    pdf.setFillColor(HexColor("#F5F7F1"))
    pdf.setFont("ModuleSansBold", 32)
    title_y = PAGE_H - 205
    for line in wrap_text(module["name"], "ModuleSansBold", 32, PAGE_W - 96):
        pdf.drawString(48, title_y, line)
        title_y -= 39
    pdf.setFillColor(HexColor("#AEB6AF"))
    pdf.setFont("ModuleSans", 13)
    for line in wrap_text(module["summary"], "ModuleSans", 13, PAGE_W - 130):
        pdf.drawString(48, title_y - 18, line)
        title_y -= 19
    pdf.setStrokeColor(Color(1, 1, 1, alpha=0.12))
    for offset in range(0, 420, 42):
        pdf.line(PAGE_W - 230 + offset, 0, PAGE_W - 30 + offset, PAGE_H)
    pdf.setFillColor(LIME)
    pdf.circle(PAGE_W - 100, 145, 54, fill=0, stroke=1)
    pdf.circle(PAGE_W - 100, 145, 38, fill=0, stroke=1)
    pdf.setFont("ModuleSansBold", 9)
    pdf.drawString(48, 58, "УЧЕБНОЕ РУКОВОДСТВО")
    pdf.showPage()

    page_frame(pdf, module, 2, "Назначение")
    section_title(pdf, "01", "Назначение и задачи", module["summary"])
    y = PAGE_H - 210
    blocks = [
        ("Цель изучения", "Понять назначение основных узлов, научиться находить их на модели и соблюдать последовательность подготовки."),
        ("Результат", "После изучения обучаемый уверенно называет элементы, объясняет их роль и проходит контрольные вопросы."),
        ("Форматы", "Используйте 3D-модель, видеоматериалы и это руководство как единый учебный маршрут."),
    ]
    for title, text in blocks:
        pdf.setFillColor(PALE)
        pdf.roundRect(48, y - 88, PAGE_W - 96, 78, 10, fill=1, stroke=0)
        pdf.setFillColor(INK)
        pdf.setFont("ModuleSansBold", 12)
        pdf.drawString(64, y - 32, title)
        draw_wrapped(pdf, text, 64, y - 52, PAGE_W - 128, size=10, leading=14, color=MUTED)
        y -= 100
    pdf.showPage()

    page_frame(pdf, module, 3, "Состав")
    section_title(pdf, "02", "Основные элементы", "Узлы, отмеченные точками интереса на 3D-модели.")
    y = PAGE_H - 210
    for index, part in enumerate(module["parts"], start=1):
        pdf.setStrokeColor(LINE)
        pdf.line(48, y - 26, PAGE_W - 48, y - 26)
        pdf.setFillColor(LIME)
        pdf.setFont("ModuleSansBold", 9)
        pdf.drawString(48, y, f"{index:02d}")
        pdf.setFillColor(INK)
        pdf.setFont("ModuleSansBold", 12)
        pdf.drawString(88, y, part)
        pdf.setFillColor(MUTED)
        pdf.setFont("ModuleSans", 9)
        pdf.drawRightString(PAGE_W - 48, y, "Изучить на 3D-модели")
        y -= 58
    pdf.showPage()

    page_frame(pdf, module, 4, "Подготовка")
    section_title(pdf, "03", "Порядок подготовки", "Базовый учебный алгоритм перед началом занятия.")
    steps = [
        "Проверить комплектность модуля и состояние корпуса.",
        "Найти на 3D-модели все отмеченные точки интереса.",
        "Сопоставить органы управления с описанием в руководстве.",
        "Открыть видеоматериал по подготовке к работе.",
        "Ответить на контрольные вопросы в конце руководства.",
    ]
    y = PAGE_H - 210
    for index, step in enumerate(steps, start=1):
        pdf.setFillColor(LIME)
        pdf.circle(66, y + 3, 15, fill=1, stroke=0)
        pdf.setFillColor(GRAPHITE)
        pdf.setFont("ModuleSansBold", 9)
        pdf.drawCentredString(66, y, str(index))
        draw_wrapped(pdf, step, 96, y + 5, PAGE_W - 150, size=11, leading=15)
        y -= 70
    pdf.showPage()

    page_frame(pdf, module, 5, "Безопасность")
    section_title(pdf, "04", "Безопасность и контроль", "Учебный модуль не заменяет действующие регламенты эксплуатации.")
    pdf.setFillColor(HexColor("#FFF1D9"))
    pdf.roundRect(48, PAGE_H - 300, PAGE_W - 96, 122, 12, fill=1, stroke=0)
    pdf.setFillColor(HexColor("#9B651A"))
    pdf.setFont("ModuleSansBold", 10)
    pdf.drawString(66, PAGE_H - 208, "ВАЖНО")
    draw_wrapped(pdf, "Перед практической работой используйте утвержденную инструкцию конкретного образца техники и указания преподавателя.", 66, PAGE_H - 236, PAGE_W - 132, size=11, leading=17, color=INK)
    y = PAGE_H - 350
    for text in ["Не подключать неизвестные источники питания.", "Не применять усилие к разъемам и подвижным узлам.", "О повреждениях сообщать руководителю занятия."]:
        pdf.setFillColor(LIME)
        pdf.circle(57, y + 4, 3, fill=1, stroke=0)
        draw_wrapped(pdf, text, 72, y + 8, PAGE_W - 126, size=11, leading=16)
        y -= 48
    pdf.showPage()

    page_frame(pdf, module, 6, "Самопроверка")
    section_title(pdf, "05", "Контрольные вопросы", "Проверьте понимание материала перед завершением модуля.")
    questions = [
        "Каково назначение изучаемого средства связи?",
        "Какие основные узлы необходимо проверить перед работой?",
        "Какие элементы отмечены точками интереса на модели?",
        "Какова рекомендуемая последовательность изучения материалов?",
        "Какие меры безопасности нужно соблюдать?",
    ]
    y = PAGE_H - 205
    for index, question in enumerate(questions, start=1):
        pdf.setFont("ModuleSansBold", 10)
        pdf.setFillColor(LIME)
        pdf.drawString(48, y, f"{index:02d}")
        draw_wrapped(pdf, question, 84, y + 1, PAGE_W - 132, size=11, leading=15)
        pdf.setStrokeColor(LINE)
        pdf.line(84, y - 24, PAGE_W - 48, y - 24)
        pdf.line(84, y - 43, PAGE_W - 48, y - 43)
        y -= 91
    pdf.save()


for item in MODULES:
    output_path = OUTPUT / f"{item['id']}-guide.pdf"
    make_pdf(item, output_path)
    target = ROOT / "public" / "modules" / item["id"] / "texts" / "guide.pdf"
    copyfile(output_path, target)
