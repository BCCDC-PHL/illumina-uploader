const baseUrl = "http://localhost"
const apiPort = 8081
const apiBasePath = "/api"

const columnDefs = [
    { field: "run_id", headerName: "Run ID", minWidth: 300 },
    { field: "upload_timestamp", headerName: "Upload Timestamp" },
    { field: "upload_status", headerName: "Upload Status" }
];

const rowData = [
];

// let the grid know which columns and what data to use
const gridOptions = {
  columnDefs: columnDefs,
  rowData: rowData
};

// setup the grid after the page has finished loading
document.addEventListener('DOMContentLoaded', () => {
    const gridDiv = document.querySelector('#runsTable');
    new agGrid.Grid(gridDiv, gridOptions);
    
    agGrid.simpleHttpRequest({url: baseUrl + ":" + apiPort + apiBasePath + "/runs"})
        .then(data => {
            gridOptions.api.setRowData(data);
        });
});
