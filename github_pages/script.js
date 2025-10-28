class OpenAIPricingViewer {
    constructor() {
        this.pricing = null;
        this.filteredPricing = null;
        this.init();
    }

    async init() {
        await this.loadPricing();
        this.setupEventListeners();
        this.renderModels();
    }

    async loadPricing() {
        try {
            const response = await fetch('./api.json?v=' + Date.now());
            const data = await response.json();
            this.pricing = data.models || {};
            this.filteredPricing = { ...this.pricing };
            
            // Update stats
            document.getElementById('models-count').textContent = data.models_count || Object.keys(this.pricing).length;
            
            const lastUpdated = new Date(data.timestamp);
            document.getElementById('last-updated').textContent = lastUpdated.toLocaleString();
            
        } catch (error) {
            console.error('Failed to load pricing:', error);
            document.getElementById('models-container').innerHTML = 
                '<div class="no-results">Failed to load pricing data. Please try again later.</div>';
        }
    }

    setupEventListeners() {
        const searchInput = document.getElementById('search-input');
        const typeFilter = document.getElementById('type-filter');

        searchInput.addEventListener('input', () => this.filterModels());
        typeFilter.addEventListener('change', () => this.filterModels());
    }

    filterModels() {
        const searchTerm = document.getElementById('search-input').value.toLowerCase();
        const typeFilter = document.getElementById('type-filter').value;

        this.filteredPricing = {};

        for (const [modelName, modelData] of Object.entries(this.pricing)) {
            const matchesSearch = modelName.toLowerCase().includes(searchTerm);
            const matchesType = typeFilter === 'all' || modelData.pricing_type === typeFilter;

            if (matchesSearch && matchesType) {
                this.filteredPricing[modelName] = modelData;
            }
        }

        this.renderModels();
    }

    renderModels() {
        const container = document.getElementById('models-container');
        
        if (Object.keys(this.filteredPricing).length === 0) {
            container.innerHTML = '<div class="no-results">No models found matching your filters.</div>';
            return;
        }

        const modelsHTML = Object.entries(this.filteredPricing)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([modelName, modelData]) => this.renderModelCard(modelName, modelData))
            .join('');

        container.innerHTML = modelsHTML;
    }

    renderModelCard(modelName, modelData) {
        const typeLabel = this.getPricingTypeLabel(modelData.pricing_type);
        const pricesHTML = this.renderPrices(modelData);

        return `
            <div class="model-card">
                <div class="model-header">
                    <div class="model-name">${modelName}</div>
                    <div class="model-type">${typeLabel}</div>
                </div>
                <div class="model-pricing">
                    ${pricesHTML}
                </div>
            </div>
        `;
    }

    renderPrices(modelData) {
        const prices = [];

        // Language models (tokens)
        if (modelData.input !== undefined) {
            prices.push(this.renderPrice('Input', `$${modelData.input.toFixed(2)} / 1M tokens`));
        }
        if (modelData.output !== undefined) {
            prices.push(this.renderPrice('Output', `$${modelData.output.toFixed(2)} / 1M tokens`));
        }
        if (modelData.cached_input !== undefined) {
            prices.push(this.renderPrice('Cached Input', `$${modelData.cached_input.toFixed(2)} / 1M tokens`));
        }

        // Image models
        if (modelData.price_1024x1024 !== undefined) {
            prices.push(this.renderPrice('1024×1024', `$${modelData.price_1024x1024.toFixed(4)}`));
        }
        if (modelData.price_1024x1792 !== undefined) {
            prices.push(this.renderPrice('1024×1792', `$${modelData.price_1024x1792.toFixed(4)}`));
        }
        if (modelData.price_1792x1024 !== undefined) {
            prices.push(this.renderPrice('1792×1024', `$${modelData.price_1792x1024.toFixed(4)}`));
        }

        // Generic price
        if (modelData.price !== undefined && prices.length === 0) {
            const unit = this.getPriceUnit(modelData.pricing_type);
            prices.push(this.renderPrice('Price', `$${modelData.price.toFixed(4)}${unit}`));
        }

        return prices.length > 0 ? prices.join('') : '<div class="price-item">No pricing data</div>';
    }

    renderPrice(label, value) {
        return `
            <div class="price-item">
                <div class="price-label">${label}</div>
                <div class="price-value">${value}</div>
            </div>
        `;
    }

    getPricingTypeLabel(type) {
        const labels = {
            'per_1m_tokens': 'Language Model',
            'per_image': 'Image Generation',
            'per_minute': 'Audio',
            'per_second': 'Video',
            'per_1k_chars': 'Text-to-Speech',
            'unknown': 'Unknown'
        };
        return labels[type] || type;
    }

    getPriceUnit(type) {
        const units = {
            'per_1m_tokens': ' / 1M tokens',
            'per_image': ' / image',
            'per_minute': ' / minute',
            'per_second': ' / second',
            'per_1k_chars': ' / 1K chars'
        };
        return units[type] || '';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new OpenAIPricingViewer();
});
