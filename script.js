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

    const layout = {
        title: "Cost by Service Plot",
        xaxis: { title: "Service" },
        yaxis: { title: "Cost (USD)" }
    };

    Plotly.newPlot("cost-chart", plotData, layout);

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
