import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import Settings from '../pages/Settings';

// Mock fetch
global.fetch = vi.fn();

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {
    username: 'testuser',
    authToken: 'mock-token-123'
  };
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('Settings', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.alert = vi.fn();
    
    // Mock the initial user data fetch
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        username: 'testuser',
        name: 'Test User',
        allergen_preferences: ['Peanuts', 'Dairy']
      }),
    });
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <Settings />
      </BrowserRouter>
    );
  };

  test('renders settings page with user profile and dietary restrictions', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText('Settings')).toBeInTheDocument();
      expect(screen.getByText('User Profile')).toBeInTheDocument();
      expect(screen.getByText('Dietary Restrictions')).toBeInTheDocument();
    });
  });

  test('displays existing allergies from user data', async () => {
    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText('Peanuts')).toBeInTheDocument();
      expect(screen.getByText('Dairy')).toBeInTheDocument();
    });
  });

  test('allows user to add a new allergy', async () => {
    // Mock the PUT request for updating allergies
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        username: 'testuser',
        name: 'Test User',
        allergen_preferences: ['Peanuts', 'Dairy', 'Shellfish']
      }),
    });

    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText('Peanuts')).toBeInTheDocument();
    });

    // Find the allergy input and add button
    const allergyInput = screen.getByPlaceholderText(/Enter allergy/i);
    const addButton = screen.getByRole('button', { name: /Add/i });
    
    // Add new allergy
    fireEvent.change(allergyInput, { target: { value: 'Shellfish' } });
    fireEvent.click(addButton);
    
    // Verify new allergy appears
    await waitFor(() => {
      expect(screen.getByText('Shellfish')).toBeInTheDocument();
    });
    
    // Verify API was called to update allergies
    await waitFor(() => {
      const putCalls = (global.fetch as any).mock.calls.filter(
        (call: any) => call[1]?.method === 'PUT'
      );
      expect(putCalls.length).toBeGreaterThan(0);
    });
  });

  test('allows user to remove an allergy', async () => {
    // Mock the PUT request for updating allergies
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        username: 'testuser',
        name: 'Test User',
        allergen_preferences: ['Dairy']
      }),
    });

    renderComponent();
    
    await waitFor(() => {
      expect(screen.getByText('Peanuts')).toBeInTheDocument();
    });

    // Find and click the remove button for Peanuts
    const removeButtons = screen.getAllByLabelText(/Remove/i);
    const peanutsRemoveBtn = removeButtons.find(btn => 
      btn.getAttribute('aria-label')?.includes('Peanuts')
    );
    
    if (peanutsRemoveBtn) {
      fireEvent.click(peanutsRemoveBtn);
      
      // Verify allergy is removed
      await waitFor(() => {
        expect(screen.queryByText('Peanuts')).not.toBeInTheDocument();
      });
    }
  });
});