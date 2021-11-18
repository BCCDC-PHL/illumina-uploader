
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

const updateTable = () => {
    fetch('http://localhost:8081/api/runs/')
      .then(response => response.json())
      .then(data => {
          gridOptions.api.setRowData(data);
      });
}

document.addEventListener('DOMContentLoaded', () => {    
    const gridDiv = document.querySelector('#runsTable');
    new agGrid.Grid(gridDiv, gridOptions);
    updateTable();
    var intervalId = window.setInterval(updateTable, 5000)
});
