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
    const [isWeeklyStats, setIsWeeklyStats] = useState(false);
    const [playerName, setPlayerName] = useState("");
    const [careerStats, setCareerStats] = useState([]);
    const [weeklyStats, setWeeklyStats] = useState([]);
    const [matchNumbers, setMatchNumbers] = useState([]);
    const [selectedMatchNumber, setSelectedMatchNumber] = useState("");
    const [conferences, setConferences] = useState([]);
    const [selectedConference, setSelectedConference] = useState("");
    const [divisions, setDivisions] = useState([]);
    const [selectedDivision, setSelectedDivision] = useState("");
    const [teams, setTeams] = useState([]);
    const [selectedTeam, setSelectedTeam] = useState("");

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

                    const uniqueDivisions = [...new Set(fetchedData.map(row => row.Division))];
                    setDivisions(uniqueDivisions);

                    const uniqueTeams = [...new Set(fetchedData.map(row => row.Team))];
                    setTeams(uniqueTeams);
                }

                if (selectedMatchNumber && fileName === "schedule.csv") {
                    fetchedData = fetchedData.filter(row => row["Match Number"] === selectedMatchNumber);
                }

                if (selectedConference && fileName === "nfl_official_team_roster.csv") {
                    fetchedData = fetchedData.filter(row => row.Conference === selectedConference);
                }

                if (selectedDivision && fileName === "nfl_official_team_roster.csv") {
                    fetchedData = fetchedData.filter(row => row.Division === selectedDivision);
                }

                if (selectedTeam && fileName === "nfl_official_team_roster.csv") {
                    fetchedData = fetchedData.filter(row => row.Team === selectedTeam);
                }

                setData(fetchedData);
            })
            .catch((error) => {
                console.error("Error loading CSV file:", error);
            });
    };

    const fetchCareerStats = (playerName, filePath) => {
        console.log(`Fetching career stats for: ${playerName}`);
        fetch(filePath)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then((csvText) => {
                const parsedData = Papa.parse(csvText, { header: true });
                setCareerStats(parsedData.data || []);
            })
            .catch((error) => {
                console.error("Error loading career stats CSV file:", error);
            });
    };

    const fetchWeeklyStats = (playerName, filePath) => {
        console.log(`Fetching weekly stats for: ${playerName}`);
        fetch(filePath)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then((csvText) => {
                const parsedData = Papa.parse(csvText, { header: true });
                setWeeklyStats(parsedData.data || []);
            })
            .catch((error) => {
                console.error("Error loading weekly stats CSV file:", error);
            });
    };

    useEffect(() => {
        fetchStats(getFileNameForActiveTab());
    }, [activeTab, selectedMatchNumber, selectedConference, selectedDivision, selectedTeam]);

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

    const handlePlayerClick = (player) => {
        let playerFileName = "";
        let careerFilePath = "";
        let weeklyFilePath = "";

        if (activeTab === "stats") {
            playerFileName = `${player.Player.replace(/ /g, "_")}`;
            careerFilePath = `/data/qb_stats/career_stats/${playerFileName}_career_passing_stats.csv`;
            weeklyFilePath = `/data/qb_stats/qb_weekly_stats/${playerFileName}_weekly_stats.csv`;
        } else if (activeTab === "rbStats") {
            playerFileName = `${player.Player.replace(/ /g, "_")}`;
            careerFilePath = `/data/rb_stats/career_stats/${playerFileName}_career_rushing_stats.csv`;
            weeklyFilePath = `/data/rb_stats/rb_weekly_stats/${playerFileName}_weekly_stats.csv`;
        } else if (activeTab === "wrStats") {
            playerFileName = `${player.Player.replace(/ /g, "_")}`;
            careerFilePath = `/data/wr_stats/career_stats/${playerFileName}_career_receiving_stats.csv`;
            weeklyFilePath = `/data/wr_stats/wr_weekly_stats/${playerFileName}_weekly_stats.csv`;
        } else if (activeTab === "kickerStats") {
            playerFileName = `${player.Player.replace(/ /g, "_")}`;
            careerFilePath = `/data/kicker_stats/career_stats/${playerFileName}_career_kicking_stats.csv`;
            weeklyFilePath = `/data/kicker_stats/kicker_weekly_stats/${playerFileName}_kicking_stats.csv`;
        }

        console.log(`Fetching player data from: ${careerFilePath} and ${weeklyFilePath}`);
        fetchCareerStats(player.Player, careerFilePath);
        fetchWeeklyStats(player.Player, weeklyFilePath);
        setIsCareerStats(true);
        setIsWeeklyStats(true);
        setPlayerName(player.Player);
    };

    const handleBackClick = () => {
        setIsCareerStats(false);
        setIsWeeklyStats(false);
        setPlayerName("");
        setSearchQuery("");
        fetchStats(getFileNameForActiveTab());
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

    const renderCareerStats = () => (
        <div>
            <h2>{playerName}'s Career Stats</h2>
            {careerStats.length > 0 ? (
                <table>
                    <thead>
                        <tr>
                            {Object.keys(careerStats[0]).map((col, index) => (
                                <th key={index} onClick={() => handleSort(col)}>
                                    {col}
                                    {sortConfig.key === col ? (sortConfig.direction === "ascending" ? " ↑" : " ↓") : ""}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {careerStats.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                                {Object.values(row).map((val, colIndex) => (
                                    <td key={colIndex}>{val}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No career stats available.</p>
            )}
        </div>
    );

    const renderWeeklyStats = () => (
        <div>
            <button onClick={handleBackClick}>Back to stats</button>
            <img 
            src={`/data/headshots/${playerName.replace(" ", "_")}_headshot.png`} 
            alt={`${playerName} Headshot`} 
            className="player-headshot" 
        />
            <h2>{playerName}'s Weekly Stats</h2>
            {weeklyStats.length > 0 ? (
                <table>
                    <thead>
                        <tr>
                            {Object.keys(weeklyStats[0]).map((col, index) => (
                                <th key={index} onClick={() => handleSort(col)}>
                                    {col}
                                    {sortConfig.key === col ? (sortConfig.direction === "ascending" ? " ↑" : " ↓") : ""}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {weeklyStats.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                                {Object.values(row).map((val, colIndex) => (
                                    <td key={colIndex}>{val}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No weekly stats available.</p>
            )}
        </div>
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
                    <button onClick={() => { setActiveTab("roster"); setSearchQuery(""); }}>NFL Roster</button>
                </nav>

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

                    {activeTab !== "schedule" && (
                        <div>
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={handleSearchChange}
                                placeholder="Search ..."
                            />
                        </div>
                    )}
                </div>
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
                {isWeeklyStats && (
                    <div>
                        {renderWeeklyStats()}
                    </div>
                )}
                {isCareerStats && (
                    <div>
                        {renderCareerStats()}
                    </div>
                )}
                {!isCareerStats && !isWeeklyStats && (
                    <div>
                        {data.length > 0 ? renderTable() : <p>Loading data...</p>}
                    </div>
                )}
            </div>
        </div>
    );
};

export default App;
