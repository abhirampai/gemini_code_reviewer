from functools import lru_cache

from fastapi import FastAPI

import config

app = FastAPI(
    title="Gemini Code Reviewer",
    description="A tool to review code using Gemini",
    version="0.1.0",
    contact={
        "name": "Gemini Code Reviewer",
        "url": "https://github.com/abhirampai/gemini_code_reviewer",
    },
)

@lru_cache
def get_settings():
    return config.Settings()

APP_ID = get_settings().GITHUB_APP_ID
PRIVATE_KEY = get_settings().GITHUB_PRIVATE_KEY
WEBHOOK_SECRET = get_settings().WEBHOOK_SECRET
GEMINI_API_KEY = get_settings().GEMINI_API_KEY

if not all([APP_ID, PRIVATE_KEY, WEBHOOK_SECRET, GEMINI_API_KEY]):
    raise ValueError(
        "Missing one or more required environment variables: "
        "GITHUB_APP_ID, GITHUB_PRIVATE_KEY, GITHUB_WEBHOOK_SECRET, GEMINI_API_KEY"
    )

@app.get("/")
def read_root():
    return {"Hello": "World"}
