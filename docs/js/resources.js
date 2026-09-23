/**
 * Resources Page - Dataset Rendering
 * Fetches data/resources.json and renders datasets grouped by category
 */

(function() {
    'use strict';

    let categories = [];

    /**
     * Validate URL is safe (http/https only, blocks javascript: URLs)
     */
    function isSafeUrl(url) {
        if (typeof url !== 'string') return false;
        return url.startsWith('https://') || url.startsWith('http://');
    }

    /**
     * Initialize resources on DOMContentLoaded
     */
    document.addEventListener('DOMContentLoaded', function() {
        const grid = document.getElementById('datasets-grid');
        if (!grid) return;

        loadResources();
    });

    /**
     * Load resources JSON and render
     */
    async function loadResources() {
        try {
            const response = await fetch('data/resources.json');
            if (!response.ok) throw new Error('Failed to load resources');
            const data = await response.json();

            categories = data.categories || [];

            // Populate last updated
            const lastUpdated = document.getElementById('datasets-last-updated');
            if (lastUpdated && data.last_updated) {
                lastUpdated.textContent = 'Updated ' + data.last_updated;
            }

            // Render all datasets
            renderDatasets(data.datasets || []);

        } catch (error) {
            const grid = document.getElementById('datasets-grid');
            if (grid) {
                grid.textContent = '';
                const msg = document.createElement('p');
                msg.className = 'loading';
                msg.textContent = 'Failed to load datasets.';
                grid.appendChild(msg);
            }
        }
    }

    /**
     * Render datasets grouped by category using details/summary accordions.
     * Uses DOM API exclusively (no innerHTML) for safe content insertion.
     */
    function renderDatasets(datasets) {
        const grid = document.getElementById('datasets-grid');
        if (!grid) return;

        grid.textContent = '';

        if (datasets.length === 0) {
            const msg = document.createElement('p');
            msg.className = 'loading';
            msg.textContent = 'No datasets available.';
            grid.appendChild(msg);
            return;
        }

        // Group datasets by category
        const grouped = {};
        for (let i = 0; i < categories.length; i++) {
            grouped[categories[i]] = [];
        }
        for (let j = 0; j < datasets.length; j++) {
            const cat = datasets[j].category;
            if (grouped[cat]) {
                grouped[cat].push(datasets[j]);
            }
        }

        let isFirst = true;

        for (let k = 0; k < categories.length; k++) {
            const catName = categories[k];
            const catDatasets = grouped[catName];
            if (!catDatasets || catDatasets.length === 0) continue;

            const details = document.createElement('details');
            details.className = 'wiki-card mb-2';

            const summary = document.createElement('summary');
            summary.appendChild(document.createTextNode(catName + ' '));
            const countSpan = document.createElement('span');
            countSpan.className = 'dataset-count';
            countSpan.textContent = '(' + catDatasets.length + ')';
            summary.appendChild(countSpan);
            details.appendChild(summary);

            const cardGrid = document.createElement('div');
            cardGrid.className = 'dataset-category-grid';

            for (let m = 0; m < catDatasets.length; m++) {
                cardGrid.appendChild(buildDatasetCard(catDatasets[m]));
            }

            details.appendChild(cardGrid);
            grid.appendChild(details);
            isFirst = false;
        }
    }

    /**
     * Build a single dataset card as a DOM element
     */
    function buildDatasetCard(dataset) {
        const card = document.createElement('div');
        card.className = 'card';

        // Name
        const h3 = document.createElement('h3');
        h3.textContent = dataset.name;
        card.appendChild(h3);

        // Description
        const desc = document.createElement('p');
        desc.className = 'card-text';
        desc.textContent = dataset.description;
        card.appendChild(desc);

        // Metadata line: availability, periodicity
        const metaParts = [];
        if (dataset.availability) metaParts.push(dataset.availability);
        if (dataset.periodicity) metaParts.push(dataset.periodicity);
        if (metaParts.length > 0) {
            const metaP = document.createElement('p');
            metaP.className = 'dataset-meta';
            metaP.textContent = metaParts.join(' \u00B7 ');
            card.appendChild(metaP);
        }

        // Python packages
        if (dataset.python_packages && dataset.python_packages.length > 0) {
            const pkgP = document.createElement('p');
            pkgP.className = 'dataset-meta';
            pkgP.appendChild(document.createTextNode('Python: '));
            for (let i = 0; i < dataset.python_packages.length; i++) {
                if (i > 0) pkgP.appendChild(document.createTextNode(', '));
                const code = document.createElement('code');
                code.textContent = dataset.python_packages[i];
                pkgP.appendChild(code);
            }
            card.appendChild(pkgP);
        }

        // License
        if (dataset.license) {
            const licP = document.createElement('p');
            licP.className = 'dataset-meta';
            licP.textContent = 'License: ' + dataset.license;
            card.appendChild(licP);
        }

        // Tags
        if (dataset.tags && dataset.tags.length > 0) {
            const tagsDiv = document.createElement('div');
            tagsDiv.className = 'mt-2';
            for (let t = 0; t < dataset.tags.length; t++) {
                const tagSpan = document.createElement('span');
                tagSpan.className = 'tag';
                tagSpan.textContent = dataset.tags[t];
                tagsDiv.appendChild(tagSpan);
            }
            card.appendChild(tagsDiv);
        }

        // Visit link
        const visitLink = document.createElement('a');
        visitLink.href = isSafeUrl(dataset.url) ? dataset.url : '#';
        visitLink.target = '_blank';
        visitLink.rel = 'noopener noreferrer';
        visitLink.className = 'btn btn-secondary mt-2';
        visitLink.textContent = 'Visit';
        card.appendChild(visitLink);

        // Code link (if present)
        if (dataset.code_url) {
            card.appendChild(document.createTextNode(' '));
            const codeLink = document.createElement('a');
            codeLink.href = isSafeUrl(dataset.code_url) ? dataset.code_url : '#';
            codeLink.target = '_blank';
            codeLink.rel = 'noopener noreferrer';
            codeLink.className = 'btn btn-secondary mt-2';
            codeLink.textContent = 'Code';
            card.appendChild(codeLink);
        }

        return card;
    }

    // Export namespace
    window.Resources = {
        loadResources: loadResources
    };

})();
