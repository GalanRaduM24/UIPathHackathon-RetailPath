import { useState } from 'react';
import { Layers, MapPin, Users, DollarSign, Car, Eye, EyeOff } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './LayerControls.css';

const layersData = [
    {
        id: 'competitors',
        name: 'Competitors',
        icon: MapPin,
        color: '#f97316',
        description: 'View competitor locations'
    },
    {
        id: 'population',
        name: 'Population Density',
        icon: Users,
        color: '#3b82f6',
        description: 'See population distribution'
    },
    {
        id: 'income',
        name: 'Income Levels',
        icon: DollarSign,
        color: '#10b981',
        description: 'Analyze income data'
    },
    {
        id: 'traffic',
        name: 'Traffic Patterns',
        icon: Car,
        color: '#8b5cf6',
        description: 'View traffic flow'
    }
];

const LayerControls = () => {
    const [activeLayers, setActiveLayers] = useState(['competitors']);
    const [isExpanded, setIsExpanded] = useState(true);

    const toggleLayer = (layerId) => {
        setActiveLayers(prev =>
            prev.includes(layerId)
                ? prev.filter(id => id !== layerId)
                : [...prev, layerId]
        );
    };

    return (
        <div className="layer-controls glass">
            <div className="layer-controls-header" onClick={() => setIsExpanded(!isExpanded)}>
                <div className="header-left">
                    <Layers size={20} color="#f97316" />
                    <h3>Map Layers</h3>
                </div>
                <button className="toggle-btn">
                    {isExpanded ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
            </div>

            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="layer-controls-content"
                    >
                        {layersData.map((layer) => {
                            const isActive = activeLayers.includes(layer.id);
                            return (
                                <div
                                    key={layer.id}
                                    className={`layer-item ${isActive ? 'active' : ''}`}
                                    onClick={() => toggleLayer(layer.id)}
                                >
                                    <div className="layer-info">
                                        <div className="layer-icon" style={{ background: `${layer.color}20` }}>
                                            <layer.icon size={20} color={layer.color} />
                                        </div>
                                        <div className="layer-text">
                                            <div className="layer-name">{layer.name}</div>
                                            <div className="layer-description">{layer.description}</div>
                                        </div>
                                    </div>
                                    <div className={`layer-toggle ${isActive ? 'active' : ''}`}>
                                        <div className="toggle-slider"></div>
                                    </div>
                                </div>
                            );
                        })}
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="layer-legend">
                <div className="legend-title">Active Layers: {activeLayers.length}</div>
            </div>
        </div>
    );
};

export default LayerControls;
