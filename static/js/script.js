/**
 * Image Sharpness Comparison Web Application
 * Frontend JavaScript Logic
 */

// Global state
const state = {
    image1: {
        file: null,
        filepath: null,
        canvas: null,
        context: null,
        originalImage: null,
        region: null,
        isDrawing: false,
        startX: 0,
        startY: 0,
        drawHandlers: { down: null, move: null, up: null, leave: null }
    },
    image2: {
        file: null,
        filepath: null,
        canvas: null,
        context: null,
        originalImage: null,
        region: null,
        isDrawing: false,
        startX: 0,
        startY: 0,
        drawHandlers: { down: null, move: null, up: null, leave: null }
    },
    metrics: [],
    selectedMetrics: [],
    comparisonChart: null
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    initializeUI();
    await loadMetrics();
    setupTabNavigation();
});

// Initialize UI elements
function initializeUI() {
    // Image 1
    setupImageSection(1);
    
    // Image 2
    setupImageSection(2);
    
    // Compare button
    document.getElementById('compareBtn').addEventListener('click', compareImages);
}

// Setup image section (1 or 2)
function setupImageSection(imageNum) {
    const section = state[`image${imageNum}`];
    const uploadAreaId = `uploadArea${imageNum}`;
    const imageInputId = `imageInput${imageNum}`;
    const canvasId = `canvas${imageNum}`;
    const drawToggleId = `drawMode${imageNum}`;
    const clearRegionId = `clearRegion${imageNum}`;
    
    const uploadArea = document.getElementById(uploadAreaId);
    const imageInput = document.getElementById(imageInputId);
    const canvas = document.getElementById(canvasId);
    
    section.canvas = canvas;
    section.context = canvas.getContext('2d');
    
    // Upload area click
    uploadArea.addEventListener('click', () => imageInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleImageUpload(imageNum, files[0]);
        }
    });
    
    // File input change
    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleImageUpload(imageNum, e.target.files[0]);
        }
    });
    
    // Draw mode toggle
    document.getElementById(drawToggleId).addEventListener('change', (e) => {
        const isDrawing = e.target.checked;
        canvas.style.cursor = isDrawing ? 'crosshair' : 'default';
        
        if (isDrawing) {
            // Create and store handlers
            const section = state[`image${imageNum}`];
            section.drawHandlers.down = (e) => startDrawing(imageNum, e);
            section.drawHandlers.move = (e) => drawRectangle(imageNum, e);
            section.drawHandlers.up = (e) => endDrawing(imageNum, e);
            section.drawHandlers.leave = (e) => endDrawing(imageNum, e);
            
            // Add listeners
            canvas.addEventListener('mousedown', section.drawHandlers.down);
            canvas.addEventListener('mousemove', section.drawHandlers.move);
            canvas.addEventListener('mouseup', section.drawHandlers.up);
            canvas.addEventListener('mouseleave', section.drawHandlers.leave);
        } else {
            // Remove listeners
            const section = state[`image${imageNum}`];
            if (section.drawHandlers.down) {
                canvas.removeEventListener('mousedown', section.drawHandlers.down);
                canvas.removeEventListener('mousemove', section.drawHandlers.move);
                canvas.removeEventListener('mouseup', section.drawHandlers.up);
                canvas.removeEventListener('mouseleave', section.drawHandlers.leave);
            }
        }
    });
    
    // Clear region button
    document.getElementById(clearRegionId).addEventListener('click', () => {
        section.region = null;
        drawImage(imageNum);
        updateMinimap(imageNum);
        document.getElementById(`regionInfo${imageNum}`).textContent = 'Region: None';
    });
}

// Load available metrics from backend
async function loadMetrics() {
    try {
        const response = await fetch('/api/metrics');
        const metricsData = await response.json();
        
        state.metrics = metricsData;
        
        // Populate each tab with metrics
        Object.entries(metricsData).forEach(([category, categoryMetrics]) => {
            const containerId = `metricsContainer-${category}`;
            const container = document.getElementById(containerId);
            
            if (!container) return;
            
            const metricsGrid = container;
            metricsGrid.innerHTML = '';
            
            // Add metrics in this category
            Object.entries(categoryMetrics).forEach(([metricKey, metricInfo]) => {
                const fullMetricName = `${category}.${metricKey}`;
                
                const div = document.createElement('div');
                div.className = 'metric-item';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `metric-${fullMetricName}`;
                checkbox.value = fullMetricName;
                checkbox.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        state.selectedMetrics.push(fullMetricName);
                    } else {
                        state.selectedMetrics = state.selectedMetrics.filter(m => m !== fullMetricName);
                    }
                });
                
                const label = document.createElement('label');
                label.htmlFor = `metric-${fullMetricName}`;
                label.style.flex = '1';
                label.style.cursor = 'pointer';
                
                const name = document.createElement('div');
                name.className = 'metric-name';
                name.textContent = metricInfo.name;
                
                const desc = document.createElement('div');
                desc.className = 'metric-description';
                desc.textContent = metricInfo.description;
                
                label.appendChild(name);
                label.appendChild(desc);
                
                div.appendChild(checkbox);
                div.appendChild(label);
                
                metricsGrid.appendChild(div);
            });
        });
    } catch (error) {
        showError('Failed to load metrics: ' + error.message);
    }
}

// Setup tab navigation
function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const tabContent = document.getElementById(`tab-${tabName}`);
            if (tabContent) {
                tabContent.classList.add('active');
            }
        });
    });
}

// Handle image upload
async function handleImageUpload(imageNum, file) {
    try {
        const formData = new FormData();
        formData.append('image', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        // Update state
        const section = state[`image${imageNum}`];
        section.file = file;
        section.filepath = data.filepath;
        
        // Create image object
        const img = new Image();
        img.onload = () => {
            section.originalImage = img;
            
            // Set canvas size as attributes (not CSS)
            section.canvas.width = img.width;
            section.canvas.height = img.height;
            
            drawImage(imageNum);
            
            // Show image container and tools
            const container = document.getElementById(`imageContainer${imageNum}`);
            container.style.display = 'block';
            document.getElementById(`tools${imageNum}`).style.display = 'flex';
            
            // Show minimap
            document.getElementById(`minimapContainer${imageNum}`).style.display = 'block';
            updateMinimap(imageNum);
            
            // Setup minimap scroll sync
            const scrollContainer = container;
            scrollContainer.addEventListener('scroll', () => {
                updateMinimap(imageNum);
            });
            
            // Update dimension info
            document.getElementById(`dimension${imageNum}`).textContent = 
                `Dimensions: ${img.width} × ${img.height}px`;
        };
        
        img.src = data.image;
        
    } catch (error) {
        showError('Upload error: ' + error.message);
    }
}

// Draw image on canvas
function drawImage(imageNum) {
    const section = state[`image${imageNum}`];
    if (!section || !section.originalImage) return;
    
    const ctx = section.context;
    const img = section.originalImage;
    
    // Clear canvas
    ctx.fillStyle = '#f8f9fa';
    ctx.fillRect(0, 0, section.canvas.width, section.canvas.height);
    
    // Draw image
    ctx.drawImage(img, 0, 0);
    
    // Draw region if exists
    if (section.region) {
        ctx.strokeStyle = '#3498db';
        ctx.lineWidth = 2;
        ctx.strokeRect(section.region.x, section.region.y, 
                      section.region.width, section.region.height);
        
        // Fill with semi-transparent blue
        ctx.fillStyle = 'rgba(52, 152, 219, 0.1)';
        ctx.fillRect(section.region.x, section.region.y, 
                    section.region.width, section.region.height);
    }
}

// Helper function to get correct mouse position on canvas
function getMousePosOnCanvas(imageNum, e) {
    const section = state[`image${imageNum}`];
    const canvas = section.canvas;
    
    // Get canvas position relative to viewport
    // getBoundingClientRect() already accounts for scroll position
    const canvasRect = canvas.getBoundingClientRect();
    
    // Get mouse position relative to canvas
    // No need to add scrollLeft/scrollTop because canvasRect.left/top already includes scroll offset
    const canvasX = e.clientX - canvasRect.left;
    const canvasY = e.clientY - canvasRect.top;
    
    // Ensure within canvas bounds
    return {
        x: Math.max(0, Math.min(canvasX, canvas.width)),
        y: Math.max(0, Math.min(canvasY, canvas.height))
    };
}

// Start drawing region
function startDrawing(imageNum, e) {
    const section = state[`image${imageNum}`];
    const canvas = section.canvas;
    
    // Only start if clicking on canvas area
    if (!canvas || !section.originalImage) return;
    
    const pos = getMousePosOnCanvas(imageNum, e);
    section.isDrawing = true;
    section.startX = pos.x;
    section.startY = pos.y;
}

// Draw rectangle while dragging
function drawRectangle(imageNum, e) {
    const section = state[`image${imageNum}`];
    if (!section.isDrawing) return;
    
    const pos = getMousePosOnCanvas(imageNum, e);
    
    // Redraw image
    drawImage(imageNum);
    
    // Draw temporary rectangle
    const ctx = section.context;
    ctx.strokeStyle = '#ff6b6b';
    ctx.lineWidth = 3;
    ctx.setLineDash([5, 5]);
    
    const x = Math.min(section.startX, pos.x);
    const y = Math.min(section.startY, pos.y);
    const width = Math.abs(pos.x - section.startX);
    const height = Math.abs(pos.y - section.startY);
    
    ctx.strokeRect(x, y, width, height);
    ctx.setLineDash([]);
    
    // Draw semi-transparent fill
    ctx.fillStyle = 'rgba(255, 107, 107, 0.1)';
    ctx.fillRect(x, y, width, height);
}

// End drawing region
function endDrawing(imageNum, e) {
    const section = state[`image${imageNum}`];
    if (!section.isDrawing) return;
    
    section.isDrawing = false;
    
    const pos = getMousePosOnCanvas(imageNum, e);
    
    const x = Math.min(section.startX, pos.x);
    const y = Math.min(section.startY, pos.y);
    const width = Math.abs(pos.x - section.startX);
    const height = Math.abs(pos.y - section.startY);
    
    if (width > 10 && height > 10) {
        section.region = { x, y, width, height };
        document.getElementById(`regionInfo${imageNum}`).textContent = 
            `Region: ${Math.round(x)}, ${Math.round(y)} | ${Math.round(width)}×${Math.round(height)}px`;
    }
    
    drawImage(imageNum);
    updateMinimap(imageNum);
    
    // Uncheck draw mode
    document.getElementById(`drawMode${imageNum}`).checked = false;
    const canvas = section.canvas;
    canvas.style.cursor = 'default';
}

// Compare images
async function compareImages() {
    try {
        // Validate inputs
        if (!state.image1.filepath || !state.image2.filepath) {
            showError('Please upload both images');
            return;
        }
        
        if (state.selectedMetrics.length === 0) {
            showError('Please select at least one metric');
            return;
        }
        
        // Disable compare button
        const compareBtn = document.getElementById('compareBtn');
        compareBtn.disabled = true;
        compareBtn.textContent = 'Comparing...';
        
        // Send comparison request
        const response = await fetch('/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image1: state.image1.filepath,
                image2: state.image2.filepath,
                metrics: state.selectedMetrics,
                region1: state.image1.region,
                region2: state.image2.region
            })
        });
        
        const result = await response.json();
        
        console.log('Comparison result:', result);
        console.log('Has rgb_histograms:', !!result.rgb_histograms);
        
        if (!result.success) {
            throw new Error(result.error);
        }
        
        // Display results
        displayResults(result);
        
    } catch (error) {
        showError('Comparison error: ' + error.message);
    } finally {
        const compareBtn = document.getElementById('compareBtn');
        compareBtn.disabled = false;
        compareBtn.textContent = 'Compare Sharpness';
    }
}

// Display comparison results
function displayResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    
    // Winner section
    const winnerSection = document.getElementById('winnerSection');
    if (result.winner === 'tie') {
        winnerSection.innerHTML = `
            <div class="winner-badge tie">🤝 Tie - Both images have similar sharpness</div>
        `;
    } else {
        const winnerImage = result.winner === 'image1' ? 'Image 1' : 'Image 2';
        const winnerScore = result.winner === 'image1' ? result.image1.combined : result.image2.combined;
        winnerSection.innerHTML = `
            <div class="winner-badge">🏆 ${winnerImage} is Sharper!</div>
            <div class="winner-detail">
                <strong>${winnerImage}</strong> is <strong>${result.difference.toFixed(1)}%</strong> sharper
            </div>
        `;
    }
    
    // Scores for image 1
    const scores1 = document.getElementById('scores1');
    scores1.innerHTML = formatScores(result.image1, result.winner === 'image1');
    
    // Scores for image 2
    const scores2 = document.getElementById('scores2');
    scores2.innerHTML = formatScores(result.image2, result.winner === 'image2');
    
    // Create comparison chart
    createComparisonChart(result);
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Format scores HTML
function formatScores(imageResult, isWinner) {
    let html = '';
    
    // Combined score
    if (imageResult.combined !== null) {
        const winnerClass = isWinner ? 'winner' : '';
        html += `
            <div class="score-item">
                <span class="score-name">📊 Overall</span>
                <span class="score-value ${winnerClass}">${imageResult.combined.toFixed(2)}</span>
            </div>
        `;
    }
    
    // Individual metric scores
    Object.entries(imageResult.scores).forEach(([metric, score]) => {
        if (score !== null) {
            // Parse category and metric name
            const [category, metricKey] = metric.split('.');
            let metricName = metric;
            
            if (state.metrics && state.metrics[category] && state.metrics[category][metricKey]) {
                metricName = state.metrics[category][metricKey].name;
            }
            
            html += `
                <div class="score-item">
                    <span class="score-name">📈 ${metricName}</span>
                    <span class="score-value">${score.toFixed(2)}</span>
                </div>
            `;
        }
    });
    
    return html;
}

// Create comparison chart
function createComparisonChart(result) {
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    
    const metricNames = state.selectedMetrics.map(m => {
        const [category, metricKey] = m.split('.');
        if (state.metrics && state.metrics[category] && state.metrics[category][metricKey]) {
            return state.metrics[category][metricKey].name;
        }
        return m;
    });
    
    const scores1 = state.selectedMetrics.map(m => result.image1.scores[m] || 0);
    const scores2 = state.selectedMetrics.map(m => result.image2.scores[m] || 0);
    
    // Destroy existing chart if it exists
    if (state.comparisonChart) {
        state.comparisonChart.destroy();
    }
    
    state.comparisonChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: metricNames,
            datasets: [
                {
                    label: 'Image 1',
                    data: scores1,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Image 2',
                    data: scores2,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.2)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                r: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // Display RGB histograms if available
    if (result.rgb_histograms) {
        drawRGBHistograms(result.rgb_histograms);
    }
}

// Draw RGB histograms
function drawRGBHistograms(rgbData) {
    console.log('Drawing RGB histograms:', rgbData);
    
    const histogramSection = document.getElementById('histogramSection');
    
    // Show histogram section
    histogramSection.style.display = 'block';
    
    // Delay drawing to ensure canvas is rendered
    setTimeout(() => {
        // Draw histograms for both images
        if (rgbData.image1) {
            console.log('Drawing histogram for image1');
            drawSingleRGBHistogram('rgbHistogramImage1', rgbData.image1);
        }
        
        if (rgbData.image2) {
            console.log('Drawing histogram for image2');
            drawSingleRGBHistogram('rgbHistogramImage2', rgbData.image2);
        }
    }, 100);
}

// Draw single RGB histogram on canvas
function drawSingleRGBHistogram(canvasId, histogramData) {
    console.log(`Drawing histogram for ${canvasId}:`, histogramData);
    
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas not found: ${canvasId}`);
        return;
    }
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error(`Cannot get context for ${canvasId}`);
        return;
    }
    
    // Set canvas dimensions - use fixed width if offsetWidth is 0
    let width = canvas.offsetWidth;
    if (width === 0) {
        width = 500; // fallback width
    }
    const height = 250;
    
    canvas.width = width;
    canvas.height = height;
    
    console.log(`Canvas size: ${width}x${height}`);
    
    const padding = 40;
    const graphWidth = width - padding * 2;
    const graphHeight = height - padding * 2;
    
    // Clear canvas
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, width, height);
    
    // Draw background grid
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 5; i++) {
        const y = padding + (graphHeight / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }
    
    // Colors for RGB channels
    const colors = {
        red: '#FF0000',
        green: '#00AA00',
        blue: '#0000FF'
    };
    
    const channels = ['red', 'green', 'blue'];
    
    // Find max histogram value for scaling
    let maxValue = 0;
    channels.forEach(channel => {
        if (histogramData[channel]) {
            const max = Math.max(...histogramData[channel]);
            maxValue = Math.max(maxValue, max);
            console.log(`  ${channel} max value: ${max}, array length: ${histogramData[channel].length}`);
        }
    });
    
    console.log(`Overall max value: ${maxValue}`);
    
    if (maxValue === 0) maxValue = 1;
    
    // Draw histogram for each channel as line graph
    channels.forEach((channel) => {
        if (!histogramData[channel]) {
            console.log(`  Skipping ${channel} - no data`);
            return;
        }
        
        const histogram = histogramData[channel];
        const binWidth = graphWidth / histogram.length;
        
        console.log(`  Drawing ${channel} with ${histogram.length} bins, binWidth=${binWidth}`);
        
        // Set line style
        ctx.strokeStyle = colors[channel];
        ctx.lineWidth = 2;
        ctx.globalAlpha = 0.8;
        
        // Draw line
        ctx.beginPath();
        
        for (let i = 0; i < histogram.length; i++) {
            const value = histogram[i];
            const x = padding + i * binWidth + binWidth / 2;
            const barHeight = (value / maxValue) * graphHeight;
            const y = height - padding - barHeight;
            
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        
        ctx.stroke();
        
        // Also draw filled area under line
        ctx.globalAlpha = 0.2;
        ctx.fillStyle = colors[channel];
        
        const lastValue = histogram[histogram.length - 1];
        const lastBarHeight = (lastValue / maxValue) * graphHeight;
        const lastY = height - padding - lastBarHeight;
        const lastX = padding + (histogram.length - 1) * binWidth + binWidth / 2;
        
        ctx.lineTo(lastX, height - padding);
        ctx.lineTo(padding + binWidth / 2, height - padding);
        ctx.fill();
        
        ctx.globalAlpha = 1;
    });
    
    // Draw axes
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(padding, padding);
    ctx.stroke();
    
    // Draw labels
    ctx.fillStyle = '#333';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    
    // X-axis labels
    ctx.textAlign = 'center';
    ctx.fillText('0', padding, height - padding + 20);
    ctx.fillText('128', padding + graphWidth / 2, height - padding + 20);
    ctx.fillText('255', width - padding, height - padding + 20);
    
    // X-axis title
    ctx.font = '12px Arial';
    ctx.fillText('Pixel Value', width / 2, height - 5);
    
    // Y-axis label
    ctx.textAlign = 'right';
    ctx.save();
    ctx.translate(12, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Frequency', 0, 0);
    ctx.restore();
    
    // Legend
    const legendY = padding / 2;
    ctx.font = 'bold 12px Arial';
    channels.forEach((channel, idx) => {
        ctx.fillStyle = colors[channel];
        ctx.fillRect(padding + idx * 80, legendY - 10, 12, 12);
        ctx.fillStyle = '#333';
        ctx.textAlign = 'left';
        ctx.fillText(channel.charAt(0).toUpperCase() + channel.slice(1), padding + idx * 80 + 18, legendY - 2);
    });
}


// Update minimap
function updateMinimap(imageNum) {
    const minimapId = `minimap${imageNum}`;
    const minimapCanvas = document.getElementById(minimapId);
    if (!minimapCanvas) return;
    
    const section = state[`image${imageNum}`];
    const container = document.getElementById(`imageContainer${imageNum}`);
    
    if (!section.originalImage) return;
    
    const ctx = minimapCanvas.getContext('2d');
    const MINIMAP_SIZE = 150;
    
    // Clear minimap
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, MINIMAP_SIZE, MINIMAP_SIZE);
    
    // Calculate scale
    const imgWidth = section.originalImage.width;
    const imgHeight = section.originalImage.height;
    const scaleX = MINIMAP_SIZE / imgWidth;
    const scaleY = MINIMAP_SIZE / imgHeight;
    const scale = Math.min(scaleX, scaleY);
    
    // Draw scaled image
    ctx.drawImage(
        section.originalImage,
        0, 0,
        imgWidth, imgHeight,
        0, 0,
        imgWidth * scale, imgHeight * scale
    );
    
    // Draw viewport indicator
    const viewportWidth = container.clientWidth;
    const viewportHeight = container.clientHeight;
    const scrollLeft = container.scrollLeft;
    const scrollTop = container.scrollTop;
    
    ctx.strokeStyle = '#ff6b6b';
    ctx.lineWidth = 2;
    ctx.strokeRect(
        scrollLeft * scale,
        scrollTop * scale,
        viewportWidth * scale,
        viewportHeight * scale
    );
    
    // Draw region if exists
    if (section.region) {
        ctx.strokeStyle = '#4ecdc4';
        ctx.lineWidth = 2;
        ctx.setLineDash([3, 3]);
        ctx.strokeRect(
            section.region.x * scale,
            section.region.y * scale,
            section.region.width * scale,
            section.region.height * scale
        );
        ctx.setLineDash([]);
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
    
    setTimeout(() => {
        errorDiv.classList.remove('show');
    }, 5000);
}
