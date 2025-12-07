"""
Chat Session and State Management

This module provides utilities for handling user chat sessions and persisting
conversation states in the database.
"""
from datetime import datetime
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from ..flow.state import ChatState
from ..db import db
import uuid

chat_states = db["chat_states"]
sessions = db["sessions"]

def get_or_create_session(user_id:str, restaurant_id:str):
    """
    Retrieve an existing active session for a user and restaurant, or create a new one.

    Parameters
    ----------
    user_id : str
        Unique identifier of the user.
    restaurant_id : str
        Unique identifier of the restaurant.

    Returns
    -------
    str
        The session ID of the existing or newly created session.

    Notes
    -----
    - Only one active session per user per restaurant is maintained.
    - New session IDs are prefixed with 'sess_' followed by a 10-character UUID.
    """
    existing_session = sessions.find_one({"user_id": user_id, "restaurant_id": restaurant_id,"active":True})

    if existing_session:
        return existing_session["session_id"]
    

    session_id = f"sess_{uuid.uuid4().hex[:10]}"
    sessions.insert_one({
        "session_id": session_id,
        "user_id": user_id,
        "restaurant_id": restaurant_id,
        "active": True,
        "created_at": datetime.utcnow()
    })
    return session_id


def save_chat_state(state:ChatState):
    """
    Save a chat state object to the database.

    Parameters
    ----------
    state : ChatState
        The chat state to be persisted.

    Notes
    -----
    - Stores the state in the 'chat_states' collection.
    - Uses FastAPI's `jsonable_encoder` to serialize Pydantic models.
    """
    chat_states.insert_one(jsonable_encoder(state))

def get_all_chat_states(session_id:str):
    """
    Retrieve all chat states associated with a given session, ordered by timestamp.

    Parameters
    ----------
    session_id : str
        The session ID to fetch chat states for.

    Returns
    -------
    list[dict]
        List of chat state documents sorted chronologically by timestamp.
    """
    docs = list(chat_states.find({"session_id":session_id}).sort("timestamp",1))
    return docs

def rebuild_context(session_id:str, user_id:str = None, last_n:int=5):
    """
    Reconstruct the conversation context from the last N chat states of a session.

    Includes user allergen preferences as the first context item if user_id is provided.

    Parameters
    ----------
    session_id : str
        The session ID to rebuild context for.
    user_id : str, optional
        The user ID to fetch allergen preferences for.
    last_n : int, optional
        Number of most recent chat states to include in the context (default is 5).

    Returns
    -------
    list[dict]
        List of dictionaries containing user preferences, query, intents, menu results,
        and info results, representing the reconstructed context for LLM processing.

    Notes
    -----
    - Helps provide context for LLM-based query resolution.
    - Includes user allergen preferences as the first context item.
    - Only includes the most recent `last_n` chat states to limit context size.
    """
    chat_states = get_all_chat_states(session_id)
    print(f"Chat States for context rebuild: {chat_states}")
    context = []

    # Add complete user profile as first context item (for compatibility scoring)
    if user_id:
        from bson import ObjectId
        users = db["users"]
        try:
            print(f"Fetching user profile for user_id: {user_id}")
            user_doc = users.find_one({"_id": ObjectId(user_id)})
            print(f"User document: {user_doc}")

            if user_doc:
                # Extract allergen preferences
                allergen_prefs = user_doc.get("allergen_preferences", [])
                if allergen_prefs:
                    print(f"Found allergen preferences: {allergen_prefs}")
                    context.append({
                        "user_allergens": allergen_prefs,
                        "message": f"User is allergic to: {', '.join(allergen_prefs)}"
                    })

                # Extract full user profile for compatibility scoring
                health_goals = user_doc.get("health_goals", [])
                cuisine_preferences = user_doc.get("cuisine_preferences", [])
                taste_preferences = user_doc.get("taste_preferences", [])
                dietary_pattern = user_doc.get("dietary_pattern", "omnivore")

                # Add full profile if any compatibility-related fields exist
                if health_goals or cuisine_preferences or taste_preferences or dietary_pattern != "omnivore":
                    print(f"Found user profile for compatibility scoring")
                    context.append({
                        "user_profile": {
                            "health_goals": health_goals,
                            "cuisine_preferences": cuisine_preferences,
                            "taste_preferences": taste_preferences,
                            "dietary_pattern": dietary_pattern
                        },
                        "message": f"User profile: {dietary_pattern} diet, health goals: {', '.join(health_goals) if health_goals else 'none'}"
                    })
            else:
                print(f"No user document found for user {user_id}")
        except Exception as e:
            print(f"Could not fetch user profile: {e}")
    else:
        print("No user_id provided, skipping user profile fetch")

    for cs in chat_states[-last_n:]:
        context.append({
            "query": cs["query"],
            "intents": cs.get("intents", []),
            "menu_results": cs.get("menu_results", {}),
            "info_results": cs.get("info_results", {})
        })
    return context
