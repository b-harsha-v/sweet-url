import asyncio
import os
import sys

# This tells Python to look in our root directory so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.models.unused_key import UnusedKey

# --- BASE62 LOGIC ---
BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(BASE62_ALPHABET)

def encode_base62(num: int) -> str:
    if num == 0: return BASE62_ALPHABET[0]
    base62_str = []
    while num > 0:
        rem = num % BASE
        base62_str.append(BASE62_ALPHABET[rem])
        num = num // BASE
    return "".join(reversed(base62_str))

# --- THE WORKER ---
async def generate_keys(start_id: int, batch_size: int):
    print(f"🚀 KGS Worker starting. Generating {batch_size} keys...")
    
    async with AsyncSessionLocal() as db:
        new_keys = []
        for i in range(start_id, start_id + batch_size):
            short_alias = encode_base62(i)
            new_keys.append(UnusedKey(key=short_alias))
            
        # Bulk insert is incredibly fast
        db.add_all(new_keys)
        await db.commit()
        
    print(f"✅ Successfully dumped {batch_size} unique keys into the pool!")

if __name__ == "__main__":
    # We start at 10,000,000 so our Base62 strings look like real URLs (e.g. 'FXsk')
    STARTING_COUNTER = 10000000 
    BATCH_SIZE = 1000
    
    asyncio.run(generate_keys(STARTING_COUNTER, BATCH_SIZE))