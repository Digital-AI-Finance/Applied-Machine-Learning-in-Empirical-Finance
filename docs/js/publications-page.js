/**
 * Publications page controller
 * Handles filtering, sorting, charts, and live refresh from OpenAlex
 */
(function() {
    'use strict';

    var allPublications = [];
    var filteredPublications = [];
    var currentSort = { column: 'year', ascending: false };
    var REFRESH_COOLDOWN_MS = 30000;

    document.addEventListener('DOMContentLoaded', async function() {
        showLoading(true);

        var data = await OpenAlexAPI.loadPublicationsFromFile();

        if (data) {
            allPublications = data.publications || [];
            filteredPublications = [].concat(allPublications);

            updateStatistics(data.statistics);
            OpenAlexAPI.populateYearFilter(allPublications);
            renderTable(filteredPublications);
            OpenAlexAPI.initPublicationsChart(data.statistics);
            OpenAlexAPI.initCitationsChart(allPublications);
        }

        showLoading(false);

        document.getElementById('search-input').addEventListener('input', applyFilters);
        document.getElementById('year-filter').addEventListener('change', applyFilters);
        document.getElementById('author-filter').addEventListener('change', applyFilters);
        document.getElementById('refresh-btn').addEventListener('click', refreshData);

        // Sortable column headers via data-sort attribute
        document.querySelectorAll('th[data-sort]').forEach(function(th) {
            function handleSort() {
                sortTable(th.getAttribute('data-sort'));
            }
            th.addEventListener('click', handleSort);
            th.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleSort();
                }
            });
        });
    });

    function showLoading(show) {
        document.getElementById('loading').style.display = show ? 'block' : 'none';
    }

    function updateStatistics(stats) {
        if (!stats) return;
        document.getElementById('stat-total').textContent =
            SiteUtils.formatNumber(stats.total_all_publications || 0);
        document.getElementById('stat-relevant').textContent =
            SiteUtils.formatNumber(stats.total_publications || 0);
        document.getElementById('stat-citations').textContent =
            SiteUtils.formatNumber(stats.total_citations || 0);
        document.getElementById('stat-recent').textContent =
            SiteUtils.formatNumber(stats.recent_count || 0);
    }

    function applyFilters() {
        var search = document.getElementById('search-input').value;
        var year = document.getElementById('year-filter').value;
        var author = document.getElementById('author-filter').value;

        filteredPublications = OpenAlexAPI.filterPublications(allPublications, { search: search, year: year, author: author });
        filteredPublications = OpenAlexAPI.sortPublications(
            filteredPublications,
            currentSort.column,
            currentSort.ascending
        );
        renderTable(filteredPublications);
    }

    function sortTable(column) {
        if (currentSort.column === column) {
            currentSort.ascending = !currentSort.ascending;
        } else {
            currentSort.column = column;
            currentSort.ascending = column === 'title';
        }

        // Update aria-sort on all sortable headers
        document.querySelectorAll('th[data-sort]').forEach(function(th) {
            if (th.getAttribute('data-sort') === column) {
                th.setAttribute('aria-sort', currentSort.ascending ? 'ascending' : 'descending');
            } else {
                th.setAttribute('aria-sort', 'none');
            }
        });

        filteredPublications = OpenAlexAPI.sortPublications(
            filteredPublications,
            currentSort.column,
            currentSort.ascending
        );
        renderTable(filteredPublications);
    }

    function renderTable(publications) {
        OpenAlexAPI.renderPublicationsTable(publications);
        var info = document.getElementById('pagination-info');
        info.textContent = 'Showing ' + publications.length + ' of ' + allPublications.length + ' publications';
    }

    async function refreshData() {
        var btn = document.getElementById('refresh-btn');
        btn.textContent = 'Refreshing...';
        btn.disabled = true;
        showLoading(true);

        try {
            var data = await OpenAlexAPI.refreshFromOpenAlex();
            var errorEl = document.getElementById('refresh-error');

            if (data.error) {
                errorEl.textContent = data.error;
                errorEl.style.display = 'block';
            } else {
                errorEl.style.display = 'none';
                allPublications = data.publications || [];
                filteredPublications = [].concat(allPublications);
                updateStatistics(data.statistics);
                applyFilters();
            }
        } catch (error) {
            console.error('Error refreshing:', error);
            var errorEl = document.getElementById('refresh-error');
            errorEl.textContent = 'Error refreshing publications. Please try again.';
            errorEl.style.display = 'block';
        }

        showLoading(false);
        startCooldown(btn);
    }

    function startCooldown(btn) {
        var remaining = REFRESH_COOLDOWN_MS / 1000;
        btn.textContent = 'Wait ' + remaining + 's';
        btn.disabled = true;

        var interval = setInterval(function() {
            remaining--;
            if (remaining <= 0) {
                clearInterval(interval);
                btn.textContent = 'Refresh from OpenAlex';
                btn.disabled = false;
            } else {
                btn.textContent = 'Wait ' + remaining + 's';
            }
        }, 1000);
    }
})();
