from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import html_pages, proxy, stremio


app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(html_pages.router)
app.include_router(proxy.router)
app.include_router(stremio.router)
