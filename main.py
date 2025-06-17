from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
# NEW IMPORTS: These are important for error handling and debugging
from google.api_core.exceptions import DeadlineExceeded, ResourceExhausted
import os
from dotenv import load_dotenv
from menu_data import MENU_DATA, get_all_dishes, get_safe_dishes_for_allergen, COMMON_ALLERGENS, get_dish_by_name
from allergen_tools import get_menu_summary
import json
import traceback # NEW IMPORT: For detailed error tracing
import sys # NEW IMPORT: For system information
import certifi

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DEBUGGING INFO (keep these lines) ---
print(f"DEBUG: Python executable: {sys.executable}")
print(f"DEBUG: Python path: {sys.path}")
try:
    import google.generativeai as debug_genai
    print(f"DEBUG: google-generativeai location: {debug_genai.__file__}")
    print(f"DEBUG: google-generativeai version: {debug_genai.__version__}")
except ImportError:
    print("DEBUG: google-generativeai not found at runtime.")
# --- END DEBUGGING INFO ---


tools = [
    {
        "name": "get_all_dishes",
        "description": "Returns a flat dictionary of all dishes in the restaurant menu, including their details like name, price, calories, and allergens.",
        "parameters": {
            "type": "OBJECT",
            "properties": {},
        },
    },
    {
        "name": "get_safe_dishes_for_allergen",
        "description": "Returns a list of dishes that do not contain any of the specified allergens.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "allergens": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "A list of allergen names (e.g., 'gluten', 'dairy', 'nuts') to avoid.",
                }
            },
            "required": ["allergens"],
        },
    },
    {
        "name": "get_dish_by_name",
        "description": "Searches for a dish by its English or Hebrew name and returns its ID and detailed information, including ingredients, allergens, price, and nutritional info. Supports partial matches.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "dish_name": {
                    "type": "STRING",
                    "description": "The English or Hebrew name of the dish to search for.",
                }
            },
            "required": ["dish_name"],
        },
    },
    {
        "name": "get_menu_summary",
        "description": "Provides a summary of the menu, including total dishes, categories count, vegetarian/vegan options, price range, and most common allergens. Can filter based on allergens to avoid.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "menu": {
                    "type": "OBJECT",
                    "description": "The full menu data dictionary. (This will be passed internally)",
                },
                "avoid_allergens": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "Optional: A list of allergens (e.g., 'gluten', 'dairy') to exclude from the summary.",
                },
            },
        },
    },
]

RESTAURANT_CONTEXT_EN = """
You are a smart chatbot for "The Taste Restaurant" in Tel Aviv.
You specialize in helping customers with:
- Presenting the menu and dish information
- Checking allergens in dishes
- Recommending suitable dishes
- Nutritional information and prices

Always answer in English, in a friendly and professional manner.
Use relevant emojis to enhance your responses.

The menu includes the following dishes. Use the provided tools to get specific information about dishes, allergens, or menu summaries.
"""
COMMON_ALLERGENS_EN = {
    'gluten': 'gluten',
    'dairy': 'dairy',
    'eggs': 'eggs',
    'nuts': 'nuts',
    'peanuts': 'peanuts',
    'soy': 'soy',
    'fish': 'fish',
    'shellfish': 'shellfish',
    'sesame': 'sesame'
}
CATEGORY_NAMES_EN = {
    'main_dishes': 'Main Dishes',
    'salads': 'Salads',
    'desserts': 'Desserts',
    'drinks': 'Drinks'
}

@app.get("/")
def root():
    return {"message": "Welcome to The Taste Restaurant Chatbot API! 🍽️"}

@app.post("/chat")
async def chat(request: Request):
    try:
        message = await request.body()
        prompt = message.decode("utf-8").strip()

        if not prompt:
            return {"response": "I didn't receive a valid message. How can I help? 🤔"}

        model = genai.GenerativeModel('gemini-1.5-flash', tools=tools)
        chat_session = model.start_chat(history=[])

        response = chat_session.send_message(RESTAURANT_CONTEXT_EN + prompt) 

        if response.candidates and response.candidates[0].function_calls:
            fc = response.candidates[0].function_calls[0]
            function_name = fc.name
            function_args = {k: v for k, v in fc.args.items()}

            if function_name == "get_menu_summary":
                function_args["menu"] = MENU_DATA

            result = None
            if function_name == "get_all_dishes":
                result = get_all_dishes()
            elif function_name == "get_safe_dishes_for_allergen":
                result = get_safe_dishes_for_allergen(**function_args)
            elif function_name == "get_dish_by_name":
                dish_id, dish_info = get_dish_by_name(**function_args)
                result = {"dish_id": dish_id, "dish_info": dish_info}
            elif function_name == "get_menu_summary":
                result = get_menu_summary(**function_args)
            else:
                result = {"error": f"Unknown function: {function_name}"}

            if result is None:
                final_response = "Sorry, I couldn't get information from the tool right now."
            else:
                tool_response = chat_session.send_message(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=function_name,
                            response=json.dumps(result)
                        )
                    )
                )
                final_response = tool_response.text

            return {"response": final_response}
        else:
            return {"response": response.text}

    except DeadlineExceeded:
        print("Error: Gemini API call timed out (DeadlineExceeded).")
        traceback.print_exc()
        return {"response": "I'm sorry, I'm taking too long to respond. Please try again in a moment. ⏳"}
    except ResourceExhausted:
        print("Error: Gemini API rate limit exceeded (ResourceExhausted).")
        traceback.print_exc()
        return {"response": "I'm experiencing high demand right now. Please try again in a few minutes. 🙏"}
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        traceback.print_exc()
        return {"response": f"Sorry, an error occurred. Please try again later. 😅 Error details: {e}"}

@app.get("/menu")
def get_menu():
     return {"menu": MENU_DATA}

@app.post("/safe-dishes")
async def get_safe_dishes(request: Request):
    try:
        data = await request.json()
        allergens = data.get('allergens', [])

        safe_dishes = get_safe_dishes_for_allergen(allergens)
        return {"safe_dishes": safe_dishes, "count": len(safe_dishes)}

    except Exception as e:
        return {"error": str(e)}