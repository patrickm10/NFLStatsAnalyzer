import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "./App.css";

const App = () => {
    const [activeTab, setActiveTab] = useState("schedule");
    const [columns, setColumns] = useState([]);
    const [data, setData] = useState([]);
    const [sortConfig, setSortConfig] = useState({ key: null, direction: "ascending" });
    const [matchNumbers, setMatchNumbers] = useState([]);
    const [selectedMatchNumber, setSelectedMatchNumber] = useState("");

    const fetchStats = (fileName) => {
        console.log(`Fetching data for: ${fileName}`);
        fetch(`/data/${fileName}`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then((csvText) => {
                const parsedData = Papa.parse(csvText, { header: true });
                setColumns(parsedData.meta.fields || []);
                let fetchedData = parsedData.data || [];

                if (fileName === "schedule.csv") {
                    const uniqueMatchNumbers = [...new Set(fetchedData.map(row => row["Match Number"]))];
                    setMatchNumbers(uniqueMatchNumbers);
                }

                if (selectedMatchNumber) {
                    fetchedData = fetchedData.filter(row => row["Match Number"] === selectedMatchNumber);
                }

                setData(fetchedData);
            })
            .catch((error) => {
                console.error("Error loading CSV file:", error);
            });
    };

    useEffect(() => {
        fetchStats(activeTab === "schedule" ? "schedule.csv" : "nfl_official_team_roster.csv");
    }, [activeTab, selectedMatchNumber]);

    const handleSort = (column) => {
        let direction = "ascending";
        if (sortConfig.key === column && sortConfig.direction === "ascending") {
            direction = "descending";
        }

        const sortedData = [...data].sort((a, b) => {
            const aValue = a[column] ?? "";
            const bValue = b[column] ?? "";

            const aNumeric = isNaN(aValue) ? aValue : parseFloat(aValue);
            const bNumeric = isNaN(bValue) ? bValue : parseFloat(bValue);

            if (aNumeric < bNumeric) return direction === "ascending" ? -1 : 1;
            if (aNumeric > bNumeric) return direction === "ascending" ? 1 : -1;
            return 0;
        });

        setData(sortedData);
        setSortConfig({ key: column, direction });
    };

    const handleMatchNumberChange = (event) => {
        setSelectedMatchNumber(event.target.value);
    };

    const renderTable = () => (
        <table>
            <thead>
                <tr>
                    {columns.map((col, index) => (
                        <th key={index} onClick={() => handleSort(col)}>
                            {col}
                            {sortConfig.key === col ? (sortConfig.direction === "ascending" ? " ↑" : " ↓") : ""}
                        </th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {data.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                        {columns.map((col, colIndex) => (
                            <td key={colIndex}>{row[col]}</td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    );

    return (
        <div>
            <header>
                <h1>NFL Statistics Analyzer</h1>
                <nav>
                    <button onClick={() => setActiveTab("schedule")}>2024-2025 Schedule</button>
                    <button onClick={() => setActiveTab("roster")}>NFL Roster</button>
                </nav>
                {activeTab === "schedule" && (
                    <div>
                        <label htmlFor="matchNumber">Select Week: </label>
                        <select
                            id="matchNumber"
                            value={selectedMatchNumber}
                            onChange={handleMatchNumberChange}
                        >
                            <option value="">All Weeks</option>
                            {matchNumbers.map((matchNumber, index) => (
                                <option key={index} value={matchNumber}>
                                    Week {matchNumber}
                                </option>
                            ))}
                        </select>
                    </div>
                )}
                <h3>{activeTab === "schedule" ? "2024-2025 Schedule" : "NFL Roster"}</h3>
            </header>
            <div>
                {data.length > 0 ? renderTable() : <p>Loading data...</p>}
            </div>
        </div>
    );
};

export default App;
