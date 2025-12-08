# Ambiguous Query Handling Fix

## Problem

User query: **"show me all dishes 20 dollars"**

Result: **"I couldn't find any results for your query"**

### Root Cause

The query is grammatically incomplete - it's missing the price relationship:
- ❌ "dishes 20 dollars" - ambiguous
- ✅ "dishes **under** 20 dollars" - clear
- ✅ "dishes **around** 20 dollars" - clear

The intent extraction LLM didn't know how to interpret the price constraint, potentially treating it as irrelevant or malformed.

## Solution

Updated [intent_service.py](backend/app/services/intent_service.py) to:

1. **Added explicit price interpretation rule:**
   ```
   - **Price interpretation**: If a user mentions a price without "under", "over",
     or "around" (e.g., "dishes 20 dollars", "dishes $15"), interpret it as
     "under [price]" by default.
   ```

2. **Added Example 5 to demonstrate:**
   ```json
   User Query: "show me all dishes 20 dollars"

   Output:
   {
     "menu_search": ["List all dishes under $20"],
     ...
   }
   ```

## What Changed

**File:** [backend/app/services/intent_service.py](backend/app/services/intent_service.py)

**Lines 65-66:** Added price interpretation rule
**Lines 144-157:** Added Example 5 demonstrating ambiguous price handling

## Expected Behavior

### Before Fix
```
User: "show me all dishes 20 dollars"
System: "I couldn't find any results for your query"
```

### After Fix
```
User: "show me all dishes 20 dollars"
Intent Extracted: "List all dishes under $20"
System: [Returns dishes under $20 with compatibility scores]
```

## Testing

Restart your backend to load the changes:

```bash
cd backend
# If running with uvicorn
uvicorn app.main:app --reload

# Backend will auto-reload if you're using --reload flag
```

Then try these queries:

1. ✅ "show me all dishes 20 dollars" → Should return dishes under $20
2. ✅ "dishes 15 dollars" → Should return dishes under $15
3. ✅ "food items $25" → Should return items under $25
4. ✅ "show me dishes" → Should return all dishes

## Additional Notes

The system now defaults to **"under [price]"** when price relationship is ambiguous because:
- Most users want to see dishes **within budget**
- "Under $X" is the most common price query pattern
- It's safer to show more results than too few

If a user specifically wants:
- Dishes **over** $20: They should say "over 20 dollars"
- Dishes **exactly** $20: They should say "exactly 20 dollars" or "priced at 20"
- Dishes **around** $20: They should say "around 20 dollars"

---

**Ready to test!** 🎯
