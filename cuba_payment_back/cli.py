"""CLI entry points for Cuba Payment Backend"""

import uvicorn


def start():
    """Start the FastAPI development server"""
    uvicorn.run(
        "cuba_payment_back.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    start()
