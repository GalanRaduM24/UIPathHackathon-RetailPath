// Panel management
function showPanel() {
    document.getElementById('street-panel').classList.add('active');
}

function hidePanel() {
    document.getElementById('street-panel').classList.remove('active');
}

function updatePanelContent(html) {
    document.getElementById('street-panel-content').innerHTML = html;
    showPanel();
}

function showLoading() {
    updatePanelContent(`
        <div class="loading">
            <div class="spinner"></div>
            <div>Extracting streets from OpenStreetMap...</div>
        </div>
    `);
}

function showError(message) {
    updatePanelContent(`
        <div class="placeholder">
            <div class="placeholder-icon">⚠️</div>
            <div>${message}</div>
        </div>
    `);
}

function displayStreets(streets) {
    if (!streets || streets.length === 0) {
        showError('No streets found in selected area');
        return;
    }

    let html = '';
    streets.forEach(street => {
        const parts = street.match(/^(.+?)\s*\((.+)\)$/);
        if (parts) {
            html += `
                <div class="street-item">
                    <div class="street-name">${parts[1]}</div>
                    <div class="street-range">${parts[2]}</div>
                </div>
            `;
        } else {
            html += `
                <div class="street-item">
                    <div class="street-name">${street}</div>
                </div>
            `;
        }
    });

    updatePanelContent(html);
}

// Real-time processing via Flask Backend
function processDrawnZone(geoJsonLayer) {
    showLoading();

    const geometry = geoJsonLayer.toGeoJSON().geometry;
    // console.log('Sending geometry to backend:', geometry);

    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ geometry: geometry }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
            } else {
                displayStreets(data.streets);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Failed to connect to analysis server. Make sure python app.py is running.');
        });
}

// Event handlers for button clicks
document.addEventListener('DOMContentLoaded', function () {
    const closeBtn = document.getElementById('close-btn');
    if (closeBtn) {
        closeBtn.addEventListener('click', hidePanel);
    }

    const copyBtn = document.getElementById('copy-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const content = document.getElementById('street-panel-content');
            const streetItems = content.querySelectorAll('.street-item');

            if (streetItems.length === 0) {
                alert('No streets to copy');
                return;
            }

            let text = 'Street Analysis Results:\n\n';
            streetItems.forEach(item => {
                const name = item.querySelector('.street-name').textContent;
                const range = item.querySelector('.street-range');
                if (range) {
                    text += `${name} (${range.textContent})\n`;
                } else {
                    text += `${name}\n`;
                }
            });

            navigator.clipboard.writeText(text).then(() => {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = '✓ Copied';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            }).catch(err => {
                alert('Failed to copy to clipboard');
            });
        });
    }
});

// Store current drawn layer for processing
let currentDrawnLayer = null;

// Function to find the Leaflet map object using multiple methods
function findLeafletMap() {
    // Method 1: Look for map in global window object (Folium pattern)
    for (let key in window) {
        if (key.startsWith('map_') && window[key] && window[key]._container) {
            console.log('✅ Found map via global variable:', key);
            return window[key];
        }
    }

    // Method 2: Get from DOM element
    const mapElement = document.querySelector('.folium-map');
    if (mapElement && mapElement._leaflet_id) {
        const map = window[mapElement._leaflet_id];
        if (map) {
            console.log('✅ Found map via DOM element:', mapElement._leaflet_id);
            return map;
        }
    }

    // Method 3: Search all Leaflet map instances
    if (window.L && window.L.Map) {
        const maps = [];
        for (let key in window) {
            try {
                if (window[key] instanceof L.Map) {
                    maps.push(window[key]);
                }
            } catch (e) { }
        }
        if (maps.length > 0) {
            console.log('✅ Found map via L.Map instance search');
            return maps[0];
        }
    }

    console.error('❌ Could not find Leaflet map using any method');
    return null;
}

// Listen for draw events - setup after DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Wait for Leaflet map to be available
    setTimeout(() => {
        const leafletMap = findLeafletMap();

        if (!leafletMap) {
            console.error('Could not access Leaflet map object');
            // Retry after more time
            setTimeout(() => {
                const retryMap = findLeafletMap();
                if (retryMap) {
                    setupDrawListeners(retryMap);
                } else {
                    console.error('Failed to find map after retry');
                }
            }, 2000);
            return;
        }

        setupDrawListeners(leafletMap);

    }, 1500);
});

// Setup all draw event listeners
function setupDrawListeners(leafletMap) {
    console.log('✅ Setting up draw event listeners...');

    // When a shape is drawn
    leafletMap.on('draw:created', function (e) {
        const layer = e.layer;
        currentDrawnLayer = layer;

        // Add the layer to the map
        leafletMap.addLayer(layer);
        // Remove any default popup that shows GeoJSON
        if (layer.unbindPopup) { layer.unbindPopup(); }

        // Add click handler to show "Extract Addresses" button
        layer.on('click', function () {
            showExtractButton(layer, leafletMap);
        });

        // REMOVED: Auto-show button hint
        // showPanelMessage('📌 Click the drawn shape to extract addresses');
    });

    // When a shape is edited
    leafletMap.on('draw:edited', function (e) {
        const layers = e.layers;
        layers.eachLayer(function (layer) {
            currentDrawnLayer = layer;
            layer.on('click', function () {
                showExtractButton(layer, leafletMap);
            });
        });
        // REMOVED: Auto-show button hint
    });

    // When a shape is deleted
    leafletMap.on('draw:deleted', function (e) {
        currentDrawnLayer = null;
        // Hide the Street Analysis panel when all shapes are deleted
        hidePanel();
    });

    // Function to show extract button in a popup
    function showExtractButton(layer, map) {
        const geometry = layer.toGeoJSON().geometry;
        const center = layer.getBounds().getCenter();

        // Create popup with Extract button
        const popupContent = `
            <div style="text-align: center; padding: 10px;">
                <button id="extract-btn" class="extract-btn" type="button">
                    📍 Extract Addresses
                </button>
            </div>
        `;

        const popup = L.popup({
            closeButton: true,
            autoClose: false,
            closeOnClick: false
        })
            .setLatLng(center)
            .setContent(popupContent)
            .openOn(map);

        // Add event listener after popup is added to DOM
        setTimeout(() => {
            const extractBtn = document.getElementById('extract-btn');
            if (extractBtn) {
                extractBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    processDrawnZone(layer);
                    popup.close();
                });
            }
        }, 100);
    }

    // Function to show message in panel without full activation
    function showPanelMessage(message) {
        updatePanelContent(`
            <div class="placeholder">
                <div class="placeholder-icon">💡</div>
                <div>${message}</div>
            </div>
        `);
    }
}
