document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('btn-upload');
    const previewImage = document.getElementById('preview-image');
    const placeholder = document.getElementById('placeholder');
    const analyzeBtn = document.getElementById('btn-analyze');
    const btnJson = document.getElementById('btn-json');
    const btnClear = document.getElementById('btn-clear');
    const statusText = document.getElementById('status-text');
    const plotlyViewer = document.getElementById('plotly-viewer');
    const btnToggleResults = document.getElementById('btn-toggle-results');
    const analysisPanel = document.getElementById('analysis-panel');

    // Toggle Analysis Panel
    btnToggleResults.addEventListener('click', () => {
        analysisPanel.classList.toggle('show');
        btnToggleResults.classList.toggle('active');
        
        const isShowing = analysisPanel.classList.contains('show');
        const span = btnToggleResults.querySelector('span:not(.material-symbols-outlined)');
        span.textContent = isShowing ? 'Hide Data' : 'Show Data';
    });

    const analysisResults = document.getElementById('analysis-results');
    const analysisPlaceholder = document.querySelector('.analysis-placeholder');

    let currentFile = null;
    let currentInputType = null; // 'image' or 'json'


    // Upload button click
    uploadBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    // Dropzone click
    dropzone.addEventListener('click', () => fileInput.click());

    // Drag and drop events
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleImageFile(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleImageFile(e.target.files[0]);
        }
    });

    function handleImageFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file');
            return;
        }

        currentFile = file;
        currentInputType = 'image';
        
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewImage.hidden = false;
            placeholder.style.display = 'none';
            analyzeBtn.disabled = false;
            updateStatus('Image loaded - Ready to analyze', true);
        };
        reader.readAsDataURL(file);
    }

    // Clear button
    btnClear.addEventListener('click', () => {
        currentFile = null;
        currentInputType = null;
        previewImage.src = '';
        previewImage.hidden = true;
        placeholder.style.display = 'flex';
        analyzeBtn.disabled = true;
        fileInput.value = '';
        updateStatus('Ready', true);
        
        plotlyViewer.style.display = 'none';
        Plotly.purge(plotlyViewer);
        
        if (analysisResults) {
            analysisResults.hidden = true;
            analysisResults.innerHTML = '';
        }
        if (analysisPlaceholder) {
            analysisPlaceholder.style.display = 'flex';
        }
    });


    // JSON button - prompt for JSON input
    btnJson.addEventListener('click', async () => {
        const input = prompt('Paste your JSON data (rooms and walls array):');
        if (!input) return;
        
        try {
            const data = JSON.parse(input);
            
            if (!data.rooms || !data.walls) {
                alert('JSON must contain "rooms" and "walls" arrays');
                return;
            }
            
            currentFile = null;
            currentInputType = 'json';
            window.pendingJsonData = data;
            
            previewImage.hidden = true;
            placeholder.style.display = 'none';
            analyzeBtn.disabled = false;
            
            updateStatus('JSON data loaded - Ready to analyze', true);
            
        } catch (e) {
            alert('Invalid JSON format: ' + e.message);
        }
    });

    // Analyze button - calls the backend API
    analyzeBtn.addEventListener('click', async () => {
        if (!currentInputType) {
            alert('Please upload an image or load JSON data first');
            return;
        }

        analyzeBtn.classList.add('loading');
        analyzeBtn.disabled = true;
        updateStatus('Analyzing...', false);

        const icon = analyzeBtn.querySelector('.material-symbols-outlined');
        icon.textContent = 'sync';

        try {
            let response;
            
            if (currentInputType === 'image') {
                // Send as FormData
                const formData = new FormData();
                formData.append('file', currentFile);
                
                response = await fetch('http://localhost:5000/analyze', {
                    method: 'POST',
                    body: formData
                });
                
            } else if (currentInputType === 'json') {
                // Send as JSON
                const jsonData = window.pendingJsonData;
                
                response = await fetch('http://localhost:5000/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(jsonData)
                });
            }

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Analysis failed');
            }

            const result = await response.json();
            
            // Render 3D Plotly if present
            if (result.diagram) {
                const fig = JSON.parse(result.diagram);
                previewImage.hidden = true;
                plotlyViewer.style.display = 'block';
                Plotly.newPlot('plotly-viewer', fig.data, fig.layout, {responsive: true});
            }
            
            // Display results
            displayResults(result);
            
            updateStatus('Analysis complete', true);
            
        } catch (error) {
            console.error('Analysis error:', error);
            alert('Analysis failed: ' + error.message);
            updateStatus('Analysis failed', false);
        } finally {
            analyzeBtn.classList.remove('loading');
            analyzeBtn.disabled = false;
            icon.textContent = 'analytics';
        }
    });

    function displayResults(result) {
        if (!analysisResults || !analysisPlaceholder) return;
        
        analysisPlaceholder.style.display = 'none';
        analysisResults.hidden = false;
        
        let html = `
            <div class="results-header">
                <span class="data-summary">${result.rooms ? result.rooms.length : 0} active zones</span>
            </div>
            
            <div class="data-section">
                <h3 class="data-section-title">Rooms</h3>
        `;
        
        if (result.rooms && result.rooms.length > 0) {
            result.rooms.forEach((room, rIdx) => {
                const roomId = room.id;
                const roomScore = result.room_scores ? result.room_scores[roomId] : 0;
                
                let rRisk = 'Low'; let rColor = '#00D9A5';
                if (roomScore >= 80) { rRisk = 'High'; rColor = '#FF4757'; }
                else if (roomScore >= 50) { rRisk = 'Medium'; rColor = '#FFB800'; }
                else if (roomScore >= 30) { rRisk = 'Elevated'; rColor = '#FDE047'; }
                
                // Color indicator colors
                const colors = ['#6c5ce7', '#00d2ff', '#00D9A5', '#FFB800', '#FF4757'];
                const accent = colors[rIdx % colors.length];
                
                html += `
                    <div class="room-card">
                        <div class="room-header">
                            <div class="room-identity">
                                <span class="room-indicator" style="background: ${accent};"></span>
                                <span class="room-name">${room.name}</span>
                            </div>
                            <span class="risk-badge" style="color: ${rColor};">
                                ${rRisk} Risk
                            </span>
                        </div>
                `;
                
                const roomWalls = (result.results || []).filter(item => item.wall.room_id === roomId);
                
                if (roomWalls.length > 0) {
                    html += `<div class="walls-collection">`;
                    roomWalls.forEach((item, index) => {
                        const wall = item.wall;
                        const materialOptions = item.material_options || [];
                        const score = item.risk_score || 0;
                        
                        let riskColor = '#00D9A5';
                        if (score >= 80) riskColor = '#FF4757';
                        else if (score >= 50) riskColor = '#FFB800';
                        else if (score >= 30) riskColor = '#FDE047';
                        
                        const optionsHtml = materialOptions.slice(0, 3).map((opt, optIdx) => {
                            const rankClass = optIdx === 0 ? 'BEST' : optIdx === 1 ? '2nd' : '3rd';
                            const rankColor = optIdx === 0 ? '#00D9A5' : optIdx === 1 ? '#FFB800' : '#6c5ce7';
                            
                            return `
                                <div class="material-chip">
                                    <div class="chip-main">
                                        <span class="chip-rank" style="background: ${rankColor};">${rankClass}</span>
                                        <span class="chip-name" style="color: ${optIdx === 0 ? '#00D9A5' : 'white'};">${opt.name}</span>
                                    </div>
                                    <span class="chip-score">${opt.tradeoff_score || '-'}</span>
                                </div>
                            `;
                        }).join('');
                        
                        html += `
                            <div class="wall-interaction-item" style="border-left-color: ${riskColor}30;">
                                <div class="wall-item-header">
                                    <span class="wall-item-name">Wall ${wall.id || index + 1}</span>
                                    <span class="wall-item-score">Score: ${score}</span>
                                </div>
                                <div class="material-options-list">
                                    ${optionsHtml}
                                </div>
                            </div>
                        `;
                    });
                    html += `</div>`;
                }
                html += `</div>`;
            });
        }
        
        html += `</div>`; // Close data-section
        analysisResults.innerHTML = html;
    }

    function updateStatus(text, ready) {
        statusText.textContent = text;
        
        if (ready) {
            statusText.classList.add('ready');
        } else {
            statusText.classList.remove('ready');
        }
    }
});
