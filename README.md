# AutoAnki

A minimal, runnable system for generating flashcards using LLMs via Ollama, LangGraph, and FastAPI.

## Architecture

```
[Supervisor Agent] → [Topic Research Agent] → [Card Generator Agent] → JSON Output
```

- **Supervisor Agent**: Receives natural language instructions and coordinates the workflow
- **Topic Research Agent**: Generates a mini lesson or summary on the given topic
- **Card Generator Agent**: Creates 3-5 flashcards in JSON format from the mini-lesson content

## Tech Stack

- **FastAPI**: Backend API
- **LangGraph**: Agent orchestration
- **LangChain**: LLM integration
- **Ollama**: Local LLM (deepseek-r1:8b, mistral, etc.)

## Quick Start

### Prerequisites

1. **Install Ollama**: [https://ollama.ai/](https://ollama.ai/)
2. **Install Poetry**: [https://python-poetry.org/](https://python-poetry.org/)

### Setup

1. **Clone and install dependencies**:
   ```bash
   git clone <your-repo>
   cd AutoAnki
   poetry install
   ```

2. **Start Ollama and pull a model**:
   ```bash
   ollama serve
   # In another terminal:
   ollama pull deepseek-r1:8b
   ```

3. **Test the system**:
   ```bash
   python test_system.py
   ```

4. **Start the FastAPI server**:
   ```bash
   poetry run uvicorn backend.main:app --reload
   ```

## Usage

### API Endpoints

#### Generate Flashcards
```bash
curl -X POST "http://localhost:8000/generate-flashcards" \
     -H "Content-Type: application/json" \
     -d '{
       "instruction": "Generate flashcards about the French Revolution",
       "model_name": "deepseek-r1:8b"
     }'
```

#### Health Check
```bash
curl http://localhost:8000/health
```

### Example Response

```json
{
  "instruction": "Generate flashcards about the French Revolution",
  "mini_lesson": "The French Revolution (1789-1799) was a period of radical social and political upheaval...",
  "flashcards": [
    {
      "question": "When did the French Revolution begin?",
      "answer": "1789",
      "category": "fact"
    },
    {
      "question": "What was the main cause of the French Revolution?",
      "answer": "Social inequality and financial crisis",
      "category": "concept"
    }
  ],
  "status": "card_generation_complete",
  "workflow_info": {
    "agent": "card_generator",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Development

### Project Structure

```
AutoAnki/
├── agents/
│   ├── supervisor_agent.py      # Coordinates workflow
│   ├── topic_research_agent.py  # Generates mini lessons
│   ├── card_generator_agent.py  # Creates flashcards
│   └── langgraph_orchestrator.py # Orchestrates agents
├── backend/
│   └── main.py                  # FastAPI server
├── test_system.py               # Test script
└── pyproject.toml              # Dependencies
```

## Workflow Graph

![Workflow Graph](graph_structure.png)

### Adding New Models

To use a different Ollama model:

1. Pull the model: `ollama pull mistral`
2. Update the model name in your request or test script
3. The system will automatically use the specified model

### Debugging

Each agent returns intermediary output as a dictionary, making it easy to debug:

- Check `test_results.json` after running the test script
- Use the `/health` endpoint to verify system status
- Monitor the FastAPI logs for detailed error messages

## Future Enhancements

- Database integration for storing generated flashcards
- Anki integration via MCP
- Web UI with Streamlit
- Support for different flashcard formats
- Batch processing capabilities

## Troubleshooting

### Common Issues

1. **"Orchestrator not initialized"**: Make sure Ollama is running (`ollama serve`)
2. **"Model not found"**: Pull the required model (`ollama pull deepseek-r1:8b`)
3. **Import errors**: Run `poetry install` to install dependencies

### Logs

The system provides detailed logging:
- FastAPI logs show API requests and responses
- Agent logs show the workflow progression
- Error messages include troubleshooting hints
