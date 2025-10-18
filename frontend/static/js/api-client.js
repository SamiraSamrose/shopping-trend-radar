// frontend/static/js/api-client.js

const API_BASE_URL = 'http://localhost:8000/api/v1';

class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'API request failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Trends endpoints
    async getTrendingProducts(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/trends/products?${queryString}`);
    }

    async getProductDetails(productId) {
        return this.request(`/trends/products/${productId}`);
    }

    async getTrendPrediction(productId) {
        return this.request(`/trends/predictions/${productId}`);
    }

    async generateTrendReport(userType, categories = []) {
        const params = new URLSearchParams({ user_type: userType });
        categories.forEach(cat => params.append('categories', cat));
        return this.request(`/trends/report?${params.toString()}`);
    }

    async getTrendingCategories() {
        return this.request('/trends/categories');
    }

    // Products endpoints
    async compareProductPrices(productName, platforms = []) {
        const params = new URLSearchParams({ product_name: productName });
        platforms.forEach(pl => params.append('platforms', pl));
        return this.request(`/products/compare/${encodeURIComponent(productName)}?${params.toString()}`);
    }

    async getEventRecommendations(daysAhead = 30) {
        return this.request(`/products/events?days_ahead=${daysAhead}`);
    }

    async getMerchantInsights(productId) {
        return this.request(`/products/merchant-insights/${productId}`);
    }

    async getConsumerInsights(productId) {
        return this.request(`/products/consumer-insights/${productId}`);
    }

    async checkProductCompliance(productName, category, description = '') {
        const params = new URLSearchParams({
            product_name: productName,
            category: category,
            description: description
        });
        return this.request(`/products/compliance-check?${params.toString()}`);
    }

    // Alerts endpoints
    async createAlert(alertData) {
        return this.request('/alerts/', {
            method: 'POST',
            body: JSON.stringify(alertData)
        });
    }

    async getUserAlerts(userId) {
        return this.request(`/alerts/user/${userId}`);
    }

    async updateAlert(alertId, alertData) {
        return this.request(`/alerts/${alertId}`, {
            method: 'PUT',
            body: JSON.stringify(alertData)
        });
    }

    async deleteAlert(alertId) {
        return this.request(`/alerts/${alertId}`, {
            method: 'DELETE'
        });
    }

    async checkAlert(alertId) {
        return this.request(`/alerts/${alertId}/check`);
    }
}

// Export for use in other scripts
const apiClient = new APIClient();
