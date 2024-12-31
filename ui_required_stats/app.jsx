import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "./App.css";

const App = () => {
    const [activeTab, setActiveTab] = useState("stats");
    const [columns, setColumns] = useState([]);
    const [data, setData] = useState([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [sortConfig, setSortConfig] = useState({ key: null, direction: "ascending" });
    const [isCareerStats, setIsCareerStats] = useState(false);
    const [playerName, setPlayerName] = useState("");
    const [matchNumbers, setMatchNumbers] = useState([]);
    const [selectedMatchNumber, setSelectedMatchNumber] = useState("");
    const [conferences, setConferences] = useState([]);
    const [selectedConference, setSelectedConference] = useState("");
    const [divisions, setDivisions] = useState([]); // State to store unique divisions
    const [selectedDivision, setSelectedDivision] = useState(""); // State to store selected division
    const [teams, setTeams] = useState([]); // State to store unique teams
    const [selectedTeam, setSelectedTeam] = useState(""); // State to store selected team

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
                    const uniqueMatchNumbers = [...new Set(fetchedData.map(row => row["Match Number"]))];
                    setMatchNumbers(uniqueMatchNumbers);
                }

                if (fileName === "nfl_official_team_roster.csv") {
                    const uniqueConferences = [...new Set(fetchedData.map(row => row.Conference))];
                    setConferences(uniqueConferences);

                    // Extract unique divisions for NFL Depth Chart
                    const uniqueDivisions = [...new Set(fetchedData.map(row => row.Division))];
                    setDivisions(uniqueDivisions);

                    // Extract unique teams for NFL Depth Chart
                    const uniqueTeams = [...new Set(fetchedData.map(row => row.Team))];
                    setTeams(uniqueTeams);
                }

                if (selectedMatchNumber && fileName === "schedule.csv") {
                    fetchedData = fetchedData.filter(row => row["Match Number"] === selectedMatchNumber);
                }

                if (selectedConference && fileName === "nfl_official_team_roster.csv") {
                    fetchedData = fetchedData.filter(row => row.Conference === selectedConference);
                }

                // Filter by division if selected
                if (selectedDivision && fileName === "nfl_official_team_roster.csv") {
                    fetchedData = fetchedData.filter(row => row.Division === selectedDivision);
                }

                // Filter by team if selected
                if (selectedTeam && fileName === "nfl_official_team_roster.csv") {
                    fetchedData = fetchedData.filter(row => row.Team === selectedTeam);
                }

                setData(fetchedData);
            })
            .catch((error) => {
                console.error("Error loading CSV file:", error);
            });
    };

    useEffect(() => {
        fetchStats(getFileNameForActiveTab());
    }, [activeTab, selectedMatchNumber, selectedConference, selectedDivision, selectedTeam]); // Include selectedTeam as dependency

    const handleSearchChange = (event) => {
        const query = event.target.value;
        setSearchQuery(query);

        if (query) {
            const filteredData = data.filter((row) =>
                row.Player.toLowerCase().includes(query.toLowerCase())
            );
            setData(filteredData);
        } else {
            fetchStats(getFileNameForActiveTab());
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

    const handleConferenceChange = (event) => {
        setSelectedConference(event.target.value);
    };

    const handleDivisionChange = (event) => {
        setSelectedDivision(event.target.value);
    };

    const handleTeamChange = (event) => {
        setSelectedTeam(event.target.value);
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
                    <button onClick={() => setActiveTab("stats")}>QB Rankings</button>
                    <button onClick={() => setActiveTab("rbStats")}>RB Rankings</button>
                    <button onClick={() => setActiveTab("wrStats")}>WR Rankings</button>
                    <button onClick={() => setActiveTab("kickerStats")}>Kicker Rankings</button>
                    <button onClick={() => setActiveTab("defenseStats")}>Defense Rankings</button>
                    <button onClick={() => setActiveTab("schedule")}>2024-2025 Schedule</button>
                    <button onClick={() => setActiveTab("roster")}>NFL Depth Chart</button>
                </nav>
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
                <div className="search-container">
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

                    {activeTab === "roster" && (
                        <div>
                            <label htmlFor="conference">Select Conference: </label>
                            <select
                                id="conference"
                                value={selectedConference}
                                onChange={handleConferenceChange}
                            >
                                <option value="">All Conferences</option>
                                {conferences.map((conference, index) => (
                                    <option key={index} value={conference}>
                                        {conference}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    {activeTab === "roster" && (
                        <div>
                            <label htmlFor="division">Select Division: </label>
                            <select
                                id="division"
                                value={selectedDivision}
                                onChange={handleDivisionChange}
                            >
                                <option value="">All Divisions</option>
                                {divisions.map((division, index) => (
                                    <option key={index} value={division}>
                                        {division}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    {activeTab === "roster" && (
                        <div>
                            <label htmlFor="team">Select Team: </label>
                            <select
                                id="team"
                                value={selectedTeam}
                                onChange={handleTeamChange}
                            >
                                <option value="">All Teams</option>
                                {teams.map((team, index) => (
                                    <option key={index} value={team}>
                                        {team}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}
                </div>
            </header>

            <div>
                {data.length > 0 ? renderTable() : <p>Loading data...</p>}
            </div>
        </div>
    );
};

export default App;
