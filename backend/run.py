"""Windows-safe local dev entrypoint.

psycopg's async mode requires a Selector event loop, but asyncio's default
Windows policy creates a Proactor loop the instant uvicorn's CLI calls
asyncio.run() - before it ever imports app.main, so setting the policy
there is too late. Set it here, before uvicorn.run() creates its loop.
"""

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
