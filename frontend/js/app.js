async function uploadFile() {

    const fileInput = document.getElementById("fileInput");

    const status = document.getElementById("status");

    const datasetInfo = document.getElementById("datasetInfo");

    const uploadButton = document.getElementById("uploadButton");


    if (!fileInput.files.length) {

        status.innerHTML =
            "Please select a CSV or Excel file.";

        return;
    }


    const file = fileInput.files[0];


    const formData = new FormData();

    formData.append("file", file);


    uploadButton.disabled = true;

    uploadButton.innerText = "Uploading...";

    status.innerHTML = "Uploading and analyzing dataset...";


    try {

        const response = await fetch(
            "/api/upload",
            {
                method: "POST",
                body: formData
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail || "Upload failed"
            );
        }


        status.innerHTML =
            "Dataset analyzed successfully!";


        document.getElementById(
            "fileName"
        ).innerText = data.filename;


        document.getElementById(
            "rowCount"
        ).innerText = data.rows;


        document.getElementById(
            "columnCount"
        ).innerText = data.columns_count;


        datasetInfo.style.display = "block";


        // Store dataset ID

        localStorage.setItem(
            "dataset_id",
            data.dataset_id
        );


    } catch (error) {

        status.innerHTML =
            "Error: " + error.message;

    }


    uploadButton.disabled = false;

    uploadButton.innerText =
        "Upload & Analyze";
}



function openDashboard() {

    const datasetId =
        localStorage.getItem("dataset_id");


    if (!datasetId) {

        alert("Please upload a dataset first.");

        return;
    }


    window.location.href =
        "/dashboard.html?dataset_id=" +
        datasetId;
}