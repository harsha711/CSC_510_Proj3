# Demo Ready - Clear Session Feature

## What's Been Added

A **"Start Fresh Chat"** button has been added to the SearchChat page that allows you to clear the conversation context and start over.

### Features

1. **Clear Session Button**
   - Located in the top-right of the chat header
   - Shows: "🔄 Start Fresh Chat"
   - When clearing: "⏳ Clearing..."

2. **Confirmation Dialog**
   - Asks user to confirm before clearing
   - Prevents accidental session loss

3. **Visual Feedback**
   - Clears all messages from UI
   - Shows success message: "✅ Chat session cleared! Starting fresh conversation with no previous context."

4. **Backend Integration**
   - Calls `DELETE /restaurants/session/clear/{user_id}/{restaurant_id}`
   - Marks old session as inactive
   - Creates new session with fresh context

## How to Use for Demo

### Scenario 1: Show Context Preservation

```
1. Ask: "show me vegetarian dishes under $20"
   → System returns filtered results

2. Ask: "show me all dishes"
   → System rewrites to: "show me all dishes under $20" (context preserved)
   → Demonstrates context memory

3. Click "🔄 Start Fresh Chat"
   → Confirm the dialog

4. Ask: "show me all dishes"
   → System shows ALL dishes (no filters applied)
   → Demonstrates fresh start
```

### Scenario 2: Allergen Context Demo

```
1. User has peanut allergy set in their profile
2. Ask: "show me desserts"
   → System shows compatibility scores (peanut dishes scored low)

3. Ask: "show me chocolate cake"
   → System considers peanut allergy from profile
   → Shows warning if chocolate cake contains peanuts

4. Click "🔄 Start Fresh Chat"
5. Ask: "show me chocolate cake"
   → Still considers allergen profile (user profile persists)
   → But conversation context is cleared
```

### Scenario 3: Price Refinement Demo

```
1. Ask: "show me pasta dishes"
   → System returns all pasta

2. Ask: "under $15"
   → System combines: "show me pasta dishes under $15"
   → Demonstrates context-aware refinement

3. Click "🔄 Start Fresh Chat"

4. Ask: "under $15"
   → System treats as new query: "show dishes under $15"
   → No longer specific to pasta
```

## Files Modified

### Frontend

1. **[frontend/src/pages/SearchChat.tsx](frontend/src/pages/SearchChat.tsx)**
   - Added `isClearing` state
   - Added `handleClearSession()` function (lines 115-158)
   - Added button to header (lines 408-418)

2. **[frontend/src/pages/SearchChat.css](frontend/src/pages/SearchChat.css)**
   - Added `.chat-header-top` styles (lines 20-25)
   - Added `.clear-session-btn` styles (lines 34-62)

### Backend

3. **[backend/app/routers/restaurant_router.py](backend/app/routers/restaurant_router.py)**
   - Added `DELETE /session/clear` endpoint (lines 110-134)

4. **[backend/app/services/state_service.py](backend/app/services/state_service.py)**
   - Added `clear_and_create_new_session()` function (lines 54-88)

## Testing Checklist

- [ ] Button appears in chat header
- [ ] Button disabled during clearing operation
- [ ] Confirmation dialog shows before clearing
- [ ] Messages cleared from UI after confirming
- [ ] Success message appears
- [ ] New queries don't use old context
- [ ] User profile (allergies) still works after clearing

## What Context IS Preserved

Even after clearing session, these persist:

- ✅ User profile (allergies, dietary preferences)
- ✅ User account information
- ✅ Restaurant data
- ✅ Dish database

## What Context IS Cleared

After clearing session, these are reset:

- ❌ Previous queries in conversation
- ❌ Dishes mentioned earlier
- ❌ Price constraints from previous queries
- ❌ Cuisine preferences from conversation
- ❌ Query rewrites based on context

## Demo Script

**Presenter**: "Let me show you how our chat system maintains context across queries."

1. **Query 1**: "show me vegetarian dishes"
   - *System returns vegetarian dishes*

2. **Query 2**: "under $15"
   - *System rewrites to: "show me vegetarian dishes under $15"*
   - **Presenter**: "Notice how the system understood 'under $15' refers to the vegetarian dishes from before. It maintains context!"

3. **Click "Start Fresh Chat"**
   - **Presenter**: "Now let me clear the session to start fresh."

4. **Query 3**: "under $15"
   - *System shows: "show dishes under $15"* (no vegetarian filter)
   - **Presenter**: "Now when I ask 'under $15', it doesn't remember we were talking about vegetarian dishes. Clean slate!"

5. **Query 4**: "show me desserts"
   - *System shows compatibility scores based on user allergies*
   - **Presenter**: "But notice it still remembers my allergen preferences from my profile. The clear only affects conversation context, not my personal settings!"

## Troubleshooting

### Button not appearing
- Check SearchChat.tsx line 408-418
- Verify CSS is loaded
- Clear browser cache

### Session not clearing
- Check backend logs for errors
- Verify endpoint: `DELETE /restaurants/session/clear/{user_id}/{restaurant_id}`
- Check MongoDB sessions collection

### Context still present after clearing
- Verify new session_id was created
- Check state_service.clear_and_create_new_session()
- Ensure context_resolver is using new session

## Related Documentation

- [CLEAR_SESSION_GUIDE.md](CLEAR_SESSION_GUIDE.md) - Detailed API documentation
- [Context Resolver](backend/app/services/context_resolver.py) - How query rewriting works
- [Session Management](backend/app/services/state_service.py) - Session lifecycle

## Visual Preview

```
┌─────────────────────────────────────────────────────┐
│  Search Chat              🔄 Start Fresh Chat       │
├─────────────────────────────────────────────────────┤
│  How to use:                                        │
│  • Ask questions in natural language...             │
│  • ...                                              │
└─────────────────────────────────────────────────────┘
```

The button is styled to be subtle but noticeable, with hover effects that make it clear it's clickable.

---

**Ready for demo!** 🎉
