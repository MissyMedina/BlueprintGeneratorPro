// Guidance Blueprint Kit Pro - Interactive Frontend

class GuidanceApp {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.formData = {
            project: '',
            description: '',
            components: [],
            platforms: [],
            mode: '',
            modules: [],
            claims_scope: 'app',
            tags: {},
            evidence_data: [],
            repo_scan: false,
            customQuestions: {},
            smartSuggestions: []
        };
        this.profiles = {};
        this.isGenerating = false;
        this.init();
    }

    init() {
        this.loadProfiles();
        this.setupEventListeners();
        this.updateUI();
        this.showStep(1);
    }

    showStep(stepNumber) {
        // Hide all steps
        document.querySelectorAll('.wizard-step').forEach(step => {
            step.classList.add('hidden');
        });

        // Show current step
        const currentStep = document.getElementById(`step${stepNumber}`);
        if (currentStep) {
            currentStep.classList.remove('hidden');
            currentStep.classList.add('fade-in');
        }

        this.currentStep = stepNumber;
        this.updateProgress();

        // Load dynamic content for specific steps
        if (stepNumber === 3) {
            this.loadDynamicQuestions();
        } else if (stepNumber === 4) {
            this.updateSummary();
        }
    }

    updateProgress() {
        const progress = (this.currentStep / this.totalSteps) * 100;
        document.getElementById('progressBar').style.width = `${progress}%`;
        document.getElementById('currentStepNum').textContent = this.currentStep;
        document.getElementById('progressPercent').textContent = Math.round(progress);
    }

    nextStep() {
        if (this.validateCurrentStep()) {
            if (this.currentStep < this.totalSteps) {
                this.showStep(this.currentStep + 1);
            }
        }
    }

    prevStep() {
        if (this.currentStep > 1) {
            this.showStep(this.currentStep - 1);
        }
    }

    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                const projectName = document.getElementById('projectNameInput').value.trim();
                const selectedComponents = this.formData.components;

                if (!projectName) {
                    this.showError('Please enter a project name');
                    return false;
                }
                if (selectedComponents.length === 0) {
                    this.showError('Please select at least one component for your project');
                    return false;
                }

                this.formData.project = projectName;
                this.formData.description = document.getElementById('projectDescription').value.trim();

                // Generate intelligent project type based on components
                this.formData.projectType = this.inferProjectType(selectedComponents);
                return true;

            case 2:
                const selectedDocType = document.querySelector('.doc-type-card.selected');
                if (!selectedDocType) {
                    this.showError('Please select a documentation type');
                    return false;
                }

                this.formData.docType = selectedDocType.dataset.type;
                return true;

            case 3:
                const selectedFocus = document.querySelector('.focus-card.selected');
                if (!selectedFocus) {
                    this.showError('Please select a focus area');
                    return false;
                }

                this.formData.claims_scope = selectedFocus.dataset.focus;
                this.collectCustomAnswers();
                return true;

            default:
                return true;
        }
    }

    async loadProfiles() {
        try {
            const response = await fetch('/api/profiles');
            const data = await response.json();
            this.profiles = data.profiles;
            this.populateProfileSelect();
        } catch (error) {
            console.error('Error loading profiles:', error);
        }
    }

    populateProfileSelect() {
        const select = document.getElementById('profileSelect');
        if (!select) return;

        select.innerHTML = '<option value="">Custom Configuration</option>';
        
        Object.entries(this.profiles).forEach(([key, profile]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = this.formatProfileName(key);
            select.appendChild(option);
        });
    }

    formatProfileName(key) {
        const names = {
            'full-eval': 'Full Evaluation',
            'sec-audit': 'Security Audit',
            'ops-readiness': 'Operations Readiness',
            'ux-review': 'UX Review'
        };
        return names[key] || key;
    }

    setupEventListeners() {
        // Component selection with checkboxes
        document.addEventListener('change', (e) => {
            if (e.target.closest('.component-card')) {
                const checkbox = e.target;
                const card = checkbox.closest('.component-card');
                const component = card.dataset.component;

                if (checkbox.checked) {
                    card.classList.add('selected');
                    if (!this.formData.components.includes(component)) {
                        this.formData.components.push(component);
                    }
                } else {
                    card.classList.remove('selected');
                    this.formData.components = this.formData.components.filter(c => c !== component);
                }

                this.updateSmartSuggestions();
            }
        });

        // Primary action selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.primary-action-card')) {
                document.querySelectorAll('.primary-action-card').forEach(card => {
                    card.classList.remove('selected', 'ring-4', 'ring-blue-300', 'ring-orange-300');
                });
                const selectedCard = e.target.closest('.primary-action-card');
                selectedCard.classList.add('selected');

                const action = selectedCard.dataset.action;
                if (action === 'validate') {
                    selectedCard.classList.add('ring-4', 'ring-orange-300');
                    this.handleAnalysisMode();
                    return;
                } else if (action === 'create') {
                    selectedCard.classList.add('ring-4', 'ring-blue-300');
                    this.showWizard();
                    return;
                }
            }

            if (e.target.closest('.doc-type-card')) {
                document.querySelectorAll('.doc-type-card').forEach(card => {
                    card.classList.remove('selected');
                });
                const selectedCard = e.target.closest('.doc-type-card');
                selectedCard.classList.add('selected');

                // Handle application analysis selection
                if (selectedCard.dataset.type === 'analysis') {
                    this.handleAnalysisMode();
                    return;
                }
            }

            if (e.target.closest('.focus-card')) {
                document.querySelectorAll('.focus-card').forEach(card => {
                    card.classList.remove('selected');
                });
                e.target.closest('.focus-card').classList.add('selected');
            }
        });

        // File upload
        const fileUpload = document.getElementById('repoUpload');
        if (fileUpload) {
            fileUpload.addEventListener('change', (e) => {
                this.handleFileUpload(e.target.files[0]);
            });
        }
    }

    updateSmartSuggestions() {
        const components = this.formData.components;
        const suggestions = this.generateSmartSuggestions(components);

        if (suggestions.length > 0) {
            document.getElementById('smartSuggestions').classList.remove('hidden');
            document.getElementById('suggestionsList').innerHTML = suggestions.map(s =>
                `<div class="flex items-start space-x-2 mb-2">
                    <i class="fas fa-arrow-right text-blue-600 text-xs mt-1"></i>
                    <span>${s}</span>
                </div>`
            ).join('');
        } else {
            document.getElementById('smartSuggestions').classList.add('hidden');
        }
    }

    generateSmartSuggestions(components) {
        const suggestions = [];

        // Frontend + Backend suggestions
        if (components.includes('frontend') && components.includes('backend')) {
            suggestions.push("Consider API design patterns and authentication flow between frontend and backend");
            suggestions.push("You'll need CORS configuration and API versioning strategy");
        }

        // Mobile + Backend suggestions
        if (components.includes('mobile') && components.includes('backend')) {
            suggestions.push("Plan for offline functionality and data synchronization");
            suggestions.push("Consider push notifications and mobile-specific API optimizations");
        }

        // Database suggestions
        if (components.includes('database')) {
            suggestions.push("Think about data backup, migration strategies, and performance optimization");
            if (components.includes('mobile')) {
                suggestions.push("Consider local database (SQLite) for offline mobile functionality");
            }
        }

        // AI/ML suggestions
        if (components.includes('ai')) {
            suggestions.push("Plan for model training data, inference infrastructure, and model versioning");
            suggestions.push("Consider privacy implications and bias testing for AI features");
        }

        // Multi-platform suggestions
        if (components.includes('mobile') && components.includes('desktop')) {
            suggestions.push("Consider cross-platform frameworks like Electron or Flutter for code reuse");
        }

        // Training platform specific suggestions (based on project description)
        const projectName = document.getElementById('projectNameInput')?.value.toLowerCase() || '';
        const description = document.getElementById('projectDescription')?.value.toLowerCase() || '';

        if (projectName.includes('training') || description.includes('training') ||
            projectName.includes('learning') || description.includes('learning') ||
            projectName.includes('course') || description.includes('course')) {
            suggestions.push("For training platforms: Consider user progress tracking, content management, and assessment tools");
            suggestions.push("Think about video streaming, interactive content, and certification systems");
            suggestions.push("Plan for instructor tools, student analytics, and discussion forums");
        }

        return suggestions.slice(0, 4); // Limit to 4 suggestions
    }

    showWizard() {
        // Show the wizard and hide primary action selection
        document.getElementById('wizardContainer').classList.remove('hidden');
        document.querySelector('.mb-12').style.display = 'none'; // Hide primary action cards
    }

    handleAnalysisMode() {
        // Skip to a special analysis step
        this.formData.docType = 'analysis';
        this.showAnalysisInterface();
    }

    showAnalysisInterface() {
        // Hide primary action cards and wizard, show analysis interface
        document.querySelector('.mb-12').style.display = 'none'; // Hide primary action cards
        document.getElementById('wizardContainer').style.display = 'none'; // Hide wizard if visible

        // Create analysis interface container
        const analysisContainer = document.createElement('div');
        analysisContainer.id = 'analysisContainer';
        analysisContainer.className = 'max-w-4xl mx-auto';
        analysisContainer.innerHTML = `
            <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
                <div class="bg-gradient-to-r from-orange-600 to-red-600 text-white p-8 text-center">
                    <div class="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-microscope text-3xl"></i>
                    </div>
                    <h2 class="text-3xl font-bold mb-2">🔍 Application Analysis & Validation</h2>
                    <p class="text-orange-100">Upload your existing codebase and get comprehensive insights about what it is, how well it's built, and what could be improved</p>
                </div>

                <div class="p-8">
                    <div class="max-w-2xl mx-auto">
                        <!-- Analysis Options -->
                        <div class="mb-8">
                            <h3 class="text-xl font-semibold text-gray-900 mb-6">Choose Your Analysis Method</h3>

                            <!-- Method Selection Tabs -->
                            <div class="flex mb-6 bg-gray-100 rounded-lg p-1">
                                <button id="localFolderTab" onclick="app.switchAnalysisMethod('local')" class="flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors bg-white text-blue-600 shadow-sm">
                                    <i class="fas fa-folder mr-2"></i>Local Folder
                                </button>
                                <button id="uploadFileTab" onclick="app.switchAnalysisMethod('upload')" class="flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors text-gray-600 hover:text-gray-900">
                                    <i class="fas fa-cloud-upload-alt mr-2"></i>Upload File
                                </button>
                            </div>

                            <!-- Local Folder Option -->
                            <div id="localFolderOption" class="analysis-option">
                                <div class="border-2 border-dashed border-blue-300 rounded-xl p-8 text-center hover:border-blue-500 transition-colors bg-blue-50">
                                    <i class="fas fa-folder-open text-4xl text-blue-600 mb-4"></i>
                                    <h4 class="text-lg font-semibold text-gray-900 mb-2">Browse Local Folder</h4>
                                    <p class="text-gray-600 mb-4">Select your project folder directly from your computer</p>
                                    <button type="button" onclick="app.selectLocalFolder()"
                                            class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold">
                                        <i class="fas fa-folder-open mr-2"></i>Choose Folder
                                    </button>
                                    <p class="text-xs text-gray-500 mt-3">✓ No upload required ✓ Keeps your code local ✓ Faster analysis</p>

                                    <!-- Selected folder display -->
                                    <div id="selectedFolderDisplay" class="hidden mt-4 p-4 bg-white rounded-lg border">
                                        <div class="flex items-center justify-between">
                                            <div class="flex items-center space-x-3">
                                                <i class="fas fa-folder text-blue-600"></i>
                                                <div class="text-left">
                                                    <div id="selectedFolderName" class="font-medium text-gray-900"></div>
                                                    <div id="selectedFolderPath" class="text-sm text-gray-500"></div>
                                                </div>
                                            </div>
                                            <button onclick="app.analyzeLocalFolder()"
                                                    class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 font-semibold">
                                                <i class="fas fa-play mr-2"></i>Analyze
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Upload File Option -->
                            <div id="uploadFileOption" class="analysis-option hidden">
                                <div class="border-2 border-dashed border-orange-300 rounded-xl p-8 text-center hover:border-orange-500 transition-colors bg-orange-50">
                                    <input type="file" id="analysisFileUpload" accept=".zip,.tar.gz,.tar" class="hidden">
                                    <i class="fas fa-cloud-upload-alt text-4xl text-orange-600 mb-4"></i>
                                    <h4 class="text-lg font-semibold text-gray-900 mb-2">Upload Codebase Archive</h4>
                                    <p class="text-gray-600 mb-4">Upload a ZIP or TAR file containing your application source code</p>
                                    <button type="button" onclick="document.getElementById('analysisFileUpload').click()"
                                            class="bg-orange-600 text-white px-6 py-3 rounded-lg hover:bg-orange-700 font-semibold">
                                        <i class="fas fa-folder-open mr-2"></i>Choose File
                                    </button>
                                    <p class="text-xs text-gray-500 mt-3">Supports: .zip, .tar.gz, .tar files (max 100MB)</p>
                                </div>
                            </div>
                        </div>

                        <!-- What We'll Analyze -->
                        <div class="bg-gray-50 rounded-xl p-6 mb-8">
                            <h4 class="font-semibold text-gray-900 mb-4">
                                <i class="fas fa-search text-orange-600 mr-2"></i>What We'll Analyze
                            </h4>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                <div class="space-y-2">
                                    <div class="flex items-center space-x-2">
                                        <i class="fas fa-check text-green-600"></i>
                                        <span>Application type detection</span>
                                    </div>
                                    <div class="flex items-center space-x-2">
                                        <i class="fas fa-check text-green-600"></i>
                                        <span>Technology stack analysis</span>
                                    </div>
                                    <div class="flex items-center space-x-2">
                                        <i class="fas fa-check text-green-600"></i>
                                        <span>Security implementation review</span>
                                    </div>
                                    <div class="flex items-center space-x-2">
                                        <i class="fas fa-check text-green-600"></i>
                                        <span>Code quality assessment</span>
                                    </div>
                                </div>
                                <div class="space-y-2">
                                    <div class="flex items-center space-x-2">
                                        <i class="fas fa-check text-green-600"></i>
                                        <span>Architecture pattern detection</span>
                                    </div>
                                    <div class="flex items-center space-x-2">
                                        <i class="fas fa-check text-green-600"></i>
                                        <span>Missing component identification</span>
                                    </div>
                                    <div class="flex items-center space-x-2">
                                        <i class="fas fa-check text-green-600"></i>
                                        <span>Improvement recommendations</span>
                                    </div>
                                    <div class="flex items-center space-x-2">
                                        <i class="fas fa-check text-green-600"></i>
                                        <span>Enhancement opportunities</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Fair Grading Scale Disclosure -->
                        <div class="bg-blue-50 rounded-xl p-6 mb-8 border border-blue-200">
                            <h4 class="font-semibold text-blue-900 mb-3">
                                <i class="fas fa-info-circle text-blue-600 mr-2"></i>Our Fair & Transparent Grading
                            </h4>
                            <div class="text-sm text-blue-800 space-y-2">
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <div class="font-medium mb-2">🔒 Security Score (0-100)</div>
                                        <div class="text-xs space-y-1">
                                            <div>• Base: 50 points (every project starts here!)</div>
                                            <div>• +25 pts: Authentication system</div>
                                            <div>• +15 pts: Input validation</div>
                                            <div>• +10 pts: Encryption/hashing</div>
                                            <div>• +5 pts: Security headers</div>
                                        </div>
                                    </div>
                                    <div>
                                        <div class="font-medium mb-2">📊 Quality Score (0-100)</div>
                                        <div class="text-xs space-y-1">
                                            <div>• Base: 40 points (working project credit!)</div>
                                            <div>• +20 pts: Documentation</div>
                                            <div>• +20 pts: Testing framework</div>
                                            <div>• +10 pts: Error handling</div>
                                            <div>• +5 pts: Code linting</div>
                                            <div>• +5 pts: CI/CD pipeline</div>
                                        </div>
                                    </div>
                                </div>
                                <div class="mt-4">
                                    <div class="font-medium mb-2">🏗️ Architecture Score (0-100)</div>
                                    <div class="text-xs space-y-1">
                                        <div>• Base: 30 points (structured project!)</div>
                                        <div>• +20 pts: Good project organization</div>
                                        <div>• +25 pts: Separation of concerns</div>
                                        <div>• +15 pts: Configuration management</div>
                                        <div>• +10 pts: API/routing structure</div>
                                    </div>
                                </div>
                                <div class="mt-3 p-3 bg-blue-100 rounded-lg">
                                    <div class="text-xs font-medium text-blue-900">
                                        💡 Remember: A 60/100 doesn't mean your project is bad - it means there are opportunities to make it even better!
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Analysis Progress -->
                        <div id="analysisProgress" class="hidden mb-8">
                            <div class="bg-blue-50 rounded-xl p-6">
                                <div class="flex items-center space-x-3 mb-4">
                                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                                    <span class="font-semibold text-blue-900">Analyzing your application...</span>
                                </div>
                                <div class="space-y-2 text-sm text-blue-800">
                                    <div id="analysisStep1" class="flex items-center space-x-2">
                                        <i class="fas fa-circle-notch fa-spin text-blue-600"></i>
                                        <span>Extracting and scanning files...</span>
                                    </div>
                                    <div id="analysisStep2" class="flex items-center space-x-2 opacity-50">
                                        <i class="fas fa-circle text-gray-400"></i>
                                        <span>Detecting technologies and patterns...</span>
                                    </div>
                                    <div id="analysisStep3" class="flex items-center space-x-2 opacity-50">
                                        <i class="fas fa-circle text-gray-400"></i>
                                        <span>Analyzing security and quality...</span>
                                    </div>
                                    <div id="analysisStep4" class="flex items-center space-x-2 opacity-50">
                                        <i class="fas fa-circle text-gray-400"></i>
                                        <span>Generating recommendations...</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Back Button -->
                        <div class="text-center">
                            <button onclick="app.goBackToHome()" class="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 font-semibold">
                                <i class="fas fa-arrow-left mr-2"></i>Back to Main Menu
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Insert the analysis container
        const mainContent = document.querySelector('main');
        mainContent.appendChild(analysisContainer);

        // Set up file upload handler
        document.getElementById('analysisFileUpload').addEventListener('change', (e) => {
            this.handleAnalysisFileUpload(e.target.files[0]);
        });
    }

    switchAnalysisMethod(method) {
        const localTab = document.getElementById('localFolderTab');
        const uploadTab = document.getElementById('uploadFileTab');
        const localOption = document.getElementById('localFolderOption');
        const uploadOption = document.getElementById('uploadFileOption');

        if (method === 'local') {
            // Switch to local folder
            localTab.className = 'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors bg-white text-blue-600 shadow-sm';
            uploadTab.className = 'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors text-gray-600 hover:text-gray-900';
            localOption.classList.remove('hidden');
            uploadOption.classList.add('hidden');
        } else {
            // Switch to upload
            uploadTab.className = 'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors bg-white text-orange-600 shadow-sm';
            localTab.className = 'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors text-gray-600 hover:text-gray-900';
            uploadOption.classList.remove('hidden');
            localOption.classList.add('hidden');
        }
    }

    async selectLocalFolder() {
        try {
            // Check if File System Access API is supported
            if ('showDirectoryPicker' in window) {
                const directoryHandle = await window.showDirectoryPicker();
                this.selectedDirectory = directoryHandle;

                // Display selected folder
                document.getElementById('selectedFolderName').textContent = directoryHandle.name;
                document.getElementById('selectedFolderPath').textContent = `Selected: ${directoryHandle.name}`;
                document.getElementById('selectedFolderDisplay').classList.remove('hidden');

            } else {
                // Fallback for browsers that don't support File System Access API
                this.showError('Local folder browsing is not supported in this browser. Please use the upload option or try Chrome/Edge.');
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Error selecting folder:', error);
                this.showError('Error selecting folder. Please try again.');
            }
        }
    }

    async analyzeLocalFolder() {
        if (!this.selectedDirectory) {
            this.showError('Please select a folder first');
            return;
        }

        try {
            // Show progress
            document.getElementById('analysisProgress').classList.remove('hidden');
            this.updateAnalysisProgress(1);

            // Read folder contents
            const folderData = await this.readDirectoryContents(this.selectedDirectory);

            this.updateAnalysisProgress(2);

            // Send folder data for analysis
            const response = await fetch('/api/analyze-local-folder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    folder_name: this.selectedDirectory.name,
                    folder_contents: folderData
                })
            });

            this.updateAnalysisProgress(3);

            const result = await response.json();

            if (result.success) {
                this.updateAnalysisProgress(4);
                setTimeout(() => {
                    this.displayAnalysisResults(result);
                }, 1000);
            } else {
                this.showError('Error analyzing folder. Please try again.');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Network error. Please check your connection and try again.');
        }
    }

    async readDirectoryContents(directoryHandle, path = '') {
        const contents = {
            files: [],
            directories: [],
            file_contents: {}
        };

        try {
            for await (const [name, handle] of directoryHandle.entries()) {
                const fullPath = path ? `${path}/${name}` : name;

                if (handle.kind === 'file') {
                    // Skip large files and binary files
                    const file = await handle.getFile();
                    if (file.size < 1024 * 1024 && this.isTextFile(name)) { // 1MB limit
                        contents.files.push(fullPath);
                        try {
                            const text = await file.text();
                            contents.file_contents[fullPath] = text;
                        } catch (e) {
                            // Skip files that can't be read as text
                        }
                    } else {
                        contents.files.push(fullPath);
                    }
                } else if (handle.kind === 'directory') {
                    // Skip common ignore directories
                    if (!['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build'].includes(name)) {
                        contents.directories.push(fullPath);
                        // Recursively read subdirectories (limit depth)
                        if (path.split('/').length < 3) {
                            const subContents = await this.readDirectoryContents(handle, fullPath);
                            contents.files.push(...subContents.files);
                            contents.directories.push(...subContents.directories);
                            Object.assign(contents.file_contents, subContents.file_contents);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error reading directory:', error);
        }

        return contents;
    }

    isTextFile(filename) {
        const textExtensions = [
            '.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cs', '.php', '.rb', '.go', '.rs',
            '.html', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
            '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            '.md', '.txt', '.rst', '.sql', '.sh', '.bat', '.ps1',
            '.dockerfile', '.gitignore', '.gitattributes', '.editorconfig'
        ];

        const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'));
        return textExtensions.includes(ext) || filename.toLowerCase().includes('makefile') || filename.toLowerCase().includes('dockerfile');
    }

    goBackToHome() {
        // Remove analysis container if it exists
        const analysisContainer = document.getElementById('analysisContainer');
        if (analysisContainer) {
            analysisContainer.remove();
        }

        // Show primary action cards
        document.querySelector('.mb-12').style.display = 'block';

        // Hide wizard
        document.getElementById('wizardContainer').classList.add('hidden');

        // Reset any selections
        document.querySelectorAll('.primary-action-card').forEach(card => {
            card.classList.remove('selected', 'ring-4', 'ring-blue-300', 'ring-orange-300');
        });

        // Reset form data
        this.formData = {
            project: '',
            description: '',
            components: [],
            docType: '',
            focusArea: '',
            customAnswers: {}
        };

        // Reset wizard to step 1
        this.currentStep = 1;
        this.updateProgress();
    }

    async handleAnalysisFileUpload(file) {
        if (!file) return;

        if (!file.name.match(/\.(zip|tar\.gz|tar)$/i)) {
            this.showError('Please upload a ZIP or TAR file');
            return;
        }

        if (file.size > 100 * 1024 * 1024) { // 100MB limit
            this.showError('File size must be less than 100MB');
            return;
        }

        try {
            // Show progress
            document.getElementById('analysisProgress').classList.remove('hidden');
            this.updateAnalysisProgress(1);

            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/analyze-app', {
                method: 'POST',
                body: formData
            });

            this.updateAnalysisProgress(2);

            const result = await response.json();

            this.updateAnalysisProgress(3);

            if (result.success) {
                this.updateAnalysisProgress(4);
                setTimeout(() => {
                    this.displayAnalysisResults(result);
                }, 1000);
            } else {
                this.showError('Error analyzing application. Please try again.');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Network error. Please check your connection and try again.');
        }
    }

    updateAnalysisProgress(step) {
        for (let i = 1; i <= 4; i++) {
            const stepElement = document.getElementById(`analysisStep${i}`);
            if (i < step) {
                stepElement.innerHTML = `<i class="fas fa-check text-green-600"></i><span>Step ${i} completed</span>`;
                stepElement.classList.remove('opacity-50');
            } else if (i === step) {
                stepElement.innerHTML = `<i class="fas fa-circle-notch fa-spin text-blue-600"></i><span>Step ${i} in progress...</span>`;
                stepElement.classList.remove('opacity-50');
            }
        }
    }

    displayAnalysisResults(result) {
        // Store result for later use
        this.lastAnalysisResult = result;

        // Hide the wizard and show results
        document.querySelector('.max-w-4xl').style.display = 'none';

        const container = document.getElementById('resultContainer');
        if (!container) return;

        const analysis = result.analysis;
        const appType = analysis.application_type;

        container.innerHTML = `
            <div class="max-w-6xl mx-auto">
                <!-- Success Header -->
                <div class="text-center mb-8">
                    <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-microscope text-green-600 text-3xl"></i>
                    </div>
                    <h2 class="text-3xl font-bold text-gray-900 mb-2">🔍 Application Analysis Complete!</h2>
                    <p class="text-gray-600">Comprehensive analysis of your ${appType.description}</p>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <!-- Analysis Report -->
                    <div class="lg:col-span-2">
                        <div class="bg-white rounded-xl shadow-lg overflow-hidden">
                            <div class="bg-gradient-to-r from-orange-600 to-red-600 text-white p-4">
                                <div class="flex justify-between items-center">
                                    <div>
                                        <h3 class="text-lg font-semibold">${result.filename}</h3>
                                        <p class="text-orange-100 text-sm">Application Type: ${appType.description}</p>
                                    </div>
                                    <div class="flex space-x-2">
                                        <button onclick="app.downloadAnalysisReport()"
                                                class="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-3 py-2 rounded-lg text-sm transition-all">
                                            <i class="fas fa-download mr-1"></i>Download Report
                                        </button>
                                        <button onclick="app.copyAnalysisToClipboard()"
                                                class="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-3 py-2 rounded-lg text-sm transition-all">
                                            <i class="fas fa-copy mr-1"></i>Copy
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div class="p-6 max-h-96 overflow-y-auto bg-gray-50">
                                <pre class="whitespace-pre-wrap text-sm font-mono leading-relaxed">${result.report}</pre>
                            </div>
                        </div>
                    </div>

                    <!-- Analysis Summary -->
                    <div class="lg:col-span-1 space-y-6">
                        <!-- Scores -->
                        <div class="bg-white rounded-xl shadow-lg p-6">
                            <h4 class="font-semibold text-gray-900 mb-4">
                                <i class="fas fa-chart-bar mr-2 text-orange-600"></i>Analysis Scores
                            </h4>
                            <div class="space-y-4">
                                <div>
                                    <div class="flex justify-between items-center mb-1">
                                        <span class="text-sm text-gray-600">Security</span>
                                        <span class="text-sm font-semibold">${analysis.security_analysis.security_score}/100</span>
                                    </div>
                                    <div class="w-full bg-gray-200 rounded-full h-2">
                                        <div class="bg-red-500 h-2 rounded-full" style="width: ${analysis.security_analysis.security_score}%"></div>
                                    </div>
                                </div>
                                <div>
                                    <div class="flex justify-between items-center mb-1">
                                        <span class="text-sm text-gray-600">Quality</span>
                                        <span class="text-sm font-semibold">${analysis.quality_assessment.quality_score}/100</span>
                                    </div>
                                    <div class="w-full bg-gray-200 rounded-full h-2">
                                        <div class="bg-blue-500 h-2 rounded-full" style="width: ${analysis.quality_assessment.quality_score}%"></div>
                                    </div>
                                </div>
                                <div>
                                    <div class="flex justify-between items-center mb-1">
                                        <span class="text-sm text-gray-600">Architecture</span>
                                        <span class="text-sm font-semibold">${analysis.architecture_insights.architectural_score}/100</span>
                                    </div>
                                    <div class="w-full bg-gray-200 rounded-full h-2">
                                        <div class="bg-purple-500 h-2 rounded-full" style="width: ${analysis.architecture_insights.architectural_score}%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Technologies -->
                        <div class="bg-white rounded-xl shadow-lg p-6">
                            <h4 class="font-semibold text-gray-900 mb-4">
                                <i class="fas fa-code mr-2 text-blue-600"></i>Technologies Found
                            </h4>
                            <div class="space-y-2 text-sm">
                                ${Object.entries(analysis.detected_technologies).map(([category, techs]) =>
                                    `<div><strong>${category}:</strong> ${techs.join(', ')}</div>`
                                ).join('')}
                            </div>
                        </div>

                        <!-- Actions -->
                        <div class="bg-white rounded-xl shadow-lg p-6">
                            <h4 class="font-semibold text-gray-900 mb-4">
                                <i class="fas fa-tools mr-2 text-green-600"></i>Next Steps
                            </h4>
                            <div class="space-y-3">
                                <button onclick="app.startOver()"
                                        class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                                    <i class="fas fa-plus mr-2"></i>Analyze Another App
                                </button>
                                <button onclick="app.generateImprovementPlan()"
                                        class="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors">
                                    <i class="fas fa-lightbulb mr-2"></i>Generate Improvement Plan
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Scroll to results
        container.scrollIntoView({ behavior: 'smooth' });
    }

    async downloadAnalysisReport() {
        if (!this.lastAnalysisResult) return;

        try {
            const blob = new Blob([this.lastAnalysisResult.report], { type: 'text/markdown' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = this.lastAnalysisResult.filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showSuccess('Analysis report downloaded!');
        } catch (error) {
            console.error('Download error:', error);
            this.showError('Error downloading report');
        }
    }

    async copyAnalysisToClipboard() {
        if (!this.lastAnalysisResult) return;

        try {
            await navigator.clipboard.writeText(this.lastAnalysisResult.report);
            this.showSuccess('Analysis report copied to clipboard!');
        } catch (error) {
            console.error('Copy error:', error);
            this.showError('Error copying to clipboard');
        }
    }

    generateImprovementPlan() {
        if (!this.lastAnalysisResult) return;

        // Generate an improvement plan based on the analysis
        const analysis = this.lastAnalysisResult.analysis;
        const improvements = analysis.improvement_suggestions;
        const enhancements = analysis.enhancement_opportunities;

        const improvementPlan = `# 🚀 Application Improvement Plan

Based on the analysis of your application, here's a prioritized improvement plan:

## 🔥 High Priority (Immediate Actions)

${improvements.slice(0, 5).map((item, index) => `${index + 1}. ${item}`).join('\n')}

## 📈 Medium Priority (Next 2-4 weeks)

${improvements.slice(5, 10).map((item, index) => `${index + 1}. ${item}`).join('\n')}

## 🌟 Enhancement Opportunities (Long-term)

${enhancements.slice(0, 10).map((item, index) => `${index + 1}. ${item}`).join('\n')}

## 📊 Success Metrics

Track these metrics to measure improvement:
- Security score improvement (target: 90+)
- Code quality score improvement (target: 85+)
- Architecture score improvement (target: 80+)
- Reduced technical debt
- Improved performance metrics

---
Generated by Guidance Blueprint Kit Pro
`;

        // Display the improvement plan
        this.displayImprovementPlan(improvementPlan);
    }

    displayImprovementPlan(plan) {
        const container = document.getElementById('resultContainer');
        if (!container) return;

        container.innerHTML = `
            <div class="max-w-4xl mx-auto">
                <div class="text-center mb-8">
                    <div class="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-rocket text-blue-600 text-3xl"></i>
                    </div>
                    <h2 class="text-3xl font-bold text-gray-900 mb-2">🚀 Your Improvement Plan</h2>
                    <p class="text-gray-600">Prioritized roadmap to enhance your application</p>
                </div>

                <div class="bg-white rounded-xl shadow-lg overflow-hidden">
                    <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4">
                        <div class="flex justify-between items-center">
                            <div>
                                <h3 class="text-lg font-semibold">Application Improvement Plan</h3>
                                <p class="text-blue-100 text-sm">Actionable steps to enhance your application</p>
                            </div>
                            <div class="flex space-x-2">
                                <button onclick="app.downloadImprovementPlan()"
                                        class="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-3 py-2 rounded-lg text-sm transition-all">
                                    <i class="fas fa-download mr-1"></i>Download Plan
                                </button>
                                <button onclick="app.copyImprovementPlan()"
                                        class="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-3 py-2 rounded-lg text-sm transition-all">
                                    <i class="fas fa-copy mr-1"></i>Copy
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="p-6">
                        <pre class="whitespace-pre-wrap text-sm leading-relaxed">${plan}</pre>
                    </div>
                </div>

                <div class="text-center mt-8">
                    <button onclick="app.startOver()"
                            class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold mr-4">
                        <i class="fas fa-plus mr-2"></i>Analyze Another Application
                    </button>
                    <button onclick="history.back()"
                            class="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 font-semibold">
                        <i class="fas fa-arrow-left mr-2"></i>Back to Analysis
                    </button>
                </div>
            </div>
        `;

        this.currentImprovementPlan = plan;
        container.scrollIntoView({ behavior: 'smooth' });
    }

    async downloadImprovementPlan() {
        if (!this.currentImprovementPlan) return;

        try {
            const blob = new Blob([this.currentImprovementPlan], { type: 'text/markdown' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'improvement-plan.md';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showSuccess('Improvement plan downloaded!');
        } catch (error) {
            console.error('Download error:', error);
            this.showError('Error downloading plan');
        }
    }

    async copyImprovementPlan() {
        if (!this.currentImprovementPlan) return;

        try {
            await navigator.clipboard.writeText(this.currentImprovementPlan);
            this.showSuccess('Improvement plan copied to clipboard!');
        } catch (error) {
            console.error('Copy error:', error);
            this.showError('Error copying to clipboard');
        }
    }

    inferProjectType(components) {
        // Create a smart project type based on selected components
        const types = [];

        if (components.includes('frontend')) types.push('frontend');
        if (components.includes('backend')) types.push('backend');
        if (components.includes('mobile')) types.push('mobile');
        if (components.includes('desktop')) types.push('desktop');
        if (components.includes('database')) types.push('database');
        if (components.includes('ai')) types.push('ai');

        // Return the most comprehensive description
        if (types.length > 1) {
            return `full-stack-${types.join('-')}`;
        } else if (types.length === 1) {
            return types[0];
        } else {
            return 'web-app'; // fallback
        }
    }

    loadDynamicQuestions() {
        const questionsContainer = document.getElementById('dynamicQuestions');
        const docType = this.formData.docType;
        const components = this.formData.components;
        const projectName = this.formData.project.toLowerCase();
        const description = this.formData.description.toLowerCase();

        let questions = this.getBaseQuestions(docType);

        // Add component-specific questions
        questions = questions.concat(this.getComponentQuestions(components));

        // Add context-specific questions based on project description
        questions = questions.concat(this.getContextualQuestions(projectName, description, docType));

        // Remove duplicates and limit to reasonable number
        questions = this.deduplicateQuestions(questions).slice(0, 8);

        questionsContainer.innerHTML = questions.map(q => this.renderQuestion(q)).join('');
    }

    getBaseQuestions(docType) {
        const baseQuestions = {
            'prd': [
                {
                    id: 'target_users',
                    question: 'Who are your primary users?',
                    type: 'text',
                    placeholder: 'e.g., Students, instructors, administrators'
                },
                {
                    id: 'main_problem',
                    question: 'What specific problem does this solve?',
                    type: 'textarea',
                    placeholder: 'Be specific about the pain points you\'re addressing'
                },
                {
                    id: 'success_metrics',
                    question: 'How will you measure success?',
                    type: 'text',
                    placeholder: 'e.g., User engagement, completion rates, revenue'
                }
            ],
            'readme': [
                {
                    id: 'main_features',
                    question: 'What are the key features users should know about?',
                    type: 'textarea',
                    placeholder: 'List the most important capabilities'
                },
                {
                    id: 'tech_stack',
                    question: 'What technologies does it use?',
                    type: 'text',
                    placeholder: 'e.g., React, Node.js, Python, PostgreSQL'
                }
            ],
            'mvp': [
                {
                    id: 'core_value',
                    question: 'What\'s your unique value proposition?',
                    type: 'textarea',
                    placeholder: 'What makes this different from existing solutions?'
                },
                {
                    id: 'must_have_features',
                    question: 'What features are absolutely essential for launch?',
                    type: 'textarea',
                    placeholder: 'Focus on the minimum viable set'
                }
            ],
            'audit': [
                {
                    id: 'security_concerns',
                    question: 'What are your main security concerns?',
                    type: 'textarea',
                    placeholder: 'e.g., Data protection, user authentication, API security'
                },
                {
                    id: 'current_stage',
                    question: 'What stage is your project in?',
                    type: 'select',
                    options: ['Planning', 'Development', 'Testing', 'Production', 'Maintenance']
                }
            ]
        };

        return baseQuestions[docType] || [];
    }

    getComponentQuestions(components) {
        const questions = [];

        if (components.includes('frontend') && components.includes('backend')) {
            questions.push({
                id: 'api_design',
                question: 'How will your frontend and backend communicate?',
                type: 'select',
                options: ['REST API', 'GraphQL', 'WebSocket', 'gRPC', 'Not sure yet']
            });
        }

        if (components.includes('mobile')) {
            questions.push({
                id: 'mobile_platforms',
                question: 'Which mobile platforms do you need to support?',
                type: 'select',
                options: ['iOS only', 'Android only', 'Both iOS and Android', 'Cross-platform (React Native/Flutter)']
            });

            questions.push({
                id: 'offline_support',
                question: 'Do you need offline functionality?',
                type: 'select',
                options: ['Yes, full offline support', 'Partial offline support', 'Online only', 'Not sure']
            });
        }

        if (components.includes('database')) {
            questions.push({
                id: 'data_type',
                question: 'What type of data will you primarily store?',
                type: 'select',
                options: ['User profiles and content', 'Transactional data', 'Analytics/metrics', 'Files and media', 'Real-time data']
            });
        }

        if (components.includes('ai')) {
            questions.push({
                id: 'ai_purpose',
                question: 'What will AI/ML be used for?',
                type: 'select',
                options: ['Recommendations', 'Content generation', 'Data analysis', 'Automation', 'Personalization']
            });
        }

        return questions;
    }

    getContextualQuestions(projectName, description, docType) {
        const questions = [];
        const isTrainingPlatform = projectName.includes('training') || description.includes('training') ||
                                 projectName.includes('learning') || description.includes('learning') ||
                                 projectName.includes('course') || description.includes('course') ||
                                 projectName.includes('education') || description.includes('education');

        if (isTrainingPlatform) {
            questions.push({
                id: 'learning_type',
                question: 'What type of training/learning will this support?',
                type: 'select',
                options: ['Video courses', 'Interactive tutorials', 'Live training sessions', 'Self-paced learning', 'Blended learning']
            });

            questions.push({
                id: 'user_roles',
                question: 'What user roles do you need?',
                type: 'select',
                options: ['Students only', 'Students and instructors', 'Students, instructors, and admins', 'Enterprise with managers']
            });

            if (docType === 'prd') {
                questions.push({
                    id: 'assessment_needs',
                    question: 'Do you need assessment/testing features?',
                    type: 'select',
                    options: ['Quizzes and tests', 'Assignments and projects', 'Peer reviews', 'Certifications', 'No assessments']
                });

                questions.push({
                    id: 'progress_tracking',
                    question: 'What progress tracking do you need?',
                    type: 'select',
                    options: ['Basic completion tracking', 'Detailed analytics', 'Learning paths', 'Competency mapping', 'Custom reporting']
                });
            }
        }

        // Add more contextual questions based on other keywords
        if (projectName.includes('ecommerce') || description.includes('shop') || description.includes('store')) {
            questions.push({
                id: 'payment_methods',
                question: 'What payment methods do you need to support?',
                type: 'select',
                options: ['Credit cards only', 'PayPal and cards', 'Cryptocurrency', 'Multiple payment gateways', 'Not sure yet']
            });
        }

        return questions;
    }

    deduplicateQuestions(questions) {
        const seen = new Set();
        return questions.filter(q => {
            if (seen.has(q.id)) {
                return false;
            }
            seen.add(q.id);
            return true;
        });
    }

    renderQuestion(question) {
        let inputHtml = '';

        switch (question.type) {
            case 'text':
                inputHtml = `<input type="text" id="${question.id}" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500" placeholder="${question.placeholder || ''}">`;
                break;
            case 'textarea':
                inputHtml = `<textarea id="${question.id}" rows="3" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500" placeholder="${question.placeholder || ''}"></textarea>`;
                break;
            case 'select':
                const options = question.options.map(opt => `<option value="${opt}">${opt}</option>`).join('');
                inputHtml = `<select id="${question.id}" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500">
                    <option value="">Choose an option...</option>
                    ${options}
                </select>`;
                break;
        }

        return `
            <div class="space-y-2">
                <label class="block text-sm font-medium text-gray-700">${question.question}</label>
                ${inputHtml}
            </div>
        `;
    }

    collectCustomAnswers() {
        const questionsContainer = document.getElementById('dynamicQuestions');
        const inputs = questionsContainer.querySelectorAll('input, textarea, select');

        inputs.forEach(input => {
            if (input.value.trim()) {
                this.formData.customQuestions[input.id] = input.value.trim();
            }
        });
    }

    updateSummary() {
        document.getElementById('summaryProject').textContent = this.formData.project || '-';
        document.getElementById('summaryType').textContent = this.getDocTypeLabel(this.formData.docType) || '-';
        document.getElementById('summaryFocus').textContent = this.getFocusLabel(this.formData.claims_scope) || '-';

        // Update deliverables list
        const deliverables = this.getDeliverables(this.formData.docType);
        document.getElementById('deliverablesList').innerHTML = deliverables.map(item =>
            `<div class="flex items-center space-x-2">
                <i class="fas fa-check text-green-600"></i>
                <span>${item}</span>
            </div>`
        ).join('');
    }

    getDocTypeLabel(type) {
        const labels = {
            'prd': 'Product Requirements Document',
            'readme': 'README Documentation',
            'mvp': 'MVP Planning Document',
            'audit': 'Security & Compliance Audit'
        };
        return labels[type] || type;
    }

    getFocusLabel(focus) {
        const labels = {
            'security': 'Security & Compliance',
            'performance': 'Performance & Scalability',
            'ux': 'User Experience',
            'app': 'Complete Application'
        };
        return labels[focus] || focus;
    }

    getDeliverables(docType) {
        const deliverables = {
            'prd': [
                'Executive summary and project scope',
                'User stories and acceptance criteria',
                'Feature specifications with priorities',
                'Technical requirements and constraints',
                'Success metrics and KPIs'
            ],
            'readme': [
                'Project overview and description',
                'Installation and setup instructions',
                'Usage examples and API documentation',
                'Contributing guidelines',
                'License and contact information'
            ],
            'mvp': [
                'Core value proposition definition',
                'Minimum viable feature set',
                'User journey and experience flow',
                'Success metrics and validation plan',
                'Launch timeline and milestones'
            ],
            'audit': [
                'Security vulnerability assessment',
                'Compliance checklist (GDPR, SOC2, etc.)',
                'Code quality and best practices review',
                'Risk assessment and mitigation plan',
                'Recommendations and action items'
            ]
        };
        return deliverables[docType] || [];
    }

    handleProfileChange(profileKey) {
        if (!profileKey) {
            this.formData.mode = '';
            this.formData.modules = [];
            this.formData.claims_scope = 'app';
        } else {
            const profile = this.profiles[profileKey];
            this.formData.mode = profileKey;
            this.formData.modules = profile.modules;
            this.formData.claims_scope = profile.claims_scope;
        }
        this.updateModuleCheckboxes();
        this.updateClaimsScope();
    }

    handleModuleChange(module, checked) {
        if (checked) {
            if (!this.formData.modules.includes(module)) {
                this.formData.modules.push(module);
            }
        } else {
            this.formData.modules = this.formData.modules.filter(m => m !== module);
        }
    }

    updateModuleCheckboxes() {
        document.querySelectorAll('input[name="modules"]').forEach(checkbox => {
            checkbox.checked = this.formData.modules.includes(checkbox.value);
        });
    }

    updateClaimsScope() {
        const claimsScope = document.getElementById('claimsScope');
        if (claimsScope) {
            claimsScope.value = this.formData.claims_scope;
        }
    }

    async handleFileUpload(file) {
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            this.showLoading('Analyzing repository...');
            const response = await fetch('/api/upload-repo', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                this.formData.evidence_data = result.findings;
                this.formData.repo_scan = true;
                this.showSuccess(`Repository analyzed: ${result.findings.length} findings`);
                this.displayFindings(result.findings);
            } else {
                this.showError('Error analyzing repository');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Error uploading repository');
        } finally {
            this.hideLoading();
        }
    }

    displayFindings(findings) {
        const container = document.getElementById('findingsContainer');
        if (!container) return;

        container.innerHTML = '';
        
        if (findings.length === 0) {
            container.innerHTML = '<p class="text-gray-500">No findings to display</p>';
            return;
        }

        const table = document.createElement('table');
        table.className = 'w-full border-collapse border border-gray-300';
        
        table.innerHTML = `
            <thead>
                <tr class="bg-gray-50">
                    <th class="border border-gray-300 px-4 py-2 text-left">Claim</th>
                    <th class="border border-gray-300 px-4 py-2 text-left">Evidence</th>
                    <th class="border border-gray-300 px-4 py-2 text-left">Status</th>
                    <th class="border border-gray-300 px-4 py-2 text-left">Notes</th>
                </tr>
            </thead>
            <tbody>
                ${findings.map(finding => `
                    <tr>
                        <td class="border border-gray-300 px-4 py-2">${finding.claim}</td>
                        <td class="border border-gray-300 px-4 py-2">${finding.evidence}</td>
                        <td class="border border-gray-300 px-4 py-2">${finding.status}</td>
                        <td class="border border-gray-300 px-4 py-2">${finding.notes}</td>
                    </tr>
                `).join('')}
            </tbody>
        `;
        
        container.appendChild(table);
    }

    async generateDocument() {
        if (this.isGenerating) return;

        this.isGenerating = true;
        document.getElementById('generateButtonText').textContent = 'Generating...';
        document.getElementById('generatingState').classList.remove('hidden');

        try {
            // Map doc type to profile and modules
            const profileMap = {
                'prd': 'full-eval',
                'readme': 'full-eval',
                'mvp': 'full-eval',
                'audit': 'sec-audit'
            };

            const requestData = {
                project: this.formData.project,
                profile: profileMap[this.formData.docType] || 'full-eval',
                modules: [],
                claims_scope: this.formData.claims_scope,
                evidence_data: this.formData.evidence_data,
                repo_scan: this.formData.repo_scan,
                tags: {
                    doc_type: this.formData.docType,
                    project_type: this.formData.projectType,
                    description: this.formData.description,
                    ...this.formData.customQuestions
                }
            };

            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (result.success) {
                this.displayResult(result);
                this.showSuccess('🎉 Your documentation is ready!');
            } else {
                this.showError('Error generating document. Please try again.');
            }
        } catch (error) {
            console.error('Generation error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.isGenerating = false;
            document.getElementById('generateButtonText').textContent = 'Generate My Documentation';
            document.getElementById('generatingState').classList.add('hidden');
        }
    }

    startOver() {
        // Use the new navigation system
        this.goBackToHome();

        // Clear any results
        const resultContainer = document.getElementById('resultContainer');
        if (resultContainer) {
            resultContainer.innerHTML = '';
        }
    }

    displayResult(result) {
        // Hide the wizard and show results
        document.querySelector('.max-w-4xl').style.display = 'none';

        const container = document.getElementById('resultContainer');
        if (!container) return;

        container.innerHTML = `
            <div class="max-w-6xl mx-auto">
                <!-- Success Header -->
                <div class="text-center mb-8">
                    <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-check text-green-600 text-3xl"></i>
                    </div>
                    <h2 class="text-3xl font-bold text-gray-900 mb-2">🎉 Your Documentation is Ready!</h2>
                    <p class="text-gray-600">High-quality ${this.getDocTypeLabel(this.formData.docType)} generated in seconds</p>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <!-- Document Preview -->
                    <div class="lg:col-span-2">
                        <div class="bg-white rounded-xl shadow-lg overflow-hidden">
                            <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4">
                                <div class="flex justify-between items-center">
                                    <div>
                                        <h3 class="text-lg font-semibold">${result.filename}</h3>
                                        <p class="text-blue-100 text-sm">${result.quality_score.words} words • Quality Score: ${result.quality_score.score}/100</p>
                                    </div>
                                    <div class="flex space-x-2">
                                        <button onclick="app.downloadDocument('${result.document_id}')"
                                                class="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-3 py-2 rounded-lg text-sm transition-all">
                                            <i class="fas fa-download mr-1"></i>Download
                                        </button>
                                        <button onclick="app.copyToClipboard('${result.document_id}')"
                                                class="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-3 py-2 rounded-lg text-sm transition-all">
                                            <i class="fas fa-copy mr-1"></i>Copy
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div class="p-6 max-h-96 overflow-y-auto bg-gray-50">
                                <pre class="whitespace-pre-wrap text-sm font-mono leading-relaxed">${result.markdown_content}</pre>
                            </div>
                        </div>
                    </div>

                    <!-- Actions & Info -->
                    <div class="lg:col-span-1 space-y-6">
                        <!-- Quality Metrics -->
                        <div class="bg-white rounded-xl shadow-lg p-6">
                            <h4 class="font-semibold text-gray-900 mb-4">
                                <i class="fas fa-chart-line mr-2 text-green-600"></i>Quality Metrics
                            </h4>
                            <div class="space-y-3">
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Overall Score</span>
                                    <div class="flex items-center">
                                        <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                                            <div class="bg-green-500 h-2 rounded-full" style="width: ${result.quality_score.score}%"></div>
                                        </div>
                                        <span class="text-sm font-semibold">${result.quality_score.score}/100</span>
                                    </div>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-sm text-gray-600">Word Count</span>
                                    <span class="text-sm font-medium">${result.quality_score.words}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-sm text-gray-600">Completeness</span>
                                    <span class="text-sm font-medium text-green-600">Excellent</span>
                                </div>
                            </div>
                        </div>

                        <!-- Export Options -->
                        <div class="bg-white rounded-xl shadow-lg p-6">
                            <h4 class="font-semibold text-gray-900 mb-4">
                                <i class="fas fa-download mr-2 text-blue-600"></i>Export Options
                            </h4>
                            <div class="space-y-2">
                                <button onclick="app.exportDocument('${result.document_id}', 'md')"
                                        class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors">
                                    <i class="fab fa-markdown mr-2 text-gray-600"></i>Markdown (.md)
                                </button>
                                <button onclick="app.exportDocument('${result.document_id}', 'html')"
                                        class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors">
                                    <i class="fas fa-code mr-2 text-orange-600"></i>HTML (.html)
                                </button>
                                <button onclick="app.exportDocument('${result.document_id}', 'json')"
                                        class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors">
                                    <i class="fas fa-brackets-curly mr-2 text-green-600"></i>JSON (.json)
                                </button>
                                <button onclick="app.exportDocument('${result.document_id}', 'txt')"
                                        class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors">
                                    <i class="fas fa-file-alt mr-2 text-gray-600"></i>Plain Text (.txt)
                                </button>
                            </div>
                        </div>

                        <!-- Actions -->
                        <div class="bg-white rounded-xl shadow-lg p-6">
                            <h4 class="font-semibold text-gray-900 mb-4">
                                <i class="fas fa-tools mr-2 text-purple-600"></i>What's Next?
                            </h4>
                            <div class="space-y-3">
                                <button onclick="app.startOver()"
                                        class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                                    <i class="fas fa-plus mr-2"></i>Create Another Document
                                </button>
                                <button onclick="app.shareDocument('${result.document_id}')"
                                        class="w-full bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors">
                                    <i class="fas fa-share mr-2"></i>Share Document
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Store result for later use
        this.lastResult = result;

        // Scroll to results
        container.scrollIntoView({ behavior: 'smooth' });
    }

    async downloadDocument(documentId) {
        try {
            const response = await fetch(`/api/document/${documentId}`);
            const blob = await response.blob();
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = this.lastResult.filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Download error:', error);
            this.showError('Error downloading document');
        }
    }

    async copyToClipboard(documentId) {
        try {
            await navigator.clipboard.writeText(this.lastResult.markdown_content);
            this.showSuccess('Document copied to clipboard!');
        } catch (error) {
            console.error('Copy error:', error);
            this.showError('Error copying to clipboard');
        }
    }

    async exportDocument(documentId, format) {
        try {
            const response = await fetch(`/api/export/${documentId}/${format}`);
            const blob = await response.blob();

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = this.lastResult.filename.replace('.md', `.${format}`);
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            this.showSuccess(`Document exported as ${format.toUpperCase()}!`);
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Error exporting document');
        }
    }

    async shareDocument(documentId) {
        try {
            const response = await fetch(`/api/share/${documentId}`);
            const result = await response.json();

            if (result.success) {
                // Show share modal or copy link
                await navigator.clipboard.writeText(result.share_url);
                this.showSuccess('Share link copied to clipboard!');
            } else {
                this.showError('Error creating share link');
            }
        } catch (error) {
            console.error('Share error:', error);
            this.showError('Error creating share link');
        }
    }

    showLoading(message) {
        const loader = document.getElementById('loadingIndicator');
        if (loader) {
            loader.textContent = message;
            loader.classList.remove('hidden');
        }
    }

    hideLoading() {
        const loader = document.getElementById('loadingIndicator');
        if (loader) {
            loader.classList.add('hidden');
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    selectQuickMode(mode) {
        const modeMap = {
            'prd': 'full-eval',
            'readme': 'full-eval',
            'mvp': 'full-eval',
            'audit': 'sec-audit'
        };

        const profileKey = modeMap[mode] || 'full-eval';
        const profileSelect = document.getElementById('profileSelect');
        if (profileSelect) {
            profileSelect.value = profileKey;
            this.handleProfileChange(profileKey);
        }
    }

    updateUI() {
        // Update any UI elements based on current state
        this.updateModuleCheckboxes();
        this.updateClaimsScope();
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new GuidanceApp();
});

// Navigation functions
function showDocumentGenerator() {
    // Update tab styles
    document.getElementById('docGeneratorTab').className = 'nav-tab active py-4 px-1 border-b-2 border-blue-500 font-medium text-sm text-blue-600';
    document.getElementById('validationServiceTab').className = 'nav-tab py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300';

    // Show/hide sections
    document.getElementById('documentGeneratorSection').classList.remove('hidden');
    document.getElementById('validationServiceSection').classList.add('hidden');
}

function showValidationService() {
    // Update tab styles
    document.getElementById('validationServiceTab').className = 'nav-tab active py-4 px-1 border-b-2 border-orange-500 font-medium text-sm text-orange-600';
    document.getElementById('docGeneratorTab').className = 'nav-tab py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300';

    // Show/hide sections
    document.getElementById('documentGeneratorSection').classList.add('hidden');
    document.getElementById('validationServiceSection').classList.remove('hidden');

    // Check validation service status
    checkValidationServiceStatus();
}

// Validation Service Integration
let currentValidationId = null;
const VALIDATION_API_BASE = 'http://localhost:8002';

async function checkValidationServiceStatus() {
    try {
        const response = await fetch(`${VALIDATION_API_BASE}/`);
        const data = await response.json();
        document.getElementById('serviceStatusNav').innerHTML = `
            <div class="w-2 h-2 bg-green-400 rounded-full"></div>
            <span class="text-xs text-gray-500">Validation Service Active</span>
        `;
    } catch (error) {
        document.getElementById('serviceStatusNav').innerHTML = `
            <div class="w-2 h-2 bg-red-400 rounded-full"></div>
            <span class="text-xs text-gray-500">Validation Service Offline</span>
        `;
    }
}

// Upload project file
async function uploadProject() {
    const fileInput = document.getElementById('fileInput');
    const projectName = document.getElementById('projectName').value;

    if (!fileInput.files[0]) {
        alert('Please select a file to upload');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    if (projectName) formData.append('project_name', projectName);

    try {
        showValidationResults();
        const response = await fetch(`${VALIDATION_API_BASE}/validate/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        currentValidationId = result.validation_id;
        pollValidationStatus();
    } catch (error) {
        alert('Upload failed: ' + error.message);
        hideValidationResults();
    }
}

// Validate Git repository
async function validateGitRepo() {
    const gitUrl = document.getElementById('gitUrl').value;
    const branch = document.getElementById('gitBranch').value;
    const projectName = document.getElementById('gitProjectName').value;

    if (!gitUrl) {
        alert('Please enter a Git repository URL');
        return;
    }

    try {
        showValidationResults();
        const response = await fetch(`${VALIDATION_API_BASE}/validate/git`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                git_url: gitUrl,
                branch: branch || 'main',
                project_name: projectName
            })
        });

        const result = await response.json();
        currentValidationId = result.validation_id;
        pollValidationStatus();
    } catch (error) {
        alert('Validation failed: ' + error.message);
        hideValidationResults();
    }
}

// Poll validation status
async function pollValidationStatus() {
    if (!currentValidationId) return;

    try {
        const response = await fetch(`${VALIDATION_API_BASE}/validate/${currentValidationId}/status`);
        const status = await response.json();

        updateValidationProgress(status.progress, status.message);

        if (status.status === 'completed') {
            await loadValidationResults();
        } else if (status.status === 'failed') {
            updateValidationStatus('❌ Validation Failed', status.message);
        } else {
            setTimeout(pollValidationStatus, 2000);
        }
    } catch (error) {
        updateValidationStatus('❌ Error', error.message);
    }
}

// Load validation results
async function loadValidationResults() {
    try {
        const response = await fetch(`${VALIDATION_API_BASE}/validate/${currentValidationId}/results`);
        const results = await response.json();

        displayValidationResults(results);
    } catch (error) {
        updateValidationStatus('❌ Error loading results', error.message);
    }
}

// Display validation results
function displayValidationResults(results) {
    updateValidationStatus('✅ Validation Complete', 'Analysis completed successfully');

    // Show scores
    document.getElementById('securityScore').textContent = results.scores.security;
    document.getElementById('qualityScore').textContent = results.scores.quality;
    document.getElementById('architectureScore').textContent = results.scores.architecture;
    document.getElementById('scoresSection').classList.remove('hidden');

    // Show recommendations
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = '';
    results.recommendations.slice(0, 5).forEach(rec => {
        const div = document.createElement('div');
        div.className = 'flex items-start space-x-2 p-3 bg-gray-50 rounded-lg';
        div.innerHTML = `
            <i class="fas fa-lightbulb text-yellow-500 mt-1"></i>
            <span class="text-sm text-gray-700">${rec}</span>
        `;
        recommendationsList.appendChild(div);
    });
    document.getElementById('recommendationsSection').classList.remove('hidden');

    // Show actions
    document.getElementById('actionsSection').classList.remove('hidden');
    document.getElementById('progressSection').classList.add('hidden');
}

// Helper functions for validation service
function showValidationResults() {
    document.getElementById('validationResults').classList.remove('hidden');
    document.getElementById('progressSection').classList.remove('hidden');
    document.getElementById('scoresSection').classList.add('hidden');
    document.getElementById('recommendationsSection').classList.add('hidden');
    document.getElementById('actionsSection').classList.add('hidden');
}

function hideValidationResults() {
    document.getElementById('validationResults').classList.add('hidden');
}

function updateValidationProgress(progress, message) {
    document.getElementById('progressBar').style.width = `${progress}%`;
    document.getElementById('progressText').textContent = `${progress}%`;
    updateValidationStatus('🔄 Processing', message);
}

function updateValidationStatus(status, message) {
    document.getElementById('validationStatus').innerHTML = `
        <span class="text-sm font-medium">${status}</span>
        <span class="text-xs text-gray-500">${message}</span>
    `;
}

async function downloadValidationReport() {
    if (!currentValidationId) return;

    try {
        const response = await fetch(`${VALIDATION_API_BASE}/validate/${currentValidationId}/report/download`);
        const blob = await response.blob();

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `validation-report-${currentValidationId}.md`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        alert('Download failed: ' + error.message);
    }
}

function startNewValidation() {
    currentValidationId = null;
    hideValidationResults();
    document.getElementById('fileInput').value = '';
    document.getElementById('projectName').value = '';
    document.getElementById('gitUrl').value = '';
    document.getElementById('gitProjectName').value = '';
}

// File drag and drop for validation service
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');

    if (uploadArea) {
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('border-blue-400', 'bg-blue-50');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('border-blue-400', 'bg-blue-50');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('border-blue-400', 'bg-blue-50');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                document.getElementById('fileInput').files = files;
            }
        });
    }

    // Check validation service status on load
    checkValidationServiceStatus();
});
