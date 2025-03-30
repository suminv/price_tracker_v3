document.addEventListener('DOMContentLoaded', function() {
    var chartElement = document.getElementById('priceHistoryChart');
    if (!chartElement) return;

    var labelsString = chartElement.getAttribute('data-labels');
    var pricesString = chartElement.getAttribute('data-prices');

    if (!labelsString || !pricesString) {
        console.log("No data to display chart.");
        return;
    }

    try {
        var labels = JSON.parse(labelsString);
        var prices = JSON.parse(pricesString);

        var priceChart = new Chart(chartElement.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Цена (€)',
                    data: prices,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Цена (€)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Дата'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return '€' + context.parsed.y.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error("Error parsing JSON:", error);
    }
});