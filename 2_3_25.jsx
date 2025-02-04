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
    const [playerRosterData, setPlayerRosterData] = useState(null);

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
            case "teStats":
                return "official_te_stats.csv";
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

    const renderPlayerDetails = () => (
        <div className="container">
            {playerRosterData && (
                <div className="physical-details">
                    <p><strong>Height:</strong> {playerRosterData.Height}</p>
                    <p><strong>Weight:</strong> {playerRosterData.Weight}</p>
                    <p><strong>Arms:</strong> {playerRosterData.Arms}</p>
                    <p><strong>Hands:</strong> {playerRosterData.Hands}</p>
                </div>
            )}
        </div>
    );

    const renderArmDetails = () => (
        <div className="container">
            {playerRosterData && (
                <div className="arm-details">
                    <p><strong>Arms:</strong> {playerRosterData.Arms}"</p>
                    <p><strong>Hands:</strong> {playerRosterData.Hands}"</p>
                </div>
            )}
        </div>
    );

    const renderPlayerCard = () => {
        const nameParts = playerRosterData?.Name.split(" ");
        const firstName = nameParts[0];
        const lastName = nameParts.slice(1).join(" "); // For cases where there is more than one last name part
    
        return (
            <div className="player-card">
                {/* Headshot Image - Adjusted to not be centered horizontally */}
                <div 
                    className="image-container" 
                    style={{ top: `38.5%`, left: '54%' }}  // Adjust left as needed
                >
                    <img 
                        src={`/data/headshots/${playerName.replace(" ", "_").replace("'", "-")}_headshot.png`} 
                        alt="Headshot Not Found" 
                        className="player-headshot" 
                    />
                </div>
        
                {/* Player Name - First Name Above Last Name */}
                <div className="card-name">
                    <p><strong>{firstName}</strong></p> {/* First Name */}
                    <p><strong>{lastName}</strong></p>  {/* Last Name */}
                </div>
        
                {/* Player Position */}
                <div className="position">
                    <p><strong>{playerRosterData?.Position}</strong></p>
                </div>
        
                {/* Team Logo */}
                <div className="team-logo-container">
                    <img 
                        src={`/data/logos/${playerRosterData.Team.replace(/ /g, "-").toLowerCase()}.png`} 
                        alt="Team Logo Not Found" 
                        className="team-logo" 
                    />
                </div>
        
                {/* Conference Logo */}
                <div className="conference-logo-container">
                    <img 
                        src={`/data/logos/${playerRosterData.Conference}.png`} 
                        alt="Conference Logo Not Found" 
                        className="conference-logo" 
                    />
                </div>
            </div>
        );
    };
    
    


    const handlePlayerClick = (player) => {
        let playerFileName = "";
        let careerFilePath = "";
        let weeklyFilePath = "";
        
        // Clean the player's name for file path consistency
        playerFileName = `${player.Player.replace(/ /g, "_").replace("'", "-")}`;
        
        // Determine the file paths for the player's career and weekly stats based on the active tab
        if (activeTab === "stats") {
            careerFilePath = `/data/qb_stats/career_stats/${playerFileName}_career_passing_stats.csv`;
            weeklyFilePath = `/data/qb_stats/qb_weekly_stats/${playerFileName}_weekly_stats.csv`;
        } else if (activeTab === "rbStats") {
            careerFilePath = `/data/rb_stats/career_stats/${playerFileName}_career_rushing_stats.csv`;
            weeklyFilePath = `/data/rb_stats/rb_weekly_stats/${playerFileName}_weekly_stats.csv`;
        } else if (activeTab === "wrStats") {
            careerFilePath = `/data/wr_stats/career_stats/${playerFileName}_career_receiving_stats.csv`;
            weeklyFilePath = `/data/wr_stats/wr_weekly_stats/${playerFileName}_weekly_stats.csv`;
        } 
        else if (activeTab === "teStats") {
            careerFilePath = `/data/te_stats/career_stats/${playerFileName}_career_receiving_stats.csv`;
            weeklyFilePath = `/data/te_stats/te_weekly_stats/${playerFileName}_weekly_stats.csv`;
        } else if (activeTab === "kickerStats") {
            careerFilePath = `/data/kicker_stats/career_stats/${playerFileName}_career_kicking_stats.csv`;
            weeklyFilePath = `/data/kicker_stats/kicker_weekly_stats/${playerFileName}_kicking_stats.csv`;
        }
    
        // Fetch the player data from the appropriate CSV files
        console.log(`Fetching player data from: ${careerFilePath} and ${weeklyFilePath}`);
        fetchCareerStats(player.Player, careerFilePath);
        fetchWeeklyStats(player.Player, weeklyFilePath);
    
        // Set the player name and other states
        setIsCareerStats(true);
        setIsWeeklyStats(true);
        setPlayerName(player.Player);
    
        // Fetch player data from the official team roster CSV
        Papa.parse("/data/nfl_official_team_roster.csv", {
            download: true,
            header: true,
            complete: (result) => {
                const playerData = result.data.find(
                    (row) => row.Name?.toLowerCase() === player.Player?.toLowerCase()
                );
                if (playerData) {
                    // Here you can update your state with player data from the roster
                    setPlayerRosterData(playerData); // Assuming you have a state for player roster data
                }
            },
            error: (error) => {
                console.error("Error loading player roster data:", error);
            },
        });
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
            <h2 className="stats-header">{playerName}'s Career Stats</h2>
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

    const renderWeeklyStats = () => { 
       
        return(
        <div>
            <div className="back-button-container">
                <button className="back" onClick={handleBackClick}>
                    Back to stats
                </button>
            </div>
            <h2_1><strong>{playerName}</strong></h2_1>
            {renderPlayerDetails()}             
            {renderPlayerCard()}
            
            <h2 className="stats-header">{playerName}'s Weekly Stats</h2>
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
}




    return (
        <div>
            <header> 
                <h1 class ="text-outline">NFL Statistics Analyzer</h1> 
               
                <nav className="tabs-nav">
                    <button onClick={() => { setIsCareerStats(false);setIsWeeklyStats(false);setActiveTab("stats"); setSearchQuery(""); }}>Player Data</button>
                    <button onClick={() => { setIsCareerStats(false);setIsWeeklyStats(false);setActiveTab("schedule"); setSearchQuery(""); }}>Schedule</button>
                    <button onClick={() => { setIsCareerStats(false);setIsWeeklyStats(false);setActiveTab("roster"); setSearchQuery(""); }}>NFL Roster</button>
                </nav>

                
                
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
                        
                    {/* Container for search bar and dropdown */}
                    {activeTab !== "schedule" && activeTab !== "roster" && (
                        <div className="controls-container">
                            {/* Dropdown tab for selecting active tab */}
                        <select
                            value={activeTab}
                            onChange={(e) => setActiveTab(e.target.value)}
                            className="tab"
                        >
                            <option value="stats">QB Stats</option>
                            <option value="rbStats">RB Stats</option>
                            <option value="wrStats">WR Stats</option>
                            <option value="teStats">TE Stats</option>
                            <option value="kickerStats">Kicker Stats</option>
                            <option value="defenseStats">Defense Stats</option>
                        </select>
                        <h3 className="position-name-stats">
                            {activeTab === "stats" ? "Quarterback Stats" :
                                activeTab === "rbStats" ? "Running Back Stats" :
                                    activeTab === "wrStats" ? "Wide Receiver Stats" :
                                        activeTab === "teStats" ? "Tight End Stats" :
                                            activeTab === "kickerStats" ? "Kicker Stats" :
                                                activeTab === "defenseStats" ? "Defense Stats" :
                                                    activeTab === "schedule" ? "2024-2025 Schedule" :
                                                        activeTab === "roster" ? "NFL Roster" :
                                                            "Schedule"}
                        </h3>
                        {/* Search bar section */}
                        
                            <div className="search-container">
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={handleSearchChange}
                                placeholder="Search Player Name ..."
                            />
                            </div>
                        
                    
                        
                        </div>
                  )}
                    {data.length > 0 ? renderTable() : <p>Loading data...</p>}
                  </div>
                )}
                
            </div>
        </div>
    );
};

export default App;
