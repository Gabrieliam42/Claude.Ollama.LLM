# Claude.Ollama.LLM

Windows launcher for running `Claude CLI` Locally, OFFLINE on your own PC via local Ollama server and Local LLMs, with a model selector.

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

- Ollama. PowerShell command: `irm https://ollama.com/install.ps1 | iex`
- Claude CLI. PowerShell command: `winget install Anthropic.ClaudeCode`
- Installed `tools capable` LLM models, for example `glm-4.7-flash:latest`, a smaller model such as `qwen3.5:latest`, or a larger model such as `gpt-oss-20b:latest` or others.

- Python 3.12+ only if running the `.py` file directly



## Usage

Run the Python script:

```powershell
python .\Claude.Ollama.LLM.py
```

Or run the packaged executable from the repository Releases page.

## Notes

- The Model List can take a moment to appear because the script checks tool support for each installed model.
- The script is intended for local, offline Ollama-backed Claude CLI usage on Windows, not cloud-hosted inference, deployment.
