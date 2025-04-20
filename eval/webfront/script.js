// script.js
document.addEventListener('DOMContentLoaded', function() {
    // --- DOM Elements ---
    const heatmapDiv = document.getElementById('heatmap');
    const loadingMessage = document.getElementById('loading-message');
    // Response Modal Elements
    const responseModal = document.getElementById('responseModal');
    const responseModalTitle = document.getElementById('modalTitle');
    const responseModalBody = document.getElementById('modalBody');
    const responseModalCloseBtn = responseModal.querySelector('.close-button');
    const viewToggleBtn = document.getElementById('viewToggleBtn');
    // View Mode Button
    const viewModeToggleBtn = document.getElementById('viewModeToggleBtn');
    // Filter Configuration Modal Elements
    const filterConfigModal = document.getElementById('filterConfigModal');
    const filterModalTypeContainer = document.getElementById('filterModalTypeContainer');
    const filterModalLabContainer = document.getElementById('filterModalLabContainer');
    const openFilterConfigBtn = document.getElementById('openFilterConfigBtn');
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    const filterConfigCloseBtns = filterConfigModal.querySelectorAll('.close-button, .close-button-alt');
    // Other Controls
    const sortSelect = document.getElementById('sortSelect');
    const controlsArea = document.getElementById('controls-area'); // For event delegation if needed

    // --- Global state ---
    let currentSortBy = 'average_score';
    let currentFilterTypes = []; // Store currently selected types
    let currentFilterLabs = [];  // Store currently selected labs
    let processedData = null; // Holds results from processInitialData { models, tasks, scores, criteriaDetails, modelAverages, uniqueTypes, uniqueLabs }
    let currentlyDisplayedModels = []; // Holds original model names in current filtered/sorted display order
    let currentViewMode = 'markdown'; // Track the current view mode: 'markdown' or 'code'
    let currentVisMode = 'heatmap'; // Track visualization mode: 'heatmap' or 'barchart'

    // --- Modal Controls ---
    function showModal(modalElement) { if (modalElement) modalElement.style.display = 'block'; }
    function hideModal(modalElement) { if (modalElement) modalElement.style.display = 'none'; }

    // Close Response Modal
    responseModalCloseBtn.onclick = () => hideModal(responseModal);
    // Close Filter Config Modal (using multiple close buttons)
    filterConfigCloseBtns.forEach(btn => btn.onclick = () => hideModal(filterConfigModal));

    // Close modals on outside click
    window.addEventListener('click', function(event) {
        if (event.target == responseModal) { hideModal(responseModal); }
        if (event.target == filterConfigModal) { hideModal(filterConfigModal); }
    });
    // --- End Modal Controls ---

    // --- Initial Data Loading and Checks ---
    loadingMessage.style.display = 'block';
    let dataValid = true;
    if (typeof allData === 'undefined' || allData === null || Object.keys(allData).length === 0) {
        displayError("Error: Summary data ('allData') is missing, empty, or invalid. Check 'data.js'.");
        dataValid = false;
    }
    if (typeof allResponses === 'undefined' || allResponses === null) {
        console.warn("Warning: Detailed response data ('allResponses') is not loaded. Check 'responses.js'. Modal popups will be limited.");
    }
    if (typeof modelInfo === 'undefined' || modelInfo === null) {
        console.warn("Warning: Model info data ('modelInfo') is not loaded. Check 'models.js'. Sorting and filtering by metadata will be limited.");
    }
    if (!dataValid) {
        loadingMessage.style.display = 'none'; // Hide loading if we stop early
        return;
    }
    // --- End Data Checks ---

    // --- Main Execution Flow ---
    try {
        // 1. Process Initial Data (also extracts filter options)
        processedData = processInitialData(allData, modelInfo); // Pass modelInfo here
        if (!processedData || !processedData.models || processedData.models.length === 0) {
             throw new Error("Initial data processing failed or resulted in no models/tasks.");
        }

        // 2. Populate Filter Checkboxes inside the Filter Modal
        populateFilterCheckboxes(filterModalTypeContainer, processedData.uniqueTypes, 'modal_type');
        populateFilterCheckboxes(filterModalLabContainer, processedData.uniqueLabs, 'modal_lab');

        // 3. Set initial filter state (all checked)
        updateCurrentFiltersFromModal(); // Read initial state from modal checkboxes

        // --- Setup Event Listeners ---
        // Sort Dropdown Change
        sortSelect.addEventListener('change', () => {
            currentSortBy = sortSelect.value;
            updateVisualization();
        });

        // Open Filter Modal Button
        openFilterConfigBtn.addEventListener('click', () => {
            // Ensure checkboxes reflect the current state before opening
            syncModalCheckboxesToState();
            showModal(filterConfigModal);
        });

        // Apply Filters Button (inside modal)
        applyFiltersBtn.addEventListener('click', () => {
            updateCurrentFiltersFromModal(); // Read selections from modal checkboxes
            hideModal(filterConfigModal);     // Close the modal
            updateVisualization();           // Re-render the visualization
        });

        // "Select All/None" Buttons (inside modal, using delegation on modal element)
        filterConfigModal.addEventListener('click', (event) => {
             const target = event.target;
             if (target.matches('.select-all-btn') || target.matches('.select-none-btn')) {
                 const optionsContainerId = target.getAttribute('data-target');
                 const optionsContainer = document.getElementById(optionsContainerId); // Find the specific container
                 if (optionsContainer) {
                     const checkState = target.matches('.select-all-btn');
                     optionsContainer.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = checkState);
                     // No need to update global state or visualization here, only on "Apply"
                 }
             }
        });

        // View Mode Toggle Button
        viewModeToggleBtn.addEventListener('click', function() {
            if (currentVisMode === 'heatmap') {
                currentVisMode = 'barchart';
                viewModeToggleBtn.textContent = 'Switch to Heatmap';
                viewModeToggleBtn.classList.add('active');
            } else {
                currentVisMode = 'heatmap';
                viewModeToggleBtn.textContent = 'Switch to Bar Chart';
                viewModeToggleBtn.classList.remove('active');
            }
            updateVisualization();
        });

        // Initial Visualization Render
        updateVisualization();

    } catch (error) {
        displayError(`An error occurred during setup: ${error.message}`);
        console.error("Setup error:", error);
    } finally {
        // loading message hidden inside updateVisualization's finally block
    }
    // --- End Main Execution Flow ---


    // --- Helper Functions ---

    /** Displays an error message in the heatmap area. */
    function displayError(message) {
         heatmapDiv.innerHTML = `<p style='color: red; text-align: center; padding: 20px;'>${message}</p>`;
         loadingMessage.style.display = 'none'; // Ensure loading is hidden
         console.error(message);
    }

    /** Escapes HTML special characters for code view */
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    /** Reads checkbox states FROM THE FILTER MODAL and updates global filter arrays. */
     function updateCurrentFiltersFromModal() {
         currentFilterTypes = Array.from(filterModalTypeContainer.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value);
         currentFilterLabs = Array.from(filterModalLabContainer.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value);
         console.log("Filters updated from modal - Types:", currentFilterTypes.length, "Labs:", currentFilterLabs.length);
     }

     /** Updates checkboxes in the modal TO MATCH the current global state. */
     function syncModalCheckboxesToState() {
        const typeSet = new Set(currentFilterTypes);
        const labSet = new Set(currentFilterLabs);
        // Ensure containers exist before querying
        if (filterModalTypeContainer) {
            filterModalTypeContainer.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = typeSet.has(cb.value));
        }
        if (filterModalLabContainer) {
            filterModalLabContainer.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = labSet.has(cb.value));
        }
     }

    /** Populates a container (inside filter modal) with checkboxes. */
    function populateFilterCheckboxes(container, optionsArray, prefix) {
        if (!container) { console.error("populateFilterCheckboxes: Container element not found."); return; }
        if (!optionsArray || optionsArray.length === 0) {
            container.innerHTML = '<span>No options available.</span>';
            return;
        }
        container.innerHTML = ''; // Clear existing
        optionsArray.sort((a, b) => a.localeCompare(b)); // Sort options alphabetically

        optionsArray.forEach(optionValue => {
             // Ensure optionValue is not null, undefined, or an empty string before creating elements
             if (optionValue != null && optionValue !== '') {
                 const div = document.createElement('div');
                 const checkbox = document.createElement('input');
                 const safeOptionValue = String(optionValue); // Ensure it's a string
                 // Create a unique and valid ID (replace common problematic characters)
                 const uniqueId = `${prefix}_${safeOptionValue.replace(/[^a-zA-Z0-9_-]/g, '_')}`;

                 checkbox.type = 'checkbox';
                 checkbox.id = uniqueId;
                 checkbox.value = safeOptionValue;
                 checkbox.name = `${prefix}_filter_modal`; // Group checkboxes logically
                 checkbox.checked = true; // Default to checked

                 const label = document.createElement('label');
                 label.htmlFor = checkbox.id;
                 label.textContent = safeOptionValue;

                 div.appendChild(checkbox);
                 div.appendChild(label);
                 container.appendChild(div);
             }
        });
    } // End populateFilterCheckboxes


    /** Main function to update the visualization based on current view mode */
    function updateVisualization() {
        if (currentVisMode === 'heatmap') {
            updateHeatmap();
        } else {
            updateBarChart();
        }
    }

    /** Main function to filter, sort, and update/render the bar chart. */
    function updateBarChart() {
        if (!processedData) { displayError("Cannot update chart: Processed data unavailable."); return; }
        loadingMessage.style.display = 'block'; // Show loading before processing

        try {
            // 1. Filter Models based on current selections from global state
            const filteredModels = filterModels(
                processedData.models,
                currentFilterTypes,
                currentFilterLabs,
                modelInfo
            );

            // Handle case where no models match filters
            if (filteredModels.length === 0) {
                heatmapDiv.innerHTML = "<p style='text-align: center; color: orange; padding: 20px;'>No models match the current filter criteria.</p>";
                loadingMessage.style.display = 'none'; // Hide loading
                currentlyDisplayedModels = []; // Reset displayed models
                return; // Stop if no models to display
            }

            // 2. Sort the Filtered Models
            const sortedFilteredModels = sortModels(
                filteredModels,
                currentSortBy,
                processedData.modelAverages,
                modelInfo
            );
            currentlyDisplayedModels = sortedFilteredModels; // Store current order for click handling

            // 3. Prepare bar chart data
            const barData = prepareBarChartData(sortedFilteredModels, modelInfo);
            
            // 4. Define Plotly Bar Chart
            const layout = {
                xaxis: {
                    title: '',
                    tickangle: -45,
                    automargin: true,
                    tickfont: { size: 10 },
                },
                yaxis: {
                    title: 'Average Score (%)',
                    range: [0, 100],
                    ticksuffix: '%'
                },
                legend: {
                    title: { text: 'Model Type' },
                    orientation: 'h',
                    x: 0.5,
                    y: 1.1,
                    xanchor: 'center',
                    yanchor: 'bottom',
                    bgcolor: 'rgba(255,255,255,0.6)'
                },
                margin: { l: 50, r: 20, t: 50, b: 120 },
                barmode: 'group',
                height: Math.max(600, filteredModels.length * 15 + 200), // Dynamic height based on model count
                plot_bgcolor: '#FFF',
                paper_bgcolor: '#FFF',
            };

            // 5. Render Bar Chart
            Plotly.react(heatmapDiv, barData, layout, { responsive: true, displaylogo: false })
                .catch(err => {
                    console.error("Bar chart rendering failed:", err);
                    displayError(`Bar chart rendering failed: ${err.message}`);
                })
                .finally(() => {
                    loadingMessage.style.display = 'none';
                });

        } catch (error) {
            displayError(`Failed to update bar chart: ${error.message}`);
            console.error("Update bar chart error:", error);
            loadingMessage.style.display = 'none';
        }
    } // End updateBarChart
    
    /** Prepares data for bar chart using model averages */
    function prepareBarChartData(sortedModels, modelInfoData) {
        const safeModelInfo = modelInfoData || {};
        
        // Prepare a single trace with all models
        const modelNames = [];
        const modelScores = [];
        const hoverTexts = [];
        const barColors = [];
        
        // Define color map for model types - use exact match for keys
        const colorMap = {
            'Flagship': 'rgb(220, 57, 18)',  // Red
            'flagship': 'rgb(220, 57, 18)',  // Red (lowercase variant)
            'Midrange': 'rgb(51, 160, 44)',  // Green
            'midrange': 'rgb(51, 160, 44)',  // Green (lowercase variant)
            'Reasoning': 'rgb(106, 61, 154)', // Purple
            'reasoning': 'rgb(106, 61, 154)'  // Purple (lowercase variant)
        };
        
        // Use default color for unknown types
        const defaultColor = 'rgb(128, 128, 128)'; // Gray
        
        // Track used model types for debugging
        const usedModelTypes = new Set();
        
        // Maintain original sort order from sortedModels
        sortedModels.forEach(modelName => {
            // Get model info, checking both modelInfo and safeModelInfo
            const info = safeModelInfo[modelName] || {};
            const avgData = processedData.modelAverages[modelName];
            const score = avgData?.average ?? null;
            
            // Skip models with no score
            if (score === null) return;
            
            // Use score as percentage (0-100 scale)
            const scorePercent = score * 100;
            
            // Get model type for color coding - check multiple possible property names
            let modelType = null;
            if (info.model_type) modelType = info.model_type;
            else if (info.modelType) modelType = info.modelType;
            else if (info.type) modelType = info.type;
            else modelType = 'Unknown';
            
            // Track model types for debugging
            usedModelTypes.add(modelType);
            
            // Add to arrays
            modelNames.push(modelName);
            modelScores.push(scorePercent);
            hoverTexts.push(`<b>${modelName}</b><br>Score: ${scorePercent.toFixed(1)}%<br>Type: ${modelType}<br>Lab: ${info.lab || 'Unknown'}`);
            
            // Use the color from colorMap or default color
            const barColor = colorMap[modelType] || defaultColor;
            barColors.push(barColor);
        });
        
        // Log the model types found (for debugging)
        console.log("Model types found:", Array.from(usedModelTypes));
        console.log("Sample colors:", barColors.slice(0, 5));
        
        // Create a single trace with all models
        return [{
            x: modelNames,
            y: modelScores,
            text: hoverTexts,
            hoverinfo: 'text',
            type: 'bar',
            marker: {
                color: barColors,
                line: {
                    width: 1,
                    color: 'rgba(0,0,0,0.3)'
                }
            }
        }];
    } // End prepareBarChartData

    /** Main function to filter, sort, and update/render the heatmap. */
    function updateHeatmap() {
        if (!processedData) { displayError("Cannot update heatmap: Processed data unavailable."); return; }
        loadingMessage.style.display = 'block'; // Show loading before processing

        try {
            // 1. Filter Models based on current selections from global state
            const filteredModels = filterModels(
                processedData.models,
                currentFilterTypes, // Pass array from global state
                currentFilterLabs,  // Pass array from global state
                modelInfo // Pass modelInfo for filtering
            );

            // Handle case where no models match filters
            if (filteredModels.length === 0) {
                heatmapDiv.innerHTML = "<p style='text-align: center; color: orange; padding: 20px;'>No models match the current filter criteria.</p>";
                loadingMessage.style.display = 'none'; // Hide loading
                currentlyDisplayedModels = []; // Reset displayed models
                return; // Stop if no models to display
            }

            // 2. Sort the Filtered Models
            const sortedFilteredModels = sortModels(
                filteredModels, // Sort the *filtered* list
                currentSortBy,
                processedData.modelAverages,
                modelInfo
            );
            currentlyDisplayedModels = sortedFilteredModels; // Store current order of *original* names for click handling

            // 3. Prepare Data for Plotly using the sorted+filtered list
            const { displayModels, zData, hoverText } = preparePlotlyData(
                sortedFilteredModels, // Pass the final list of models in the desired order
                processedData.tasks,
                processedData.scores,
                processedData.criteriaDetails
            );

             // 4. Add Average Score Column data (based on original averages data)
             const avgColumnLabel = 'Ø Average';
             const finalTasks = [...processedData.tasks, avgColumnLabel]; // Add column label
             const finalZData = zData.map((row, index) => {
                 const modelName = sortedFilteredModels[index];
                 return [...row, processedData.modelAverages[modelName]?.average ?? null];
             });
             const finalHoverText = hoverText.map((row, index) => {
                 const modelName = sortedFilteredModels[index];
                 const avgData = processedData.modelAverages[modelName];
                 const avgScore = avgData?.average ?? 'N/A';
                 const numTasks = avgData?.count ?? 0;
                 const avgHover = `<b>Model:</b> ${modelName}<br>Overall Average: ${avgScore === 'N/A' ? 'N/A' : avgScore.toFixed(3)}<br>(${numTasks} tasks evaluated)`;
                 return [...row, avgHover];
             });
             // --- End Add Average Score Column ---

            // 5. Define Plotly Trace and Layout
            const trace = {
                x: finalTasks,
                y: displayModels, // Use just model names for Y-axis labels
                z: finalZData,
                type: 'heatmap',
                hoverongaps: false,
                hovertext: finalHoverText, // Use hover text including the average column
                hoverinfo: 'text', // Crucial: use our custom hovertext
                colorscale: 'YlGnBu',
                reversescale: true,
                showscale: true,
                xgap: 1.5,
                ygap: 1.5,
                zmin: 0,
                zmax: 1,
                colorbar: { thickness: 15, len: 0.8, y: 0.5, ypad: 0, title: { text: 'Score', side: 'right' }, tickvals: [0, 0.2, 0.4, 0.6, 0.8, 1.0], ticktext: ['0.0', '0.2', '0.4', '0.6', '0.8', '1.0'] }
            };
            const layout = {
                xaxis: {
                    side: 'bottom', tickangle: -45, automargin: true, tickfont: { size: 10 },
                    showticklabels: true, ticks: 'outside', linewidth: 1, linecolor: '#444'
                },
                yaxis: {
                    side: 'left', automargin: true, tickfont: { size: 10 },
                    autorange: 'reversed', // Crucial for correct sort display (index 0 at top)
                    showticklabels: true, ticks: 'outside', linewidth: 1, linecolor: '#444',
                    type: 'category' // Explicitly set as category axis for Plotly
                },
                autosize: true, // Let plot resize with container
                margin: { l: 0, r: 0, b: 0, t: 0, pad: 4 }, // Use automargin primarily
                plot_bgcolor: '#FFF', // White background for plot area
                paper_bgcolor: '#FFF', // White background for surrounding paper
                annotations: [], // No annotations
                shapes: [], // No shapes
                height: Math.max(600, filteredModels.length * 18 + 150), // Dynamically adjust height
                // Configure the modebar position
                modebar: {
                    orientation: 'v' // Horizontal orientation
                }
            };

            // 6. Render/Update Plot using Plotly.react for efficiency
            // Pass the config object with displayModeBar: true (or default)
            Plotly.react(heatmapDiv, [trace], layout, { responsive: true, displaylogo: false })
                 .then(gd => { // gd is the graph div after plotting/reacting
                     // ** Removed calls to addYAxisLabelHovers **
                     setupClickHandler(); // Attach click handler for response modal
                     console.log("Heatmap updated successfully.");
                 })
                 .catch(err => {
                     console.error("Plotly rendering/update failed:", err);
                     displayError(`Plotly rendering failed: ${err.message}`);
                 })
                 .finally(() => {
                    loadingMessage.style.display = 'none'; // Hide loading indicator regardless of success/failure
                 });

        } catch (error) {
             displayError(`Failed to update heatmap: ${error.message}`);
             console.error("Update heatmap error:", error);
             loadingMessage.style.display = 'none'; // Hide loading on error
        }
    } // End updateHeatmap


    /** Attaches the click handler to the heatmap div for showing response details. */
    function setupClickHandler() {
        const gd = document.getElementById('heatmap');
        if (!gd) { console.error("setupClickHandler: Heatmap div not found."); return; }

        // Initialize markdown-it parser
        const md = window.markdownit({
            html: false,        // Disable HTML tags in source
            breaks: true,       // Convert '\n' in paragraphs into <br>
            linkify: true,      // Autoconvert URL-like text to links
            typographer: true,  // Enable some language-neutral replacements
        });

        gd.onclick = null; // Clear previous simple JS onclick listener

        // Add Plotly's specific click event listener
        gd.on('plotly_click', function(data) {
            if (!data.points || data.points.length === 0) return; // No point clicked

            const clickedPoint = data.points[0];
            const taskName = clickedPoint.x;
            const avgColumnLabel = 'Ø Average';
            if (taskName === avgColumnLabel) return; // Prevent modal for average column

            const modelIndex = clickedPoint.pointNumber[0]; // Row index
            if (modelIndex === undefined || modelIndex < 0 || modelIndex >= currentlyDisplayedModels.length) {
                console.error("Invalid model index from click event:", modelIndex); return;
            }
            const modelName = currentlyDisplayedModels[modelIndex]; // Get original name

            console.log(`Clicked on: Task='${taskName}', Model='${modelName}'`);

            if (typeof allResponses === 'undefined' || allResponses === null) {
                alert("Detailed response data ('allResponses') is not loaded."); return;
            }
            const responses = allResponses[taskName]?.[modelName];

            // Populate and Show the RESPONSE Modal
            responseModalTitle.textContent = `Responses: ${modelName} on ${taskName}`;
            responseModalBody.innerHTML = ''; // Clear previous
            
            // Use the existing view mode instead of resetting to markdown
            // Set the button text based on current mode
            viewToggleBtn.textContent = currentViewMode === 'markdown' ? 'View as Code' : 'View as Markdown';
            viewToggleBtn.style.display = 'inline-block'; // Show the toggle button

            if (responses?.length > 0) {
                // Extract the question from the first response (should be the same for all)
                const question = responses[0]?.original_question || 'N/A';
                
                // Add the question once at the top of the modal
                const questionDiv = document.createElement('div');
                questionDiv.className = 'modal-question';
                questionDiv.innerHTML = `<p><b>Question:</b> ${question}</p>`;
                responseModalBody.appendChild(questionDiv);
                
                // Add a divider between question and responses
                const divider = document.createElement('hr');
                divider.className = 'modal-divider';
                responseModalBody.appendChild(divider);

                // Now add each response without repeating the question
                responses.forEach((response, index) => {
                    if (!response) return;
                    const itemDiv = document.createElement('div'); 
                    itemDiv.className = 'response-item';
                    
                    let criteriaHTML = '<ul class="criteria-list">';
                    if (response.criteria_results?.length > 0) {
                        response.criteria_results.forEach(c => {
                            if (!c) return;
                            const sc = c.met ? 'true' : 'false'; const st=c.met?'Met':'Not Met';
                            criteriaHTML += `<li><span class="criterion-met-${sc}">[${st}]</span> ${c.criterion||'N/A'}</li>`;
                        });
                    } else { criteriaHTML += '<li>N/A</li>'; }
                    criteriaHTML += '</ul>';
                    
                    const fb = response.feedback ? `<div class="feedback-section"><b>Feedback:</b> ${response.feedback}</div>` : '';
                    const score = (typeof response.total_score === 'number' && !isNaN(response.total_score)) ? response.total_score.toFixed(2) : 'N/A';
                    const a = response.original_response || 'N/A';
                    
                    // Store both rendered and raw response formats
                    const renderedResponse = md.render(a);
                    const rawResponse = escapeHtml(a);
                    
                    // Set initial display based on current view mode
                    const markdownDisplay = currentViewMode === 'markdown' ? 'block' : 'none';
                    const codeDisplay = currentViewMode === 'code' ? 'block' : 'none';
                    
                    // Use the rendered markdown HTML with both display options
                    itemDiv.innerHTML = `
                        <h4>Evaluation ${index + 1} (Score: ${score})</h4>
                        <p><b>Response:</b></p>
                        <div class="markdown-content view-markdown" style="display:${markdownDisplay}">${renderedResponse}</div>
                        <pre class="code-view view-code" style="display:${codeDisplay}">${rawResponse}</pre>
                        ${criteriaHTML}${fb}`;
                    
                    responseModalBody.appendChild(itemDiv);
                });
            } else { 
                responseModalBody.innerHTML = '<p>No detailed responses found.</p>'; 
                viewToggleBtn.style.display = 'none'; // Hide toggle if no responses
            }

            showModal(responseModal); // Show the response modal
        });
        
        // Set up view toggle button handler
        viewToggleBtn.addEventListener('click', function() {
            if (currentViewMode === 'markdown') {
                // Switch to code view
                document.querySelectorAll('.view-markdown').forEach(el => el.style.display = 'none');
                document.querySelectorAll('.view-code').forEach(el => el.style.display = 'block');
                viewToggleBtn.textContent = 'View as Markdown';
                currentViewMode = 'code';
            } else {
                // Switch to markdown view
                document.querySelectorAll('.view-markdown').forEach(el => el.style.display = 'block');
                document.querySelectorAll('.view-code').forEach(el => el.style.display = 'none');
                viewToggleBtn.textContent = 'View as Code';
                currentViewMode = 'markdown';
            }
        });
    } // End setupClickHandler


    /** Processes initial data: extracts models, tasks, scores, averages, and unique filter options. */
     function processInitialData(rawData, modelInfoData) {
         const baseData = processBaseData(rawData);
         if (!baseData) { console.error("processInitialData failed: Base data processing error."); return null; }
         const safeModelInfo = modelInfoData || {}; const uniqueTypes = new Set(); const uniqueLabs = new Set();
         baseData.models.forEach(modelName => { const info = safeModelInfo[modelName]; if(info){if(info.model_type)uniqueTypes.add(info.model_type); if(info.lab)uniqueLabs.add(info.lab);} });
         console.log("Initial data and filter options processed.");
         return { ...baseData, uniqueTypes: Array.from(uniqueTypes), uniqueLabs: Array.from(uniqueLabs) };
     } // End processInitialData


     /** Sub-function to handle core data extraction from allData. */
     function processBaseData(rawData) {
         const tasksSet = new Set(); const modelsSet = new Set(); const scores = {}; const criteriaDetails = {};
         if (!rawData || typeof rawData !== 'object') { console.error("processBaseData: Invalid rawData."); return null; }
         for(const taskName in rawData){if(Object.hasOwnProperty.call(rawData,taskName)){ if(!taskName || typeof taskName!=='string'||taskName.trim()==='')continue; const tT=taskName.trim(); tasksSet.add(tT); const tR=rawData[taskName]; if(!tR||typeof tR!=='object')continue; for(const modelName in tR){if(Object.hasOwnProperty.call(tR,modelName)){ if(!modelName||typeof modelName!=='string'||modelName.trim()==='')continue; const tM=modelName.trim(); modelsSet.add(tM); if(!scores[tM]){scores[tM]={}; criteriaDetails[tM]={};} const r=tR[modelName]; if(r&&typeof r.average_total_score==='number'&&!isNaN(r.average_total_score)){scores[tM][tT]=r.average_total_score; criteriaDetails[tM][tT]={num_evaluations:r.num_evaluations??'N/A', criteria_stats:r.criteria_stats??{}}; } else { scores[tM][tT]=null; }}}}}
         const models = Array.from(modelsSet); const tasks = Array.from(tasksSet).sort();
         if (models.length === 0 || tasks.length === 0) { console.error("processBaseData: No models or tasks found."); return null; }
         const modelAverages = {}; models.forEach(model => { let tS=0, c=0; tasks.forEach(task => { const score=scores[model]?.[task]; if (score!=null && typeof score==='number'&&!isNaN(score)){tS+=score; c++;}}); modelAverages[model] = {average:c>0?tS/c:null, count:c};});
         return { models, tasks, scores, criteriaDetails, modelAverages };
     } // End processBaseData


    /** Filters models based on arrays of selected types and labs. */
    function filterModels(allModels, filterTypes, filterLabs, modelInfoData) {
        const safeModelInfo = modelInfoData || {};
        const isTypeFilterActive = Array.isArray(filterTypes) && filterTypes.length > 0;
        const isLabFilterActive = Array.isArray(filterLabs) && filterLabs.length > 0;
        if (!isTypeFilterActive && !isLabFilterActive) { return allModels; } // No filters active
        const typeSet = new Set(filterTypes); const labSet = new Set(filterLabs);
        return allModels.filter(modelName => {
            const info = safeModelInfo[modelName];
            const typeMatch = !isTypeFilterActive || (info && info.model_type && typeSet.has(info.model_type));
            const labMatch = !isLabFilterActive || (info && info.lab && labSet.has(info.lab));
            return typeMatch && labMatch;
        });
    } // End filterModels


    /** Sorts an array of model names based on the selected criteria. */
    function sortModels(modelsToSort, sortBy, modelAverages, modelInfoData) {
        const safeModelInfo = modelInfoData || {};
        modelsToSort.sort((a, b) => {
            let compareResult = 0; const infoA = safeModelInfo[a]; const infoB = safeModelInfo[b];
            const avgA = modelAverages[a]?.average; const avgB = modelAverages[b]?.average;
            switch (sortBy) {
                case 'average_score': compareResult = (avgB ?? -Infinity) - (avgA ?? -Infinity); break;
                case 'model_type': const typeA = infoA?.model_type?.toLowerCase() ?? 'zzz'; const typeB = infoB?.model_type?.toLowerCase() ?? 'zzz'; compareResult = typeA.localeCompare(typeB); break;
                case 'lab': const labA = infoA?.lab?.toLowerCase() ?? 'zzz'; const labB = infoB?.lab?.toLowerCase() ?? 'zzz'; compareResult = labA.localeCompare(labB); break;
                case 'name': default: compareResult = a.localeCompare(b); break;
            }
            if (compareResult === 0 && sortBy !== 'name') { compareResult = a.localeCompare(b); }
            if (compareResult === 0 && sortBy !== 'average_score') { compareResult = (avgB ?? -Infinity) - (avgA ?? -Infinity); }
            return compareResult;
        });
        return modelsToSort;
    } // End sortModels


    /** Prepares data matrices for Plotly (Y labels are just names). */
    function preparePlotlyData(sortedOriginalModels, tasks, scores, criteriaDetails) {
        const displayModels = sortedOriginalModels; // Y-axis labels are just the model names
        const zData = []; const hoverText = []; // Cell tooltips
        sortedOriginalModels.forEach(modelName => {
            const rowData = []; const hoverRow = [];
            tasks.forEach(taskName => {
                const score = scores[modelName]?.[taskName] ?? null;
                rowData.push(score);
                let cellHoverInfo = `<b>Model:</b> ${modelName}<br><b>Task:</b> ${taskName}`;
                 if (score !== null) { cellHoverInfo += `<br><b>Score:</b> ${score.toFixed(3)}`; const details = criteriaDetails?.[modelName]?.[taskName]; if (details) cellHoverInfo += `<br>Evaluations: ${details.num_evaluations}`; }
                 else { cellHoverInfo += "<br>Score: N/A"; }
                //  cellHoverInfo += "<extra></extra>";
                hoverRow.push(cellHoverInfo);
            });
            zData.push(rowData); hoverText.push(hoverRow);
        });
        return { displayModels, zData, hoverText };
    } // End preparePlotlyData

    // ** addYAxisLabelHovers function removed entirely **

}); // End DOMContentLoaded