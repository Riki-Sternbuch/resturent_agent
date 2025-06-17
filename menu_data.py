from typing import List, Dict, Any, Tuple
COMMON_ALLERGENS = {
    'gluten': 'גלוטן',
    'dairy': 'חלב ומוצרי חלב',
    'eggs': 'ביצים',
    'nuts': 'אגוזים',
    'peanuts': 'בוטנים',
    'soy': 'סויה',
    'fish': 'דגים',
    'shellfish': 'פירות ים',
    'sesame': 'שומשום'
}

# The Restaurant Menu Data
MENU_DATA = {
    "main_dishes": {
        "pasta_carbonara": {
            "name_he": "פסטה קרבונרה",
            "name_en": "Pasta Carbonara",
            "description": "Classic Italian pasta with creamy egg sauce, bacon, and Parmesan.",
            "ingredients": ["pasta", "eggs", "bacon", "parmesan_cheese", "black_pepper", "cream"],
            "allergens": ["gluten", "dairy", "eggs"],
            "price": 65,
            "calories": 450,
            "protein_g": 20,
            "carbs_g": 50,
            "fat_g": 20,
            "vegetarian": False,
            "vegan": False
        },
        "grilled_salmon": {
            "name_he": "סלמון בגריל",
            "name_en": "Grilled Salmon",
            "description": "Perfectly grilled salmon fillet with seasonal vegetables.",
            "ingredients": ["salmon", "broccoli", "asparagus", "olive_oil", "lemon"],
            "allergens": ["fish"],
            "price": 80,
            "calories": 380,
            "protein_g": 35,
            "carbs_g": 10,
            "fat_g": 25,
            "vegetarian": False,
            "vegan": False
        },
        "vegan_burger": {
            "name_he": "המבורגר טבעוני",
            "name_en": "Vegan Burger",
            "description": "Juicy plant-based patty in a bun with fresh toppings.",
            "ingredients": ["vegan_patty", "bun", "lettuce", "tomato", "onion", "vegan_mayo"],
            "allergens": ["gluten", "soy"], # Assuming bun has gluten, patty has soy
            "price": 70,
            "calories": 400,
            "protein_g": 25,
            "carbs_g": 40,
            "fat_g": 18,
            "vegetarian": True,
            "vegan": True
        }
    },
    "salads": {
        "caesar_salad": {
            "name_he": "סלט קיסר",
            "name_en": "Caesar Salad",
            "description": "Crisp romaine lettuce, croutons, Parmesan, and Caesar dressing.",
            "ingredients": ["romaine_lettuce", "croutons", "parmesan_cheese", "caesar_dressing"],
            "allergens": ["dairy", "eggs", "gluten"],
            "price": 45,
            "calories": 300,
            "protein_g": 10,
            "carbs_g": 25,
            "fat_g": 18,
            "vegetarian": True,
            "vegan": False
        },
        "quinoa_salad": {
            "name_he": "סלט קינואה",
            "name_en": "Quinoa Salad",
            "description": "Healthy quinoa salad with fresh vegetables and herbs.",
            "ingredients": ["quinoa", "cucumber", "tomato", "parsley", "mint", "lemon_dressing"],
            "allergens": [],
            "price": 50,
            "calories": 280,
            "protein_g": 8,
            "carbs_g": 40,
            "fat_g": 10,
            "vegetarian": True,
            "vegan": True
        }
    },
    "desserts": {
        "chocolate_lava_cake": {
            "name_he": "עוגת לבה שוקולד",
            "name_en": "Chocolate Lava Cake",
            "description": "Warm chocolate cake with a molten center, served with vanilla ice cream.",
            "ingredients": ["chocolate", "flour", "sugar", "eggs", "butter", "vanilla_ice_cream"],
            "allergens": ["gluten", "dairy", "eggs"],
            "price": 40,
            "calories": 550,
            "protein_g": 8,
            "carbs_g": 60,
            "fat_g": 30,
            "vegetarian": True,
            "vegan": False
        },
        "fruit_sorbet": {
            "name_he": "סורבה פירות",
            "name_en": "Fruit Sorbet",
            "description": "Refreshing selection of seasonal fruit sorbets.",
            "ingredients": ["seasonal_fruits", "sugar", "water"],
            "allergens": [],
            "price": 35,
            "calories": 150,
            "protein_g": 1,
            "carbs_g": 35,
            "fat_g": 0,
            "vegetarian": True,
            "vegan": True
        }
    },
    "drinks": {
        "cola": {
            "name_he": "קולה",
            "name_en": "Cola",
            "description": "Classic refreshing cola.",
            "ingredients": ["carbonated_water", "sugar", "caramel_color", "phosphoric_acid", "natural_flavors", "caffeine"],
            "allergens": [],
            "price": 12,
            "calories": 140,
            "protein_g": 0,
            "carbs_g": 39,
            "fat_g": 0,
            "vegetarian": True,
            "vegan": True
        },
        "orange_juice": {
            "name_he": "מיץ תפוזים",
            "name_en": "Orange Juice",
            "description": "Freshly squeezed orange juice.",
            "ingredients": ["oranges"],
            "allergens": [],
            "price": 15,
            "calories": 110,
            "protein_g": 2,
            "carbs_g": 26,
            "fat_g": 0,
            "vegetarian": True,
            "vegan": True
        }
    }
}
def get_all_dishes() -> Dict[str, Dict[str, Any]]:
 all_dishes = {}
 for category in MENU_DATA.values():
        all_dishes.update(category)
 return all_dishes

def get_dish_by_name(dish_name: str) -> Tuple[str | None, Dict[str, Any] | None]:
 all_dishes = get_all_dishes()

 for dish_id, dish_info in all_dishes.items():
        if dish_info['name_en'].lower() == dish_name.lower() or \
           dish_info['name_he'] == dish_name:
            return dish_id, dish_info
 for dish_id, dish_info in all_dishes.items():
        if dish_name.lower() in dish_info['name_en'].lower() or \
           dish_name in dish_info['name_he']:
            return dish_id, dish_info
 return None, None


def get_safe_dishes_for_allergen(allergens: List[str]) -> List[Dict[str, Any]]:
 safe_dishes = []
 all_dishes_values = get_all_dishes().values()
 allergens_lower = [a.lower() for a in allergens]
 for dish_info in all_dishes_values:
        dish_allergens = [a.lower() for a in dish_info.get('allergens', [])]
        is_safe = True
        for avoided_allergen in allergens_lower:
            if avoided_allergen in dish_allergens:
                is_safe = False
                break
        if is_safe:
            safe_dishes.append(dish_info)
 return safe_dishes


def search_dishes_by_allergen(allergen: str) -> List[Dict[str, Any]]:
 matching_dishes = []
 all_dishes = get_all_dishes()
 allergen_lower = allergen.lower()

 for dish_id, dish_info in all_dishes.items():
        if allergen_lower in [a.lower() for a in dish_info.get('allergens', [])]:
            matching_dishes.append(dish_info)
 return matching_dishes