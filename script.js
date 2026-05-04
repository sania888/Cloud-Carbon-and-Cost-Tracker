const API_BASE =  "https://cloud-carbon-and-cost-tracker.onrender.com";

async function loadData() {

    const region = document.getElementById("region").value;
    const service = document.getElementById("service").value;

    const params = [];
    if (region) params.push(`region=${region}`);
    if (service) params.push(`service=${service}`);

    let url = `${API_BASE}/usage/all`;
    if (params.length > 0) {
        url += "?" + params.join("&");
    }

    const tableBody = document.getElementById("table-body");
    const loading = document.getElementById("loading");
    const noData = document.getElementById("no-data");

    // Show loading state
    loading.style.display = "block";
    noData.style.display = "none";
    tableBody.innerHTML = ""; // Clear old data

    
    const response = await fetch(url); // FETCH DATA
    const result = await response.json();  // THEN PARSE

    // hid loading
    loading.style.display = "none";

    if (!result.data || result.data.length === 0) {
        noData.style.display = "block";
        return;
    }


    result.data.forEach(item => {
        const tr = document.createElement("tr");
        
        tr.innerHTML =`
            <td>${item.service}</td>
            <td>${item.region}</td>
            <td>${item.usage_hours}</td>
            <td>${item.usage_type}</td>
            <td>${item.cost_usd}</td>
            <td>${item.emission_kg}</td>
        `;
        tableBody.appendChild(tr);
    });

    let summaryUrl = `${API_BASE}/usage/summary`;
    if (params.length > 0) {
        summaryUrl += "?" + params.join("&");
    }
    // FETCH SUMMARY DATA
    const summaryResponse = await fetch(summaryUrl);
    const summaryResult = await summaryResponse.json();

    // Update UI
    document.getElementById("total-cost").innerText = summaryResult.total_cost;
    document.getElementById("total-emissions").innerText = summaryResult.total_emissions;

    console.log(result); // OPTIONAL DEBUG

    if(!result.data) {
        console.error("Data not found in response");
        return;
    }

    // prepare plot data
    const services = [];
    const costs = [];

    result.data.forEach(item => {
        services.push(item.service);
        costs.push(item.cost_usd);
    });

    // plotly bar chart (Cost by service)
    const plotData = [
        {
            x: services,
            y: costs,
            type: "bar"
        }
    ];

    const isDark = document.body.classList.contains("dark-mode")

    const layout = {
        title: "Cost by Service Plot",
        xaxis: { title: "Service" },
        yaxis: { title: "Cost (USD)" },
        paper_bgcolor: isDark ? "#1e1e1e" : "#ffffff",
        plot_bgcolor: isDark ? "#1e1e1e" : "#ffffff",
        font: {
            color: isDark ? "#ffffff" : "#000000"
        }
    };

    Plotly.newPlot("cost-chart", plotData, layout);

    const emissions = [];

    result.data.forEach(item => {
        emissions.push(item.emission_kg);
    });

    const emissionPlotData = [
        {
            x: services,
            y: emissions,
            type: "bar"
        }
    ];

    const emissionLayout = {
        title: "Emissions by Service Plot",
        xaxis: { title: "Service" },
        yaxis: { title: "Emissions (kg)" },
        paper_bgcolor: isDark ? "#1e1e1e" : "#ffffff",
        plot_bgcolor: isDark ? "#1e1e1e" : "#ffffff",
        font: {
            color: isDark ? "#ffffff" : "#000000"
        }
    };

    Plotly.newPlot("emission-chart", emissionPlotData, emissionLayout);


    // INSIGHTS LOGIC
    let maxCostService = "";
    let maxCost = 0;

    let maxEmissionService = "";
    let maxEmission = 0;
      
    result.data.forEach(item => {
        // highest cose
        if (item.cost_usd > maxCost) {
            maxCost = item.cost_usd;
            maxCostService = item.service;
        }

        // highest emission
        if (item.emission_kg > maxEmission) {
            maxEmission = item.emission_kg;
            maxEmissionService = item.service;
        }
    });

    const totalServices = result.data.length;

    const insightList = document.getElementById("insights-list");

    insightList.innerHTML = `
        <li><strong>Highest Cost Service:</strong> ${maxCostService} ($${maxCost})</li>
        <li><strong>Highest Emission Service:</strong> ${maxEmissionService} (${maxEmission} kg)</li>
        <li><strong>Total Services Used:</strong> ${totalServices}</li>
    `;
}


function getQueryParams() {
    const region = document.getElementById("region").value;
    const service = document.getElementById("service").value;

    const params = [];

    if (region) params.push(`region=${region}`);
    if(service) params.push(`service=${service}`);

    return params.length > 0 ? "?" + params.join("&") : "";
}


function downloadCSV() {
    const query = getQueryParams();
    const url = `${API_BASE}/usage/export${query}`;

    window.open(url, "_blank");
}


function downloadPDF() {
    const query = getQueryParams();
    const url = `${API_BASE}/usage/export/pdf${query}`;

    window.open(url, "_blank");
}


document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("theme-toggle");
    toggleBtn.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
    });
});