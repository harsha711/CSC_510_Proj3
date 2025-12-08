"""
Menu Retrieval Service

This module handles retrieving and filtering menu items for restaurants
based on user queries, semantic search, and applied filters.
"""
import logging
from ..models.dish_info_model import DishData
from .faiss_service import semantic_retrieve_with_negation
from .restaurant_service import apply_filters, validate_retrieved_dishes
from ..models.exception_model import GenericException
from ..models.restaurant_model import MenuResultResponse

logger = logging.getLogger(__name__)

def get_menu_items(state):
    """
    Retrieve and filter menu items for the given restaurant based on user query parts.

    Args:
        state (ChatState): Current conversation or session state containing restaurant_id and query_parts.

    Returns:
        Dict[str, Any]: Dictionary with structure { "menu_results": {query: [filtered_dishes, ...] } }
    """
    results = {}
    restaurant_id = getattr(state,"restaurant_id",None)
    query_parts = getattr(state,"query_parts",{}).get("menu_search",[])

    if not query_parts:
        logger.warning("No menu_search query parts found in state.")
        return MenuResultResponse(menu_results=results)

    logger.info(f"Processing {len(query_parts)} menu search queries for restaurant {restaurant_id}")
    for q in query_parts:
        logging.debug(f"Retrieving menu items for query: {q} and restaurant_id: {restaurant_id}")
        try:
            # Store original query for logging
            original_query = q

            # DO NOT append current_context to FAISS query - it confuses semantic search
            # Context should only be used AFTER retrieval for filtering/scoring
            # if state.current_context:
            #     logging.debug(f"Appending current context to query: {state.current_context}")
            #     q = f"{q}\n\nAdditional context:\n{state.current_context}"

            logger.info(f"Searching FAISS for: '{original_query}' (restaurant: {restaurant_id})")
            hits = semantic_retrieve_with_negation(q, restaurant_id)
            logger.info(f"FAISS returned {len(hits)} dishes")
            logging.debug(f"Retrieved data from semantic search: {hits}")
            dish_results = [DishData(
                dish_id=hit.dish["_id"],
                dish_name=hit.dish["name"],
                restaurant_id=hit.dish.get("restaurant_id"),
                description=hit.dish["description"],
                price=hit.dish["price"],
                ingredients=hit.dish["ingredients"],
                serving_size=hit.dish.get("serving_size"),
                availability=hit.dish.get("availability", True),
                allergens=[a["allergen"] for a in hit.dish.get("explicit_allergens", [])],
                nutrition_facts=hit.dish.get("nutrition_facts", {})
            ) for hit in hits]

            if not dish_results:
                logger.warning(f"No dishes found for query= {q}")
                results[q] = []
                continue

            logger.info(f"Retrieved {len(dish_results)} dishes from semantic search")

            # Apply lenient filtering
            dish_results = apply_filters(q,dish_results)
            logger.info(f"After lenient filtering: {len(dish_results)} dishes")

            # TEMPORARILY DISABLED: LLM validation is too strict with limited data
            # Let compatibility scoring handle relevance and quality checks
            # dish_results = validate_retrieved_dishes(q,dish_results)

            results[q] = dish_results
            logger.info(f"Final dish count for query '{q}': {len(dish_results)}")
        except Exception as e:
            logger.error(f"Error processing query '{q}': {e}", exc_info=True)
            results[q] = []
            # raise GenericException(str(e))

    return {"menu_results": MenuResultResponse(menu_results=results)}