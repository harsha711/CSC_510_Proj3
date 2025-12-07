# Debugging "No Dishes Found" Issue

## Changes Made to Add Logging

To debug why searches return 0 dishes, we've added comprehensive logging throughout the pipeline:

### 1. Retrieval Service Logging
**File**: [backend/app/services/retrieval_service.py](backend/app/services/retrieval_service.py)

```python
logger.info(f"Searching FAISS for: '{original_query}' (restaurant: {restaurant_id})")
logger.info(f"FAISS returned {len(hits)} dishes")
logger.info(f"Retrieved {len(dish_results)} dishes from semantic search")
logger.info(f"After lenient filtering: {len(dish_results)} dishes")
logger.info(f"Final dish count for query '{q}': {len(dish_results)}")
```

### 2. FAISS Service Logging
**File**: [backend/app/services/faiss_service.py](backend/app/services/faiss_service.py)

```python
logger.info(f"Extracted intents - Positive: {intents.positive}, Negative: {intents.negative}")
logger.info(f"Positive intent '{p}' returned {len(hits)} dishes")
logger.info(f"Negative intent '{n}' returned {len(hits)} dishes (will be excluded)")
logger.info(f"Total positive hits: {len(pos_hits)}, Total negative hits: {len(neg_hits)}")
logger.info(f"After negative filtering: {len(filtered_dishes)} dishes remain")
```

### 3. LLM Validation Disabled
**File**: [backend/app/services/retrieval_service.py:66-68](backend/app/services/retrieval_service.py#L66-L68)

```python
# TEMPORARILY DISABLED: LLM validation is too strict with limited data
# Let compatibility scoring handle relevance and quality checks
# dish_results = validate_retrieved_dishes(q,dish_results)
```

## How to Debug

### Step 1: Run a Search Query

```bash
curl -X POST "http://localhost:8000/restaurants/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "restaurant_id": "rest_1",
    "query": "List dishes under $20 that do not contain fish"
  }'
```

### Step 2: Check Logs

Look for these INFO messages in your backend logs:

```
INFO | Searching FAISS for: 'List dishes under $20 that do not contain fish'
INFO | Extracted intents - Positive: [...], Negative: [...]
INFO | Positive intent 'X' returned N dishes
INFO | Negative intent 'Y' returned M dishes (will be excluded)
INFO | Total positive hits: N, Total negative hits: M
INFO | After negative filtering: X dishes remain
INFO | FAISS returned X dishes
INFO | Retrieved X dishes from semantic search
INFO | After lenient filtering: X dishes
INFO | Final dish count: X
```

### Step 3: Identify the Bottleneck

The logs will show where dishes are being filtered out:

#### Bottleneck #1: FAISS Threshold Too High
```
INFO | Positive intent 'dishes' returned 2 dishes  <- PROBLEM: Should be more
```
**Solution**: Lower FAISS threshold (already done: 0.8 → 0.5)

#### Bottleneck #2: Negative Intent Filtering Too Aggressive
```
INFO | Positive intent 'dishes' returned 10 dishes
INFO | Negative intent 'fish' returned 9 dishes (will be excluded)  <- PROBLEM
INFO | After negative filtering: 1 dishes remain  <- Only 1 left!
```
**Solution**: Modify intent extraction to be less aggressive with negatives

#### Bottleneck #3: Lenient Filter Still Filtering
```
INFO | Retrieved 5 dishes from semantic search
INFO | After lenient filtering: 0 dishes  <- PROBLEM
```
**Solution**: Make filtering even more lenient

#### Bottleneck #4: No Dishes in Database
```
INFO | Positive intent 'dishes' returned 0 dishes  <- PROBLEM
```
**Solution**: Add more dishes to database

## Common Issues and Fixes

### Issue: Query "do not contain X" filters out too many dishes

**Problem**:
```
Query: "dishes without fish"
Negative intent: ["fish", "seafood", "salmon", "tuna", ...]
Result: Most dishes filtered out
```

**Fix**: Modify intent extraction to ignore allergen-based negations:

```python
# In faiss_service.py extract_query_intent()
# Lines 61-63 already have this, but ensure it's working:

- **IMPORTANT**: For allergen-based exclusions (e.g., "nut-free", "dairy-free", "no peanuts"),
  DO NOT add allergens to the negative list. Leave negative list EMPTY for allergen queries.
  Allergen filtering will be handled by a separate filter system.
```

### Issue: Context confusing semantic search

**Problem**:
```
Original query: "show dishes"
Query with context: "show dishes\n\nAdditional context: User is allergic to fish..."
Result: Search finds dishes related to "fish" instead of general dishes
```

**Fix**: Don't append full context to semantic search query:

```python
# In retrieval_service.py, comment out lines 40-42
# if state.current_context:
#     logging.debug(f"Appending current context to query: {state.current_context}")
#     q = f"{q}\n\nAdditional context:\n{state.current_context}"
```

### Issue: Database empty or not indexed

**Problem**:
```
INFO | Positive intent 'dishes' returned 0 dishes
```

**Check**:
1. Is MongoDB running? `mongosh` → `use safebites` → `db.dishes.count()`
2. Is FAISS index built? `ls faiss_index_restaurant/`
3. Rebuild index: `python -m app.utils.rebuild_faiss`

## Testing Checklist

After making changes, test these queries:

### Test 1: General Query
```bash
Query: "show me all dishes"
Expected: Return ALL dishes in database
```

### Test 2: Price Filter
```bash
Query: "dishes under $20"
Expected: Return dishes around $20 (with 10% margin)
```

### Test 3: Allergen Query
```bash
Query: "dishes without fish"
Expected:
- Positive intent: ["dishes", "anything", "non-fish"]
- Negative intent: [] (empty, allergen handled separately)
- Result: All dishes returned, sorted by compatibility
```

### Test 4: Complex Query
```bash
Query: "show me vegetarian pasta under $15"
Expected:
- Positive intent: ["vegetarian pasta", "pasta", "vegetarian"]
- Negative intent: [] or ["meat", "chicken", "beef"]
- Result: Multiple dishes, best matches first
```

## Monitoring in Production

Add these metrics to track search quality:

```python
# Log search metrics
logger.info(f"Search metrics: {
    'query': query,
    'faiss_hits': len(hits),
    'after_filtering': len(dish_results),
    'has_results': len(dish_results) > 0,
    'avg_compatibility_score': avg_score if dish_results else 0
}")
```

## Temporary vs Permanent Fixes

### Temporary Fixes (Current)
- ✅ Disabled LLM validation
- ✅ Lowered FAISS threshold to 0.5
- ✅ Disabled allergen/ingredient filtering

### Permanent Fixes (Future)
- Re-enable LLM validation with better prompt
- Fine-tune FAISS threshold based on database size
- Implement soft filtering (warnings instead of exclusions)
- Add more dishes to database

## Next Steps

1. **Run search with logging** to see exact numbers
2. **Identify bottleneck** from logs
3. **Apply targeted fix** based on where dishes are lost
4. **Test again** until dishes are returned
5. **Verify compatibility scores** appear correctly

## Related Files

- [LENIENT_FILTERING_MODE.md](LENIENT_FILTERING_MODE.md) - Overview of lenient filtering approach
- [FAISS_THRESHOLD_FIX.md](FAISS_THRESHOLD_FIX.md) - FAISS threshold changes
- [backend/app/services/retrieval_service.py](backend/app/services/retrieval_service.py) - Main retrieval logic
- [backend/app/services/faiss_service.py](backend/app/services/faiss_service.py) - FAISS search logic
