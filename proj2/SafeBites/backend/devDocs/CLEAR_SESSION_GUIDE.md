# Clear Session Feature - Start Fresh Conversations

## Problem

The SafeBites chat system maintains conversation context across sessions. When you ask "show all dishes", the system rewrites it based on previous queries, resulting in:

```
Previous query: "show me dishes under $20 that do not contain fish"
Current query: "show all dishes"
Rewritten to: "show me all dishes under $20 that do not contain fish"
```

This happens because the context resolver interprets new queries as **refinements** of previous queries.

## Solution: Clear Session Endpoint

A new API endpoint has been added to clear the session and start fresh:

### Endpoint
```
DELETE /restaurants/session/clear/{user_id}/{restaurant_id}
```

### Usage

#### From Command Line
```bash
curl -X DELETE "http://localhost:8000/restaurants/session/clear/YOUR_USER_ID/rest_1"
```

#### From Frontend
```javascript
const clearSession = async () => {
  const userId = localStorage.getItem('userId');
  const restaurantId = 'rest_1';

  const response = await fetch(
    `http://localhost:8000/restaurants/session/clear/${userId}/${restaurantId}`,
    { method: 'DELETE' }
  );

  const result = await response.json();
  console.log(result.message); // "Session cleared successfully"
  console.log(result.session_id); // New session ID
};
```

### Response
```json
{
  "message": "Session cleared successfully",
  "session_id": "sess_a1b2c3d4e5"
}
```

## How It Works

1. **Marks old session as inactive**
   - Sets `active: false` on the current session
   - Adds `ended_at` timestamp

2. **Creates a new session**
   - Generates a fresh session ID
   - No conversation history
   - Clean context state

3. **Next query uses new session**
   - No previous context
   - Queries are not rewritten
   - Fresh start for conversation

## Demo Conversation Examples

### Without Clearing Session (Old Behavior)
```
Query 1: "show me dishes under $20 without fish"
Result: [Returns filtered dishes]

Query 2: "show all dishes"
Rewritten to: "show me all dishes under $20 that do not contain fish"
Result: [Still filtered by previous constraints]
```

### With Clearing Session (New Behavior)
```
Query 1: "show me dishes under $20 without fish"
Result: [Returns filtered dishes]

[CLEAR SESSION]

Query 2: "show all dishes"
NOT rewritten (fresh session, no context)
Result: [Returns ALL dishes, no filters]
```

## Frontend Integration

### Add Clear Button to Chat Interface

```tsx
// In SearchChat.tsx
import { useState } from 'react';

const SearchChat = () => {
  const [sessionCleared, setSessionCleared] = useState(false);

  const handleClearSession = async () => {
    const userId = localStorage.getItem('userId');
    const restaurantId = 'rest_1';

    try {
      const response = await fetch(
        `${API_ENDPOINTS.restaurants.base}/session/clear/${userId}/${restaurantId}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        setSessionCleared(true);
        alert('Chat session cleared! Starting fresh conversation.');
      }
    } catch (error) {
      console.error('Failed to clear session:', error);
    }
  };

  return (
    <div className="search-chat-container">
      <div className="chat-header">
        <h1>Restaurant Search</h1>
        <button
          className="clear-session-btn"
          onClick={handleClearSession}
        >
          🔄 Start Fresh Chat
        </button>
      </div>
      {/* Rest of chat interface */}
    </div>
  );
};
```

### Add CSS
```css
.clear-session-btn {
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.clear-session-btn:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}
```

## Testing the Feature

### Test Case 1: Basic Clear
```bash
# Query 1
curl -X POST "http://localhost:8000/restaurants/search" \
  -H "Content-Type: application/json" \
  -d '{"restaurant_id": "rest_1", "query": "show vegetarian dishes"}'

# Query 2 (will be affected by context)
curl -X POST "http://localhost:8000/restaurants/search" \
  -H "Content-Type: application/json" \
  -d '{"restaurant_id": "rest_1", "query": "under $15"}'
# Expected: "show vegetarian dishes under $15" (context applied)

# Clear session
curl -X DELETE "http://localhost:8000/restaurants/session/clear/USER_ID/rest_1"

# Query 3 (fresh session, no context)
curl -X POST "http://localhost:8000/restaurants/search" \
  -H "Content-Type: application/json" \
  -d '{"restaurant_id": "rest_1", "query": "under $15"}'
# Expected: "show dishes under $15" (no vegetarian filter)
```

### Test Case 2: Multiple Users
```bash
# User A clears session
curl -X DELETE "http://localhost:8000/restaurants/session/clear/user_a/rest_1"

# User B's session remains intact
# User A gets fresh session
# User B keeps conversation context
```

## When to Clear Session

### ✅ Clear Session When:
- User clicks "New Chat" or "Start Fresh"
- User switches to a different restaurant
- Debugging query rewriting issues
- Demo/presentation (to show fresh start)
- User explicitly wants to forget previous context

### ❌ Don't Clear Session When:
- Normal conversation flow
- User is refining previous queries
- Building on previous results
- Follow-up questions about same topic

## Alternative: Context Resolver Improvements

Instead of clearing sessions, you could also improve the context resolver to better detect when a query is truly new vs a refinement:

```python
# In context_resolver.py, add this rule:
4. If the user query is a **completely different topic** (new dish type, new cuisine),
   treat it as a NEW request, not a refinement.
   - Example: Previous: "show burgers", Current: "show pizzas" → NEW (don't combine)
   - Example: Previous: "Italian dishes", Current: "show Chinese food" → NEW
```

But for demos and testing, the clear session endpoint is cleaner!

## Implementation Details

### Backend Files Modified

1. **[backend/app/routers/restaurant_router.py](backend/app/routers/restaurant_router.py#L110-L134)**
   - Added `DELETE /session/clear/{user_id}/{restaurant_id}` endpoint

2. **[backend/app/services/state_service.py](backend/app/services/state_service.py#L54-L88)**
   - Added `clear_and_create_new_session()` function
   - Marks old session as inactive
   - Creates new session with fresh ID

### Database Changes

Sessions collection now tracks:
```javascript
{
  session_id: "sess_abc123",
  user_id: "user_1",
  restaurant_id: "rest_1",
  active: true,          // false when session is cleared
  created_at: ISODate(...),
  ended_at: ISODate(...) // set when session is cleared
}
```

## Related Issues

- **Issue**: "show all dishes" being rewritten to previous query
- **Root Cause**: Context resolver treats new queries as refinements
- **Solution**: Clear session or improve context resolver logic

## See Also

- [Context Resolver Documentation](backend/app/services/context_resolver.py)
- [Session Management](backend/app/services/state_service.py)
- [Chat State Flow](Workflow_doc/README.md)
