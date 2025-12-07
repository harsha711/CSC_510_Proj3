# Frontend Integration Guide for AI Compatibility Scoring

## ✅ What's Already Done

### Backend Implementation
- ✅ Compatibility scoring fully implemented in backend
- ✅ API returns compatibility scores in `responses` array
- ✅ Scores calculated for logged-in users with dietary profiles

### Frontend UI (SearchChat.tsx)
- ✅ TypeScript interfaces updated to include `CompatibilityScore`
- ✅ API response processing updated to use new `responses` format
- ✅ Compatibility score display component added to dish cards
- ✅ CSS styling added for visual presentation

## 🎯 How It Works Now

When a logged-in user searches for dishes:

1. **Backend automatically:**
   - Fetches user's dietary profile (allergens, health goals, cuisine preferences, dietary pattern)
   - Analyzes each dish against user preferences
   - Calculates 4-dimensional compatibility scores
   - Returns scores in the API response

2. **Frontend displays:**
   - Overall compatibility score (0-100)
   - 4 breakdown scores with visual indicators:
     - ✅/⚠️/❌ Allergen Safety
     - ✅/⚠️/❌ Nutrition Match
     - ✅/⚠️/❌ Taste Preference
     - ✅/⚠️/❌ Diet Match
   - AI-generated recommendation
   - Alternative dish suggestions (if score < 70)

## 🚀 Testing the Feature

### 1. Update User Profile with Dietary Preferences

First, users need to have a dietary profile. Update the Settings page or use the API directly:

```bash
# Update user profile via API
curl -X PATCH http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "allergen_preferences": ["peanuts", "shellfish"],
    "health_goals": ["low-carb", "high-protein"],
    "cuisine_preferences": ["Italian", "Mexican"],
    "taste_preferences": ["spicy", "savory"],
    "dietary_pattern": "vegetarian"
  }'
```

### 2. Test the Search Feature

1. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

2. Start the backend:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   ```

3. Log in with a user that has dietary preferences set

4. Go to Search Chat page

5. Search for dishes:
   - "show me all dishes"
   - "show me vegetarian options"
   - "find me healthy meals"

6. You should see compatibility scores displayed for each dish!

## 📋 Next Steps to Complete Integration

### Step 1: Add Dietary Preferences to Settings Page

The Settings page needs fields for users to configure their dietary profile:

```tsx
// In Settings.tsx, add state for new fields:
const [healthGoals, setHealthGoals] = useState<string[]>([]);
const [cuisinePreferences, setCuisinePreferences] = useState<string[]>([]);
const [tastePreferences, setTastePreferences] = useState<string[]>([]);
const [dietaryPattern, setDietaryPattern] = useState<string>('omnivore');

// Update fetchUserData to load these fields:
setHealthGoals(userData.health_goals || []);
setCuisinePreferences(userData.cuisine_preferences || []);
setTastePreferences(userData.taste_preferences || []);
setDietaryPattern(userData.dietary_pattern || 'omnivore');

// Add UI sections in the render:
<div className="settings-section">
  <h2>Dietary Preferences</h2>

  {/* Dietary Pattern */}
  <div className="setting-group">
    <label>Dietary Pattern</label>
    <select value={dietaryPattern} onChange={(e) => setDietaryPattern(e.target.value)}>
      <option value="omnivore">Omnivore</option>
      <option value="vegetarian">Vegetarian</option>
      <option value="vegan">Vegan</option>
      <option value="pescatarian">Pescatarian</option>
      <option value="keto">Keto</option>
      <option value="paleo">Paleo</option>
    </select>
  </div>

  {/* Health Goals */}
  <div className="setting-group">
    <label>Health Goals</label>
    <div className="checkbox-group">
      {['low-carb', 'high-protein', 'low-fat', 'low-sodium', 'high-fiber'].map(goal => (
        <label key={goal} className="checkbox-label">
          <input
            type="checkbox"
            checked={healthGoals.includes(goal)}
            onChange={(e) => {
              if (e.target.checked) {
                setHealthGoals([...healthGoals, goal]);
              } else {
                setHealthGoals(healthGoals.filter(g => g !== goal));
              }
            }}
          />
          {goal}
        </label>
      ))}
    </div>
  </div>

  {/* Cuisine Preferences */}
  <div className="setting-group">
    <label>Favorite Cuisines</label>
    <div className="checkbox-group">
      {['Italian', 'Mexican', 'Chinese', 'Indian', 'Japanese', 'Mediterranean'].map(cuisine => (
        <label key={cuisine} className="checkbox-label">
          <input
            type="checkbox"
            checked={cuisinePreferences.includes(cuisine)}
            onChange={(e) => {
              if (e.target.checked) {
                setCuisinePreferences([...cuisinePreferences, cuisine]);
              } else {
                setCuisinePreferences(cuisinePreferences.filter(c => c !== cuisine));
              }
            }}
          />
          {cuisine}
        </label>
      ))}
    </div>
  </div>

  {/* Taste Preferences */}
  <div className="setting-group">
    <label>Taste Preferences</label>
    <div className="checkbox-group">
      {['spicy', 'savory', 'sweet', 'sour', 'umami', 'bitter'].map(taste => (
        <label key={taste} className="checkbox-label">
          <input
            type="checkbox"
            checked={tastePreferences.includes(taste)}
            onChange={(e) => {
              if (e.target.checked) {
                setTastePreferences([...tastePreferences, taste]);
              } else {
                setTastePreferences(tastePreferences.filter(t => t !== taste));
              }
            }}
          />
          {taste}
        </label>
      ))}
    </div>
  </div>

  {/* Save Button */}
  <button className="save-btn" onClick={handleSaveDietaryPreferences}>
    Save Dietary Preferences
  </button>
</div>
```

### Step 2: Implement Save Function

```tsx
const handleSaveDietaryPreferences = async () => {
  try {
    setIsSaving(true);
    const authToken = localStorage.getItem('authToken');

    const response = await fetch(API_ENDPOINTS.users.me, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        health_goals: healthGoals,
        cuisine_preferences: cuisinePreferences,
        taste_preferences: tastePreferences,
        dietary_pattern: dietaryPattern
      })
    });

    if (!response.ok) {
      throw new Error('Failed to update dietary preferences');
    }

    alert('Dietary preferences saved successfully!');
  } catch (error) {
    console.error('Error saving dietary preferences:', error);
    alert('Failed to save dietary preferences');
  } finally {
    setIsSaving(false);
  }
};
```

### Step 3: Add CSS for New Settings

Add to `Settings.css`:

```css
.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.checkbox-label:hover {
  background: #f3f4f6;
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}
```

### Step 4: Update SignUp Page (Optional)

Allow users to set dietary preferences during signup:

```tsx
// In SignUp.tsx, add the same dietary preference fields
// Include them in the signup request body
const requestBody = {
  name: name,
  username: username,
  password: password,
  allergen_preferences: allergens,
  health_goals: healthGoals,
  cuisine_preferences: cuisinePreferences,
  taste_preferences: tastePreferences,
  dietary_pattern: dietaryPattern
};
```

## 🎨 Customization Options

### Adjust Score Thresholds

In `SearchChat.css`, you can modify the color coding:

```css
/* Current: 0-40 red, 40-60 orange, 60-100 green */
/* You can add more granular ranges */
.score-0 { background: #dc2626; } /* 0-20: Very Poor */
.score-1 { background: #ef4444; } /* 20-40: Poor */
.score-2 { background: #f59e0b; } /* 40-60: Fair */
.score-3 { background: #84cc16; } /* 60-80: Good */
.score-4, .score-5 { background: #10b981; } /* 80-100: Excellent */
```

### Add Expandable Details

Make the compatibility breakdown collapsible:

```tsx
const [showDetails, setShowDetails] = useState(false);

// In the compatibility score section:
<button onClick={() => setShowDetails(!showDetails)}>
  {showDetails ? 'Hide Details' : 'Show Details'}
</button>

{showDetails && (
  <div className="compatibility-breakdown">
    {/* All the breakdown items */}
  </div>
)}
```

### Add Tooltips

Show reasoning on hover:

```tsx
<div
  className="compatibility-item"
  title={dish.compatibility_score.allergen_safety.reasoning}
>
  {/* Item content */}
</div>
```

## 🐛 Troubleshooting

### Scores Not Showing

1. **Check if user is logged in:**
   ```javascript
   const userId = localStorage.getItem("authToken");
   console.log("User ID:", userId);
   ```

2. **Verify user has dietary profile:**
   - Go to Settings page
   - Check if dietary preferences are set

3. **Check API response:**
   ```javascript
   console.log('API Response:', data);
   console.log('Has responses?', data.responses);
   console.log('Dishes:', data.responses?.[0]?.result);
   ```

4. **Verify backend is running latest code:**
   - Restart backend server
   - Check backend logs for compatibility scoring activity

### Scores Show as Undefined

Check the data structure:
```javascript
console.log('Dish:', dish);
console.log('Compatibility Score:', dish.compatibility_score);
```

The backend returns scores in this format:
```json
{
  "responses": [
    {
      "type": "menu_search",
      "result": [
        {
          "name": "Shakshuka",
          "price": 13.71,
          "compatibility_score": {
            "overall_score": 80,
            "allergen_safety": { ... },
            ...
          }
        }
      ]
    }
  ]
}
```

## 📊 Feature Metrics

Track how the feature performs:

```tsx
// Log when scores are displayed
useEffect(() => {
  if (menuResults.length > 0) {
    const scoresDisplayed = menuResults.filter(d => d.compatibility_score).length;
    console.log(`Compatibility scores displayed: ${scoresDisplayed}/${menuResults.length}`);
  }
}, [menuResults]);
```

## 🎉 Final Result

Once complete, users will:

1. **Set their dietary profile** in Settings
2. **Search for dishes** in Search Chat
3. **See personalized compatibility scores** for each dish
4. **Get AI recommendations** based on their preferences
5. **Discover alternative dishes** that better match their needs

The feature provides a **unique, personalized dining experience** powered by AI!

---

## Need Help?

- Backend docs: `backend/devDocs/COMPATIBILITY_SCORING_IMPLEMENTATION.md`
- Test script: `backend/test_compatibility_scoring.py`
- API endpoint: `POST http://localhost:8000/restaurants/search`
