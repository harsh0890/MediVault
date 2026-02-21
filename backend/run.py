"""
Run script for MediVault application
Can be executed directly from PyCharm
"""
import uvicorn
from app.config import config

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
