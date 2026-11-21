
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# --------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# --------------------------------

load_dotenv(Path(__file__).resolve().parent / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")

DB_NAME = os.getenv("DB_NAME", "GenAI_DB")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "Prompt_Logs")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY missing in .env")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI missing in .env")


# --------------------------------
# 2. INITIALIZE GEMINI
# --------------------------------

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-3.5-flash"


# --------------------------------
# 3. INITIALIZE MONGODB
# --------------------------------

mongo_client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=10000
)

db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]


# --------------------------------
# 4. TOKEN PRICING
# --------------------------------

# Example estimated rates per 1 million tokens.
# Update these according to current model pricing.

INPUT_PRICE = 0.30
OUTPUT_PRICE = 2.50


# --------------------------------
# 5. CALCULATE COST
# --------------------------------

def calculate_cost(input_tokens, output_tokens):

    input_cost = (input_tokens / 1_000_000) * INPUT_PRICE

    output_cost = (output_tokens / 1_000_000) * OUTPUT_PRICE

    return input_cost + output_cost


# --------------------------------
# 6. SAVE LOGS TO MONGODB
# --------------------------------

def save_log(record):

    collection.insert_one(record)


# --------------------------------
# 7. ASK GEMINI
# --------------------------------

def ask_gemini(prompt):

    request_id = str(uuid.uuid4())

    for attempt in range(1, 4):

        start_time = time.perf_counter()

        input_tokens = 0
        output_tokens = 0
        total_tokens = 0

        status = "success"
        error_message = None
        answer = ""

        try:

            response = gemini_client.models.generate_content(
                model=MODEL,
                contents=prompt
            )

            answer = response.text or ""

            usage = response.usage_metadata

            if usage:

                input_tokens = usage.prompt_token_count or 0

                output_tokens = usage.candidates_token_count or 0

                total_tokens = usage.total_token_count or 0

        except Exception as error:

            status = "failed"
            error_message = str(error)

        latency = round(time.perf_counter() - start_time, 3)

        cost = calculate_cost(input_tokens, output_tokens)

        # Create MongoDB log
        record = {
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc),
            "model": MODEL,
            "prompt": prompt,
            "attempt": attempt,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "latency_seconds": latency,
            "estimated_cost_usd": cost,
            "status": status,
            "error": error_message
        }

        # Save log
        try:

            save_log(record)

            print(f"Attempt {attempt}: Log saved to MongoDB.")

        except PyMongoError as db_error:

            print("MongoDB logging error:", db_error)

        # If successful
        if status == "success":

            print("\nGemini Response:")
            print("------------------------------")
            print(answer)

            print("\nAPI Usage Details")
            print("------------------------------")

            print("Request ID:", request_id)
            print("Model:", MODEL)
            print("Input tokens:", input_tokens)
            print("Output tokens:", output_tokens)
            print("Total tokens:", total_tokens)
            print("Latency:", latency, "seconds")
            print("Estimated cost: $", round(cost, 8))

            return

        # If failed
        print("\nGemini API error:", error_message)

        if attempt < 3:

            print("Retrying after 5 seconds...")

            time.sleep(5)

    print("\nAll attempts failed.")


# --------------------------------
# 8. MAIN PROGRAM
# --------------------------------

def main():

    try:

        # Test MongoDB connection
        mongo_client.admin.command("ping")

        print("MongoDB connected successfully!")

        print("Database:", db.name)

        print("Collection:", collection.name)

        print("\nGEMINI API MONITORING SYSTEM")
        print("=" * 40)

        while True:

            prompt = input(
                "\nEnter your prompt (or type exit): "
            ).strip()

            if prompt.lower() == "exit":

                print("\nExiting program...")
                break

            if not prompt:

                print("Please enter a prompt.")
                continue

            ask_gemini(prompt)

    except PyMongoError as error:

        print("MongoDB connection error:", error)

    except Exception as error:

        print("Program error:", error)

    finally:

        mongo_client.close()

        print("\nMongoDB connection closed.")


# --------------------------------
# 9. RUN PROGRAM
# --------------------------------

if __name__ == "__main__":

    main()
