
const quotes = [
    {
        text: "Великие дела начинаются с маленьких шагов.",
        author: "Авторская цитата"
    },
    {
        text: "Ошибки — это часть пути к новым знаниям.",
        author: "Авторская цитата"
    },
    {
        text: "Лучший момент начать — это момент, когда ты решил действовать.",
        author: "Авторская цитата"
    },
    {
        text: "Даже долгое путешествие начинается с первого шага.",
        author: "Пословица"
    }
];

const quoteText = document.getElementById("quote-text");
const quoteAuthor = document.getElementById("quote-author");
const message = document.getElementById("message");
let currentQuoteId = null;

const generateButton = document.getElementById("generate-btn");

generateButton.addEventListener("click", async () => {
    generateButton.disabled = true;
    message.textContent = "Загружаем случайную цитату из коллекции...";

    try {
        const response = await fetch("/api/quotes/random");
        const quote = await response.json();

        if (!response.ok) {
            throw new Error(quote.error || "Не удалось получить цитату.");
        }

        quoteText.textContent = quote.text;
        quoteAuthor.textContent = "— " + quote.author;

        // Запоминаем ID цитаты из базы данных.
        currentQuoteId = quote.id;

        message.textContent = "Цитата из вашей коллекции.";
    } catch (error) {
        message.textContent = error.message;
    } finally {
        generateButton.disabled = false;
    }
});


document.getElementById("copy-btn").addEventListener("click", async () => {
    const text = `${quoteText.textContent} ${quoteAuthor.textContent}`;

    try {
        await navigator.clipboard.writeText(text);
        message.textContent = "Цитата скопирована!";
    } catch {
        message.textContent = "Не удалось скопировать цитату.";
    }
});


const combineButton = document.getElementById("combine-btn");

combineButton.addEventListener("click", async () => {
    combineButton.disabled = true;
    message.textContent = "Создаём новую комбинацию...";

    try {
        const response = await fetch("/api/generate");

        if (!response.ok) {
            throw new Error("Ошибка генерации");
        }

        const quote = await response.json();

        quoteText.textContent = quote.text;
        quoteAuthor.textContent = "— " + quote.author;
        message.textContent = "Создана авторская комбинация!";
    } catch (error) {
        message.textContent = "Не удалось создать комбинацию.";
    } finally {
        combineButton.disabled = false;
    }
});



const externalButton = document.getElementById("external-btn");

externalButton.addEventListener("click", async () => {
    externalButton.disabled = true;
    message.textContent = "Получаем цитату из интернета...";

    try {
        const response = await fetch("/api/external-quote");
        const quote = await response.json();

        if (!response.ok) {
            throw new Error(quote.error || "Ошибка внешнего API");
        }

        quoteText.textContent = quote.text;
        quoteAuthor.textContent = "— " + quote.author;
        message.textContent = "Источник: ZenQuotes";
    } catch (error) {
        message.textContent =
            error.message || "Не удалось получить внешнюю цитату.";
    } finally {
        externalButton.disabled = false;
    }
});



const addQuoteForm = document.getElementById("add-quote-form");
const saveQuoteButton = document.getElementById("save-quote-btn");
const saveMessage = document.getElementById("save-message");

addQuoteForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const quoteData = {
        text: document.getElementById("new-quote-text").value.trim(),
        author: document.getElementById("new-quote-author").value.trim(),
        category: document.getElementById("new-quote-category").value
    };

    saveQuoteButton.disabled = true;
    saveMessage.textContent = "Сохраняем цитату...";

    try {
        const response = await fetch("/api/quotes", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(quoteData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Не удалось сохранить цитату");
        }

        saveMessage.textContent =
            `Цитата сохранена! Автор: ${result.author}.`;

        addQuoteForm.reset();
    } catch (error) {
        saveMessage.textContent = error.message;
    } finally {
        saveQuoteButton.disabled = false;
    }
});


const saveCurrentButton = document.getElementById("save-current-btn");
const refreshQuotesButton = document.getElementById("refresh-quotes-btn");
const savedQuotesList = document.getElementById("saved-quotes-list");
const collectionMessage = document.getElementById("collection-message");

// Сохраняем цитату, которая сейчас отображается на экране.
saveCurrentButton.addEventListener("click", async () => {
    const text = quoteText.textContent.trim();
    const author = quoteAuthor.textContent.replace(/^—\s*/, "").trim();

    if (!text || !author) {
        message.textContent = "Нет цитаты для сохранения.";
        return;
    }

    saveCurrentButton.disabled = true;
    message.textContent = "Сохраняем цитату...";

    try {
        const response = await fetch("/api/quotes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text,
                author,
                category: "другое"
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Не удалось сохранить цитату.");
        }

        message.textContent = "Цитата сохранена в базе данных!";
        await loadSavedQuotes();
    } catch (error) {
        message.textContent = error.message;
    } finally {
        saveCurrentButton.disabled = false;
    }
});

// Загружаем список цитат из базы данных.
async function loadSavedQuotes() {
    collectionMessage.textContent = "Загружаем коллекцию...";
    savedQuotesList.replaceChildren();

    try {
        const response = await fetch("/api/quotes");
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Не удалось загрузить цитаты.");
        }

        // Поддерживаем как массив, так и объект {quotes: [...]}.
        const quotesFromDb = Array.isArray(data) ? data : data.quotes;

        if (!Array.isArray(quotesFromDb)) {
            throw new Error("Неожиданный формат ответа /api/quotes.");
        }

        if (quotesFromDb.length === 0) {
            collectionMessage.textContent = "Коллекция пока пуста.";
            return;
        }

        collectionMessage.textContent = `Цитат в коллекции: ${quotesFromDb.length}`;

        for (const quote of quotesFromDb) {
            const card = document.createElement("article");
            card.className = "saved-quote";

            const text = document.createElement("p");
            text.textContent = quote.text;

            const author = document.createElement("p");
            author.className = "saved-author";
            author.textContent = `— ${
                typeof quote.author === "string"
                    ? quote.author
                    : quote.author?.name || "Неизвестный автор"
            }`;

            const category = document.createElement("p");
            category.className = "saved-author";
            category.textContent = `Категория: ${quote.category || "не указана"}`;

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.className = "delete-quote-btn";
            deleteButton.textContent = "Удалить из коллекции";

            deleteButton.addEventListener("click", async () => {
                if (!confirm("Удалить эту цитату из базы данных?")) {
                    return;
                }

                deleteButton.disabled = true;

                try {
                    const deleteResponse = await fetch(
                        `/api/quotes/${quote.id}`,
                        { method: "DELETE" }
                    );

                    const result = await deleteResponse.json();

                    if (!deleteResponse.ok) {
                        throw new Error(result.error || "Не удалось удалить цитату.");
                    }

                    await loadSavedQuotes();
                } catch (error) {
                    collectionMessage.textContent = error.message;
                    deleteButton.disabled = false;
                }
            });

            card.append(text, author, category, deleteButton);
            savedQuotesList.append(card);
        }
    } catch (error) {
        collectionMessage.textContent = error.message;
    }
}

refreshQuotesButton.addEventListener("click", loadSavedQuotes);
loadSavedQuotes();
