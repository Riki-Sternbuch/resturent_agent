from collections import Counter
from typing import List, Dict, Any

def get_menu_summary(menu: Dict[str, Dict[str, Any]], avoid_allergens: List[str] = None) -> Dict[str, Any]:
 if avoid_allergens is None:
        avoid_allergens = []
 all_dishes_matching_criteria = []
 categories_count = {}
 vegetarian_count = 0
 vegan_count = 0
 prices = []
 all_allergens_list = []

 for category_name, dishes_in_category in menu.items():
    categories_count[category_name] = len(dishes_in_category)
    for dish_id, dish_info in dishes_in_category.items():
        dish_allergens = [a.lower() for a in dish_info.get("allergens", [])]
        is_safe = not any(allergen.lower() in dish_allergens for allergen in avoid_allergens)

        if is_safe:
            all_dishes_matching_criteria.append(dish_info)
        if dish_info.get("vegetarian"):
                vegetarian_count += 1
        if dish_info.get("vegan"):
                vegan_count += 1
        prices.append(dish_info.get("price", 0))
        all_allergens_list.extend(dish_allergens)

 if prices:
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
 else:
        min_price = max_price = avg_price = 0
 common_allergens_summary = [item for item, count in Counter(all_allergens_list).most_common(5)]
 return {
        "success": True,
        "total_dishes_matching_criteria": len(all_dishes_matching_criteria),
        "total_dishes_overall": sum(categories_count.values()),
        "categories_dish_counts": categories_count,
        "vegetarian_dishes_count": vegetarian_count,
        "vegan_dishes_count": vegan_count,
        "price_range": {
            "min": min_price,
            "max": max_price,
            "average": round(avg_price, 2) # Round for better presentation
        },
        "most_common_allergens": common_allergens_summary,
        "filter_applied": len(avoid_allergens) > 0,
        "avoided_allergens": avoid_allergens
    }