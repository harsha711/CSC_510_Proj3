import logging
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
        raise Exception("No Menu Search Queries found in state.query_parts.")

    logger.info(f"Processing {len(query_parts)} menu search queries for restaurant {restaurant_id}")
    for q in query_parts:
        logging.debug(f"Retrieving menu items for query: {q} and restaurant_id: {restaurant_id}")
        try:
            hits = semantic_retrieve_with_negation(q, restaurant_id)
            dish_results = [res.get("dish") for res in hits if "dish" in res]

            if not dish_results:
                logger.warning(f"No dishes found for query= {q}")
                results[q] = []
                continue
            
            dish_results = apply_filters(q,dish_results)
            dish_results = validate_retrieved_dishes(q,dish_results)
            results[q] = dish_results
        except Exception as e:
            results[q] = []
            raise GenericException(str(e))
        
    # return {"menu_results":results}
    return MenuResultResponse(menu_results=results)