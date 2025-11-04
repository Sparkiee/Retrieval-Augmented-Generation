# Retrieval-Augmented-Generation

## What is this?
This project implements a full workflow for **Retrieval-Augmented Generation (RAG)**: combining a retrieval component with a generative model.
In short, when a user query arrives, the system:
1. Retrieves relevant context from a knowledge base.
2. Feeds that context + the query into a generative model.
3. Produces a more accurate/grounded response than a standalone generative model alone.

This repository contains a minimal demo that queries a MySQL vehicles database, builds a short prompt from the retrieved rows, and sends it to an OpenAI model to produce a concise vehicle recommendation.

## Features
- Simple web UI to enter a natural-language vehicle request.
- NLP-based query parser (spaCy) to extract brand, model, price and other constraints.
- SQL retrieval from a MySQL database (sample DB in `db/init.sql`).
- Generative final answer using the OpenAI API.
- Docker Compose stack for local development (backend + MySQL).

## Repository layout
- `backend/` – Flask app, model logic, templates and static assets.
	- `app.py` – Flask routes (`GET /` serves the UI, `POST /query` accepts JSON queries).
	- `RAGmodel.py` – QueryParser: parses user text, queries MySQL, builds prompt and calls OpenAI.
	- `requirements.txt` – Python dependencies for the backend.
	- `templates/index.html`, `static/script.js`, `static/style.css` – front-end.
- `db/init.sql` – sample SQL used to populate the MySQL container on first run.
- `docker-compose.yml` – quick local stack (backend + MySQL).

## Quick start

You can run the app either with Docker Compose (recommended for an isolated run) or locally in a Python virtualenv.

1) Using Docker Compose

 - Make a copy of `backend/.env` (if it exists) and ensure it contains the OpenAI and MySQL connection variables. Example keys required:
	 - `OPENAI_API_KEY` (your OpenAI API key)
	 - `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` (the compose file will provide defaults when using the included MySQL service)

 - Start the stack from the repo root:

```powershell
docker-compose up --build
```

 - The backend will be available at: http://localhost:8000

2) Running locally with Python (no Docker)

 - Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
# download the spaCy English model used by the project
python -m spacy download en_core_web_sm
```

 - Create a `backend/.env` file with these environment variables (example):

```
OPENAI_API_KEY=sk-...
MYSQL_HOST=localhost
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_DATABASE=mydatabase
```

 - Run the Flask app:

```powershell
python backend/app.py
```

 - Open http://localhost:8000 in your browser.

## API / Endpoints
- `GET /` – web UI (served from `templates/index.html`).
- `POST /query` – accepts JSON { "query": "..." } and returns JSON { "response": "..." }.

Example JSON request body:

```json
{ "query": "looking for a cheap petrol hatchback around $5k" }
```

The endpoint returns a concise, single-line vehicle recommendation from the generative model.

## Environment variables
The backend expects these environment variables (set them in `backend/.env`, or in your environment):

- `OPENAI_API_KEY` – OpenAI API key (required). The code uses the OpenAI Python client.
- `MYSQL_HOST` – MySQL host (e.g. `db` when running via docker-compose).
- `MYSQL_USER` – MySQL username.
- `MYSQL_PASSWORD` – MySQL password.
- `MYSQL_DATABASE` – MySQL database name.

Important: Do not commit secrets to Git. Keep `.env` out of source control.

## Dependencies
See `backend/requirements.txt`. Key packages:
- Flask, Flask-Cors – web server and CORS.
- spaCy – NLP parsing. Remember to run `python -m spacy download en_core_web_sm`.
- mysql-connector-python – DB connector.
- openai – OpenAI client.
- python-dotenv – loads `.env` file.

## Notes & troubleshooting
- If you see `No API key found` on startup, ensure `OPENAI_API_KEY` is set in `backend/.env` or the environment.
- If the app can't connect to MySQL:
	- When using Docker Compose, the `db` service will initialize using `db/init.sql`. Allow a minute after starting the containers for MySQL to be ready.
	- Verify the `MYSQL_*` env variables match the running DB credentials.
- spaCy model: the code calls `spacy.load('en_core_web_sm')`. If missing, run: `python -m spacy download en_core_web_sm`.
- OpenAI model: `RAGmodel.py` currently requests `gpt-4o-mini` — adjust this if you want a different model (and be aware of cost/availability).

## Design / Architecture notes
- The `QueryParser` in `RAGmodel.py` performs rule-based extraction (brands, fuels, price cues), then builds a SQL query, fetches candidate rows, and constructs a prompt for the generative model. This is a simple example of RAG where retrieval is the SQL query results.
- For production-grade RAG, consider:
	- Using a vector database (FAISS, Milvus, Pinecone, etc.) for semantic retrieval.
	- Adding query sanitization and prepared statements to avoid SQL injection.
	- Adding caching and rate-limiting when calling the LLM.

## Next steps / Improvements
1. Replace raw SQL string concatenation with parameterized queries to prevent SQL injection.
2. Add unit tests for `QueryParser` (parsing and query building).
3. Add integration tests that spin up a test MySQL instance and validate end-to-end results.
4. Add a simple server-side rate limit and logging for OpenAI requests.
5. Move retrieval to a vector store for semantic RAG and re-rank retrieved documents.

## License
This project does not include a license file. Add one (for example, MIT) if you plan to publish.

---

If you want, I can also:
- add a sample `backend/.env.example` file,
- harden the SQL queries (parameterize them), or
- add a minimal unit test for the `QueryParser` parsing behavior.
