import sys
import traceback
from config import GEMINI_API_KEY, EMBEDDING_MODEL
from langchain_google_genai import GoogleGenerativeAIEmbeddings

try:
    print(f"Using model: {EMBEDDING_MODEL}")
    e = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=GEMINI_API_KEY)
    print("Instance model:", e.model)
    res = e.embed_query('hello')
    print("Success, length:", len(res))
except Exception as ex:
    traceback.print_exc()
