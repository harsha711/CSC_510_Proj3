import logging
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os, json
from dotenv import load_dotenv
from ..models.dish_info_model import DishInfoResponse, DishData, DishInfoResult, GeneralKnowledgeResponse, IntentResponse
from app.services.faiss_service import semantic_retrieve_with_negation
from .restaurant_service import apply_filters, validate_retrieved_dishes
from ..utils.llm_tracker import LLMUsageTracker
from app.models.exception_model import NotFoundException, BadRequestException, DatabaseException,GenericException


logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatOpenAI(model="gpt-5",temperature=1,openai_api_key=os.getenv("OPENAI_KEY"),callbacks=[LLMUsageTracker()])

def derive_dish_info_intent(query):
    """
    Determine whether a user query requires restaurant-specific menu data or general food knowledge.

    This function uses an LLM to analyze the query and classify it as either:
    - "requires_menu_data" (when query involves dishes, ingredients, allergens, or calories)
    - "general_knowledge" (when query is conceptual or unrelated to a restaurant’s menu)

    Args:
        query (str): The user's natural language question.

    Returns:
        dict: JSON-like dictionary containing:
            - type (str): Either "requires_menu_data" or "general_knowledge".
            - message (Optional[str]): Error message if parsing fails.
    """
    logging.debug(f"Deriving intent for query: {query}")

    prompt = ChatPromptTemplate.from_template("""
                                              
        You are an intent analyzer for a food assistant.

        Given a query, decide whether the answer requires fetching restaurant menu data.

        Possible outputs:
        - "requires_menu_data" → if the question is about dishes, ingredients, allergens, calories, or menu items that might exist in the restaurant data.
        - "general_knowledge" → if the question is conceptual and doesn’t depend on any restaurant data.

        Query: {query}

        Format the response in JSON:
        - type: "requires_menu_data" or "general_knowledge"

    """)
    response = llm.invoke(prompt.format_messages(query=query))
    logging.debug(f"LLM Intent Response: {response.content}")
    try:
        intent_json = json.loads(response.content)
        return IntentResponse(**intent_json)
    except Exception as e:
        logging.error(str(e))
        raise GenericException(f"Unexpected error: {str(e)}")


def handle_general_knowledge(query):
    """
    Handle general food knowledge queries.

    Args:
        query (str): User query text.

    Returns:
        GeneralKnowledgeResponse: Pydantic model with answer text.
    """
    logging.debug(f"Handling general knowledge query: {query}")
    prompt = ChatPromptTemplate.from_template("""
        You are a food assistant. Answer the following query using general food knowledge only. 
        Do NOT assume restaurant-specific information unless explicitly mentioned.
        Query: {query}
                                                    
        Format the response in JSON:
        - "answer": your answer to the query
    """)
    response = llm.invoke(prompt.format_messages(query=query))
    logging.debug(f"LLM Response: {response.content}")
    try:
        answer_json = json.loads(response.content)
        return GeneralKnowledgeResponse(**answer_json)
    except Exception as e:
        raise GenericException(str(e))

def handle_food_item_query(query, restaurant_id=None):
    """
        Retrieve and structure dish data from the semantic search.

        Args:
            query (str): User query text.
            restaurant_id (Optional[str]): Restaurant identifier.

        Returns:
            List[DishData]: List of structured dish data.

        Raises:
            NotFoundException: If no dishes are found.
    """
    logging.debug(f"Handling food item query: {query} for restaurant_id: {restaurant_id}")
    hits = semantic_retrieve_with_negation(query, restaurant_id=restaurant_id)

    if not hits:
        raise NotFoundException(f"No relevant dishes found for query {query}")

    results = []
    for hit in hits:
        dish = hit["dish"]
        results.append(DishData(
            dish_name = dish.get("name", "N/A"),
            description = dish.get("description", "N/A"),
            price = dish.get("price", "N/A"),
            ingredients = dish.get("ingredients", []),
            serving_size = dish.get("serving_size", "N/A"),
            availability = dish.get("availability", "N/A"),
            allergens = [a['allergen'] for a in dish.get("inferred_allergens", [])],
            nutrition_facts = dish.get("nutrition_facts", {})
        ))
    logging.debug(f"Food item query results: {results}")
    return results


def get_dish_info(state):
    """
    Retrieve dish information based on user queries.

    Args:
        state: State object containing restaurant_id and query_parts.

    Returns:
        DishInfoResult: Pydantic model containing query results.

    Raises:
        GenericException: If LLM parsing fails.
    """
    results : Dict[str,DishInfoResult] = {}
    restaurant_id = getattr(state,"restaurant_id", None)

    for query in state.query_parts.get("dish_info",[]):
        query = query.strip()
        logging.debug(f"Getting dish info for query: {query} and restaurant_id: {restaurant_id}")
        
        try:
            intent = derive_dish_info_intent(query)
        except GenericException as e:
            results[query] = DishInfoResponse(message=str(e))
            continue
        
        logging.debug(f"Query intent: {intent}")
        if intent.type == "general_knowledge":
            response = handle_general_knowledge(query=query)
            results[query] = DishInfoResponse(requested_info=response.answer)  
            continue
            
        try:
            dishes = handle_food_item_query(query, restaurant_id=restaurant_id)
            dishes = apply_filters(query,dishes)
            dishes = validate_retrieved_dishes(query,dishes)
        except NotFoundException as e:
            results[query] = DishInfoResponse(message=str(e))
            continue
        except Exception as e:
            results[query] = DishInfoResponse(message=f"Unexpected error : {str(e)}")
            continue
    
        context = ""
        context = "\n".join([
            f"Dish Name : {d.dish_name}\n"
            f"Description : {d.description}\n"
            f"Price : {d.price}\n"
            f"Ingredients : {', '.join(d.ingredients or [])}\n"
            f"Serving Size: {d.serving_size}\n"
            f"Availibility: {d.availibility}\n"
            f"Allergens : {', '.join(d.allergens or [])}\n"
            f"Nutrition : {d.nutrition_facts}\n"
            for d in dishes
        ])
            
        prompt = ChatPromptTemplate.from_template("""
    You are a food information assistant.
        Using ONLY the following dish data, answer the user's query.
        Format the response as JSON:
        - "dish_name"
        - "requested_info"
        - "source_data"

        User Query: {query}

        Dish Data: {context}
        """)
        response = llm.invoke(prompt.format_messages(query=query,context=context))
        logging.debug(f"LLM Response: {response.content}")
        
        try:
            response_json = json.loads(response.content)
            results[query] = DishInfoResponse(**response_json)
        except Exception as e:
            results[query] = DishInfoResponse(message="Could not parse LLM Response.")

    # return {"info_results":results}
    return DishInfoResult(info_results=results)