import { motion } from 'framer-motion';
import { MapPin, TrendingUp, Users, BarChart3, Target, Zap } from 'lucide-react';
import './Features.css';

const featuresData = [
    {
        icon: MapPin,
        title: 'Competitor Analysis',
        description: 'Identify and analyze competitor locations to find strategic gaps and opportunities in the market.',
        color: '#f97316'
    },
    {
        icon: Users,
        title: 'Population Density',
        description: 'Access detailed demographic data to understand foot traffic potential and customer base.',
        color: '#fb923c'
    },
    {
        icon: TrendingUp,
        title: 'Income Analytics',
        description: 'Evaluate purchasing power and income levels to match your target market perfectly.',
        color: '#ea580c'
    },
    {
        icon: BarChart3,
        title: 'Traffic Patterns',
        description: 'Analyze real-time and historical traffic data to optimize location visibility and accessibility.',
        color: '#f97316'
    },
    {
        icon: Target,
        title: 'AI Strategy Testing',
        description: 'Test different business strategies with our AI chatbot before making real-world decisions.',
        color: '#fb923c'
    },
    {
        icon: Zap,
        title: 'Real-Time Insights',
        description: 'Get instant recommendations and insights powered by machine learning algorithms.',
        color: '#ea580c'
    }
];

const Features = () => {
    return (
        <section id="features" className="features section">
            <div className="container">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="features-header"
                >
                    <h2 className="section-title">
                        Powerful Features for
                        <br />
                        <span className="gradient-text">Data-Driven Decisions</span>
                    </h2>
                    <p className="section-description">
                        Everything you need to find and validate the perfect retail location in Bucharest
                    </p>
                </motion.div>

                <div className="features-grid">
                    {featuresData.map((feature, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1, duration: 0.5 }}
                            className="feature-card glass"
                            whileHover={{ y: -8, transition: { duration: 0.2 } }}
                        >
                            <div className="feature-icon" style={{ background: `linear-gradient(135deg, ${feature.color}20, ${feature.color}10)` }}>
                                <feature.icon size={28} color={feature.color} />
                            </div>
                            <h3 className="feature-title">{feature.title}</h3>
                            <p className="feature-description">{feature.description}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Features;
