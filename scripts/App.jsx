import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "./App.css";

const App = () => {
    
    const [matchNumbers, setMatchNumbers] = useState([]);
    const [conferences, setConferences] = useState([]);
    const [divisions, setDivisions] = useState([]);
    const [teams, setTeams] = useState([]);
    const [activeTab, setActiveTab] = useState("stats");
    const [columns, setColumns] = useState([]);
    const [data, setData] = useState([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [sortConfig, setSortConfig] = useState({ key: null, direction: "ascending" });
    const [isCareerStats, setIsCareerStats] = useState(false);
    const [isCareerStats1, setIsCareerStats1] = useState(false);
    const [isWeeklyStats, setIsWeeklyStats] = useState(false);
    const [playerName, setPlayerName] = useState("");
    const [playerPos, setPlayerPos] = useState("");
    const [weeklyPlayerTeamName, setWeeklyPlayerTeamName] = useState("");
    const [weeklyPlayerFileName, setWeeklyPlayerFileName] = useState("");
    const [statType, setStatType] = useState("");
    const [statType1, setStatType1] = useState("");
    const [playerExperience, setPlayerExperience] = useState(0);
    const [careerStats, setCareerStats] = useState([]);
    const [careerStats1, setCareerStats1] = useState([]);
    const [weeklyStats, setWeeklyStats] = useState([]);
    const [selectedMatchNumber, setSelectedMatchNumber] = useState("");
    const [selectedConference, setSelectedConference] = useState("");
    const [selectedDivision, setSelectedDivision] = useState("");
    const [selectedTeam, setSelectedTeam] = useState("");
    const [playerRosterData, setPlayerRosterData] = useState(null);
    
    const handlePlayerClick = (player) => {
        let playerFileName = player.Player.replace(/ /g, "-").replace("'", "-");
        let playerFileName1 = player.Player.replace(/ /g, "_").replace("'", "-");
        let playerTeamName = "";
        let careerFilePath = "";
        let careerFilePath1 = "";
        let weeklyFilePath = "";
        let statTypes = [];
        let position = "";
    
        // Find the team name for consistency
        const teamEntry = team_names.find(team => team.value.startsWith(player.Team));
        if (teamEntry) {
            playerTeamName = teamEntry.team;
        }
    
        setIsWeeklyStats(true);
        setPlayerName(player.Player);
    
        // Assign stat types based on position
        if (activeTab == "stats" || player.Position === "QB") {
            statTypes = ["Passing", "Rushing"];
            position = "QB";
        } else if (activeTab == "rbStats" || player.Position === "RB") {
            statTypes = ["Rushing", "Receiving"];
            position = "RB";
        } else if (activeTab == "wrStats" ||  player.Position === "WR") {
            statTypes = ["Receiving", "Rushing"];
            position = "WR";
        } 
        else if (player.Position === "TE" || activeTab == "teStats"){
            statTypes = ["Receiving", "Rushing"];
            position = "TE";
        }
        else if (activeTab == "kickerStats" || player.Position === "K") {
            statTypes = ["Kicking"];
            position = "K";
        }
        setPlayerPos(position);
    
        // Define Stat Types
        setStatType(statTypes[0]);
        setStatType1(statTypes[1] || "");
    
        // Check if Experience is available; if not, fetch from CSV
        if (player.Experience) {
            setPlayerExperience(player.Experience);
        } else {
            // Look up player experience from fullNFLSkillRoster.csv
            fetch('/data/fullNFLSkillRoster.csv')
                .then(response => response.text())
                .then(csvData => {
                    // Parse CSV data
                    const rows = csvData.split('\n');
                    let experienceFound = false;
    
                    console.log("CSV rows:", rows); // Log CSV content for debugging
    
                    // Loop through the rows to find the player
                    rows.forEach(row => {
                        const columns = row.split(',');
    
                        if (columns.length > 1) {
                            const playerName = columns[0].trim(); // Get the player name from the first column
                            const playerExperience = columns[6].trim(); // Get the experience from the 7th column (index 6)
    
                            // Normalize player names by removing spaces and converting to lowercase for comparison
                            const normalizedPlayerName = playerName.replace(/ /g, '').toLowerCase();
                            const normalizedInputName = player.Player.replace(/ /g, '').toLowerCase();
    
                            console.log("CSV Player Name:", playerName, "CSV Experience:", playerExperience);
                            console.log("Normalized CSV Player Name:", normalizedPlayerName, "Normalized Input Name:", normalizedInputName);
    
                            // Compare the normalized names
                            if (normalizedPlayerName === normalizedInputName) {
                                setPlayerExperience(playerExperience);
                                experienceFound = true;
                            }
                        }
                    });
    
                    // If player not found in CSV, log an error
                    if (!experienceFound) {
                        console.error("Player experience not found in CSV for:", player.Player);
                        setPlayerExperience("Unknown"); // Set to a default value or handle as needed
                    }
                })
                .catch(error => {
                    console.error("Error fetching experience data:", error);
                    setPlayerExperience("Unknown"); // Set to a default value or handle as needed
                });
        }
    
        // Define the weekly stats file path
        weeklyFilePath = `/data/skillPlayersStats/${playerTeamName}/${playerFileName}-2024.csv`;
    
        // Determine the file paths for the player's career stats
        if (statTypes.length === 2) {
            careerFilePath = `/data/skillPlayerCareerStats/${position}/${statTypes[0].toLowerCase()}/${playerFileName1}_${statTypes[0].toLowerCase()}.csv`;
            if (position != "K") {
                careerFilePath1 = `/data/skillPlayerCareerStats/${position}/${statTypes[1].toLowerCase()}/${playerFileName1}_${statTypes[1].toLowerCase()}.csv`;
            }
        } else {
            careerFilePath = `/data/skillPlayerCareerStats/${position}/${statTypes[0].toLowerCase()}/${playerFileName1}_${statTypes[0].toLowerCase()}.csv`;
        }
    
        // Fetch the player data
        console.log(`Fetching player data from: ${careerFilePath} and ${weeklyFilePath}`);
        fetchCareerStats(player.Player, careerFilePath);
        if (position != "K") {
            setIsCareerStats1(true);
            fetchCareerStats1(player.Player, careerFilePath1);
        }
        else{
            setIsCareerStats1(false);
        }
        setWeeklyPlayerFileName(playerFileName);
        setWeeklyPlayerTeamName(playerTeamName);
    
        fetchWeeklyStats(player.Player, weeklyFilePath);
    
        // Scroll to the top of the page
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    
    
    

    const fetchStats = (fileName) => {
        console.log(`Fetching data for: ${fileName}`);
        console.log("selectedMatchNumber:", selectedMatchNumber);
        console.log("selectedConference:", selectedConference);
        console.log("selectedDivision:", selectedDivision);
        console.log("selectedTeam:", selectedTeam);
    
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
        
                // Filter and set data for different file names
                if (fileName === "schedule.csv") {
                    const uniqueMatchNumbers = [...new Set(fetchedData.map(row => row["Match Number"]))];
                    setMatchNumbers(uniqueMatchNumbers);
                }
        
                if (fileName === "fullNFLSkillRoster.csv") {
                    const uniqueConferences = [...new Set(fetchedData.map(row => row.Conference))];
                    setConferences(uniqueConferences);
        
                    const uniqueDivisions = [...new Set(fetchedData.map(row => row.Division))];
                    setDivisions(uniqueDivisions);
        
                    const uniqueTeams = [...new Set(fetchedData.map(row => row.Team))];
                    setTeams(uniqueTeams);
                }
        
                // Apply filtering based on selected values
                if (selectedMatchNumber && fileName === "schedule.csv") {
                    console.log(`Filtering schedule by Match Number: ${selectedMatchNumber}`);
                    fetchedData = fetchedData.filter(row => row["Match Number"] === selectedMatchNumber);
                }
        
                if (selectedConference && fileName === "fullNFLSkillRoster.csv") {
                    console.log(`Filtering roster by Conference: ${selectedConference}`);
                    fetchedData = fetchedData.filter(row => row.Conference === selectedConference);
                }
        
                if (selectedDivision && fileName === "fullNFLSkillRoster.csv") {
                    console.log(`Filtering roster by Division: ${selectedDivision}`);
                    fetchedData = fetchedData.filter(row => row.Division === selectedDivision);
                }
        
                if (selectedTeam && fileName === "fullNFLSkillRoster.csv") {
                    console.log(`Filtering roster by Team: ${selectedTeam}`);
                    fetchedData = fetchedData.filter(row => row.Team === selectedTeam);
                }
        
                // Filter out empty rows (rows where all values are null, undefined, or "")
                const columns = parsedData.meta.fields || [];
                fetchedData = fetchedData.filter(row =>
                    columns.some(col => row[col] !== undefined && row[col] !== null && row[col] !== "")
                );
        
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

    const fetchCareerStats1 = (playerName, filePath) => {
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
                setCareerStats1(parsedData.data || []);
            })
            .catch((error) => {
                console.error("Error loading career stats CSV file:", error);
            });
    };


    const fetchWeeklyStats = (player, filePath) => {
        console.log(`Fetching weekly stats for: ${player}`);
        
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

    
    

    const fileMapping = {
        stats: "official_stats/official_qb_stats.csv",
        rbStats: "official_stats/official_rb_stats.csv",
        wrStats: "official_stats/official_wr_stats.csv",
        teStats: "official_stats/official_te_stats.csv",
        kickerStats: "official_stats/official_kicker_stats.csv",
        defenseStats: "official_stats/official_defense_stats.csv",
        schedule: "schedule.csv",
        roster: "fullNFLSkillRoster.csv",
        AZRoster: "rosters/arizona-cardinals.csv",
        ATLRoster: "rosters/atlanta-falcons.csv",
        BALRoster: "rosters/baltimore-ravens.csv",
        BUFRoster: "rosters/buffalo-bills.csv",
        CARRoster: "rosters/carolina-panthers.csv",
        CHIRoster: "rosters/chicago-bears.csv",
        CINRoster: "rosters/cincinnati-bengals.csv",
        CLERoster: "rosters/cleveland-browns.csv",
        DALRoster: "rosters/dallas-cowboys.csv",
        DENRoster: "rosters/denver-broncos.csv",
        DETRoster: "rosters/detroit-lions.csv",
        GBRoster: "rosters/green-bay-packers.csv",
        HOURoster: "rosters/houston-texans.csv",
        INDRoster: "rosters/indianapolis-colts.csv",
        JAXRoster: "rosters/jacksonville-jaguars.csv",
        KCRoster: "rosters/kansas-city-chiefs.csv",
        LVRoster: "rosters/las-vegas-raiders.csv",
        LACRoster: "rosters/los-angeles-chargers.csv",
        LARRoster: "rosters/los-angeles-rams.csv",
        MIARoster: "rosters/miami-dolphins.csv",
        MINRoster: "rosters/minnesota-vikings.csv",
        NERoster: "rosters/new-england-patriots.csv",
        NORoster: "rosters/new-orleans-saints.csv",
        NYGRoster: "rosters/new-york-giants.csv",
        NYJRoster: "rosters/new-york-jets.csv",
        PHIRoster: "rosters/philadelphia-eagles.csv",
        PITRoster: "rosters/pittsburgh-steelers.csv",
        SFRoster: "rosters/san-francisco-49ers.csv",
        SEARoster: "rosters/seattle-seahawks.csv",
        TBRoster: "rosters/tampa-bay-buccaneers.csv",
        TENRoster: "rosters/tennessee-titans.csv",
        WASRoster: "rosters/washington-commanders.csv",
        
    };
    
    const getFileNameForActiveTab = () => {
        return fileMapping[activeTab] || "nothing found"; // Returns empty string if activeTab is not found
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
       
    
        const nameParts = playerName?.split(" ") || ["Unknown"];
        const firstName = nameParts[0];
        const lastName = nameParts.slice(1).join(" ") || "";
    
        const playerName = playerRosterData.Name || "default_name"; // Ensure playerName exists
        return (
        <div className="player-card-container">
            {/* Gold Card Background */}
            <img 
                src="/data/images/gold_card.png" 
                alt="Gold Card" 
                className="gold-card-bg" 
            />

            <div className="player-card">
                {/* Headshot Image */}
                <div 
                    className="image-container" 
                    style={{ top: `38.5%`, left: '54%' }}  
                >
                    <img 
                        src={`/data/headshots/${playerName.replace(" ", "_").replace("'", "-")}_headshot.png`} 
                        alt="Headshot Not Found" 
                        className="player-headshot" 
                    />
                </div>

                {/* Player Name */}
                <div className="card-name">
                    <p><strong>{firstName}</strong></p> 
                    <p><strong>{lastName}</strong></p>  
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
                <div className="container">
                    {/*Player Physical Details*/ }
                    {playerRosterData && (
                        <div className="player-details">
                            <p><strong>Height:</strong> {playerRosterData.Height}</p>
                            <p><strong>Weight:</strong> {playerRosterData.Weight}</p>
                            <p><strong>Arms:</strong> {playerRosterData.Arms}</p>
                            <p><strong>Hands:</strong> {playerRosterData.Hands}</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
        );
    };

    const renderPlayerHeadshot= () => {
       
    
        const nameParts = playerName?.split(" ") || ["Unknown"];
    
        return (
        <div className="player-card-container">
            

            <div className="player-card">
                {/* Headshot Image */}
                <div 
                    className="image-container" 
                    style={{ top: `38.5%`, left: '54%' }}  
                >
                    <img 
                        src={`/data/headshots/${playerName.replace(" ", "_").replace("'", "-")}_headshot.png`} 
                        alt="Headshot Not Found" 
                        className="player-headshot" 
                    />
                </div>

                
            </div>
        </div>
        );
    };


   
    
    

    const handleBackClick = () => {
        setIsCareerStats(false);
        setIsCareerStats1(false);
        setIsWeeklyStats(false);
        setPlayerName("");
        setStatType("");
        setStatType1("");
        setPlayerPos("");
        setPlayerExperience(0);
        setWeeklyPlayerFileName("");
        setWeeklyPlayerTeamName("");
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

    const renderCareerStats = () => {
        if (careerStats.length === 0) return <p>No career stats available.</p>;
        
        const columns = Object.keys(careerStats[0]); // Ensure consistent columns
    
        // Remove empty rows (rows where all values are undefined, null, or empty)
        const filteredStats = careerStats.filter(row =>
            columns.some(col => row[col] !== undefined && row[col] !== null && row[col] !== "")
        );
        
        if (filteredStats.length === 0) return <p>No career stats available.</p>;
        const formattedPlayerName = playerName.replace(/\s+/g, '_'); // Replaces spaces with underscores
        const pngSrc = `/data/headshots/${formattedPlayerName}_headshot.png`; // Adjust path as needed
    
        // Example of position variables you could dynamically set
        return (
            <div>
                {/* Displaying the PNG with dynamic positioning */}
                <div className="headshot-container">
                    <img
                        src={pngSrc}
                        alt={`${playerName}'s Headshot`}
                        className="team-logo headshot_position"
                    />
                </div>
                <div className="back-button-container">
                    <button2 className="back" onClick={handleBackClick}>
                        Back
                    </button2>
                </div>          
                
                <nav className="player-tabs-nav">
                    <button2 onClick={() => { 
                        setIsCareerStats(false);
                        setIsCareerStats1(false);
                        setIsWeeklyStats(true);
                        setSearchQuery(""); }}>Weekly</button2>
                    <button2 onClick={() => { 
                        setIsCareerStats(true);
                        setIsWeeklyStats(false);
                        setSearchQuery(""); }}>Career</button2>
                </nav>
                <h2 className="stats-header">{playerName}'s Career {statType} Stats</h2>
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
                        {filteredStats.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                                {columns.map((col, colIndex) => (
                                    <td key={colIndex}>{row[col] !== undefined ? row[col] : ""}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    const renderCareerStats1 = () => {
        if (careerStats1.length === 0) return <p>No career stats available.</p>;
    
        const columns = Object.keys(careerStats1[0]); // Ensure consistent columns
    
        // Remove empty rows (rows where all values are undefined, null, or empty)
        const filteredStats = careerStats1.filter(row =>
            columns.some(col => row[col] !== undefined && row[col] !== null && row[col] !== "")
        );
    
        if (filteredStats.length === 0) return <p>No career stats available.</p>;
    
        return (
            <div>
                <h2 className="stats-header">{playerName}'s Career {statType1} Stats</h2>
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
                        {filteredStats.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                                {columns.map((col, colIndex) => (
                                    <td key={colIndex}>{row[col] !== undefined ? row[col] : ""}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };
    
    
    const renderWeeklyStats = () => {
        let newFilePath = `/data/skillPlayersStats/${weeklyPlayerTeamName}/${weeklyPlayerFileName}-`;
        if (weeklyStats.length === 0) return <p>No weekly stats available.</p>;
    
        const columns = Object.keys(weeklyStats[0]); // Ensure consistent columns
    
        // Remove empty rows (rows where all values are undefined, null, or empty)
        const filteredStats = weeklyStats.filter(row =>
            columns.some(col => row[col] !== undefined && row[col] !== null && row[col] !== "")
        );
    
        if (filteredStats.length === 0) return <p>No weekly stats available.</p>;
    
        // Format playerName for the PNG file path (replace spaces with underscores)
        const formattedPlayerName = playerName.replace(/\s+/g, '_'); // Replaces spaces with underscores
        const pngSrc = `/data/headshots/${formattedPlayerName}_headshot.png`; // Adjust path as needed
    
        
    
        return (
            <div>
                {/* Displaying the PNG with dynamic positioning */}
                <div className="headshot-container">
                <img
                    src={pngSrc}
                    alt={`${playerName}'s Headshot`}
                    className="team-logo headshot_position"
                />
                </div>
    
                <div className="back-button-container">
                    <button2 className="back" onClick={handleBackClick}>
                        Back
                    </button2>
                </div>         
                <nav className="player-tabs-nav">
                    <button2 onClick={() => { setIsCareerStats(false); setIsCareerStats1(false); setIsWeeklyStats(true); setSearchQuery(""); }}>Weekly</button2>
                    <button2 onClick={() => { setIsCareerStats(true); setIsCareerStats1(true); setIsWeeklyStats(false); setSearchQuery(""); }}>Career</button2>
                </nav>
                <div className="controls-container">
                    <select
                        onChange={(e) =>
                            fetchWeeklyStats({ playerName }, newFilePath + e.target.value + ".csv")
                        }
                        className="year-tab"
                    >
                        {Array.from({ length: playerExperience }, (_, i) => {
                            const year = 2024 - i;
                            return (
                                <option key={year} value={year}>
                                    {year}
                                </option>
                            );
                        })}
                    </select>
                </div>
                    
                <h2 className="stats-header">{playerName}'s Weekly Stats</h2>
                
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
                        {filteredStats.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                                {columns.map((col, colIndex) => (
                                    <td key={colIndex}>{row[col] !== undefined ? row[col] : ""}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };
    
    
    
    const team_names = [
        { label: "All Teams", value: "roster", team: "fullNFLSkillRoster" },
        { label: "AZ", value: "AZRoster", team: "arizona-cardinals" },
        { label: "ATL", value: "ATLRoster", team: "atlanta-falcons" },
        { label: "BAL", value: "BALRoster", team: "baltimore-ravens" },
        { label: "BUF", value: "BUFRoster", team: "buffalo-bills" },
        { label: "CAR", value: "CARRoster", team: "carolina-panthers" },
        { label: "CHI", value: "CHIRoster", team: "chicago-bears" },
        { label: "CIN", value: "CINRoster", team: "cincinnati-bengals" },
        { label: "CLE", value: "CLERoster", team: "cleveland-browns" },
        { label: "DAL", value: "DALRoster", team: "dallas-cowboys" },
        { label: "DEN", value: "DENRoster", team: "denver-broncos" },
        { label: "DET", value: "DETRoster", team: "detroit-lions" },
        { label: "GB", value: "GBRoster", team: "green-bay-packers" },
        { label: "HOU", value: "HOURoster", team: "houston-texans" },
        { label: "IND", value: "INDRoster", team: "indianapolis-colts" },
        { label: "JAX", value: "JAXRoster", team: "jacksonville-jaguars" },
        { label: "KC", value: "KCRoster", team: "kansas-city-chiefs" },
        { label: "LV", value: "LVRoster", team: "las-vegas-raiders" },
        { label: "LAC", value: "LACRoster", team: "los-angeles-chargers" },
        { label: "LAR", value: "LARRoster", team: "los-angeles-rams" },
        { label: "MIA", value: "MIARoster", team: "miami-dolphins" },
        { label: "MIN", value: "MINRoster", team: "minnesota-vikings" },
        { label: "NE", value: "NERoster", team: "new-england-patriots" },
        { label: "NO", value: "NORoster", team: "new-orleans-saints" },
        { label: "NYG", value: "NYGRoster", team: "new-york-giants" },
        { label: "NYJ", value: "NYJRoster", team: "new-york-jets" },
        { label: "PHI", value: "PHIRoster", team: "philadelphia-eagles" },
        { label: "PIT", value: "PITRoster", team: "pittsburgh-steelers" },
        { label: "SF", value: "SFRoster", team: "san-francisco-49ers" },
        { label: "SEA", value: "SEARoster", team: "seattle-seahawks" },
        { label: "TB", value: "TBRoster", team: "tampa-bay-buccaneers" },
        { label: "TEN", value: "TENRoster", team: "tennessee-titans" },
        { label: "WAS", value: "WASRoster", team: "washington-commanders" }
    ];
    
    const getRosterLabel = (activeTab) => {
        const team = team_names.find(team => team.value === activeTab);
        return team ? `${team.label} Roster` : "All Teams Roster";
    };

    return (
        <div>
            <header> 
                <h1 class ="text-outline">NFL Statistics Analyzer</h1> 
               
                <nav className="tabs-nav">
                    <button onClick={() => { setIsCareerStats(false);setIsCareerStats1(false);setIsWeeklyStats(false);setActiveTab("stats"); setSearchQuery(""); }}>Player Data</button>
                    <button onClick={() => { setIsCareerStats(false);setIsCareerStats1(false);setIsWeeklyStats(false);setActiveTab("stats"); setSearchQuery(""); }}>Draft Hub</button>
                    <button onClick={() => { setIsCareerStats(false);setIsCareerStats1(false);setIsWeeklyStats(false);setActiveTab("schedule"); setSearchQuery(""); }}>Schedule</button>
                    <button onClick={() => { setIsCareerStats(false);setIsCareerStats1(false);setIsWeeklyStats(false);setActiveTab("roster"); setSearchQuery(""); }}>NFL Roster</button>
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
                {isCareerStats1 && !isWeeklyStats && (
                    <div>
                        {renderCareerStats1()}
                    </div>
                )}
                {!isCareerStats1 && !isCareerStats && !isWeeklyStats && (
                    <div>
                        
                    {/* Container for search bar and dropdown */}
                    {["stats", "rbStats", "wrStats", "teStats", "kickerStats", "defenseStats"].includes(activeTab) && (
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
                    {/* Team selection dropdown */}
                    {!["stats", "rbStats", "wrStats", "teStats", "kickerStats", "defenseStats", "schedule"].includes(activeTab) && (
                        <div className="controls-container">
                            <select
                                value={activeTab}
                                onChange={(e) => setActiveTab(e.target.value)}
                                className="tab"
                            >
                                {team_names.map((team) => (
                                    <option key={team.value} value={team.value}>
                                        {team.label}
                                    </option>
                                ))}
                            </select>

                            <h3 className="position-name-stats">{getRosterLabel(activeTab)}</h3>
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
