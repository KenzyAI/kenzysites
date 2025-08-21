import { render, screen } from '@testing-library/react'
import Home from '@/app/page'

describe('Home Page', () => {
  it('renders the main heading', () => {
    render(<Home />)

    const heading = screen.getByRole('heading', {
      name: /wordpress ai builder/i,
    })

    expect(heading).toBeInTheDocument()
  })

  it('renders the description', () => {
    render(<Home />)

    const description = screen.getByText(
      /plataforma saas para criação de sites wordpress com inteligência artificial/i
    )

    expect(description).toBeInTheDocument()
  })
})
