import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Use the same URI from your .env or config
MONGO_URI = "mongodb://localhost:27017" 
DB_NAME = "master_db"

async def reset():
    client = AsyncIOMotorClient(MONGO_URI)
    await client.drop_database(DB_NAME)
    print(f"Database '{DB_NAME}' has been deleted. You can now start fresh.")
    client.close()

if __name__ == "__main__":
    asyncio.run(reset())