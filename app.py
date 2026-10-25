
from flask import Flask, jsonify, render_template, request
from sqlalchemy.orm import joinedload
import random
from external_api import get_external_quote

from database import (
    init_db,
    SessionLocal,
    Author,
    Quote,
    QuotePart,
)

app = Flask(__name__)

# Создаём таблицы, если их ещё нет
init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def status():
    return jsonify({
        "status": "ok",
        "project": "Генератор цитат",
    })


# Получение случайной цитаты
@app.route("/api/quotes/random")
def random_quote():
    category = request.args.get("category")

    with SessionLocal() as db:
        query = db.query(Quote).options(
            joinedload(Quote.author)
        )

        if category:
            query = query.filter(Quote.category == category)

        quotes = query.all()

        if not quotes:
            return jsonify({
                "error": "Цитаты не найдены"
            }), 404

        quote = random.choice(quotes)

        return jsonify({
            "id": quote.id,
            "text": quote.text,
            "author": quote.author.name,
            "category": quote.category,
        })



# Генерация новой фразы из двух случайных частей
@app.route("/api/generate")
def generate_quote():
    with SessionLocal() as db:
        starts = (
            db.query(QuotePart)
            .filter(QuotePart.part_type == "start")
            .all()
        )

        ends = (
            db.query(QuotePart)
            .filter(QuotePart.part_type == "end")
            .all()
        )

        if not starts or not ends:
            return jsonify({
                "error": "Недостаточно частей для генерации"
            }), 500

        start = random.choice(starts)
        end = random.choice(ends)

        text = f"{start.text} {end.text}"

        return jsonify({
            "text": text,
            "author": "Генератор цитат",
            "category": "авторская комбинация",
            "generated": True,
        })


# Получение всех цитат
@app.route("/api/quotes")
def all_quotes():
    with SessionLocal() as db:
        quotes = (
            db.query(Quote)
            .options(joinedload(Quote.author))
            .order_by(Quote.id)
            .all()
        )

        return jsonify([
            {
                "id": quote.id,
                "text": quote.text,
                "author": quote.author.name,
                "category": quote.category,
            }
            for quote in quotes
        ])


# Получение всех авторов
@app.route("/api/authors")
def all_authors():
    with SessionLocal() as db:
        authors = db.query(Author).order_by(Author.id).all()

        return jsonify([
            {
                "id": author.id,
                "name": author.name,
                "description": author.description,
            }
            for author in authors
        ])


@app.route("/api/external-quote")
def external_quote():
    quote = get_external_quote()

    if quote is None:
        return jsonify({
            "error": "Внешний сервис временно недоступен. Попробуйте позже."
        }), 502

    return jsonify(quote)


# Добавление новой цитаты в базу данных
@app.route("/api/quotes", methods=["POST"])
def add_quote():
    data = request.get_json(silent=True) or {}

    text = data.get("text", "").strip()
    author_name = data.get("author", "").strip()
    category = data.get("category", "").strip()

    if not text or not author_name or not category:
        return jsonify({
            "error": "Заполните все поля"
        }), 400

    if len(text) > 1000 or len(author_name) > 100 or len(category) > 50:
        return jsonify({
            "error": "Превышена допустимая длина одного из полей"
        }), 400

    with SessionLocal() as db:
        author = db.query(Author).filter_by(
            name=author_name
        ).first()

        if author is None:
            author = Author(
                name=author_name,
                description="Добавлен пользователем",
            )
            db.add(author)
            db.flush()

        quote = Quote(
            text=text,
            author_id=author.id,
            category=category,
        )

        db.add(quote)
        db.commit()
        db.refresh(quote)

        return jsonify({
            "message": "Цитата успешно сохранена",
            "id": quote.id,
            "text": quote.text,
            "author": author.name,
            "category": quote.category,
        }), 201


# Удаление цитаты из базы данных
@app.route("/api/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id):
    with SessionLocal() as db:
        quote = db.get(Quote, quote_id)

        if quote is None:
            return jsonify({
                "error": "Цитата не найдена"
            }), 404

        db.delete(quote)
        db.commit()

        return jsonify({
            "message": "Цитата успешно удалена",
            "id": quote_id
        }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
