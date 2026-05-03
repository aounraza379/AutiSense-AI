# AutiSense-AI

AutiSense-AI is a Gradio-based voice assistant for autistic children, built for fast deployment on GitHub and Hugging Face Spaces.

## What is included

- `app.py` — main Gradio app entrypoint
- `requirements.txt` — required Python packages
- `.env.example` — environment variable template
- `.gitignore` — local files to exclude from Git
- `DEPLOYMENT.md` — deployment instructions
- `README.md` — project overview and quick start

## Quick start

```bash
git clone https://github.com/<your-user>/AutiSense-AI.git
cd AutiSense-AI
python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
python app.py
```

## Hugging Face Spaces deployment

This repo is ready for direct Hugging Face deployment using `app.py` as the entrypoint.

1. Push the repo to GitHub.
2. Create a new Space on Hugging Face and choose the Gradio SDK.
3. Connect your repository to the Space.
4. Add a secret named `GROQ_API_KEY` in Space settings.
5. Hugging Face Spaces will build and launch the app automatically.

## Required environment variables

```
GROQ_API_KEY=<your-key>
```

## Notes

- `.env` is local only and must not be committed.
- Use `.env.example` as the public template.
- `app.py` is the only required deployment file for Hugging Face.

## License

MIT
