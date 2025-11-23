import Navbar from '../components/shared/Navbar';
import MapContainer from '../components/map/MapContainer';
import ChatbotSidebar from '../components/map/ChatbotSidebar';
import './MapPage.css';

const MapPage = () => {
    return (
        <div className="map-page">
            <Navbar />
            <div className="map-page-content">
                <div className="map-section">
                    <MapContainer />
                </div>
                <div className="chatbot-section">
                    <ChatbotSidebar />
                </div>
            </div>
        </div>
    );
};

export default MapPage;
