import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Welcome from '../pages/Welcome'

// Mock the useNavigate hook
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('Welcome Component', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
  })

  it('renders the SafeBites logo and title', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText('SafeBites')).toBeInTheDocument()
    expect(screen.getByAltText('SafeBites Logo')).toBeInTheDocument()
  })

  it('renders the Sign Up button in header', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    const signUpButton = screen.getByRole('button', { name: /sign up/i })
    expect(signUpButton).toBeInTheDocument()
  })

  it('navigates to signup page when Sign Up button is clicked', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    const signUpButton = screen.getByRole('button', { name: /sign up/i })
    fireEvent.click(signUpButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/signup')
  })

  it('renders the hero section with search bar', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Find Restaurants Near You')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/enter street address or zip code/i)).toBeInTheDocument()
  })

  it('renders the search button with icon', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    const searchIcon = screen.getByAltText('Search')
    expect(searchIcon).toBeInTheDocument()
  })

  it('renders all three feature cards', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Eat Safely, Every Time')).toBeInTheDocument()
    expect(screen.getByText('Search Like You Talk')).toBeInTheDocument()
    expect(screen.getByText('Set It Once, Use It Forever')).toBeInTheDocument()
  })

  it('renders feature card descriptions', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText(/never worry about hidden allergens/i)).toBeInTheDocument()
    expect(screen.getByText(/forget complex filters/i)).toBeInTheDocument()
    expect(screen.getByText(/tell us your allergies/i)).toBeInTheDocument()
  })

  it('renders the About SafeBites section', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText('About SafeBites')).toBeInTheDocument()
    expect(screen.getByText(/dining out shouldn't be a guessing game/i)).toBeInTheDocument()
    expect(screen.getByText('Safe dining made simple.')).toBeInTheDocument()
  })

  it('renders the about section image', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    const aboutImage = screen.getByAltText('Food Allergy Items')
    expect(aboutImage).toBeInTheDocument()
  })

  it('renders footer with all columns', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Get to know us')).toBeInTheDocument()
    expect(screen.getByText('Useful links')).toBeInTheDocument()
    expect(screen.getByText('Doing Business')).toBeInTheDocument()
  })

  it('renders footer links', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText('About Us')).toBeInTheDocument()
    expect(screen.getByText('Help')).toBeInTheDocument()
    expect(screen.getByText('Add your restaurant')).toBeInTheDocument()
  })

  it('renders social media icons', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByAltText('Twitter')).toBeInTheDocument()
    expect(screen.getByAltText('Facebook')).toBeInTheDocument()
    expect(screen.getByAltText('Instagram')).toBeInTheDocument()
  })

  it('renders copyright text', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText('© 2025 SafeBites - Group 6')).toBeInTheDocument()
  })

  it('renders all feature icons', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByAltText('Allergen Protection')).toBeInTheDocument()
    expect(screen.getByAltText('AI Search')).toBeInTheDocument()
    expect(screen.getByAltText('Smart Filtering')).toBeInTheDocument()
  })

  it('search input accepts user input', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    const searchInput = screen.getByPlaceholderText(/enter street address or zip code/i) as HTMLInputElement
    fireEvent.change(searchInput, { target: { value: '27606' } })
    
    expect(searchInput.value).toBe('27606')
  })
})