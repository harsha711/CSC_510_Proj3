import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Dashboard from '../pages/Dashboard'

// Mock the useNavigate hook
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('Dashboard Component', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
  })

  // Header Tests
  it('renders the SafeBites logo and title', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    expect(screen.getByText('SafeBites')).toBeInTheDocument()
    expect(screen.getByAltText('SafeBites Logo')).toBeInTheDocument()
  })

  it('renders the search bar in header', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    expect(screen.getByPlaceholderText('Search for dishes, restaurants...')).toBeInTheDocument()
    expect(screen.getByAltText('Search')).toBeInTheDocument()
  })

  it('renders the profile button', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const profileButton = screen.getByRole('button', { name: /profile/i })
    expect(profileButton).toBeInTheDocument()
  })

  // Profile Dropdown Tests
  it('toggles profile dropdown when profile button is clicked', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const profileButton = screen.getByRole('button', { name: /profile/i })
    
    // Initially closed
    expect(screen.queryByText('John Doe')).not.toBeInTheDocument()
    
    // Click to open
    fireEvent.click(profileButton)
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('@johndoe')).toBeInTheDocument()
    
    // Click to close
    fireEvent.click(profileButton)
    expect(screen.queryByText('John Doe')).not.toBeInTheDocument()
  })

  it('displays user information in profile dropdown', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const profileButton = screen.getByRole('button', { name: /profile/i })
    fireEvent.click(profileButton)
    
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('@johndoe')).toBeInTheDocument()
  })

  it('displays logout button in profile dropdown', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const profileButton = screen.getByRole('button', { name: /profile/i })
    fireEvent.click(profileButton)
    
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument()
  })

  it('navigates to login page when logout is clicked', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const profileButton = screen.getByRole('button', { name: /profile/i })
    fireEvent.click(profileButton)
    
    const logoutButton = screen.getByRole('button', { name: /logout/i })
    fireEvent.click(logoutButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/login')
  })

  // Sidebar Tests
  it('renders sidebar with all navigation items', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    // Use getAllByText for items that appear multiple times, or be more specific
    expect(screen.getByAltText('Home')).toBeInTheDocument()
    expect(screen.getByText('Search Chat')).toBeInTheDocument()
    expect(screen.getByText('Menu')).toBeInTheDocument()
    expect(screen.getByText('Dish')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('sidebar starts in open state', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    // Check that sidebar has 'open' class
    const sidebar = document.querySelector('.sidebar')
    expect(sidebar).toHaveClass('open')
  
    // Or check for close icon (only visible when open)
    expect(screen.getByText('✕')).toBeInTheDocument()
  })

  it('toggles sidebar open and closed', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const toggleButton = screen.getByText('✕')
    
    // Click to close
    fireEvent.click(toggleButton)
    
    // Sidebar should now show hamburger icon
    expect(screen.getByText('☰')).toBeInTheDocument()
    
    // Click to open again
    const hamburgerButton = screen.getByText('☰')
    fireEvent.click(hamburgerButton)
    
    // Should show close icon again
    expect(screen.getByText('✕')).toBeInTheDocument()
  })

  // Navigation Tests
  it('displays Home content by default', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    expect(screen.getByRole('heading', { name: /home/i })).toBeInTheDocument()
    expect(screen.getByText(/work in progress/i)).toBeInTheDocument()
  })

  it('navigates to Menu page when Menu button is clicked', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const menuButton = screen.getByText('Menu')
    fireEvent.click(menuButton)
    
    expect(screen.getByRole('heading', { name: /menu/i })).toBeInTheDocument()
  })

  it('navigates to Search Chat page when Search Chat button is clicked', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const searchChatButton = screen.getByText('Search Chat')
    fireEvent.click(searchChatButton)
    
    expect(screen.getByRole('heading', { name: /search chat/i })).toBeInTheDocument()
  })

  it('navigates to Dish page when Dish button is clicked', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const dishButton = screen.getByText('Dish')
    fireEvent.click(dishButton)
    
    expect(screen.getByRole('heading', { name: /dish/i })).toBeInTheDocument()
  })

  it('navigates to Settings page when Settings button is clicked', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const settingsButton = screen.getByText('Settings')
    fireEvent.click(settingsButton)
    
    expect(screen.getByRole('heading', { name: /settings/i })).toBeInTheDocument()
  })

  it('applies active class to current page button', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    // Find the Home button by its icon alt text, then get the button
    const homeButton = screen.getByAltText('Home').closest('button')
    expect(homeButton).toHaveClass('active')
  
    // Click Menu
    const menuButton = screen.getByText('Menu').closest('button')
    fireEvent.click(menuButton!)
  
    // Menu should now be active
    expect(menuButton).toHaveClass('active')
    // Home should no longer be active
    expect(homeButton).not.toHaveClass('active')
  })

  // Search Input Test
  it('search input accepts user input', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const searchInput = screen.getByPlaceholderText('Search for dishes, restaurants...') as HTMLInputElement
    fireEvent.change(searchInput, { target: { value: 'pizza' } })
    
    expect(searchInput.value).toBe('pizza')
  })

  it('renders main content area', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const mainContent = screen.getByRole('main')
    expect(mainContent).toBeInTheDocument()
  })
})