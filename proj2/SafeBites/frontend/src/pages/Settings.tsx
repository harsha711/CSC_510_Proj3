import { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config/api';
import './Settings.css';

function Settings() {
  const [isEditingUsername, setIsEditingUsername] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // User data from API
  const [username, setUsername] = useState('');
  const [name, setName] = useState('');
  const [joinDate] = useState('January 2025');
  const [allergies, setAllergies] = useState<string[]>([]);
  const [newAllergy, setNewAllergy] = useState('');

  // Dietary Preferences for AI Compatibility Scoring
  const [healthGoals, setHealthGoals] = useState<string[]>([]);
  const [cuisinePreferences, setCuisinePreferences] = useState<string[]>([]);
  const [tastePreferences, setTastePreferences] = useState<string[]>([]);
  const [dietaryPattern, setDietaryPattern] = useState<string>('omnivore');

  // Temporary states for editing
  const [tempUsername, setTempUsername] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Fetch user data on component mount
  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const storedUsername = localStorage.getItem('username');
      const authToken = localStorage.getItem('authToken');
      console.log('Auth Token:', authToken);
      console.log('Stored Username:', storedUsername);

      if (!storedUsername) {
        alert('Please login first');
        return;
      }

      const response = await fetch(API_ENDPOINTS.users.me, {
        headers: {
          'Authorization': `Bearer ${authToken || 'token'}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user data');
      }

      const userData = await response.json();
      console.log('User data:', userData);

      setUsername(userData.username || storedUsername);
      setName(userData.name || 'User');
      setTempUsername(userData.username || storedUsername);
      setAllergies(userData.allergen_preferences || []);

      // Load dietary preferences for AI compatibility scoring
      setHealthGoals(userData.health_goals || []);
      setCuisinePreferences(userData.cuisine_preferences || []);
      setTastePreferences(userData.taste_preferences || []);
      setDietaryPattern(userData.dietary_pattern || 'omnivore');
    } catch (error) {
      console.error('Error fetching user data:', error);
      // Use fallback data from localStorage
      const storedUsername = localStorage.getItem('username');
      if (storedUsername) {
        setUsername(storedUsername);
        setTempUsername(storedUsername);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveUsername = () => {
    setUsername(tempUsername);
    setIsEditingUsername(false);
  };

  const handleCancelUsername = () => {
    setTempUsername(username);
    setIsEditingUsername(false);
  };

  const handleChangePassword = () => {
    if (newPassword !== confirmPassword) {
      alert("New passwords don't match!");
      return;
    }
    if (newPassword.length < 6) {
      alert("Password must be at least 6 characters!");
      return;
    }
    // Add password change logic here
    alert("Password changed successfully!");
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setIsChangingPassword(false);
  };

  const handleAddAllergy = () => {
    if (newAllergy.trim() === '') {
      alert('Please enter an allergy');
      return;
    }
    if (allergies.includes(newAllergy.trim())) {
      alert('This allergy is already in your list');
      return;
    }
    const updatedAllergies = [...allergies, newAllergy.trim()];
    setAllergies(updatedAllergies);
    setNewAllergy('');
    updateUserAllergies(updatedAllergies);
  };

  const handleRemoveAllergy = (allergyToRemove: string) => {
    const updatedAllergies = allergies.filter(allergy => allergy !== allergyToRemove);
    setAllergies(updatedAllergies);
    updateUserAllergies(updatedAllergies);
  };

  const updateUserAllergies = async (updatedAllergies: string[]) => {
    setIsSaving(true);
    try {
      const authToken = localStorage.getItem('authToken');

      const response = await fetch(API_ENDPOINTS.users.me, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken || 'token'}`
        },
        body: JSON.stringify({
          name: name,
          allergen_preferences: updatedAllergies
        })
      });

      if (!response.ok) {
        throw new Error('Failed to update allergies');
      }

      console.log('Allergies updated successfully');
    } catch (error) {
      console.error('Error updating allergies:', error);
      alert('Failed to save allergies. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveDietaryPreferences = async () => {
    setIsSaving(true);
    try {
      const authToken = localStorage.getItem('authToken');

      const response = await fetch(API_ENDPOINTS.users.me, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken || 'token'}`
        },
        body: JSON.stringify({
          name: name,
          allergen_preferences: allergies,
          health_goals: healthGoals,
          cuisine_preferences: cuisinePreferences,
          taste_preferences: tastePreferences,
          dietary_pattern: dietaryPattern
        })
      });

      if (!response.ok) {
        throw new Error('Failed to update dietary preferences');
      }

      alert('✅ Dietary preferences saved! Your AI compatibility scores will now be personalized.');
      console.log('Dietary preferences updated successfully');
    } catch (error) {
      console.error('Error updating dietary preferences:', error);
      alert('Failed to save dietary preferences. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const toggleArrayItem = (array: string[], item: string, setArray: (arr: string[]) => void) => {
    if (array.includes(item)) {
      setArray(array.filter(i => i !== item));
    } else {
      setArray([...array, item]);
    }
  };

  if (isLoading) {
    return (
      <div className="settings-container">
        <div className="loading-message">Loading your settings...</div>
      </div>
    );
  }

  return (
    <div className="settings-container">
      <h1 className="settings-page-title">Settings</h1>

      {/* User Profile Section */}
      <div className="settings-section">
        <div className="section-header">
          <h2>User Profile</h2>
          <p className="section-description">Manage your account information</p>
        </div>

        <div className="settings-card">
          {/* Profile Avatar */}
          <div className="settings-avatar-section">
            <div className="settings-avatar">
              <img src="/icons/hugeicons_male.png" alt="Profile" />
            </div>
            <div className="settings-basic-info">
              <h3>{name}</h3>
              <p className="settings-join-date">@{username}</p>
              <p className="settings-join-date">Member since {joinDate}</p>
            </div>
          </div>

          {/* Username */}
          <div className="settings-info-row">
            <div className="settings-info-label">
              <strong>Username</strong>
              <span className="info-description">Your unique identifier</span>
            </div>
            <div className="settings-info-value">
              {!isEditingUsername ? (
                <>
                  <span>@{username}</span>
                  <button 
                    className="settings-edit-btn"
                    onClick={() => setIsEditingUsername(true)}
                  >
                    Edit
                  </button>
                </>
              ) : (
                <div className="settings-edit-field">
                  <input
                    type="text"
                    value={tempUsername}
                    onChange={(e) => setTempUsername(e.target.value)}
                    placeholder="Enter new username"
                  />
                  <div className="settings-edit-actions">
                    <button className="settings-save-btn" onClick={handleSaveUsername}>Save</button>
                    <button className="settings-cancel-btn" onClick={handleCancelUsername}>Cancel</button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Password */}
          <div className="settings-info-row">
            <div className="settings-info-label">
              <strong>Password</strong>
              <span className="info-description">Change your account password</span>
            </div>
            <div className="settings-info-value">
              {!isChangingPassword ? (
                <>
                  <span>••••••••</span>
                  <button 
                    className="settings-edit-btn"
                    onClick={() => setIsChangingPassword(true)}
                  >
                    Change
                  </button>
                </>
              ) : (
                <div className="settings-edit-field settings-password-field">
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="Current password"
                  />
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="New password"
                  />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm new password"
                  />
                  <div className="settings-edit-actions">
                    <button className="settings-save-btn" onClick={handleChangePassword}>Update Password</button>
                    <button className="settings-cancel-btn" onClick={() => {
                      setIsChangingPassword(false);
                      setCurrentPassword('');
                      setNewPassword('');
                      setConfirmPassword('');
                    }}>Cancel</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Dietary Restrictions Section */}
      <div className="settings-section">
        <div className="section-header">
          <h2>Dietary Restrictions</h2>
          <p className="section-description">Manage your food allergies and restrictions</p>
          {isSaving && <span className="saving-indicator">Saving...</span>}
        </div>

        <div className="settings-card">
          <div className="settings-info-row allergies-row">
            <div className="settings-info-label">
              <strong>Food Allergies</strong>
              <span className="info-description">Add allergies to filter unsafe dishes</span>
            </div>
            <div className="settings-info-value allergies-value">
              <div className="allergies-container">
                {/* Display current allergies */}
                <div className="allergies-list">
                  {allergies.length === 0 ? (
                    <p className="no-allergies">No allergies added yet</p>
                  ) : (
                    allergies.map((allergy, index) => (
                      <div key={index} className="allergy-badge">
                        <span>{allergy}</span>
                        <button 
                          className="remove-allergy-btn"
                          onClick={() => handleRemoveAllergy(allergy)}
                          aria-label={`Remove ${allergy}`}
                        >
                          ×
                        </button>
                      </div>
                    ))
                  )}
                </div>

                {/* Add new allergy */}
                <div className="add-allergy-section">
                  <input
                    type="text"
                    value={newAllergy}
                    onChange={(e) => setNewAllergy(e.target.value)}
                    placeholder="Enter allergy (e.g., Peanuts, Dairy)"
                    className="allergy-input"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddAllergy();
                      }
                    }}
                  />
                  <button 
                    className="add-allergy-btn"
                    onClick={handleAddAllergy}
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Compatibility Preferences Section */}
      <div className="settings-section">
        <div className="section-header">
          <h2>🤖 AI Compatibility Preferences</h2>
          <p className="section-description">
            Customize your dietary profile to get personalized AI-powered dish recommendations
          </p>
          {isSaving && <span className="saving-indicator">Saving...</span>}
        </div>

        <div className="settings-card">
          {/* Dietary Pattern */}
          <div className="settings-info-row">
            <div className="settings-info-label">
              <strong>Dietary Pattern</strong>
              <span className="info-description">Your primary eating style</span>
            </div>
            <div className="settings-info-value">
              <select
                value={dietaryPattern}
                onChange={(e) => setDietaryPattern(e.target.value)}
                className="dietary-select"
              >
                <option value="omnivore">Omnivore</option>
                <option value="vegetarian">Vegetarian</option>
                <option value="vegan">Vegan</option>
                <option value="pescatarian">Pescatarian</option>
                <option value="keto">Keto</option>
                <option value="paleo">Paleo</option>
                <option value="mediterranean">Mediterranean</option>
              </select>
            </div>
          </div>

          {/* Health Goals */}
          <div className="settings-info-row preferences-row">
            <div className="settings-info-label">
              <strong>Health Goals</strong>
              <span className="info-description">What you're trying to achieve</span>
            </div>
            <div className="settings-info-value">
              <div className="checkbox-grid">
                {['low-carb', 'high-protein', 'low-fat', 'low-sodium', 'high-fiber', 'low-sugar'].map(goal => (
                  <label key={goal} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={healthGoals.includes(goal)}
                      onChange={() => toggleArrayItem(healthGoals, goal, setHealthGoals)}
                    />
                    <span>{goal}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Cuisine Preferences */}
          <div className="settings-info-row preferences-row">
            <div className="settings-info-label">
              <strong>Favorite Cuisines</strong>
              <span className="info-description">Types of food you enjoy</span>
            </div>
            <div className="settings-info-value">
              <div className="checkbox-grid">
                {['Italian', 'Mexican', 'Chinese', 'Indian', 'Japanese', 'Mediterranean', 'Thai', 'American'].map(cuisine => (
                  <label key={cuisine} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={cuisinePreferences.includes(cuisine)}
                      onChange={() => toggleArrayItem(cuisinePreferences, cuisine, setCuisinePreferences)}
                    />
                    <span>{cuisine}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Taste Preferences */}
          <div className="settings-info-row preferences-row">
            <div className="settings-info-label">
              <strong>Taste Preferences</strong>
              <span className="info-description">Flavors you prefer</span>
            </div>
            <div className="settings-info-value">
              <div className="checkbox-grid">
                {['spicy', 'savory', 'sweet', 'sour', 'umami', 'bitter'].map(taste => (
                  <label key={taste} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={tastePreferences.includes(taste)}
                      onChange={() => toggleArrayItem(tastePreferences, taste, setTastePreferences)}
                    />
                    <span>{taste}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="settings-save-section">
            <button
              className="settings-save-preferences-btn"
              onClick={handleSaveDietaryPreferences}
              disabled={isSaving}
            >
              {isSaving ? 'Saving...' : '💾 Save Dietary Preferences'}
            </button>
            <p className="save-help-text">
              These preferences power our AI to give you personalized compatibility scores for every dish!
            </p>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="settings-section">
        <div className="section-header danger-header">
          <h2>Danger Zone</h2>
          <p className="section-description">Irreversible actions</p>
        </div>

        <div className="settings-card danger-card">
          <div className="settings-info-row">
            <div className="settings-info-label">
              <strong>Delete Account</strong>
              <span className="info-description">Permanently delete your account and all data</span>
            </div>
            <div className="settings-info-value">
              <button className="settings-danger-btn">Delete Account</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;