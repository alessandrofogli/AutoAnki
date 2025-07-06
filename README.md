# AutoAnki

A web application to interact with your Anki account using LLM-powered agents. Built with FastAPI (backend), Streamlit (frontend), LangGraph for orchestration, LangChain for LLM integration, and Ollama for local LLMs.

## Structure
- `backend/`: FastAPI backend, MCP endpoints, and API logic
- `frontend/`: Streamlit app for user interface
- `agents/`: LLM agent logic, LangGraph orchestration
- `anki_integration/`: Anki API wrappers and utilities


## Setup
1. Install Python 3.10+
2. Install [Poetry](https://python-poetry.org/docs/#installation)
3. Install dependencies and set up the environment:
   ```sh
   poetry install
   ```
4. Run the backend:
   ```sh
   poetry run uvicorn backend.main:app --reload
   ```
5. In a separate terminal, run the frontend:
   ```sh
   poetry run streamlit run frontend/app.py
   ```

**Note:** Poetry manages dependencies and virtual environments. Do not use `requirements.txt`.

## Features
- Create/review Anki decks and cards with LLM agents
- Orchestrate workflows with LangGraph
- Use Ollama for local LLMs

## TODO
- Implement authentication
- Add more agent skills
- Improve UI/UX
