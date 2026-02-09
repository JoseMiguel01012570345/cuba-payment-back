"""CLI entry points for Cuba Payment Backend"""

import uvicorn
from dotenv import load_dotenv


def start():
    """Start the FastAPI development server"""
    # Load environment variables from .env file
    load_dotenv()
    
    uvicorn.run(
        "cuba_payment_back.src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    start()
