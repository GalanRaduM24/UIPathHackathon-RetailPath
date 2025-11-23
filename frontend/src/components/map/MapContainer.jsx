import { useState, useEffect } from 'react';
import './MapContainer.css';

const MapContainer = () => {
    const [mapLoaded, setMapLoaded] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Check if map data is available
        fetch('/api/map-data')
            .then(response => {
                if (response.ok) {
                    setMapLoaded(true);
                } else {
                    setError('Map data not available');
                }
            })
            .catch(err => {
                console.error('Error loading map:', err);
                setError('Failed to load map');
            });
    }, []);

    return (
        <div className="map-container">
            {/* Embedded Bucharest Map */}
            <div className="map-iframe-container">
                {error ? (
                    <div className="map-error">
                        <h3>Map Loading Error</h3>
                        <p>{error}</p>
                        <p className="error-hint">Make sure the Flask backend is running on port 5001</p>
                    </div>
                ) : mapLoaded ? (
                    <iframe
                        src="/api/map-data"
                        title="Bucharest Interactive Map"
                        className="bucharest-map-iframe"
                        style={{
                            width: '100%',
                            height: '100%',
                            border: 'none',
                            borderRadius: '12px'
                        }}
                    />
                ) : (
                    <div className="map-loading">
                        <div className="loading-spinner"></div>
                        <p>Loading Bucharest map...</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MapContainer;
