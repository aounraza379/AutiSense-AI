# Deploy AutiSense-AI to Hugging Face Spaces

This repository is prepared for direct deployment to GitHub and Hugging Face Spaces.

## Required files

- `app.py` — main Gradio app
- `requirements.txt` — dependencies
- `.env.example` — environment template
- `.gitignore` — excludes local secrets
- `README.md` — project documentation

## 1. Push to GitHub

```bash
cd AutiSense-AI
# Initialize git if needed
git init

git add .
git commit -m "Prepare AutiSense-AI for GitHub and Hugging Face deployment"

git remote add origin https://github.com/arounraza379/AutiSense-AI.git

git push -u origin main
```

> Confirm `.env` is not tracked by Git by running `git status` before pushing.

## 2. Create a Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click **Create new Space**
3. Select **Gradio** as the SDK
4. Choose a name (for example `autisense-ai`)
5. Set visibility to public or private
6. Create the Space

## 3. Connect GitHub repo

1. Open your new Space
2. Go to **Settings** → **Repository**
3. Connect the GitHub repository `aounraza379/AutiSense-AI`
4. HF Spaces will sync from the repository automatically

## 4. Add Hugging Face Secret

1. In HF Space, go to **Settings** → **Repository secrets**
2. Add a secret named `GROQ_API_KEY`
3. Paste your Groq API key as the value
4. Save the secret

## 5. Verify deployment

Once the repository is connected and the secret is set, Hugging Face Spaces will:

- install packages from `requirements.txt`
- use `app.py` as the Gradio entrypoint
- launch the app automatically

If the app does not start, inspect the Space logs for installation or runtime errors.

## Local testing

```bash
cp .env.example .env
# edit .env and add your GROQ_API_KEY
python -m pip install -r requirements.txt
python app.py
```

## Environment variables

```
GROQ_API_KEY=<your-key>
```

## Important notes

- `.env` should remain local and must not be committed.
- Use `.env.example` for collaborators.
- `app.py` is the official entrypoint for Hugging Face Spaces.

## Troubleshooting

- `GROQ_API_KEY not found`: add the secret in HF Space settings
- Build errors: check `requirements.txt` compatibility in the Space logs
- Audio issues: verify the runtime environment supports audio dependencies
