@echo off
REM start.bat  —  Production startup for Windows
REM Run this instead of "uvicorn main:app --reload"

echo Starting Acme RAG Chatbot (production mode)...
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
