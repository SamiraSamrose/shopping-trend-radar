// frontend/static/js/main.js

// Global state
let currentProducts = [];
let currentFilters = {
    categories: [],
    platforms: [],
    minScore: 0.5,
    status: null
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    showLoading();
    
    try {
        // Load initial data
        await loadTrendingProducts();
        await loadTrendingCategories();
        
        // Setup event listeners
        setupEventListeners();
        
        hideLoading();
    } catch (error) {
        console.error('Initialization error:', error);
        showError('Failed to initialize application');
        hideLoading();
    }
}

function setupEventListeners() {
    // Filter buttons
    const filterButtons = document.querySelectorAll('[data-filter]');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', handleFilterClick);
    });

    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 500));
    }

    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshData);
    }

    // Min score slider
    const minScoreSlider = document.getElementById('minScoreSlider');
    if (minScoreSlider) {
        minScoreSlider.addEventListener('input', handleMinScoreChange);
    }
}

async function loadTrendingProducts() {
    try {
        const products = await apiClient.getTrendingProducts(currentFilters);
        currentProducts = products;
        renderProducts(products);
        updateStats(products);
    } catch (error) {
        console.error('Error loading products:', error);
        showError('Failed to load trending products');
    }
}

async function loadTrendingCategories() {
    try {
        const categories = await apiClient.getTrendingCategories();
        renderCategories(categories);
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

function renderProducts(products) {
    const container = document.getElementById('productsContainer');
    if (!container) return;

    if (products.length === 0) {
        container.innerHTML = '<p class="text-center">No products found matching your criteria.</p>';
        return;
    }

    container.innerHTML = products.map(product => `
        <div class="product-item fade-in" data-product-id="${product.id}">
            <div class="product-image">
                ${product.image_url ? 
                    `<img src="${product.image_url}" alt="${product.name}">` :
                    '<div class="placeholder-image">No Image</div>'
                }
            </div>
            <div class="product-info">
                <div class="product-name">${product.name}</div>
                <div class="product-category">${product.category}</div>
                <div class="product-platforms">
                    ${product.platforms.map(p => `<span class="platform-tag">${p}</span>`).join('')}
                </div>
            </div>
            <div class="product-metrics">
                <div class="trend-score">${(product.trend_score * 100).toFixed(0)}%</div>
                <div class="trend-status status-${product.status}">${product.status}</div>
                <button class="btn btn-primary btn-sm" onclick="viewProductDetails('${product.id}')">
                    View Details
                </button>
            </div>
        </div>
    `).join('');
}

function renderCategories(categories) {
    const container = document.getElementById('categoriesContainer');
    if (!container) return;

    container.innerHTML = categories.map(cat => `
        <div class="card">
            <div class="card-header">
                <div class="card-title">${cat.category}</div>
                <div class="card-badge badge-${cat.momentum === 'rising' ? 'success' : 'info'}">
                    ${cat.momentum}
                </div>
            </div>
            <div class="stat-value">${cat.product_count}</div>
            <div class="stat-label">Products</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${cat.avg_trend_score * 100}%"></div>
            </div>
            <div class="stat-label">Avg Score: ${(cat.avg_trend_score * 100).toFixed(0)}%</div>
        </div>
    `).join('');
}

function updateStats(products) {
    const stats = {
        total: products.length,
        emerging: products.filter(p => p.status === 'emerging').length,
        rising: products.filter(p => p.status === 'rising').length,
        avgScore: products.reduce((sum, p) => sum + p.trend_score, 0) / products.length || 0
    };

    // Update stat cards
    updateStatCard('totalProducts', stats.total);
    updateStatCard('emergingTrends', stats.emerging);
    updateStatCard('risingTrends', stats.rising);
    updateStatCard('avgTrendScore', `${(stats.avgScore * 100).toFixed(0)}%`);

    // Update charts if available
    updateCharts(products);
}

function updateStatCard(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function updateCharts(products) {
    // Platform distribution
    const platformData = getPlatformDistribution(products);
    if (document.getElementById('platformChart')) {
        chartManager.createPlatformChart('platformChart', platformData);
    }

    // Category distribution
    const categoryData = getCategoryDistribution(products);
    if (document.getElementById('categoryChart')) {
        chartManager.createCategoryChart('categoryChart', categoryData);
    }

    // Trend timeline
    const trendData = getTrendTimeline(products);
    if (document.getElementById('trendChart')) {
        chartManager.createTrendChart('trendChart', trendData);
    }
}

function getPlatformDistribution(products) {
    const platforms = {};
    
    products.forEach(product => {
        product.platforms.forEach(platform => {
            platforms[platform] = (platforms[platform] || 0) + 1;
        });
    });

    return {
        labels: Object.keys(platforms),
        values: Object.values(platforms)
    };
}

function getCategoryDistribution(products) {
    const categories = {};
    
    products.forEach(product => {
        categories[product.category] = (categories[product.category] || 0) + 1;
    });

    return {
        labels: Object.keys(categories),
        values: Object.values(categories)
    };
}

function getTrendTimeline(products) {
    // Simplified - in production, use actual historical data
    const days = 7;
    const labels = [];
    const values = [];

    for (let i = days; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        values.push(Math.random() * 0.3 + 0.5); // Mock data
    }

    return { labels, values };
}

async function viewProductDetails(productId) {
    showLoading();
    
    try {
        const product = await apiClient.getProductDetails(productId);
        const prediction = await apiClient.getTrendPrediction(productId);
        
        showProductModal(product, prediction);
        hideLoading();
    } catch (error) {
        console.error('Error loading product details:', error);
        showError('Failed to load product details');
        hideLoading();
    }
}

function showProductModal(product, prediction) {
    const modal = document.getElementById('productModal') || createProductModal();
    
    const content = modal.querySelector('.modal-content');
    content.innerHTML = `
        <div class="modal-header">
            <h2>${product.name}</h2>
            <button class="modal-close" onclick="closeModal('productModal')">&times;</button>
        </div>
        <div class="modal-body">
            <div class="product-detail-grid">
                <div class="detail-section">
                    <h3>Overview</h3>
                    <p><strong>Category:</strong> ${product.category}</p>
                    <p><strong>Trend Score:</strong> ${(product.trend_score * 100).toFixed(0)}%</p>
                    <p><strong>Status:</strong> <span class="status-${product.status}">${product.status}</span></p>
                    <p><strong>Viral Velocity:</strong> ${(product.viral_velocity * 100).toFixed(0)}%</p>
                </div>
                
                <div class="detail-section">
                    <h3>Platforms</h3>
                    ${product.platforms.map(p => `<span class="platform-tag">${p}</span>`).join('')}
                </div>
                
                <div class="detail-section">
                    <h3>Prediction</h3>
                    <p><strong>Confidence:</strong> ${(prediction.confidence_score * 100).toFixed(0)}%</p>
                    <p><strong>Recommendation:</strong> ${prediction.recommendation}</p>
                    ${prediction.predicted_peak_date ? 
                        `<p><strong>Predicted Peak:</strong> ${new Date(prediction.predicted_peak_date).toLocaleDateString()}</p>` : 
                        ''
                    }
                </div>
                
                <div class="detail-section">
                    <h3>Actions</h3>
                    <button class="btn btn-primary btn-block" onclick="compareProduct('${product.name}')">
                        Compare Prices
                    </button>
                    <button class="btn btn-secondary btn-block" onclick="createAlertForProduct('${product.id}')">
                        Create Alert
                    </button>
                </div>
            </div>
        </div>
    `;
    
    modal.classList.add('active');
}

function createProductModal() {
    const modal = document.createElement('div');
    modal.id = 'productModal';
    modal.className = 'modal';
    modal.innerHTML = '<div class="modal-content"></div>';
    document.body.appendChild(modal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal('productModal');
        }
    });
    
    return modal;
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

async function compareProduct(productName) {
    showLoading();
    
    try {
        const comparison = await apiClient.compareProductPrices(productName);
        showComparisonModal(comparison);
        hideLoading();
    } catch (error) {
        console.error('Error comparing product:', error);
        showError('Failed to compare product prices');
        hideLoading();
    }
}

function showComparisonModal(comparison) {
    const modal = document.getElementById('comparisonModal') || createComparisonModal();
    
    const content = modal.querySelector('.modal-content');
    content.innerHTML = `
        <div class="modal-header">
            <h2>Price Comparison: ${comparison.product_name}</h2>
            <button class="modal-close" onclick="closeModal('comparisonModal')">&times;</button>
        </div>
        <div class="modal-body">
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Platform</th>
                        <th>Price</th>
                        <th>Availability</th>
                        <th>Reviews</th>
                        <th>Rating</th>
                    </tr>
                </thead>
                <tbody>
                    ${comparison.comparisons.map(comp => `
                        <tr>
                            <td><strong>${comp.platform}</strong></td>
                            <td>$${comp.price.toFixed(2)}</td>
                            <td>${comp.availability}</td>
                            <td>${comp.reviews}</td>
                            <td>${comp.rating ? comp.rating.toFixed(1) + ' ⭐' : 'N/A'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
            
            ${comparison.best_deal ? `
                <div class="alert alert-success">
                    <strong>Best Deal:</strong> ${comparison.best_deal.platform} at $${comparison.best_deal.price.toFixed(2)}
                </div>
            ` : ''}
        </div>
    `;
    
    modal.classList.add('active');
}

function createComparisonModal() {
    const modal = document.createElement('div');
    modal.id = 'comparisonModal';
    modal.className = 'modal';
    modal.innerHTML = '<div class="modal-content"></div>';
    document.body.appendChild(modal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal('comparisonModal');
        }
    });
    
    return modal;
}

async function createAlertForProduct(productId) {
    const userId = localStorage.getItem('userId') || 'demo_user';
    
    try {
        const alertData = {
            user_id: userId,
            product_id: productId,
            keywords: [],
            categories: [],
            min_trend_score: 0.7,
            platforms: []
        };
        
        await apiClient.createAlert(alertData);
        showSuccess('Alert created successfully!');
        closeModal('productModal');
    } catch (error) {
        console.error('Error creating alert:', error);
        showError('Failed to create alert');
    }
}

function handleFilterClick(event) {
    const button = event.target;
    const filterType = button.dataset.filter;
    const filterValue = button.dataset.value;
    
    button.classList.toggle('active');
    
    if (filterType === 'category') {
        const index = currentFilters.categories.indexOf(filterValue);
        if (index > -1) {
            currentFilters.categories.splice(index, 1);
        } else {
            currentFilters.categories.push(filterValue);
        }
    } else if (filterType === 'platform') {
        const index = currentFilters.platforms.indexOf(filterValue);
        if (index > -1) {
            currentFilters.platforms.splice(index, 1);
        } else {
            currentFilters.platforms.push(filterValue);
        }
    } else if (filterType === 'status') {
        currentFilters.status = button.classList.contains('active') ? filterValue : null;
    }
    
    loadTrendingProducts();
}

function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    
    const filteredProducts = currentProducts.filter(product => {
        return product.name.toLowerCase().includes(searchTerm) ||
               product.category.toLowerCase().includes(searchTerm);
    });
    
    renderProducts(filteredProducts);
}

function handleMinScoreChange(event) {
    const value = parseFloat(event.target.value);
    currentFilters.minScore = value;
    
    const label = document.getElementById('minScoreLabel');
    if (label) {
        label.textContent = `${(value * 100).toFixed(0)}%`;
    }
    
    loadTrendingProducts();
}

async function refreshData() {
    showLoading();
    await loadTrendingProducts();
    await loadTrendingCategories();
    showSuccess('Data refreshed successfully!');
    hideLoading();
}

function showLoading() {
    const loader = document.getElementById('loader') || createLoader();
    loader.style.display = 'flex';
}

function hideLoading() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = 'none';
    }
}

function createLoader() {
    const loader = document.createElement('div');
    loader.id = 'loader';
    loader.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    `;
    loader.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(loader);
    return loader;
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'danger');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for use in HTML
window.viewProductDetails = viewProductDetails;
window.compareProduct = compareProduct;
window.createAlertForProduct = createAlertForProduct;
window.closeModal = closeModal;
window.refreshData = refreshData;
