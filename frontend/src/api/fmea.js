// Import the authenticated axios client
import api from '../axios';

class FMEAApi {
    constructor() {
        // Token management is now handled by the axios interceptor
        this.token = null;
    }

    setToken(token) {
        this.token = token;
        // Store in localStorage for axios interceptor
        if (token) {
            localStorage.setItem('token', token);
        }
    }

    async ensureValidToken() {
        // Check if token exists in localStorage
        let token = localStorage.getItem('token');
        if (!token) {
            await this.devLogin();
        }
        return token;
    }

    // Development login
    async devLogin() {
        try {
            // Use native fetch for dev-login to avoid circular dependency
            const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
            
            const response = await fetch(`${baseURL}/auth/dev-login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                const token = data.access_token;
                
                if (token) {
                    this.setToken(token);
                    
                    // Store user object in localStorage (create default if not provided)
                    const user = data.user || {
                        id: 'dev-user-123',
                        username: 'dev-user',
                        role: 'admin',
                        email: 'dev@example.com'
                    };
                    localStorage.setItem('user', JSON.stringify(user));
                    
                    console.log('[fmea.js] devLogin: Token and user stored successfully');
                    return data;
                } else {
                    throw new Error('No access token received');
                }
            } else {
                const errorText = await response.text();
                throw new Error(`Dev login failed: ${response.status} ${errorText}`);
            }
        } catch (error) {
            console.error('[fmea.js] Dev login error:', error);
            throw error;
        }
    }

    // Generate Hazard Analysis data using AI
    async generateHazardAnalysis(component, hazardType = 'general') {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/hazard-analysis/generate`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({
                    component: component,
                    hazard_type: hazardType
                }),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to generate hazard analysis');
            }
        } catch (error) {
            console.error('Generate hazard analysis error:', error);
            throw error;
        }
    }

    // Save Hazard Analysis to project
    async saveHazardAnalysisToProject(projectId, hazardAnalysisData) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/projects/${projectId}/hazard-analyses`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(hazardAnalysisData),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to save hazard analysis');
            }
        } catch (error) {
            console.error('Save hazard analysis error:', error);
            throw error;
        }
    }

    // Get Hazard Analysis data from project
    async getHazardAnalysesFromProject(projectId) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/projects/${projectId}/hazard-analyses`, {
                method: 'GET',
                headers: this.getHeaders(),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to fetch hazard analysis data');
            }
        } catch (error) {
            console.error('Get hazard analyses error:', error);
            throw error;
        }
    }

    // Generate CAPA data using AI
    async generateCapa(component, capaType = 'general') {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/capa/generate`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({
                    component: component,
                    capa_type: capaType
                }),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to generate CAPA');
            }
        } catch (error) {
            console.error('Generate CAPA error:', error);
            throw error;
        }
    }

    // Save CAPA to project
    async saveCapaToProject(projectId, capaData) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/projects/${projectId}/capas`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(capaData),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to save CAPA');
            }
        } catch (error) {
            console.error('Save CAPA error:', error);
            throw error;
        }
    }

    // Get CAPA data from project
    async getCapasFromProject(projectId) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/projects/${projectId}/capas`, {
                method: 'GET',
                headers: this.getHeaders(),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to fetch CAPA data');
            }
        } catch (error) {
            console.error('Get CAPAs error:', error);
            throw error;
        }
    }

    // Generate Risk Evaluation Report using AI
    async generateRiskEvaluationReport(data) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/risk-evaluation-report/generate`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to generate risk evaluation report');
            }
        } catch (error) {
            console.error('Generate risk evaluation report error:', error);
            throw error;
        }
    }

    // Save Risk Evaluation Report to project
    async saveRiskEvaluationReport(data) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/risk-evaluation-report/save`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to save risk evaluation report');
            }
        } catch (error) {
            console.error('Save risk evaluation report error:', error);
            throw error;
        }
    }

    // Generate Residual Risk & Risk-Benefit analysis using AI
    async generateResidualRiskRiskBenefit(data) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/residual-risk-risk-benefit/generate`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to generate residual risk risk-benefit analysis');
            }
        } catch (error) {
            console.error('Generate residual risk risk-benefit analysis error:', error);
            throw error;
        }
    }

    // Save Residual Risk & Risk-Benefit analysis to project
    async saveResidualRiskRiskBenefit(data) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/residual-risk-risk-benefit/save`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to save residual risk risk-benefit analysis');
            }
        } catch (error) {
            console.error('Save residual risk risk-benefit analysis error:', error);
            throw error;
        }
    }

    // Generate Risk Traceability Matrix using AI
    async generateRiskTraceabilityMatrix(data) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/risk-traceability-matrix/generate`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to generate risk traceability matrix');
            }
        } catch (error) {
            console.error('Generate risk traceability matrix error:', error);
            throw error;
        }
    }

    // Save Risk Traceability Matrix to project
    async saveRiskTraceabilityMatrix(data) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/risk-traceability-matrix/save`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to save risk traceability matrix');
            }
        } catch (error) {
            console.error('Save risk traceability matrix error:', error);
            throw error;
        }
    }

    // Generate Risk Management Plan using AI
    async generateRiskManagementPlan(data) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/risk-management-plan/generate`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to generate risk management plan');
            }
        } catch (error) {
            console.error('Generate risk management plan error:', error);
            throw error;
        }
    }

    // Save Risk Management Plan to project
    async saveRiskManagementPlan(data) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/risk-management-plan/save`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to save risk management plan');
            }
        } catch (error) {
            console.error('Save risk management plan error:', error);
            throw error;
        }
    }

    // Generate Risk Management Report using AI
    async generateRiskManagementReport(data) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/risk-management-report/generate`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to generate risk management report');
            }
        } catch (error) {
            console.error('Generate risk management report error:', error);
            throw error;
        }
    }

    // Save Risk Management Report to project
    async saveRiskManagementReport(data) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/risk-management-report/save`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to save risk management report');
            }
        } catch (error) {
            console.error('Save risk management report error:', error);
            throw error;
        }
    }

    // Generate Word report using template
    async generateWordReport(data) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/risk-management-report/generate-word`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(data),
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Failed to generate Word report');
            }
        } catch (error) {
            console.error('Generate Word report error:', error);
            throw error;
        }
    }

    // Download generated Word report
    async downloadWordReport(filename) {
        try {
            await this.ensureValidToken();
            
            const response = await fetch(`${this.baseURL}/fmea/risk-management-report/download-word/${filename}`);

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                return true;
            } else {
                throw new Error('Failed to download Word report');
            }
        } catch (error) {
            console.error('Download Word report error:', error);
            throw error;
        }
    }

    // Get all projects - uses authenticated axios client
    async getProjects() {
        try {
            await this.ensureValidToken();
            
            // Use the authenticated axios client - interceptor handles auth header
            const response = await api.get('/projects');
            return response.data;
        } catch (error) {
            console.error('[fmea.js] Get projects error:', error);
            if (error.response?.status === 401) {
                throw new Error('You\'re not logged in or your session expired. Please refresh the page.');
            }
            throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch projects');
        }
    }

    // Create a new project - uses authenticated axios client
    async createProject(projectData) {
        try {
            await this.ensureValidToken();
            
            // Use the authenticated axios client - interceptor handles auth header
            const response = await api.post('/projects', projectData);
            return response.data;
        } catch (error) {
            console.error('[fmea.js] Create project error:', error);
            if (error.response?.status === 401) {
                throw new Error('You\'re not logged in or your session expired. Please refresh the page.');
            }
            throw new Error(error.response?.data?.detail || error.message || 'Failed to create project');
        }
    }

    // Create FMEA row - uses authenticated axios client
    async createFMEA(projectId, fmeaData) {
        try {
            await this.ensureValidToken();
            
            // Use the authenticated axios client - interceptor handles auth header
            const response = await api.post(`/projects/${projectId}/fmea`, fmeaData);
            return response.data;
        } catch (error) {
            console.error('[fmea.js] Create FMEA error:', error);
            if (error.response?.status === 401) {
                throw new Error('You\'re not logged in or your session expired. Please refresh the page.');
            }
            throw new Error(error.response?.data?.detail || error.message || 'Failed to create FMEA');
        }
    }
}

// Create a global instance
const fmeaApi = new FMEAApi();

// Initialize with token from localStorage if available
const existingToken = localStorage.getItem('token');
const existingUser = localStorage.getItem('user');

console.log('fmea.js initialization:', {
    hasExistingToken: !!existingToken,
    hasExistingUser: !!existingUser,
    tokenLength: existingToken ? existingToken.length : 0,
    userLength: existingUser ? existingUser.length : 0
});

if (existingToken) {
    fmeaApi.setToken(existingToken);
    console.log('fmeaApi initialized with existing token');
}

if (existingUser) {
    console.log('fmeaApi: Existing user found in localStorage');
} else {
    console.log('fmeaApi: No existing user found in localStorage');
}

// Make it globally available
window.fmeaApi = fmeaApi;
console.log('fmeaApi assigned to window.fmeaApi:', !!window.fmeaApi);

export default fmeaApi;