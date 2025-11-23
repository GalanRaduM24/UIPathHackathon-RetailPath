import { motion } from 'framer-motion';
import { ArrowRight, MapPin } from 'lucide-react';
import { Link } from 'react-router-dom';
import './Hero.css';

const Hero = () => {
    return (
        <section className="hero">
            <div className="hero-background"></div>

            <div className="container">
                <div className="hero-content">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="hero-text"
                    >
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.2, duration: 0.6 }}
                            className="hero-badge"
                        >
                            <MapPin size={16} />
                            <span>AI-Powered Location Intelligence</span>
                        </motion.div>

                        <h1 className="hero-title">
                            Find the Perfect
                            <br />
                            <span className="gradient-text">Retail Location</span>
                            <br />
                            in Bucharest
                        </h1>

                        <p className="hero-description">
                            Make data-driven decisions for your retail business. Analyze competitors,
                            demographics, traffic patterns, and income levels to discover optimal
                            locations that maximize your success.
                        </p>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.4, duration: 0.6 }}
                            className="hero-cta"
                        >
                            <Link to="/map" className="btn btn-primary btn-large">
                                Start Exploring
                                <ArrowRight size={20} />
                            </Link>
                            <a href="#features" className="btn btn-secondary btn-large">
                                Learn More
                            </a>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.6, duration: 0.8 }}
                            className="hero-stats"
                        >
                            <div className="stat">
                                <div className="stat-value">500+</div>
                                <div className="stat-label">Data Points</div>
                            </div>
                            <div className="stat-divider"></div>
                            <div className="stat">
                                <div className="stat-value">95%</div>
                                <div className="stat-label">Accuracy</div>
                            </div>
                            <div className="stat-divider"></div>
                            <div className="stat">
                                <div className="stat-value">24/7</div>
                                <div className="stat-label">Analysis</div>
                            </div>
                        </motion.div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, x: 30 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3, duration: 0.8 }}
                        className="hero-visual"
                    >
                        <div className="floating-card card-1">
                            <div className="card-icon">📍</div>
                            <div className="card-text">
                                <div className="card-title">Prime Location</div>
                                <div className="card-subtitle">High Traffic Area</div>
                            </div>
                        </div>
                        <div className="floating-card card-2">
                            <div className="card-icon">📊</div>
                            <div className="card-text">
                                <div className="card-title">Market Analysis</div>
                                <div className="card-subtitle">Real-time Data</div>
                            </div>
                        </div>
                        <div className="floating-card card-3">
                            <div className="card-icon">🎯</div>
                            <div className="card-text">
                                <div className="card-title">Target Demographics</div>
                                <div className="card-subtitle">Perfect Match</div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
};

export default Hero;
