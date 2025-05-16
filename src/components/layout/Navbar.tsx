import { useState } from 'react';
import { Menu, X, Star, BookOpen } from 'lucide-react';
import Container from '../ui/Container';

interface NavbarProps {
  scrolled: boolean;
}

const Navbar: React.FC<NavbarProps> = ({ scrolled }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <header 
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-white shadow-md py-3' : 'bg-transparent py-5'
      }`}
    >
      <Container>
        <nav className="flex items-center justify-between">
          <div className="flex items-center">
            <Star className="h-8 w-8 text-blue-500 mr-2" />
            <span className="text-2xl font-bold text-blue-900">PathToJudaism</span>
          </div>

          {/* Desktop Navigation */}
          <ul className="hidden md:flex space-x-8">
            {['Home', 'About', 'Resources', 'Testimonials', 'Events', 'FAQ', 'Contact'].map((item) => (
              <li key={item}>
                <a 
                  href={`#${item.toLowerCase()}`} 
                  className={`font-medium transition-colors hover:text-blue-600 ${
                    scrolled ? 'text-gray-800' : 'text-gray-800'
                  }`}
                >
                  {item}
                </a>
              </li>
            ))}
          </ul>

          {/* CTA Button */}
          <div className="hidden md:block">
            <a 
              href="#contact" 
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-5 rounded-md transition-all hover:shadow-lg flex items-center"
            >
              <BookOpen className="h-4 w-4 mr-2" />
              Start Journey
            </a>
          </div>

          {/* Mobile menu button */}
          <button 
            className="md:hidden text-gray-800" 
            onClick={toggleMenu}
            aria-label="Toggle menu"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </nav>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden bg-white absolute top-full left-0 right-0 shadow-md">
            <ul className="py-4">
              {['Home', 'About', 'Resources', 'Testimonials', 'Events', 'FAQ', 'Contact'].map((item) => (
                <li key={item}>
                  <a 
                    href={`#${item.toLowerCase()}`} 
                    className="block py-3 px-6 text-gray-800 hover:bg-blue-50 hover:text-blue-600"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {item}
                  </a>
                </li>
              ))}
              <li className="px-6 py-3">
                <a 
                  href="#contact" 
                  className="block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md text-center transition-all hover:shadow-lg"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Start Your Journey
                </a>
              </li>
            </ul>
          </div>
        )}
      </Container>
    </header>
  );
};

export default Navbar;