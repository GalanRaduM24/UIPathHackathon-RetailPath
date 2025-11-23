import { Link } from 'react-router-dom';
import { Menu, X, MapPin } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './Navbar.css';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  return (
    <nav className="navbar">
      <div className="container">
        <div className="navbar-content">
          {/* Logo */}
          <Link to="/" className="navbar-logo">
            <MapPin className="logo-icon" size={28} />
            <span className="logo-text">
              <span className="gradient-text">Retail</span>Path
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="navbar-links">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/map" className="nav-link">Platform</Link>
            <a href="#features" className="nav-link">Features</a>
            <a href="#how-it-works" className="nav-link">How It Works</a>
          </div>

          {/* CTA Button */}
          <Link to="/map" className="btn btn-primary navbar-cta">
            Get Started
          </Link>

          {/* Mobile Menu Button */}
          <button className="mobile-menu-btn" onClick={toggleMenu}>
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              className="mobile-menu"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Link to="/" className="mobile-nav-link" onClick={toggleMenu}>
                Home
              </Link>
              <Link to="/map" className="mobile-nav-link" onClick={toggleMenu}>
                Platform
              </Link>
              <a href="#features" className="mobile-nav-link" onClick={toggleMenu}>
                Features
              </a>
              <a href="#how-it-works" className="mobile-nav-link" onClick={toggleMenu}>
                How It Works
              </a>
              <Link to="/map" className="btn btn-primary" onClick={toggleMenu}>
                Get Started
              </Link>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  );
};

export default Navbar;
