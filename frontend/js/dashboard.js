/* =========================================================
   AI BUSINESS INTELLIGENCE DASHBOARD
   ========================================================= */

const API_URL = "/api";

let activeCharts = [];
let currentDatasetId = null;
let activeFilters = {};


/* =========================================================
   LOAD DASHBOARD
   ========================================================= */

async function loadDashboard() {

    const dashboard = document.getElementById("dashboard");

    try {

        /* -------------------------------------------------
           GET DATASET ID
        ------------------------------------------------- */

        const params = new URLSearchParams(
            window.location.search
        );

        currentDatasetId = params.get("dataset_id");

        if (!currentDatasetId) {

            throw new Error(
                "Dataset ID is missing from the URL."
            );

        }


        /* -------------------------------------------------
           BUILD API URL
        ------------------------------------------------- */

        const url = new URL(
            `${API_URL}/dashboard`,
            window.location.origin
        );

        url.searchParams.set(
            "dataset_id",
            currentDatasetId
        );


        /* -------------------------------------------------
           ADD ACTIVE FILTERS
        ------------------------------------------------- */

        if (
            activeFilters &&
            Object.keys(activeFilters).length > 0
        ) {

            url.searchParams.set(
                "filters",
                JSON.stringify(activeFilters)
            );

        }


        console.log(
            "Loading dashboard:",
            url.toString()
        );


        /* -------------------------------------------------
           FETCH DATA
        ------------------------------------------------- */

        const response = await fetch(
            url.toString(),
            {
                cache: "no-store"
            }
        );


        if (!response.ok) {

            const errorData =
                await response
                    .json()
                    .catch(() => ({}));

            throw new Error(
                errorData.detail ||
                "Could not load dashboard."
            );

        }


        const data = await response.json();


        console.log(
            "Dashboard response:",
            data
        );


        /* -------------------------------------------------
           RENDER
        ------------------------------------------------- */

        renderDatasetInfo(data);

        renderFilters(
            data.filter_options || {},
            data.active_filters || {}
        );

        renderKPIs(
            data.kpis || []
        );

        renderDetectedColumns(
            data.detected_columns || {}
        );

        renderCharts(
            data.charts || []
        );

    }

    catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

        if (dashboard) {

            dashboard.innerHTML = `
                <div class="error-box">

                    <div class="error-icon">
                        ⚠
                    </div>

                    <h2>
                        Dashboard Error
                    </h2>

                    <p>
                        ${escapeHtml(
                            error.message
                        )}
                    </p>

                    <button
                        class="retry-btn"
                        onclick="loadDashboard()"
                    >
                        Try Again
                    </button>

                </div>
            `;

        }

    }

}


/* =========================================================
   DATASET INFORMATION
   ========================================================= */

function renderDatasetInfo(data) {

    const dataset = data.dataset || {};


    const datasetName =
        document.getElementById("datasetName");

    const filename =
        document.getElementById("filename");

    const rowCount =
        document.getElementById("rowCount");

    const columnCount =
        document.getElementById("columnCount");


    if (datasetName) {

        datasetName.textContent =
            dataset.dataset_name || "Unknown";

    }


    if (filename) {

        filename.textContent =
            dataset.filename || "-";

    }


    if (rowCount) {

        rowCount.textContent =
            formatNumber(
                dataset.rows
            );

    }


    if (columnCount) {

        columnCount.textContent =
            formatNumber(
                dataset.columns
            );

    }

}


/* =========================================================
   FILTERS
   ========================================================= */

function renderFilters(
    filterOptions,
    serverActiveFilters = {}
) {

    const container =
        document.getElementById(
            "filterContainer"
        );


    if (!container) {

        console.warn(
            "filterContainer not found."
        );

        return;

    }


    container.innerHTML = "";


    const categories =
        filterOptions.categories || {};

    const categoryNames =
        Object.keys(categories);


    /* -----------------------------------------------------
       CATEGORY FILTERS
       ----------------------------------------------------- */

    categoryNames.forEach(
        column => {

            const wrapper =
                document.createElement(
                    "div"
                );

            wrapper.className =
                "filter-item";


            const label =
                document.createElement(
                    "label"
                );

            label.textContent =
                formatColumnName(column);


            const select =
                document.createElement(
                    "select"
                );

            select.dataset.column =
                column;


            const allOption =
                document.createElement(
                    "option"
                );

            allOption.value = "";

            allOption.textContent =
                `All ${formatColumnName(column)}`;

            select.appendChild(
                allOption
            );


            const values =
                categories[column] || [];


            values.forEach(
                value => {

                    const option =
                        document.createElement(
                            "option"
                        );

                    option.value =
                        String(value);

                    option.textContent =
                        String(value);

                    select.appendChild(
                        option
                    );

                }
            );


            /* Restore selected value */

            if (
                serverActiveFilters[column] !==
                undefined
            ) {

                select.value =
                    String(
                        serverActiveFilters[column]
                    );

            }


            wrapper.appendChild(
                label
            );

            wrapper.appendChild(
                select
            );

            container.appendChild(
                wrapper
            );

        }
    );


    /* -----------------------------------------------------
       DATE FILTER
       ----------------------------------------------------- */

    const dateColumn =
        filterOptions.date_column;


    if (dateColumn) {

        createDateFilter(
            container,
            dateColumn,
            serverActiveFilters
        );

    }


    /* -----------------------------------------------------
       EMPTY FILTER MESSAGE
       ----------------------------------------------------- */

    if (
        categoryNames.length === 0 &&
        !dateColumn
    ) {

        container.innerHTML = `
            <div class="filter-empty">
                No automatic filters are available
                for this dataset.
            </div>
        `;

    }

}


/* =========================================================
   DATE FILTER
   ========================================================= */

function createDateFilter(
    container,
    dateColumn,
    serverActiveFilters
) {

    const title =
        document.createElement(
            "div"
        );

    title.className =
        "filter-date-title";

    title.textContent =
        `${formatColumnName(dateColumn)} Range`;


    const dateWrapper =
        document.createElement(
            "div"
        );

    dateWrapper.className =
        "date-filter-group";


    /* FROM */

    const fromWrapper =
        document.createElement(
            "div"
        );

    fromWrapper.className =
        "date-filter-item";


    const fromLabel =
        document.createElement(
            "label"
        );

    fromLabel.textContent =
        "From";


    const fromInput =
        document.createElement(
            "input"
        );

    fromInput.type =
        "date";

    fromInput.id =
        "dateFrom";

    fromInput.dataset.column =
        "date_from";


    if (
        serverActiveFilters.date_from
    ) {

        fromInput.value =
            serverActiveFilters.date_from;

    }


    fromWrapper.appendChild(
        fromLabel
    );

    fromWrapper.appendChild(
        fromInput
    );


    /* TO */

    const toWrapper =
        document.createElement(
            "div"
        );

    toWrapper.className =
        "date-filter-item";


    const toLabel =
        document.createElement(
            "label"
        );

    toLabel.textContent =
        "To";


    const toInput =
        document.createElement(
            "input"
        );

    toInput.type =
        "date";

    toInput.id =
        "dateTo";

    toInput.dataset.column =
        "date_to";


    if (
        serverActiveFilters.date_to
    ) {

        toInput.value =
            serverActiveFilters.date_to;

    }


    toWrapper.appendChild(
        toLabel
    );

    toWrapper.appendChild(
        toInput
    );


    dateWrapper.appendChild(
        fromWrapper
    );

    dateWrapper.appendChild(
        toWrapper
    );


    const dateContainer =
        document.createElement(
            "div"
        );

    dateContainer.className =
        "date-filter-container";

    dateContainer.appendChild(
        title
    );

    dateContainer.appendChild(
        dateWrapper
    );


    container.appendChild(
        dateContainer
    );

}


/* =========================================================
   APPLY FILTERS
   ========================================================= */

function applyFilters() {

    const newFilters = {};


    /* -----------------------------------------------------
       CATEGORY SELECTS
       ----------------------------------------------------- */

    const selects =
        document.querySelectorAll(
            "#filterContainer select"
        );


    selects.forEach(
        select => {

            const column =
                select.dataset.column;

            const value =
                select.value;


            if (
                column &&
                value
            ) {

                newFilters[column] =
                    value;

            }

        }
    );


    /* -----------------------------------------------------
       DATE FROM
       ----------------------------------------------------- */

    const dateFrom =
        document.getElementById(
            "dateFrom"
        );


    if (
        dateFrom &&
        dateFrom.value
    ) {

        newFilters.date_from =
            dateFrom.value;

    }


    /* -----------------------------------------------------
       DATE TO
       ----------------------------------------------------- */

    const dateTo =
        document.getElementById(
            "dateTo"
        );


    if (
        dateTo &&
        dateTo.value
    ) {

        newFilters.date_to =
            dateTo.value;

    }


    activeFilters =
        newFilters;


    console.log(
        "Applying filters:",
        activeFilters
    );


    loadDashboard();

}


/* =========================================================
   CLEAR FILTERS
   ========================================================= */

function clearFilters() {

    activeFilters = {};

    console.log(
        "Filters cleared."
    );

    loadDashboard();

}


/* =========================================================
   KPI
   ========================================================= */

function renderKPIs(kpis) {

    const container =
        document.getElementById(
            "kpiContainer"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (
        !kpis ||
        !kpis.length
    ) {

        container.innerHTML = `
            <div class="empty-state">
                No KPIs available for this dataset.
            </div>
        `;

        return;

    }


    kpis.forEach(
        kpi => {

            const card =
                document.createElement(
                    "div"
                );

            card.className =
                "kpi-card";


            const value =
                formatKPIValue(
                    kpi.value
                );


            card.innerHTML = `

                <span class="kpi-title">
                    ${escapeHtml(
                        kpi.title || "KPI"
                    )}
                </span>

                <strong class="kpi-value">
                    ${escapeHtml(value)}
                </strong>

                ${
                    kpi.column
                    ?
                    `
                    <div class="kpi-column">
                        ${escapeHtml(
                            kpi.column
                        )}
                    </div>
                    `
                    :
                    ""
                }

            `;


            container.appendChild(
                card
            );

        }
    );

}


/* =========================================================
   DETECTED COLUMNS
   ========================================================= */

function renderDetectedColumns(
    detected
) {

    const container =
        document.getElementById(
            "detectedColumns"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    const entries =
        Object.entries(
            detected || {}
        );


    if (!entries.length) {

        container.innerHTML = `
            <span class="muted">
                No detected column information.
            </span>
        `;

        return;

    }


    entries.forEach(
        ([type, value]) => {

            if (
                value === null ||
                value === undefined
            ) {

                return;

            }


            const values =
                Array.isArray(value)
                    ? value
                    : [value];


            if (!values.length) {
                return;
            }


            const title =
                formatColumnName(type);


            const wrapper =
                document.createElement(
                    "div"
                );

            wrapper.className =
                "detected-group";


            const heading =
                document.createElement(
                    "strong"
                );

            heading.textContent =
                title;


            const content =
                document.createElement(
                    "div"
                );

            content.className =
                "detected-values";


            values.forEach(
                item => {

                    const pill =
                        document.createElement(
                            "span"
                        );

                    pill.className =
                        getDetectedPillClass(
                            type
                        );

                    pill.textContent =
                        formatColumnName(
                            item
                        );

                    content.appendChild(
                        pill
                    );

                }
            );


            wrapper.appendChild(
                heading
            );

            wrapper.appendChild(
                content
            );


            container.appendChild(
                wrapper
            );

        }
    );

}


/* =========================================================
   CHARTS
   ========================================================= */

function renderCharts(charts) {

    const container =
        document.getElementById(
            "chartContainer"
        );


    if (!container) {

        console.error(
            "chartContainer not found."
        );

        return;

    }


    /* Destroy existing charts */

    activeCharts.forEach(
        chart => {

            try {

                chart.destroy();

            }

            catch (error) {

                console.warn(
                    "Could not destroy chart:",
                    error
                );

            }

        }
    );


    activeCharts = [];


    container.innerHTML = "";


    if (
        !charts ||
        !charts.length
    ) {

        container.innerHTML = `
            <div class="empty-state chart-empty">
                <div class="empty-icon">
                    📊
                </div>

                <h3>
                    No charts available
                </h3>

                <p>
                    The current dataset does not
                    contain enough compatible data.
                </p>
            </div>
        `;

        return;

    }


    charts.forEach(
        (chartData, index) => {

            try {

                const card =
                    document.createElement(
                        "div"
                    );

                card.className =
                    "chart-card";


                /* -----------------------------------------
                   HEADER
                   ----------------------------------------- */

                const header =
                    document.createElement(
                        "div"
                    );

                header.className =
                    "chart-header";


                const titleBlock =
                    document.createElement(
                        "div"
                    );


                const title =
                    document.createElement(
                        "h3"
                    );

                title.textContent =
                    chartData.title ||
                    `Chart ${index + 1}`;


                const description =
                    document.createElement(
                        "p"
                    );

                if (
                    chartData.description
                ) {

                    description.textContent =
                        chartData.description;

                }


                titleBlock.appendChild(
                    title
                );


                if (
                    chartData.description
                ) {

                    titleBlock.appendChild(
                        description
                    );

                }


                const badge =
                    document.createElement(
                        "span"
                    );

                badge.className =
                    "chart-badge";

                badge.textContent =
                    getChartDisplayType(
                        chartData.type
                    );


                header.appendChild(
                    titleBlock
                );

                header.appendChild(
                    badge
                );


                /* -----------------------------------------
                   WRAPPER
                   ----------------------------------------- */

                const wrapper =
                    document.createElement(
                        "div"
                    );

                wrapper.className =
                    "chart-wrapper";


                const canvas =
                    document.createElement(
                        "canvas"
                    );

                canvas.id =
                    `chart-${index}`;


                wrapper.appendChild(
                    canvas
                );


                card.appendChild(
                    header
                );

                card.appendChild(
                    wrapper
                );


                container.appendChild(
                    card
                );


                createChart(
                    canvas,
                    chartData
                );

            }

            catch (error) {

                console.error(
                    "Chart creation error:",
                    error,
                    chartData
                );

                const errorCard =
                    document.createElement(
                        "div"
                    );

                errorCard.className =
                    "chart-card chart-error";

                errorCard.innerHTML = `
                    <h3>
                        ${escapeHtml(
                            chartData.title ||
                            `Chart ${index + 1}`
                        )}
                    </h3>

                    <p>
                        Could not render this chart.
                    </p>
                `;

                container.appendChild(
                    errorCard
                );

            }

        }
    );

}


/* =========================================================
   CREATE CHART
   ========================================================= */

function createChart(
    canvas,
    chartData
) {

    if (
        typeof window.Chart ===
        "undefined"
    ) {

        throw new Error(
            "Chart.js is not loaded."
        );

    }


    const rawData =
        chartData.data || [];


    if (!rawData.length) {

        throw new Error(
            "Chart contains no data."
        );

    }


    let chartType =
        chartData.type ||
        "bar";


    /* -----------------------------------------------------
       CONVERT BACKEND TYPES TO CHART.JS TYPES
       ----------------------------------------------------- */

    if (
        chartType ===
        "horizontalBar"
    ) {

        chartType =
            "bar";

    }


    if (
        chartType ===
        "histogram"
    ) {

        chartType =
            "bar";

    }


    /* -----------------------------------------------------
       DOUGHNUT
       ----------------------------------------------------- */

    if (
        chartType ===
        "doughnut"
    ) {

        const labels =
            rawData.map(
                item =>
                    item.x ??
                    item.label ??
                    ""
            );


        const values =
            rawData.map(
                item =>
                    Number(
                        item.y ??
                        item.value ??
                        0
                    )
            );


        const chart =
            new Chart(
                canvas,
                {

                    type: "doughnut",

                    data: {

                        labels: labels,

                        datasets: [

                            {
                                label:
                                    chartData.title ||
                                    "Value",

                                data:
                                    values
                            }

                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,

                        animation: {
                            duration: 500
                        },

                        plugins: {

                            legend: {

                                position:
                                    "bottom"

                            }

                        }

                    }

                }
            );


        activeCharts.push(
            chart
        );

        return;

    }


    /* -----------------------------------------------------
       SCATTER
       ----------------------------------------------------- */

    if (
        chartType ===
        "scatter"
    ) {

        const points =
            rawData.map(
                item => ({

                    x: Number(
                        item.x
                    ),

                    y: Number(
                        item.y
                    )

                })
            );


        const chart =
            new Chart(
                canvas,
                {

                    type: "scatter",

                    data: {

                        datasets: [

                            {

                                label:
                                    chartData.title ||
                                    "Relationship",

                                data:
                                    points

                            }

                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio:
                            false,

                        plugins: {

                            legend: {
                                display: true
                            }

                        },

                        scales: {

                            x: {
                                type: "linear"
                            },

                            y: {
                                beginAtZero: true
                            }

                        }

                    }

                }
            );


        activeCharts.push(
            chart
        );

        return;

    }


    /* -----------------------------------------------------
       BAR / LINE
       ----------------------------------------------------- */

    const labels =
        rawData.map(
            item =>
                item.x ??
                item.label ??
                ""
        );


    const values =
        rawData.map(
            item =>
                Number(
                    item.y ??
                    item.value ??
                    0
                )
        );


    const isHorizontal =
        chartData.type ===
        "horizontalBar";


    const isHistogram =
        chartData.type ===
        "histogram";


    const chart =
        new Chart(
            canvas,
            {

                type: chartType,

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                chartData.title ||
                                "Value",

                            data:
                                values,

                            borderWidth:
                                chartType ===
                                "line"
                                    ? 2
                                    : 1,

                            tension:
                                chartType ===
                                "line"
                                    ? 0.3
                                    : 0

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio:
                        false,

                    animation: {
                        duration: 500
                    },

                    indexAxis:
                        isHorizontal
                            ? "y"
                            : "x",

                    plugins: {

                        legend: {

                            display:
                                chartType ===
                                "line"

                        }

                    },

                    scales: {

                        x: {

                            beginAtZero:
                                !isHorizontal

                        },

                        y: {

                            beginAtZero:
                                true

                        }

                    }

                }

            }
        );


    activeCharts.push(
        chart
    );

}


/* =========================================================
   REFRESH
   ========================================================= */

function refreshDashboard() {

    loadDashboard();

}


/* =========================================================
   HELPERS
   ========================================================= */

function formatColumnName(
    value
) {

    return String(value || "")
        .replace(/_/g, " ")
        .replace(/\s+/g, " ")
        .trim()
        .replace(/\b\w/g, char =>
            char.toUpperCase()
        );

}


function formatNumber(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        return "-";

    }


    const number =
        Number(value);


    if (
        Number.isNaN(number)
    ) {

        return String(value);

    }


    return number.toLocaleString(
        "en-IN"
    );

}


function formatKPIValue(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "-";

    }


    const number =
        Number(value);


    if (
        Number.isNaN(number)
    ) {

        return String(value);

    }


    if (
        Number.isInteger(number)
    ) {

        return number.toLocaleString(
            "en-IN"
        );

    }


    return number.toLocaleString(
        "en-IN",
        {
            maximumFractionDigits: 2
        }
    );

}


function getChartDisplayType(
    type
) {

    switch (type) {

        case "horizontalBar":
            return "Bar";

        case "doughnut":
            return "Doughnut";

        case "line":
            return "Trend";

        case "histogram":
            return "Distribution";

        case "scatter":
            return "Relationship";

        case "bar":
            return "Bar";

        default:
            return "Chart";

    }

}


function getDetectedPillClass(
    type
) {

    const normalized =
        String(type)
            .toLowerCase();


    if (
        normalized ===
        "numeric"
    ) {

        return "data-pill numeric-pill";

    }


    if (
        normalized ===
        "category"
    ) {

        return "data-pill category-pill";

    }


    if (
        normalized ===
        "date"
    ) {

        return "data-pill date-pill";

    }


    return "data-pill";

}


function escapeHtml(value) {

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}


/* =========================================================
   START
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadDashboard();

    }
);