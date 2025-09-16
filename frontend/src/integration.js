document.addEventListener('DOMContentLoaded', function() {
    console.log('FMEA Frontend Integration Loaded');
    
    // Initialize API connection
    let isConnected = false;
    let currentProject = null;
    let allProjects = [];
    
    // Connect to backend
    async function connectToBackend() {
        try {
            const healthCheck = await fmeaApi.healthCheck();
            console.log('Backend health check:', healthCheck);
            
            // Get development token
            const loginResult = await fmeaApi.devLogin();
            console.log('Development login successful');
            
            isConnected = true;
            updateConnectionStatus(true);
            
            // Clear any existing FMEA table data on initial load
            clearFMEATable();
            
            loadProjects();
            
        } catch (error) {
            console.error('Failed to connect to backend:', error);
            updateConnectionStatus(false);
        }
    }
    
    // Update connection status in UI
    function updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = connected ? 'Connected' : 'Disconnected';
            statusElement.className = connected ? 'text-green-600' : 'text-red-600';
        }
    }
    
    // Load projects from backend
    async function loadProjects() {
        if (!isConnected) return;
        
        try {
            allProjects = await fmeaApi.getProjects();
            displayProjects(allProjects);
            updateProjectSelector(allProjects);
        } catch (error) {
            console.error('Failed to load projects:', error);
        }
    }
    
    // Update project selector dropdown
    function updateProjectSelector(projects) {
        const selector = document.getElementById('project-selector');
        if (!selector) return;
        
        // Clear existing options except the first one
        while (selector.children.length > 1) {
            selector.removeChild(selector.lastChild);
        }
        
        // Add project options
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            selector.appendChild(option);
        });
    }
    
    // Display projects in the UI
    function displayProjects(projects) {
        const projectsTable = document.querySelector('#project-dashboard table tbody');
        if (!projectsTable) return;
        
        // Clear existing rows (except the header)
        const existingRows = projectsTable.querySelectorAll('tr:not(:first-child)');
        existingRows.forEach(row => row.remove());
        
        // Add project rows
        projects.forEach(project => {
            const row = document.createElement('tr');
            row.className = 'border-t border-gray-100';
            row.innerHTML = `
                <td class="px-6 py-4 font-medium">${project.name}</td>
                <td class="px-6 py-4 text-gray-600">${formatDate(project.created_at)}</td>
                <td class="px-6 py-4">
                    <span class="bg-${getStatusColor(project.status)}-100 text-${getStatusColor(project.status)}-800 px-2 py-1 rounded text-xs font-medium">${project.status}</span>
                </td>
                <td class="px-6 py-4">
                    <div class="flex space-x-3">
                        <button class="text-primary-600 hover:text-primary-800" title="Open" onclick="openProject(${project.id})">
                            <i class="fa-solid fa-folder-open"></i>
                        </button>
                        <button class="text-gray-500 hover:text-gray-700" title="Export" onclick="exportProject(${project.id})">
                            <i class="fa-solid fa-file-export"></i>
                        </button>
                        <button class="text-red-500 hover:text-red-700" title="Delete" onclick="deleteProject(${project.id})">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </td>
            `;
            projectsTable.appendChild(row);
        });
    }
    
    // Format date for display
    function formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) return 'Today';
        if (diffDays === 2) return 'Yesterday';
        return date.toLocaleDateString();
    }
    
    // Get status color
    function getStatusColor(status) {
        switch (status) {
            case 'draft': return 'yellow';
            case 'final': return 'green';
            case 'exported': return 'blue';
            default: return 'gray';
        }
    }
    
    // Create new project
    async function createNewProject() {
        if (!isConnected) return;
        
        const projectName = prompt('Enter project name:');
        if (!projectName) return;
        
        try {
            const project = await fmeaApi.createProject({
                name: projectName,
                description: prompt('Enter project description (optional):') || null
            });
            
            console.log('Project created:', project);
            loadProjects();
            
            // Auto-select the new project
            if (document.getElementById('project-selector')) {
                document.getElementById('project-selector').value = project.id;
                openProject(project.id);
            }
            
        } catch (error) {
            console.error('Failed to create project:', error);
            alert('Failed to create project: ' + error.message);
        }
    }
    
    // Open a specific project
    async function openProject(projectId) {
        console.log('openProject called with projectId:', projectId);
        if (!isConnected) return;
        
        try {
            // Clear the table first
            console.log('Calling clearFMEATable...');
            clearFMEATable();
            console.log('clearFMEATable completed');
            
            // Load project details
            console.log('Loading project details...');
            const project = await fmeaApi.getProject(projectId);
            if (!project) {
                console.error('Project not found');
                return;
            }
            console.log('Project loaded:', project);
            
            // Load FMEA data for this project
            console.log('Loading FMEA data...');
            const fmeas = await fmeaApi.getFMEAs(projectId);
            console.log('FMEA data loaded:', fmeas);
            
            // Update UI
            currentProject = project;
            updateProjectInfo(project, fmeas);
            console.log('Calling displayFMEAs...');
            displayFMEAs(fmeas);
            console.log('displayFMEAs completed');
            showProjectIsolationNotice();
            
            console.log(`Opened project: ${project.name} with ${fmeas.length} FMEA entries`);
            
        } catch (error) {
            console.error('Failed to open project:', error);
            alert('Failed to open project: ' + error.message);
        }
    }
    
    // Update project information display
    function updateProjectInfo(project, fmeas) {
        const projectName = document.getElementById('current-project-name');
        const fmeaCount = document.getElementById('fmea-count');
        const totalEntries = document.getElementById('total-entries');
        const highRiskCount = document.getElementById('high-risk-count');
        
        if (projectName) projectName.textContent = project ? project.name : 'No project selected';
        if (fmeaCount) fmeaCount.textContent = project ? `${fmeas.length} FMEA entries` : '0 FMEA entries';
        if (totalEntries) totalEntries.textContent = fmeas ? fmeas.length : 0;
        
        // Count high risk entries (RPN > 100)
        const highRisk = fmeas ? fmeas.filter(fmea => fmea.rpn > 100).length : 0;
        if (highRiskCount) highRiskCount.textContent = highRisk;
    }
    
    // Show project isolation notice
    function showProjectIsolationNotice() {
        const notice = document.getElementById('project-isolation-notice');
        if (notice) {
            notice.classList.remove('hidden');
        }
    }
    
    // Hide project isolation notice
    function hideProjectIsolationNotice() {
        const notice = document.getElementById('project-isolation-notice');
        if (notice) {
            notice.classList.add('hidden');
        }
    }
    
    // Display FMEA data in the table
    function displayFMEAs(fmeas) {
        console.log('displayFMEAs called with:', fmeas);
        const fmeaTable = document.querySelector('#fmea-table table tbody');
        console.log('Found fmeaTable in displayFMEAs:', fmeaTable);
        if (!fmeaTable) {
            console.error('Could not find fmea-table tbody in displayFMEAs');
            return;
        }
        
        console.log('Before clearing in displayFMEAs - rows count:', fmeaTable.children.length);
        // Clear ALL existing rows completely
        fmeaTable.innerHTML = '';
        console.log('After clearing in displayFMEAs - rows count:', fmeaTable.children.length);
        
        // Check if we have FMEA data
        if (!fmeas || fmeas.length === 0) {
            console.log('No FMEA data, showing empty state');
            // Show empty state for new projects
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = `
                <td colspan="15" class="px-4 py-8 text-center text-gray-500">
                    <div class="flex flex-col items-center">
                        <i class="fa-solid fa-plus-circle text-4xl mb-2 text-gray-300"></i>
                        <p class="text-lg font-medium">No FMEA entries yet</p>
                        <p class="text-sm mb-4">This project is ready for your first FMEA analysis</p>
                        <div class="flex space-x-3">
                            <button class="bg-primary-600 text-white hover:bg-primary-700 px-4 py-2 rounded text-sm flex items-center" onclick="addNewFMEARow()">
                                <i class="fa-solid fa-plus mr-2"></i>
                                Add First Entry
                            </button>
                            <button class="bg-green-600 text-white hover:bg-green-700 px-4 py-2 rounded text-sm flex items-center" onclick="getAISuggestionsForNewProject()">
                                <i class="fa-solid fa-robot mr-2"></i>
                                AI Suggestions
                            </button>
                        </div>
                    </div>
                </td>
            `;
            fmeaTable.appendChild(emptyRow);
            console.log('After adding empty state - rows count:', fmeaTable.children.length);
            return;
        }
        
        console.log('Adding FMEA rows:', fmeas.length);
        // Add FMEA rows
        fmeas.forEach(fmea => {
            const row = document.createElement('tr');
            row.className = 'border-t border-gray-100';
            row.innerHTML = `
                <td class="px-4 py-3 text-gray-500 align-bottom">${fmea.id}</td>
                <td class="px-4 py-3 align-bottom">${fmea.component}</td>
                <td class="px-4 py-3 align-bottom">${fmea.failure_mode}</td>
                <td class="px-4 py-3 align-bottom">${fmea.effect}</td>
                <td class="px-4 py-3 align-bottom">${fmea.cause}</td>
                <td class="px-4 py-3 font-medium align-bottom">${fmea.severity}</td>
                <td class="px-4 py-3 font-medium align-bottom">${fmea.occurrence}</td>
                <td class="px-4 py-3 font-medium align-bottom">${fmea.detection}</td>
                <td class="px-4 py-3 font-medium ${getRPNClass(fmea.rpn)} align-bottom">${fmea.rpn}</td>
                <td class="px-4 py-3 align-bottom w-64">${fmea.mitigation || '-'}</td>
                <td class="px-4 py-3 align-bottom w-64">${fmea.action_taken || '-'}</td>
                <td class="px-4 py-3 font-medium align-bottom">${fmea.revised_severity || '-'}</td>
                <td class="px-4 py-3 font-medium align-bottom">${fmea.revised_occurrence || '-'}</td>
                <td class="px-4 py-3 font-medium align-bottom">${fmea.revised_detection || '-'}</td>
                <td class="px-4 py-3 font-medium ${getRPNClass(fmea.revised_rpn)} align-bottom">${fmea.revised_rpn || '-'}</td>
            `;
            fmeaTable.appendChild(row);
        });
        
        // Add "Add New Row" button
        const addRow = document.createElement('tr');
        addRow.className = 'border-t border-gray-100';
        addRow.innerHTML = `
            <td class="px-4 py-3 text-gray-500 align-bottom" colspan="15">
                <button class="flex items-center text-primary-600 hover:text-primary-800" onclick="addNewFMEARow()">
                    <i class="fa-solid fa-plus mr-2"></i>
                    Add New Row
                </button>
            </td>
        `;
        fmeaTable.appendChild(addRow);
        console.log('After adding all rows - rows count:', fmeaTable.children.length);

        // Attach AI Suggest Rows handler robustly, even if button is rendered later
        attachAISuggestHandler();
    }
    
    // Get RPN class for styling
    function getRPNClass(rpn) {
        if (!rpn) return '';
        if (rpn >= 200) return 'text-red-600 font-bold';
        if (rpn >= 100) return 'text-orange-600 font-semibold';
        if (rpn >= 50) return 'text-yellow-600';
        return 'text-green-600';
    }
    
    // Add new FMEA row
    async function addNewFMEARow() {
        if (!isConnected || !currentProject) {
            alert('Please select a project first');
            return;
        }
        
        const component = prompt('Enter component name:');
        if (!component) return;
        
        const failureMode = prompt('Enter failure mode:');
        if (!failureMode) return;
        
        const effect = prompt('Enter effect:');
        if (!effect) return;
        
        const cause = prompt('Enter cause:');
        if (!cause) return;
        
        const severity = parseInt(prompt('Enter severity (1-10):')) || 5;
        const occurrence = parseInt(prompt('Enter occurrence (1-10):')) || 5;
        const detection = parseInt(prompt('Enter detection (1-10):')) || 5;
        const rpn = severity * occurrence * detection;
        
        try {
            const fmea = await fmeaApi.createFMEA(currentProject.id, {
                component,
                failure_mode: failureMode,
                effect,
                cause,
                severity,
                occurrence,
                detection,
                rpn,
                mitigation: prompt('Enter mitigation (optional):') || null,
                action_taken: null,
                revised_severity: null,
                revised_occurrence: null,
                revised_detection: null,
                revised_rpn: null
            });
            
            console.log('FMEA created:', fmea);
            openProject(currentProject.id); // Refresh table
            
        } catch (error) {
            console.error('Failed to create FMEA:', error);
            alert('Failed to create FMEA: ' + error.message);
        }
    }
    
    // Export project
    async function exportProject(projectId) {
        if (!isConnected) return;
        
        const format = prompt('Enter export format (csv/pdf):').toLowerCase();
        if (!format || !['csv', 'pdf'].includes(format)) {
            alert('Please enter either "csv" or "pdf"');
            return;
        }
        
        try {
            if (format === 'csv') {
                await fmeaApi.exportCSV(projectId);
            } else {
                await fmeaApi.exportPDF(projectId);
            }
            
            console.log(`Project exported as ${format.toUpperCase()}`);
            
        } catch (error) {
            console.error('Failed to export project:', error);
            alert('Failed to export project: ' + error.message);
        }
    }
    
    // Delete project
    async function deleteProject(projectId) {
        if (!isConnected) return;
        
        if (!confirm('Are you sure you want to delete this project? This will also delete all FMEA entries associated with this project.')) return;
        
        try {
            await fmeaApi.deleteProject(projectId);
            console.log('Project deleted');
            loadProjects();
            
            // If the deleted project was the current project, clear the view
            if (currentProject && currentProject.id === projectId) {
                currentProject = null;
                clearFMEATable();
            }
            
        } catch (error) {
            console.error('Failed to delete project:', error);
            alert('Failed to delete project: ' + error.message);
        }
    }
    
    // Get AI suggestions for new project
    async function getAISuggestionsForNewProject() {
        if (!isConnected || !currentProject) {
            alert('Please select a project first');
            return;
        }
        
        const component = prompt('Enter component name for AI suggestions:');
        if (!component) return;
        
        try {
            const result = await fmeaApi.getAISuggestions({ component });
            if (result.suggestions && Array.isArray(result.suggestions)) {
                for (const suggestion of result.suggestions) {
                    await fmeaApi.createFMEA(currentProject.id, {
                        component,
                        failure_mode: suggestion.failure_mode,
                        effect: suggestion.effect,
                        cause: suggestion.cause,
                        severity: suggestion.severity,
                        occurrence: suggestion.occurrence,
                        detection: suggestion.detection,
                        rpn: suggestion.severity * suggestion.occurrence * suggestion.detection,
                        mitigation: suggestion.mitigation,
                        action_taken: suggestion.action_taken,
                        revised_severity: suggestion.revised_severity,
                        revised_occurrence: suggestion.revised_occurrence,
                        revised_detection: suggestion.revised_detection,
                        revised_rpn: suggestion.revised_rpn
                    });
                }
                openProject(currentProject.id); // Refresh table
                alert(`AI suggestions added to project "${currentProject.name}"!`);
            } else {
                alert('No suggestions returned or error: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            alert('Failed to get AI suggestions: ' + error.message);
        }
    }
    
    // Get AI suggestions
    async function getAISuggestions(component) {
        if (!isConnected) return;
        
        try {
            const suggestions = await fmeaApi.getAISuggestions({
                component: component
            });
            
            console.log('AI suggestions:', suggestions);
            return suggestions;
            
        } catch (error) {
            console.error('Failed to get AI suggestions:', error);
            return null;
        }
    }
    
    // Bind event listeners
    document.addEventListener('click', function(e) {
        // Create new project button
        if (e.target.closest('button') && e.target.closest('button').textContent.includes('Create New Project')) {
            e.preventDefault();
            createNewProject();
        }
        
        // Start new FMEA button
        if (e.target.closest('button') && e.target.closest('button').textContent.includes('Start New FMEA')) {
            e.preventDefault();
            createNewProject();
        }
        
        // New project button in FMEA table
        if (e.target.closest('#new-project-btn')) {
            e.preventDefault();
            createNewProject();
        }
    });
    
    // Project selector change handler
    document.addEventListener('change', function(e) {
        if (e.target.id === 'project-selector') {
            const projectId = e.target.value;
            if (projectId) {
                openProject(parseInt(projectId));
            } else {
                // Clear current project and table
                currentProject = null;
                clearFMEATable();
            }
        }
    });
    
    // Make functions globally available
    window.openProject = openProject;
    window.exportProject = exportProject;
    window.deleteProject = deleteProject;
    window.addNewFMEARow = addNewFMEARow;
    window.getAISuggestions = getAISuggestions;
    window.getAISuggestionsForNewProject = getAISuggestionsForNewProject;
    
    // CSV Upload functionality
    function attachCSVUploadHandler() {
        const csvBtn = document.getElementById('csv-upload-btn');
        const fileInput = document.getElementById('csv-file-input');
        
        if (csvBtn && fileInput && !csvBtn._csvHandlerAttached) {
            csvBtn.onclick = function() {
                if (!isConnected || !currentProject) {
                    alert('Please open a project first');
                    return;
                }
                fileInput.click();
            };
            
            fileInput.onchange = async function(e) {
                const file = e.target.files[0];
                if (!file) return;
                
                if (!file.name.toLowerCase().endsWith('.csv')) {
                    alert('Please select a CSV file');
                    return;
                }
                
                try {
                    console.log('Uploading CSV file:', file.name);
                    const result = await fmeaApi.importCSV(currentProject.id, file);
                    
                    console.log('CSV import result:', result);
                    
                    if (result.imported_count > 0) {
                        alert(`Successfully imported ${result.imported_count} FMEA entries to project "${currentProject.name}"!`);
                        if (result.errors && result.errors.length > 0) {
                            console.warn('Import errors:', result.errors);
                            alert(`Import completed with ${result.errors.length} errors. Check console for details.`);
                        }
                        // Refresh the FMEA table
                        openProject(currentProject.id);
                    } else {
                        alert('No entries were imported. Please check your CSV format.');
                    }
                    
                } catch (error) {
                    console.error('CSV upload error:', error);
                    alert('Failed to upload CSV: ' + error.message);
                }
                
                // Clear the file input
                fileInput.value = '';
            };
            
            csvBtn._csvHandlerAttached = true;
        }
    }
    
    // Initialize connection
    connectToBackend();
    
    // Attach AI Suggest Rows handler robustly, even if button is rendered later
    function attachAISuggestHandler() {
        const aiBtn = document.getElementById('ai-suggest-btn');
        if (aiBtn && !aiBtn._aiHandlerAttached) {
            aiBtn.onclick = async function() {
                if (!isConnected || !currentProject) {
                    alert('Please open a project first');
                    return;
                }
                const component = prompt('Enter component name for AI suggestions:');
                if (!component) return;
                try {
                    const result = await fmeaApi.getAISuggestions({ component });
                    if (result.suggestions && Array.isArray(result.suggestions)) {
                        for (const suggestion of result.suggestions) {
                            await fmeaApi.createFMEA(currentProject.id, {
                                component,
                                failure_mode: suggestion.failure_mode,
                                effect: suggestion.effect,
                                cause: suggestion.cause,
                                severity: suggestion.severity,
                                occurrence: suggestion.occurrence,
                                detection: suggestion.detection,
                                rpn: suggestion.severity * suggestion.occurrence * suggestion.detection,
                                mitigation: suggestion.mitigation,
                                action_taken: suggestion.action_taken,
                                revised_severity: suggestion.revised_severity,
                                revised_occurrence: suggestion.revised_occurrence,
                                revised_detection: suggestion.revised_detection,
                                revised_rpn: suggestion.revised_rpn
                            });
                        }
                        openProject(currentProject.id); // Refresh table
                        alert(`AI suggestions added to project "${currentProject.name}"!`);
                    } else {
                        alert('No suggestions returned or error: ' + (result.error || 'Unknown error'));
                    }
                } catch (error) {
                    alert('Failed to get AI suggestions: ' + error.message);
                }
            };
            aiBtn._aiHandlerAttached = true;
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        attachAISuggestHandler();
        attachCSVUploadHandler();
    });
    
    const observer = new MutationObserver(function() {
        attachAISuggestHandler();
        attachCSVUploadHandler();
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Clear FMEA table completely
    function clearFMEATable() {
        console.log('clearFMEATable called');
        const fmeaTable = document.querySelector('#fmea-table table tbody');
        console.log('Found fmeaTable:', fmeaTable);
        if (fmeaTable) {
            console.log('Before clearing - rows count:', fmeaTable.children.length);
            // Clear ALL rows completely
            fmeaTable.innerHTML = '';
            console.log('After clearing - rows count:', fmeaTable.children.length);
            
            // Add empty state message
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = `
                <td colspan="15" class="px-4 py-8 text-center text-gray-500">
                    <div class="flex flex-col items-center">
                        <i class="fa-solid fa-table text-4xl mb-2 text-gray-300"></i>
                        <p class="text-lg font-medium">No FMEA data to display</p>
                        <p class="text-sm">Select a project from the dropdown above to view FMEA entries</p>
                    </div>
                </td>
            `;
            fmeaTable.appendChild(emptyRow);
            console.log('After adding empty row - rows count:', fmeaTable.children.length);
        } else {
            console.error('Could not find fmea-table tbody');
        }
        
        // Clear project info
        updateProjectInfo(null, []);
        hideProjectIsolationNotice();
    }
}); 