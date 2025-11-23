import Navbar from '../components/shared/Navbar';
import Hero from '../components/landing/Hero';
import Features from '../components/landing/Features';
import HowItWorks from '../components/landing/HowItWorks';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
    return (
        <div className="landing-page">
            <Navbar />
            <Hero />
            <Features />
            <HowItWorks />

            {/* CTA Section */}
            <section className="cta-section section">
                <div className="container">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className="cta-card glass-strong"
                    >
                        <h2 className="cta-title">
                            Ready to Find Your
                            <br />
                            <span className="gradient-text">Perfect Location?</span>
                        </h2>
                        <p className="cta-description">
                            Start exploring Bucharest with our powerful location intelligence platform
                        </p>
                        <Link to="/map" className="btn btn-primary btn-large">
                            Launch Platform
                            <ArrowRight size={20} />
                        </Link>
                    </motion.div>
                </div>
            </section>

            {/* Footer */}
            <footer className="footer">
                <div className="container">
                    <div className="footer-content">
                        <div className="footer-brand">
                            <div className="footer-logo">
                                <span className="logo-text">
                                    <span className="gradient-text">Retail</span>Path
                                </span>
                            </div>
                            <p className="footer-tagline">
                                AI-powered location intelligence for retail success
                            </p>
                        </div>
                        <div className="footer-links">
                            <div className="footer-column">
                                <h4>Product</h4>
                                <a href="#features">Features</a>
                                <a href="#how-it-works">How It Works</a>
                                <Link to="/map">Platform</Link>
                            </div>
                            <div className="footer-column">
                                <h4>Company</h4>
                                <a href="#about">About</a>
                                <a href="#contact">Contact</a>
                                <a href="#privacy">Privacy</a>
                            </div>
                        </div>
                    </div>
                    <div className="footer-bottom">
                        <p>&copy; 2025 RetailPath. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
