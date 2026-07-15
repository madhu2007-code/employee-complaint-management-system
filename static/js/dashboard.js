document.addEventListener('DOMContentLoaded', function () {
    // Mobile Sidebar Toggle
    const toggleBtn = document.querySelector('.toggle-sidebar-btn');
    const sidebar = document.querySelector('.sidebar');
    
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
    }
    // Chart.js initialization for Admin Dashboard
    const statusChartEl = document.getElementById('statusChart');
    if (statusChartEl) {
        const pendingCount = parseInt(statusChartEl.dataset.pending || 0);
        const assignedCount = parseInt(statusChartEl.dataset.assigned || 0);
        const progressCount = parseInt(statusChartEl.dataset.progress || 0);
        const resolvedCount = parseInt(statusChartEl.dataset.resolved || 0);
        const closedCount = parseInt(statusChartEl.dataset.closed || 0);
        new Chart(statusChartEl, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'Assigned', 'In Progress', 'Resolved', 'Closed'],
                datasets: [{
                    data: [pendingCount, assignedCount, progressCount, resolvedCount, closedCount],
                    backgroundColor: [
                        '#d97706', // Pending - Amber
                        '#0369a1', // Assigned - Light Blue
                        '#1d4ed8', // In Progress - Blue
                        '#15803d', // Resolved - Green
                        '#64748b'  // Closed - Slate Gray
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                family: "'Inter', sans-serif",
                                size: 12
                            },
                            boxWidth: 15
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }
    const deptChartEl = document.getElementById('deptChart');
    if (deptChartEl) {
        // Extracting data passed from dataset
        try {
            const rawData = JSON.parse(deptChartEl.dataset.deptData || '{}');
            const labels = Object.keys(rawData);
            const dataValues = Object.values(rawData);
            new Chart(deptChartEl, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Complaints',
                        data: dataValues,
                        backgroundColor: 'rgba(102, 126, 234, 0.7)',
                        borderColor: '#667eea',
                        borderWidth: 1.5,
                        borderRadius: 6
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
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            },
                            grid: {
                                color: '#f1f5f9'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        } catch (e) {
            console.error("Error loading department chart data:", e);
        }
    }
});
