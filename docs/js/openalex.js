/**
 * OpenAlex API Integration for Publications
 * Fetches and displays academic publications with live refresh capability
 */

const OPENALEX_BASE = 'https://api.openalex.org';
const EMAIL = 'dennis.hoffmann@utwente.nl';

// Team author IDs from OpenAlex - Only Joerg and Axel
const TEAM_AUTHORS = [
    { id: 'A5032430973', name: 'Joerg Osterrieder', minWorks: 50 },
    { id: 'A5049079953', name: 'Axel Gross-Klussmann', minWorks: 5 }
];

// Cache for publications
let publicationsCache = null;
let statisticsCache = null;

// Chart instances (for proper cleanup on re-init)
let publicationsChartInstance = null;
let citationsChartInstance = null;

/**
 * Load publications from local JSON file
 */
async function loadPublicationsFromFile() {
    try {
        const response = await fetch('data/publications.json');
        if (!response.ok) throw new Error('Failed to load publications');
        const data = await response.json();
        publicationsCache = data.publications;
        statisticsCache = data.statistics;
        return data;
    } catch (error) {
        console.error('Error loading publications:', error);
        return null;
    }
}

/**
 * Fetch fresh publications from OpenAlex API
 */
async function refreshFromOpenAlex() {
    const publications = [];
    const seenIds = new Set();
    let failedCount = 0;

    for (const author of TEAM_AUTHORS) {
        try {
            let cursor = '*';
            while (cursor) {
                const url = `${OPENALEX_BASE}/works?filter=author.id:${author.id}&per_page=200&sort=publication_year:desc&cursor=${cursor}&mailto=${EMAIL}`;
                const response = await fetch(url);
                if (!response.ok) { failedCount++; break; }

                const data = await response.json();
                const results = data.results || [];
                if (results.length === 0) break;

                for (const work of results) {
                    if (seenIds.has(work.id)) continue;
                    seenIds.add(work.id);

                    publications.push({
                        id: work.id,
                        title: work.title || 'Untitled',
                        year: work.publication_year,
                        doi: (work.doi || '').replace('https://doi.org/', ''),
                        authors: (work.authorships || []).slice(0, 5).map(a => ({
                            name: a.author?.display_name || '',
                            orcid: (a.author?.orcid || '').replace('https://orcid.org/', '')
                        })),
                        venue: work.primary_location?.source?.display_name || '',
                        cited_by_count: work.cited_by_count || 0,
                        is_open_access: work.open_access?.is_oa || false,
                        oa_url: work.open_access?.oa_url || ''
                    });
                }

                cursor = data.meta?.next_cursor || null;
                if (cursor) await new Promise(r => setTimeout(r, 500));
            }
        } catch (error) {
            console.error(`Error fetching works for ${author.name}:`, error);
            failedCount++;
        }
    }

    if (failedCount === TEAM_AUTHORS.length) {
        return { publications: [], statistics: null, error: 'Failed to fetch publications from OpenAlex. Please try again later.' };
    }

    // Sort by year descending
    publications.sort((a, b) => (b.year || 0) - (a.year || 0));
    publicationsCache = publications;

    // Calculate statistics
    statisticsCache = calculateStatistics(publications);

    return { publications, statistics: statisticsCache };
}

/**
 * Calculate publication statistics
 */
function calculateStatistics(publications) {
    const byYear = {};
    let totalCitations = 0;

    for (const pub of publications) {
        if (pub.year) {
            byYear[pub.year] = (byYear[pub.year] || 0) + 1;
        }
        totalCitations += pub.cited_by_count || 0;
    }

    const currentYear = new Date().getFullYear();
    const recentCount = publications.filter(p => p.year && p.year >= currentYear - 2).length;

    return {
        total_publications: publications.length,
        total_citations: totalCitations,
        by_year: byYear,
        recent_count: recentCount
    };
}

/**
 * Format author name in APA style: Last, F. M.
 */
function formatAuthorAPA(name) {
    if (!name) return 'Unknown';
    const parts = name.trim().split(/\s+/);
    if (parts.length === 0) return 'Unknown';
    if (parts.length === 1) return parts[0];
    const lastName = parts[parts.length - 1];
    const initials = parts.slice(0, -1).map(p => p[0] + '.').join(' ');
    return `${lastName}, ${initials}`;
}

/**
 * Format publication in APA 7th edition style
 */
function formatAPACitation(pub) {
    // Format authors
    const authors = pub.authors || [];
    let authorStr = '';
    if (authors.length === 0) {
        authorStr = 'Unknown';
    } else if (authors.length === 1) {
        authorStr = formatAuthorAPA(authors[0].name);
    } else if (authors.length === 2) {
        authorStr = `${formatAuthorAPA(authors[0].name)} & ${formatAuthorAPA(authors[1].name)}`;
    } else if (authors.length <= 20) {
        const authorParts = authors.slice(0, -1).map(a => formatAuthorAPA(a.name));
        authorStr = authorParts.join(', ') + `, & ${formatAuthorAPA(authors[authors.length - 1].name)}`;
    } else {
        const authorParts = authors.slice(0, 19).map(a => formatAuthorAPA(a.name));
        authorStr = authorParts.join(', ') + `, ... ${formatAuthorAPA(authors[authors.length - 1].name)}`;
    }

    // Year
    const yearStr = pub.year ? `(${pub.year})` : '(n.d.)';

    // Title (sentence case)
    let title = pub.title || 'Untitled';
    if (title.length > 1) {
        title = title[0].toUpperCase() + title.slice(1).toLowerCase();
    }

    // Venue
    const venueStr = pub.venue ? ` ${pub.venue}.` : '';

    // DOI
    const doiStr = pub.doi ? ` https://doi.org/${pub.doi}` : '';

    return `${authorStr} ${yearStr}. ${title}.${venueStr}${doiStr}`;
}

/**
 * Render publications table using DOM API (no innerHTML) for XSS safety
 */
function renderPublicationsTable(publications, containerId = 'publications-table-body') {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.textContent = '';

    if (!publications || publications.length === 0) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = 5;
        td.className = 'text-center';
        td.textContent = 'No publications found';
        tr.appendChild(td);
        container.appendChild(tr);
        return;
    }

    for (const pub of publications) {
        const tr = document.createElement('tr');

        // Year
        const tdYear = document.createElement('td');
        tdYear.textContent = pub.year || 'N/A';
        tr.appendChild(tdYear);

        // Title & Venue
        const tdTitle = document.createElement('td');
        const titleDiv = document.createElement('div');
        titleDiv.className = 'publication-title';
        if (pub.doi) {
            const a = document.createElement('a');
            a.href = 'https://doi.org/' + pub.doi;
            a.target = '_blank';
            a.rel = 'noopener noreferrer';
            a.textContent = pub.title || 'Untitled';
            titleDiv.appendChild(a);
        } else {
            titleDiv.textContent = pub.title || 'Untitled';
        }
        tdTitle.appendChild(titleDiv);

        const venueDiv = document.createElement('div');
        venueDiv.className = 'publication-venue';
        venueDiv.textContent = pub.venue || '';
        tdTitle.appendChild(venueDiv);

        const apaDiv = document.createElement('div');
        apaDiv.className = 'publication-apa';
        apaDiv.textContent = formatAPACitation(pub);
        tdTitle.appendChild(apaDiv);

        tr.appendChild(tdTitle);

        // Authors
        const tdAuthors = document.createElement('td');
        tdAuthors.textContent = (pub.authors || []).map(a => a.name).join(', ');
        tr.appendChild(tdAuthors);

        // Citations
        const tdCitations = document.createElement('td');
        if (pub.cited_by_count > 0) {
            const span = document.createElement('span');
            span.className = 'publication-citations';
            span.textContent = pub.cited_by_count;
            tdCitations.appendChild(span);
        } else {
            tdCitations.textContent = '-';
        }
        tr.appendChild(tdCitations);

        // Links
        const tdLinks = document.createElement('td');
        if (pub.is_open_access) {
            const oaSpan = document.createElement('span');
            oaSpan.className = 'publication-oa';
            oaSpan.textContent = 'OA';
            tdLinks.appendChild(oaSpan);
            tdLinks.appendChild(document.createTextNode(' '));
        }
        if (pub.doi) {
            const doiLink = document.createElement('a');
            doiLink.href = 'https://doi.org/' + pub.doi;
            doiLink.target = '_blank';
            doiLink.rel = 'noopener noreferrer';
            doiLink.title = 'View DOI';
            doiLink.textContent = 'DOI';
            tdLinks.appendChild(doiLink);
        }
        tr.appendChild(tdLinks);

        container.appendChild(tr);
    }
}

/**
 * Filter publications based on search and year
 */
function filterPublications(publications, { search = '', year = '', author = '' } = {}) {
    return publications.filter(pub => {
        // Search filter
        if (search) {
            const searchLower = search.toLowerCase();
            const titleMatch = (pub.title || '').toLowerCase().includes(searchLower);
            const authorMatch = (pub.authors || []).some(a =>
                (a.name || '').toLowerCase().includes(searchLower)
            );
            const venueMatch = (pub.venue || '').toLowerCase().includes(searchLower);
            if (!titleMatch && !authorMatch && !venueMatch) return false;
        }

        // Year filter
        if (year && pub.year !== parseInt(year)) {
            return false;
        }

        // Author filter
        if (author) {
            const authorLower = author.toLowerCase();
            if (!(pub.authors || []).some(a => (a.name || '').toLowerCase().includes(authorLower))) {
                return false;
            }
        }

        return true;
    });
}

/**
 * Sort publications by column
 */
function sortPublications(publications, column, ascending = true) {
    const sorted = [...publications];

    sorted.sort((a, b) => {
        let valA, valB;

        switch (column) {
            case 'year':
                valA = a.year || 0;
                valB = b.year || 0;
                break;
            case 'title':
                valA = (a.title || '').toLowerCase();
                valB = (b.title || '').toLowerCase();
                break;
            case 'citations':
                valA = a.cited_by_count || 0;
                valB = b.cited_by_count || 0;
                break;
            default:
                return 0;
        }

        if (valA < valB) return ascending ? -1 : 1;
        if (valA > valB) return ascending ? 1 : -1;
        return 0;
    });

    return sorted;
}

/**
 * Get theme-appropriate colors for Chart.js
 */
function getChartThemeColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
        text: isDark ? '#e2e8f0' : '#1f2937',
        grid: isDark ? '#334155' : '#e2e8f0',
        barBg: isDark ? 'rgba(96, 165, 250, 0.8)' : 'rgba(59, 130, 246, 0.8)',
        barBorder: isDark ? 'rgba(96, 165, 250, 1)' : 'rgba(59, 130, 246, 1)',
        lineBg: isDark ? 'rgba(167, 139, 250, 0.2)' : 'rgba(139, 92, 246, 0.2)',
        lineBorder: isDark ? 'rgba(167, 139, 250, 1)' : 'rgba(139, 92, 246, 1)',
    };
}

/**
 * Initialize publications chart using Chart.js
 */
function initPublicationsChart(statistics, canvasId = 'publications-chart') {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !statistics?.by_year) return;

    const years = Object.keys(statistics.by_year).sort();
    const counts = years.map(y => statistics.by_year[y]);
    const colors = getChartThemeColors();

    if (publicationsChartInstance) publicationsChartInstance.destroy();
    publicationsChartInstance = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [{
                label: 'Publications',
                data: counts,
                backgroundColor: colors.barBg,
                borderColor: colors.barBorder,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    ticks: { color: colors.text },
                    grid: { color: colors.grid }
                },
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 5, color: colors.text },
                    grid: { color: colors.grid }
                }
            }
        }
    });
}

/**
 * Initialize citations chart
 */
function initCitationsChart(publications, canvasId = 'citations-chart') {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !publications) return;

    // Calculate cumulative citations by year
    const citationsByYear = {};
    for (const pub of publications) {
        const year = pub.year;
        if (year) {
            citationsByYear[year] = (citationsByYear[year] || 0) + (pub.cited_by_count || 0);
        }
    }

    const years = Object.keys(citationsByYear).sort();
    const citations = years.map(y => citationsByYear[y]);
    const colors = getChartThemeColors();

    if (citationsChartInstance) citationsChartInstance.destroy();
    citationsChartInstance = new Chart(canvas, {
        type: 'line',
        data: {
            labels: years,
            datasets: [{
                label: 'Citations',
                data: citations,
                fill: true,
                backgroundColor: colors.lineBg,
                borderColor: colors.lineBorder,
                borderWidth: 2,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    ticks: { color: colors.text },
                    grid: { color: colors.grid }
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: colors.text },
                    grid: { color: colors.grid }
                }
            }
        }
    });
}

/**
 * Get unique years from publications for filter dropdown
 */
function getUniqueYears(publications) {
    const years = new Set();
    for (const pub of publications) {
        if (pub.year) years.add(pub.year);
    }
    return Array.from(years).sort((a, b) => b - a);
}

/**
 * Populate year filter dropdown
 */
function populateYearFilter(publications, selectId = 'year-filter') {
    const select = document.getElementById(selectId);
    if (!select) return;

    const years = getUniqueYears(publications);
    select.textContent = '';
    const allOpt = document.createElement('option');
    allOpt.value = '';
    allOpt.textContent = 'All Years';
    select.appendChild(allOpt);
    for (const y of years) {
        const opt = document.createElement('option');
        opt.value = y;
        opt.textContent = y;
        select.appendChild(opt);
    }
}

// Export functions for use in HTML
window.OpenAlexAPI = {
    loadPublicationsFromFile,
    refreshFromOpenAlex,
    renderPublicationsTable,
    filterPublications,
    sortPublications,
    initPublicationsChart,
    initCitationsChart,
    populateYearFilter,
    formatAPACitation,
    formatAuthorAPA,
    getCache: () => ({ publications: publicationsCache, statistics: statisticsCache })
};
