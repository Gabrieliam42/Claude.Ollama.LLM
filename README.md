# Claude.Ollama.LLM

Windows launcher for running `claude` against a local Ollama server with a dark Tk model picker.

## What it does

- Starts `ollama serve` with elevation.
- Reads installed Ollama models with `ollama list`.
- Filters out models that do not advertise `tools` support via `ollama show -v`.
- Deduplicates aliases that share the same Ollama model ID, preferring `:latest` when present.
- Shows a dark anthracite Tkinter model picker with model sizes.
- Prioritizes a small preferred-model list at the top.
- Launches `claude --model <selected-model>` with:
  - `ANTHROPIC_BASE_URL=http://localhost:11434`
  - `ANTHROPIC_AUTH_TOKEN=ollama`
  - `ANTHROPIC_API_KEY=`

## Requirements

- Windows
- Ollama installed locally
- Claude CLI installed and available on `PATH`
- Installed Ollama models, for example `glm-4.7-flash:latest`, a smaller model such as `qwen3.5:latest`, or a larger model such as `gpt-oss-20b:latest`
- Python 3.12+ if running the `.py` file directly
- `ollama_path.py` next to `Claude.Ollama.LLM.py`

## Files

- `Claude.Ollama.LLM.py`: source script
- `Claude.Ollama.LLM.exe`: standalone PyInstaller build in Releases

## Usage

Run the Python script:

```powershell
python .\Claude.Ollama.LLM.py
```

Or run the packaged executable from the repository Releases page.

## Notes

- The model list can take a moment to appear because the script checks tool support for each installed model.
- The script is intended for local Ollama-backed Claude CLI usage on Windows, not for deployment or server use.
