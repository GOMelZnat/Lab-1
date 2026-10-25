
from database import init_db, SessionLocal, Author, Quote, QuotePart

init_db()

with SessionLocal() as db:
    # Добавляем авторов, если их ещё нет
    authors_data = [
        ("Неизвестный автор", "Авторские и анонимные цитаты"),
        ("Генератор цитат", "Фразы, созданные комбинацией частей"),
        ("Народная мудрость", "Пословицы и обобщённые мысли"),
    ]

    for name, description in authors_data:
        author = db.query(Author).filter_by(name=name).first()

        if author is None:
            db.add(Author(name=name, description=description))

    db.commit()

    anonymous = db.query(Author).filter_by(
        name="Неизвестный автор"
    ).first()

    folk = db.query(Author).filter_by(
        name="Народная мудрость"
    ).first()

    quotes_data = [
        (
            "Великие дела начинаются с маленьких шагов.",
            "мотивация",
            anonymous.id,
        ),
        (
            "Ошибки — это часть пути к новым знаниям.",
            "учёба",
            anonymous.id,
        ),
        (
            "Даже долгое путешествие начинается с первого шага.",
            "мудрость",
            folk.id,
        ),
        (
            "Терпение помогает увидеть то, что скрыто от спешки.",
            "философия",
            anonymous.id,
        ),
        (
            "Хороший вопрос иногда важнее быстрого ответа.",
            "учёба",
            anonymous.id,
        ),
    ]

    for text, category, author_id in quotes_data:
        exists = db.query(Quote).filter_by(text=text).first()

        if exists is None:
            db.add(
                Quote(
                    text=text,
                    category=category,
                    author_id=author_id,
                )
            )

    # Части для генерации новых комбинаций
    parts_data = [
        ("Большие цели", "start"),
        ("Новые знания", "start"),
        ("Неожиданные открытия", "start"),
        ("начинаются с маленьких шагов.", "end"),
        ("требуют любопытства.", "end"),
        ("рождаются из смелых вопросов.", "end"),
    ]

    for text, part_type in parts_data:
        exists = db.query(QuotePart).filter_by(
            text=text,
            part_type=part_type,
        ).first()

        if exists is None:
            db.add(QuotePart(text=text, part_type=part_type))

    db.commit()

print("Начальные данные добавлены!")
