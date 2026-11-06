import io, pathlib, re
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from i18n import translate

pdfmetrics.registerFont(
    TTFont(
        "Nanum", str(pathlib.Path(__file__).parent / "fonts/NanumGothic-Regular.ttf")
    )
)


def make_pdf(data, labs, f):
    lang = f.get("document_language", "ko")
    if lang not in ("ko", "en"):
        raise ValueError("문서 언어를 선택하세요.")

    def text(k, default="", limit=1200):
        value = f.get(k, default).strip()
        if len(value) > limit:
            raise ValueError("입력 길이를 확인하세요.")
        return value

    host = text("host", "", 120)
    if not re.fullmatch(r"[A-Za-z0-9.-]+", host):
        raise ValueError("서버 주소를 확인하세요.")
    tr = lambda s: translate(s, lang)
    body = ParagraphStyle(
        "body",
        fontName="Nanum",
        fontSize=9,
        leading=14,
        wordWrap="CJK",
        textColor=colors.HexColor("#233c48"),
    )
    head = ParagraphStyle("head", parent=body, fontSize=22, leading=30, spaceAfter=12)
    p = lambda s: Paragraph(escape(str(s)).replace("\n", "<br/>"), body)
    lab = labs[0]
    story = [
        Paragraph(tr("연구실 환경 안내서"), head),
        p(text("document_title", lab["title"], 100)),
        Spacer(1, 18),
    ]

    def table(rows, widths):
        t = Table(
            [[p(v) for v in row] for row in rows],
            colWidths=widths,
            repeatRows=1,
            hAlign="LEFT",
        )
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9f3f3")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#dce6e8")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.extend([t, Spacer(1, 15)])

    table([[tr("서버 주소"), host]], [120, 375])
    include = f.get("include_passwords") == "yes"
    rows = [
        [tr("계정 ID"), "SSH " + ("포트" if lang == "ko" else "port")]
        + ([tr("비밀번호")] if include else [])
    ]
    for u in lab["users"]:
        rows.append(
            [u["name"], u["port"]]
            + ([text("pw_" + u["name"], "", 128) or tr("별도 안내")] if include else [])
        )
    table(rows, [190, 85, 220] if include else [350, 145])
    gpu = next((g for g in data["gpus"] if g["index"] == lab["gpu"]), None)
    gpu_spec = (
        (
            gpu.get("name", "NVIDIA GPU")
            + " / "
            + str(round(gpu["total"] / 1024, 1))
            + " GiB"
        )
        if gpu
        else "NVIDIA GPU"
    )
    users = data.get("account_resources", [])
    cpu = " / ".join(
        u["name"] + ": " + (str(u["cpu"]) + " cores" if u["cpu"] else text("cpu", ""))
        for u in users
    )
    if users and all(u["cpu"] == users[0]["cpu"] for u in users):
        cpu = (
            str(users[0]["cpu"]) + " cores / account"
            if users[0]["cpu"]
            else text("cpu", "")
        )
    ram = " / ".join(
        u["name"]
        + ": "
        + (
            str(u["ram"]) + " GiB"
            if u["ram"]
            else str(data["memory_total_gib"]) + " GiB " + tr("공유")
        )
        for u in users
    )
    if users and all(u["ram"] == users[0]["ram"] for u in users):
        ram = (
            str(users[0]["ram"]) + " GiB / account"
            if users[0]["ram"]
            else str(data["memory_total_gib"]) + " GiB " + tr("공유")
        )
    table(
        [
            [tr("사용 가능한 자원"), tr("사양")],
            ["GPU", gpu_spec],
            ["CPU", cpu or text("cpu", "")],
            [tr("시스템 메모리"), ram or str(data["memory_total_gib"]) + " GiB"],
            [
                tr("저장공간"),
                str(lab["storage_gb"])
                + " GB · "
                + tr("연구실 계정 합계 (파일시스템 기준)"),
            ],
            [tr("기본 개발 환경"), text("environment")],
            [tr("권한 범위"), text("permissions")],
        ],
        [120, 375],
    )
    story.extend(
        [
            p(tr("시스템 메모리는 모든 서버 이용자가 공유합니다.")),
            Spacer(1, 12),
            p(tr("접속 명령")),
        ]
    )
    for u in lab["users"]:
        story.append(p("ssh -p " + str(u["port"]) + " " + u["name"] + "@" + host))
    if text("note", "", 600):
        story.extend([Spacer(1, 12), p(text("note", "", 600))])
    stream = io.BytesIO()
    doc = SimpleDocTemplate(
        stream,
        pagesize=A4,
        leftMargin=50,
        rightMargin=50,
        topMargin=44,
        bottomMargin=42,
        title=tr("연구실 환경 안내서"),
        author="LabHarbor",
    )

    def footer(c, d):
        c.setFont("Nanum", 8)
        c.setFillColor(colors.HexColor("#728a95"))
        c.drawString(50, 23, "LabHarbor")
        c.drawRightString(A4[0] - 50, 23, str(d.page))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    stream.seek(0)
    return stream
