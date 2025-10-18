// frontend/static/js/charts.js

class ChartManager {
    constructor() {
        this.charts = {};
    }

    createTrendChart(containerId, data, options = {}) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        this.charts[containerId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: options.label || 'Trend Score',
                    data: data.values,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: '#fff'
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#a0aec0' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        ticks: { color: '#a0aec0' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });

        return this.charts[containerId];
    }

    createPlatformChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        this.charts[containerId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Products',
                    data: data.values,
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(237, 100, 166, 0.8)',
                        'rgba(255, 154, 158, 0.8)',
                        'rgba(250, 208, 196, 0.8)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#a0aec0' },
                        grid: { display: false }
                    },
                    y: {
                        ticks: { color: '#a0aec0' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        beginAtZero: true
                    }
                }
            }
        });

        return this.charts[containerId];
    }

    createCategoryChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        this.charts[containerId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#ed64a6',
                        '#ff9a9e',
                        '#fad0c4',
                        '#ffecd2'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#fff',
                            padding: 15
                        }
                    }
                }
            }
        });

        return this.charts[containerId];
    }

    createViralVelocityChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        this.charts[containerId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Viral Velocity',
                    data: data.values,
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: '#667eea',
                    borderWidth: 2,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#667eea'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff'
                        }
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        pointLabels: {
                            color: '#a0aec0'
                        },
                        ticks: {
                            color: '#a0aec0',
                            backdropColor: 'transparent'
                        },
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });

        return this.charts[containerId];
    }

    destroyChart(containerId) {
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
            delete this.charts[containerId];
        }
    }

    destroyAll() {
        Object.keys(this.charts).forEach(id => {
            this.charts[id].destroy();
        });
        this.charts = {};
    }
}

const chartManager = new ChartManager();
