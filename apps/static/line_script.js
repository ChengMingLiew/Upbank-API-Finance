const container = document.getElementById("data-container");
const spendingData = JSON.parse(container.dataset.items);

const configElement = document.getElementById('current-year');
const year = configElement.dataset.thisYear;

Chart.defaults.font.family = "'Figtree";

const ctx = document.getElementById("myChart");

new Chart(ctx, {
    type: "line",
    data: {
        datasets: [
            {
                label: `${year} Expenditure`,
                data: spendingData,
            },
        ],  
    },
    options: {
        elements: {
            line: {
                tension: 0.25,
                backgroundColor: "#f6f4f2",
                borderColor: "#ff705c",
                borderWidth: 3,
            },
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: "Month",
                },
                ticks: {
                    callback: function(value, index, ticks) {
                        return  this.getLabelForValue(value) + " " + year
                    }
                }
            },
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: "Spending",
                },
            },
        },
    },
});