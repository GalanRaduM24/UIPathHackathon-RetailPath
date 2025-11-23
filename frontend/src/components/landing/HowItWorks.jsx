import { motion } from 'framer-motion';
import { Search, Database, Brain, CheckCircle } from 'lucide-react';
import './HowItWorks.css';

const steps = [
    {
        icon: Search,
        number: '01',
        title: 'Explore the Map',
        description: 'Browse Bucharest and visualize key data layers including competitors, demographics, and traffic patterns.'
    },
    {
        icon: Database,
        number: '02',
        title: 'Analyze Data',
        description: 'Toggle different data layers to understand market dynamics, population density, and income distribution.'
    },
    {
        icon: Brain,
        number: '03',
        title: 'Test Strategies',
        description: 'Use our AI chatbot to simulate different business strategies and get personalized recommendations.'
    },
    {
        icon: CheckCircle,
        number: '04',
        title: 'Make Decisions',
        description: 'Choose the optimal location backed by comprehensive data analysis and AI-powered insights.'
    }
];

const HowItWorks = () => {
    return (
        <section id="how-it-works" className="how-it-works section">
            <div className="container">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="how-it-works-header"
                >
                    <h2 className="section-title">
                        How It <span className="gradient-text">Works</span>
                    </h2>
                    <p className="section-description">
                        Four simple steps to find your perfect retail location
                    </p>
                </motion.div>

                <div className="steps-container">
                    {steps.map((step, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.15, duration: 0.6 }}
                            className="step-card"
                        >
                            <div className="step-number">{step.number}</div>
                            <div className="step-icon-wrapper">
                                <div className="step-icon glass">
                                    <step.icon size={32} color="#f97316" />
                                </div>
                            </div>
                            <div className="step-content">
                                <h3 className="step-title">{step.title}</h3>
                                <p className="step-description">{step.description}</p>
                            </div>
                            {index < steps.length - 1 && (
                                <div className="step-connector"></div>
                            )}
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default HowItWorks;
