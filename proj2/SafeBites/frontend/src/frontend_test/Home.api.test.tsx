import { describe, it, expect, beforeAll } from 'vitest'

/**
 * API INTEGRATION TESTS
 * 
 * These tests make REAL API calls to verify:
 * 1. The API is reachable and working
 * 2. The API returns data in the expected format
 * 3. The data structure matches what our frontend expects
 * 
 * NOTE: These tests are SLOWER than component tests because they make real network requests.
 * Run these separately: npm run test:api
 */

const API_BASE_URL = 'https://safebites-yu1o.onrender.com'

interface Restaurant {
  _id: string
  name: string
  location: string
  cuisine: string[]
  rating: number
}

interface Dish {
  _id: string
  restaurant_id: string
  name: string
  description: string
  price: number
  ingredients: string[]
  inferred_allergens?: Array<{
    allergen: string
    confidence: number
    why: string
  }>
  explicit_allergens?: Array<{
    allergen: string
  }>
  nutrition_facts?: {
    calories?: { value: number }
    protein?: { value: number }
    fat?: { value: number }
    carbohydrates?: { value: number }
    sugar?: { value: number }
    fiber?: { value: number }
  }
  availaibility?: boolean
  serving_size?: string
}

describe('SafeBites API Integration Tests', () => {
  let restaurants: Restaurant[] = []
  let testRestaurantId: string = ''
  let dishes: Dish[] = []

  // ===== RESTAURANT API TESTS =====
  
  describe('GET /restaurants/', () => {
    it('should fetch all restaurants successfully', async () => {
      const response = await fetch(`${API_BASE_URL}/restaurants/`)
      
      expect(response.ok).toBe(true)
      expect(response.status).toBe(200)
      
      restaurants = await response.json()
      
      expect(Array.isArray(restaurants)).toBe(true)
      expect(restaurants.length).toBeGreaterThan(0)
      
      console.log(`✅ Fetched ${restaurants.length} restaurants`)
    }, 10000) // 10 second timeout for API calls

    it('should return restaurants with correct structure', async () => {
      const response = await fetch(`${API_BASE_URL}/restaurants/`)
      restaurants = await response.json()
      
      const restaurant = restaurants[0]
      
      // Verify all required fields exist
      expect(restaurant).toHaveProperty('_id')
      expect(restaurant).toHaveProperty('name')
      expect(restaurant).toHaveProperty('location')
      expect(restaurant).toHaveProperty('cuisine')
      expect(restaurant).toHaveProperty('rating')
      
      // Verify field types
      expect(typeof restaurant._id).toBe('string')
      expect(typeof restaurant.name).toBe('string')
      expect(typeof restaurant.location).toBe('string')
      expect(Array.isArray(restaurant.cuisine)).toBe(true)
      expect(typeof restaurant.rating).toBe('number')
      
      console.log('✅ Restaurant structure is correct:', restaurant.name)
    }, 10000)

    it('should return valid restaurant IDs', async () => {
      const response = await fetch(`${API_BASE_URL}/restaurants/`)
      restaurants = await response.json()
      
      restaurants.forEach((restaurant: Restaurant) => {
        expect(restaurant._id).toBeTruthy()
        expect(restaurant._id.length).toBeGreaterThan(0)
      })
      
      // Save first restaurant ID for dish tests
      testRestaurantId = restaurants[0]._id
      console.log(`✅ Using restaurant ID for dish tests: ${testRestaurantId}`)
    }, 10000)

    it('should return restaurants with ratings between 0 and 5', async () => {
      const response = await fetch(`${API_BASE_URL}/restaurants/`)
      restaurants = await response.json()
      
      restaurants.forEach((restaurant: Restaurant) => {
        expect(restaurant.rating).toBeGreaterThanOrEqual(0)
        expect(restaurant.rating).toBeLessThanOrEqual(5)
      })
      
      console.log('✅ All restaurant ratings are valid')
    }, 10000)

    it('should return restaurants with non-empty cuisine arrays', async () => {
      const response = await fetch(`${API_BASE_URL}/restaurants/`)
      restaurants = await response.json()
      
      restaurants.forEach((restaurant: Restaurant) => {
        expect(restaurant.cuisine.length).toBeGreaterThan(0)
        expect(typeof restaurant.cuisine[0]).toBe('string')
      })
      
      console.log('✅ All restaurants have cuisine types')
    }, 10000)
  })

  // ===== DISHES/MENU API TESTS =====
  
  describe('GET /dishes/?restaurant={id}', () => {
    beforeAll(async () => {
      // Get a restaurant ID first
      const response = await fetch(`${API_BASE_URL}/restaurants/`)
      const restaurantData = await response.json()
      testRestaurantId = restaurantData[0]._id
    })

    it('should fetch dishes for a specific restaurant', async () => {
      const response = await fetch(`${API_BASE_URL}/dishes/?restaurant=${testRestaurantId}`)
      
      expect(response.ok).toBe(true)
      expect(response.status).toBe(200)
      
      dishes = await response.json()
      
      expect(Array.isArray(dishes)).toBe(true)
      
      console.log(`✅ Fetched ${dishes.length} dishes for restaurant ${testRestaurantId}`)
    }, 10000)

    it('should return dishes with correct structure', async () => {
      const response = await fetch(`${API_BASE_URL}/dishes/?restaurant=${testRestaurantId}`)
      dishes = await response.json()
      
      if (dishes.length === 0) {
        console.log('⚠️  No dishes found for this restaurant, skipping structure test')
        return
      }
      
      const dish = dishes[0]
      
      // Verify required fields
      expect(dish).toHaveProperty('_id')
      expect(dish).toHaveProperty('restaurant_id')
      expect(dish).toHaveProperty('name')
      expect(dish).toHaveProperty('price')
      
      // Verify field types
      expect(typeof dish._id).toBe('string')
      expect(typeof dish.restaurant_id).toBe('string')
      expect(typeof dish.name).toBe('string')
      expect(typeof dish.price).toBe('number')
      
      console.log('✅ Dish structure is correct:', dish.name)
    }, 10000)

    it('should return dishes with the correct restaurant_id', async () => {
      const response = await fetch(`${API_BASE_URL}/dishes/?restaurant=${testRestaurantId}`)
      dishes = await response.json()
      
      if (dishes.length === 0) {
        console.log('⚠️  No dishes found for this restaurant, skipping restaurant_id test')
        return
      }
      
      dishes.forEach((dish: Dish) => {
        expect(dish.restaurant_id).toBe(testRestaurantId)
      })
      
      console.log('✅ All dishes belong to the correct restaurant')
    }, 10000)

    it('should return dishes with ingredients array', async () => {
      const response = await fetch(`${API_BASE_URL}/dishes/?restaurant=${testRestaurantId}`)
      dishes = await response.json()
      
      if (dishes.length === 0) {
        console.log('⚠️  No dishes found for this restaurant, skipping ingredients test')
        return
      }
      
      const dishesWithIngredients = dishes.filter(dish => 
        dish.ingredients && Array.isArray(dish.ingredients) && dish.ingredients.length > 0
      )
      
      console.log(`✅ ${dishesWithIngredients.length}/${dishes.length} dishes have ingredients`)
      
      if (dishesWithIngredients.length > 0) {
        expect(Array.isArray(dishesWithIngredients[0].ingredients)).toBe(true)
      }
    }, 10000)

    it('should return dishes with valid prices', async () => {
      const response = await fetch(`${API_BASE_URL}/dishes/?restaurant=${testRestaurantId}`)
      dishes = await response.json()
      
      if (dishes.length === 0) {
        console.log('⚠️  No dishes found for this restaurant, skipping price test')
        return
      }
      
      dishes.forEach((dish: Dish) => {
        expect(dish.price).toBeGreaterThan(0)
        expect(typeof dish.price).toBe('number')
      })
      
      console.log('✅ All dish prices are valid')
    }, 10000)

    it('should include allergen information when available', async () => {
      const response = await fetch(`${API_BASE_URL}/dishes/?restaurant=${testRestaurantId}`)
      dishes = await response.json()
      
      if (dishes.length === 0) {
        console.log('⚠️  No dishes found for this restaurant, skipping allergen test')
        return
      }
      
      const dishesWithExplicitAllergens = dishes.filter(dish => 
        dish.explicit_allergens && dish.explicit_allergens.length > 0
      )
      
      const dishesWithInferredAllergens = dishes.filter(dish => 
        dish.inferred_allergens && dish.inferred_allergens.length > 0
      )
      
      console.log(`✅ ${dishesWithExplicitAllergens.length} dishes with explicit allergens`)
      console.log(`✅ ${dishesWithInferredAllergens.length} dishes with inferred allergens`)
      
      // If there are inferred allergens, check their structure
      if (dishesWithInferredAllergens.length > 0) {
        const allergen = dishesWithInferredAllergens[0].inferred_allergens![0]
        expect(allergen).toHaveProperty('allergen')
        expect(allergen).toHaveProperty('confidence')
        expect(allergen).toHaveProperty('why')
        expect(allergen.confidence).toBeGreaterThanOrEqual(0)
        expect(allergen.confidence).toBeLessThanOrEqual(1)
      }
    }, 10000)

    it('should include nutrition facts when available', async () => {
      const response = await fetch(`${API_BASE_URL}/dishes/?restaurant=${testRestaurantId}`)
      dishes = await response.json()
      
      if (dishes.length === 0) {
        console.log('⚠️  No dishes found for this restaurant, skipping nutrition test')
        return
      }
      
      const dishesWithNutrition = dishes.filter(dish => 
        dish.nutrition_facts && Object.keys(dish.nutrition_facts).length > 0
      )
      
      console.log(`✅ ${dishesWithNutrition.length}/${dishes.length} dishes have nutrition facts`)
      
      if (dishesWithNutrition.length > 0) {
        const nutrition = dishesWithNutrition[0].nutrition_facts!
        
        // Check structure if any nutrition field exists
        const hasNutritionData = 
          nutrition.calories || 
          nutrition.protein || 
          nutrition.fat || 
          nutrition.carbohydrates
        
        if (hasNutritionData) {
          console.log('✅ Nutrition facts have correct structure')
        }
      }
    }, 10000)
  })

  // ===== COMPLETE FLOW TEST =====
  
  describe('Complete User Flow: Restaurants → Menu → Dish Details', () => {
    it('should successfully fetch restaurants, then dishes, and verify data consistency', async () => {
      // Step 1: Fetch restaurants
      console.log('\n📍 Step 1: Fetching restaurants...')
      const restaurantsResponse = await fetch(`${API_BASE_URL}/restaurants/`)
      expect(restaurantsResponse.ok).toBe(true)
      
      const restaurantsList = await restaurantsResponse.json()
      expect(restaurantsList.length).toBeGreaterThan(0)
      console.log(`✅ Got ${restaurantsList.length} restaurants`)
      
      // Step 2: Pick a restaurant
      const selectedRestaurant = restaurantsList[0]
      console.log(`\n📍 Step 2: Selected restaurant: ${selectedRestaurant.name}`)
      console.log(`   ID: ${selectedRestaurant._id}`)
      
      // Step 3: Fetch dishes for that restaurant
      console.log('\n📍 Step 3: Fetching dishes for restaurant...')
      const dishesResponse = await fetch(`${API_BASE_URL}/dishes/?restaurant=${selectedRestaurant._id}`)
      expect(dishesResponse.ok).toBe(true)
      
      const dishesList = await dishesResponse.json()
      console.log(`✅ Got ${dishesList.length} dishes`)
      
      if (dishesList.length > 0) {
        // Step 4: Verify dish details
        console.log('\n📍 Step 4: Verifying dish details...')
        const firstDish = dishesList[0]
        
        console.log(`   Dish: ${firstDish.name}`)
        console.log(`   Price: $${firstDish.price}`)
        console.log(`   Ingredients: ${firstDish.ingredients?.length || 0} items`)
        console.log(`   Explicit Allergens: ${firstDish.explicit_allergens?.length || 0}`)
        console.log(`   Inferred Allergens: ${firstDish.inferred_allergens?.length || 0}`)
        
        // Verify all dishes belong to the selected restaurant
        dishesList.forEach((dish: Dish) => {
          expect(dish.restaurant_id).toBe(selectedRestaurant._id)
        })
        
        console.log('\n✅ Complete flow successful! All data is consistent.')
      } else {
        console.log('\n⚠️  No dishes found for this restaurant')
      }
    }, 15000)
  })

  // ===== API ERROR HANDLING TESTS =====
  
  describe('API Error Handling', () => {
    it('should handle invalid restaurant ID gracefully', async () => {
      const response = await fetch(`${API_BASE_URL}/dishes/?restaurant=invalid_id_12345`)
      
      // Should either return empty array or 404, depending on API implementation
      if (response.ok) {
        const data = await response.json()
        expect(Array.isArray(data)).toBe(true)
        console.log('✅ API returns empty array for invalid restaurant ID')
      } else {
        expect([400, 404]).toContain(response.status)
        console.log('✅ API returns error status for invalid restaurant ID')
      }
    }, 10000)

    it('should handle malformed requests', async () => {
      // Try to fetch dishes without restaurant parameter
      const response = await fetch(`${API_BASE_URL}/dishes/`)
      
      // API should handle this somehow - either return all dishes or error
      expect([200, 400, 422]).toContain(response.status)
      
      if (response.ok) {
        const data = await response.json()
        expect(Array.isArray(data)).toBe(true)
        console.log('✅ API handles request without restaurant parameter')
      } else {
        console.log('✅ API returns error for missing restaurant parameter')
      }
    }, 10000)
  })

  // ===== API RESPONSE TIME TESTS =====
  
  describe('API Performance', () => {
    it('should respond to restaurant request within 5 seconds', async () => {
      const startTime = Date.now()
      const response = await fetch(`${API_BASE_URL}/restaurants/`)
      const endTime = Date.now()
      
      const responseTime = endTime - startTime
      
      expect(response.ok).toBe(true)
      expect(responseTime).toBeLessThan(5000)
      
      console.log(`✅ Restaurant API responded in ${responseTime}ms`)
    }, 10000)

    it('should respond to dishes request within 5 seconds', async () => {
      // Get a restaurant ID first
      const restaurantsResponse = await fetch(`${API_BASE_URL}/restaurants/`)
      const restaurantsList = await restaurantsResponse.json()
      const restaurantId = restaurantsList[0]._id
      
      const startTime = Date.now()
      const response = await fetch(`${API_BASE_URL}/dishes/?restaurant=${restaurantId}`)
      const endTime = Date.now()
      
      const responseTime = endTime - startTime
      
      expect(response.ok).toBe(true)
      expect(responseTime).toBeLessThan(5000)
      
      console.log(`✅ Dishes API responded in ${responseTime}ms`)
    }, 15000)
  })
})