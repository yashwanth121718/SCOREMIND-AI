// ============================================================
// Dashboard Live Search & Chart.js Visualizations
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    // Live Table Filter
    const searchInput = document.getElementById('tableSearchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', (e) => {
            const query = e.target.value.toLowerCase();
            const tableRows = document.querySelectorAll('.custom-table tbody tr');

            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }

    // Initialize Chart.js overview charts if canvas present
    const ctx = document.getElementById('analyticsChart');
    if (ctx && typeof Chart !== 'undefined') {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Avg Similarity', 'Avg Keyword Score', 'Avg Grammar Score', 'Overall Pass Rate'],
                datasets: [{
                    label: 'System Performance Score (%)',
                    data: [82.5, 78.4, 88.0, 91.2],
                    backgroundColor: [
                        'rgba(0, 229, 255, 0.6)',
                        'rgba(124, 77, 255, 0.6)',
                        'rgba(105, 240, 174, 0.6)',
                        'rgba(255, 213, 79, 0.6)'
                    ],
                    borderColor: [
                        '#00e5ff',
                        '#7c4dff',
                        '#69f0ae',
                        '#ffd54f'
                    ],
                    borderWidth: 1.5,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { color: '#b0bec5' } }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#b0bec5' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    x: {
                        ticks: { color: '#b0bec5' },
                        grid: { display: false }
                    }
                }
            }
        });
    }
});
