# Claude.Ollama.LLM

Windows launcher for running `Claude` locally, offline on your own PC via local Ollama server and local LLMs, with a model selector.

## What it does

- Starts reading installed Ollama models with `ollama list`.
- Filters out Models that do not support `tools` via `ollama show -v`.
- Deduplicates aliases that share the same Ollama model ID, preferring `:latest` when present.
- Launches `claude --model <selected-model>` with:
  - `ANTHROPIC_BASE_URL=http://localhost:11434`
  - `ANTHROPIC_AUTH_TOKEN=ollama`
  - `ANTHROPIC_API_KEY=`

[Download Latest Release (v1.0.0)](https://github.com/Gabrieliam42/Claude.Ollama.LLM/releases/download/v1.0.0/Claude.Ollama.LLM.exe)

## Requirements

- Windows
- Ollama installed locally. PowerShell command: `irm https://ollama.com/install.ps1 | iex`
- Claude CLI installed. PowerShell command: `winget install Anthropic.ClaudeCode`
- Installed Ollama `tools capable` models, for example `glm-4.7-flash:latest`, a smaller model such as `qwen3.5:latest`, or a larger model such as `gpt-oss-20b:latest`
- Python 3.12+ if running the `.py` file directly

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
- The script is intended for local, offline Ollama-backed Claude CLI usage on Windows, not cloud-hosted inference, deployment, or server use.
