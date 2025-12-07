# FAISS Threshold Fix

## Problem

When searching for "dishes under $20 that do not contain fish", the system was returning **0 dishes** even though there were dishes in the database matching the criteria.

### Root Cause

The FAISS semantic search was using a **threshold of 0.8**, which is too strict. This meant:

1. FAISS would retrieve up to 20 dishes (`top_k=20`)
2. Then filter out any dishes with similarity score < 0.8
3. Only 1 dish (Peanut Butter Cookies at $22.55) passed the 0.8 threshold
4. That dish was then filtered out because it exceeded the $20 price limit
5. Result: 0 dishes returned

### Evidence from Logs

```
2025-12-07 16:52:31,726 | WARNING | app.services.retrieval_service |
No dishes found for query= Show dishes under $20 that do not contain fish

Additional context:
The only dish mentioned in the context is the Peanut Butter Cookies, which are described as follows:
- Price: $22.55 (this exceeds the user's budget of under $20)
```

## Solution

**Lowered the FAISS similarity threshold from 0.8 to 0.5**

### Files Modified

1. [backend/app/services/faiss_service.py:259](backend/app/services/faiss_service.py#L259)
   ```python
   # BEFORE
   def search_dishes(query, restaurant_id=None, top_k=20, threshold=0.8):

   # AFTER
   def search_dishes(query, restaurant_id=None, top_k=20, threshold=0.5):
   ```

2. [backend/app/utils/faiss_index.py:234](backend/app/utils/faiss_index.py#L234)
   ```python
   # BEFORE
   def search_dishes(query, restaurant_id=None, top_k=20, threshold=0.8):

   # AFTER
   def search_dishes(query, restaurant_id=None, top_k=20, threshold=0.5):
   ```

## Why This Works

### FAISS Similarity Scores
- FAISS uses cosine similarity, which ranges from 0 to 1
- 1.0 = identical vectors (exact match)
- 0.8 = very high similarity (almost exact match)
- 0.5-0.7 = good similarity (semantically related)
- 0.3-0.5 = moderate similarity
- < 0.3 = low similarity

### Previous Threshold (0.8)
- Too strict for general search queries
- Only returned dishes that are **almost identical** to the query
- Caused many relevant dishes to be filtered out

### New Threshold (0.5)
- Allows more semantically related dishes through
- Better balance between precision and recall
- Downstream filters (price, allergens, nutrition) handle specificity
- Compatibility scoring provides personalized ranking

## System Architecture

The dish retrieval pipeline has multiple filtering stages:

```
User Query
    ↓
[1. FAISS Semantic Search] ← threshold=0.5 (was 0.8)
    ↓
Retrieved Dishes (20 max)
    ↓
[2. LLM-Based Filter Extraction]
    ↓
[3. Price/Allergen/Nutrition Filtering]
    ↓
[4. LLM Validation]
    ↓
[5. Compatibility Scoring]
    ↓
Final Results
```

**Key Insight**: Since we have 4 additional filtering/validation stages after FAISS, we can afford to be more lenient in the initial semantic search (stage 1). This increases recall without sacrificing precision.

## Testing

After the fix, the same query should now:
1. Retrieve more dishes from FAISS (those with score >= 0.5)
2. Apply price filter (under $20)
3. Apply allergen filter (no fish)
4. Return relevant results with compatibility scores

### Test Command
```bash
curl -X POST "http://localhost:8000/restaurants/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "restaurant_id": "rest_1",
    "query": "Show dishes under $20 that do not contain fish"
  }'
```

Expected: Multiple dish results with prices < $20 and no fish ingredients.

## Additional Recommendations

### 1. Make Threshold Configurable
Consider adding threshold as a query parameter:
```python
def search_dishes(query, restaurant_id=None, top_k=20, threshold=0.5):
    # Allow override from environment or config
    threshold = float(os.getenv("FAISS_THRESHOLD", threshold))
```

### 2. Log Similarity Scores
Add debug logging to understand score distribution:
```python
logger.debug(f"FAISS scores: {[score for _, score in results]}")
logger.debug(f"Dishes passing threshold {threshold}: {len(structured_res)}")
```

### 3. Adaptive Thresholds
Consider different thresholds for different query types:
- Simple queries ("show me pizza"): threshold=0.4
- Complex queries ("gluten-free high-protein dishes"): threshold=0.6
- Allergen queries: threshold=0.3 (maximize recall for safety)

## Related Issues

- If you see "No dishes found" warnings, check FAISS threshold first
- If getting irrelevant results, downstream LLM validation should filter them
- Compatibility scoring provides personalized ranking, so cast a wide net initially

## References

- FAISS Documentation: https://github.com/facebookresearch/faiss
- Cosine Similarity: https://en.wikipedia.org/wiki/Cosine_similarity
- Precision vs Recall: https://en.wikipedia.org/wiki/Precision_and_recall
