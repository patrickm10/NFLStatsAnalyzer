import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "./App.css";

const App = () => {
    const [activeTab, setActiveTab] = useState("stats");
    const [columns, setColumns] = useState([]);
    const [data, setData] = useState([]);
    const [sortConfig, setSortConfig] = useState({ key: null, direction: "ascending" });
    const [isCareerStats, setIsCareerStats] = useState(false);
    const [playerName, setPlayerName] = useState("");
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
        fetchStats(getFileNameForActiveTab());
    }, [activeTab, selectedMatchNumber]);

    const getFileNameForActiveTab = () => {
        switch (activeTab) {
            case "stats": return "official_qb_stats.csv";
            case "rbStats": return "official_rb_stats.csv";
            case "wrStats": return "official_wr_stats.csv";
            case "kickerStats": return "official_kicker_stats.csv";
            case "defenseStats": return "official_defense_stats.csv";
            case "schedule": return "schedule.csv";
            case "roster": return "nfl_official_team_roster.csv";
            default: return "";
        }
    };

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

    const handlePlayerClick = (player) => {
        let playerFileName = "";
        let filePath = "";

        if (activeTab === "stats") {
            playerFileName = `${player.Player.replace(/ /g, "_")}_career_passing_stats.csv`;
            filePath = `/data/qb_stats/career_stats/${playerFileName}`;
        } else if (activeTab === "rbStats") {
            playerFileName = `${player.Player.replace(/ /g, "_")}_career_rushing_stats.csv`;
            filePath = `/data/rb_stats/career_stats/${playerFileName}`;
        } else if (activeTab === "wrStats") {
            playerFileName = `${player.Player.replace(/ /g, "_")}_career_receiving_stats.csv`;
            filePath = `/data/wr_stats/career_stats/${playerFileName}`;
        } else if (activeTab === "kickerStats") {
            playerFileName = `${player.Player.replace(/ /g, "_")}_career_kicking_stats.csv`;
            filePath = `/data/kicker_stats/career_stats/${playerFileName}`;
        }

        console.log(`Fetching player data from: ${filePath}`);
        fetch(filePath)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then((csvText) => {
                const parsedData = Papa.parse(csvText, { header: true });
                setColumns(parsedData.meta.fields || []);
                setData(parsedData.data || []);
                setIsCareerStats(true);
                setPlayerName(player.Player);
            })
            .catch((error) => {
                console.error("Error loading player CSV file:", error);
            });
    };

    const handleBackClick = () => {
        setIsCareerStats(false);
        setPlayerName("");
        fetchStats(getFileNameForActiveTab());
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
                    <tr key={rowIndex} onClick={() => handlePlayerClick(row)}>
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
                    <button onClick={() => setActiveTab("stats")}>QB Rankings</button>
                    <button onClick={() => setActiveTab("rbStats")}>RB Rankings</button>
                    <button onClick={() => setActiveTab("wrStats")}>WR Rankings</button>
                    <button onClick={() => setActiveTab("kickerStats")}>Kicker Rankings</button>
                    <button onClick={() => setActiveTab("defenseStats")}>Defense Rankings</button>
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
                <h3>
                    {activeTab === "stats" ? "Quarterback Stats" :
                        activeTab === "rbStats" ? "Running Back Stats" :
                        activeTab === "wrStats" ? "Wide Receiver Stats" :
                        activeTab === "kickerStats" ? "Kicker Stats" :
                        activeTab === "defenseStats" ? "Defense Stats" :
                        activeTab === "schedule" ? "2024-2025 Schedule" :
                        activeTab === "roster" ? "NFL Roster" :
                        "Schedule"}
                </h3>
            </header>
            <div>
                {isCareerStats && (
                    <div>
                        <button onClick={handleBackClick}>Back to stats</button>
                        <h3>{playerName}'s Career Stats</h3>
                    </div>
                )}
                {data.length > 0 ? renderTable() : <p>Loading data...</p>}
            </div>
        </div>
    );
};

export default App;
