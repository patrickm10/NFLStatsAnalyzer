import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "./App.css";

const App = () => {
    const [activeTab, setActiveTab] = useState("stats");
    const [columns, setColumns] = useState([]);
    const [data, setData] = useState([]);
    const [searchQuery, setSearchQuery] = useState(""); // State to store the search query
    const [sortConfig, setSortConfig] = useState({ key: null, direction: "ascending" }); // State for sorting
    const [isCareerStats, setIsCareerStats] = useState(false); // State to track if career stats are being displayed
    const [playerName, setPlayerName] = useState(""); // State to store the player's name
    const [matchNumbers, setMatchNumbers] = useState([]); // State to store unique match numbers
    const [selectedMatchNumber, setSelectedMatchNumber] = useState(""); // State to store selected match number

    // Fetch stats for the specific tab
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
                    // Extract unique match numbers from the schedule
                    const uniqueMatchNumbers = [...new Set(fetchedData.map(row => row["Match Number"]))];
                    setMatchNumbers(uniqueMatchNumbers);
                }

                // Filter by match number if selected
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
    }, [activeTab, selectedMatchNumber]); // Include selectedMatchNumber as dependency to re-fetch when it changes

    const handleSearchChange = (event) => {
        const query = event.target.value;
        setSearchQuery(query);

        // Filter data dynamically as user types in the search bar
        if (query) {
            const filteredData = data.filter((row) =>
                row.Player.toLowerCase().includes(query.toLowerCase())
            );
            setData(filteredData);
        } else {
            fetchStats(getFileNameForActiveTab()); // Reset to the original data
        }
    };

    const getFileNameForActiveTab = () => {
        switch (activeTab) {
            case "stats":
                return "official_qb_stats.csv";
            case "rbStats":
                return "official_rb_stats.csv";
            case "wrStats":
                return "official_wr_stats.csv";
            case "kickerStats":
                return "official_kicker_stats.csv";
            case "defenseStats":
                return "official_defense_stats.csv";
            case "schedule":
                return "schedule.csv";
            case "roster":
                return "nfl_official_team_roster.csv";
            default:
                return "";
        }
    };

    // Function to handle sorting of columns
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
                setIsCareerStats(true); // Show career stats
                setPlayerName(player.Player); // Set the player's name
            })
            .catch((error) => {
                console.error("Error loading player CSV file:", error);
            });
    };

    const handleBackClick = () => {
        setIsCareerStats(false); // Go back to the previous view
        setPlayerName(""); // Clear the player's name
        setSearchQuery(""); // Reset search query
        fetchStats(getFileNameForActiveTab()); // Re-fetch the stats data
    };

    // Handle the change of match number from dropdown
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
                <nav className="tabs-nav">
                    <button onClick={() => { setActiveTab("stats"); setSearchQuery(""); }}>QB Rankings</button>
                    <button onClick={() => { setActiveTab("rbStats"); setSearchQuery(""); }}>RB Rankings</button>
                    <button onClick={() => { setActiveTab("wrStats"); setSearchQuery(""); }}>WR Rankings</button>
                    <button onClick={() => { setActiveTab("kickerStats"); setSearchQuery(""); }}>Kicker Rankings</button>
                    <button onClick={() => { setActiveTab("defenseStats"); setSearchQuery(""); }}>Defense Rankings</button>
                    <button onClick={() => { setActiveTab("schedule"); setSearchQuery(""); }}>2024-2025 Schedule</button>
                    <button onClick={() => { setActiveTab("roster"); setSearchQuery(""); }}>NFL Depth Chart</button>
                </nav>

                <div className="search-container">
                    {/* Match number dropdown for schedule */}
                    {activeTab === "schedule" && (
                        <div>
                            <label htmlFor="matchNumber">Select Week: </label>
                            <select
                                id="matchNumber"
                                value={selectedMatchNumber}
                                onChange={handleMatchNumberChange}
                            >
                                <option value="">All Weeks</option>
                                {/* Add options dynamically based on matchNumbers */}
                                {matchNumbers.map((matchNumber, index) => (
                                    <option key={index} value={matchNumber}>
                                        Week {matchNumber}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    <div>
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={handleSearchChange}
                            placeholder="Search ..."
                        />
                    </div>
                </div>
                <h3>
                    {activeTab === "stats" ? "Quarterback Stats" :
                        activeTab === "rbStats" ? "Running Back Stats" :
                        activeTab === "wrStats" ? "Wide Receiver Stats" :
                        activeTab === "kickerStats" ? "Kicker Stats" :
                        activeTab === "defenseStats" ? "Defense Stats" :
                        activeTab === "schedule" ? "2024-2025 Schedule" :
                        activeTab === "roster" ? "NFL Depth Chart" :
                        "Schedule"}
                </h3>
            </header>

            {/* Content for active tab */}
            <div>
                {/* Show back button and player name if viewing career stats */}
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
