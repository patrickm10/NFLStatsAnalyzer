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
    const [isSchedule, setIsSchedule] = useState(false);
    const [isCareerStats, setIsCareerStats] = useState(false);
    const [isCareerStats1, setIsCareerStats1] = useState(false);
    const [isWeeklyStats, setIsWeeklyStats] = useState(false);
    const [isGameInfo, setIsGameInfo] = useState(false);
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
    const [homeTeam, setHomeTeam] = useState(null);
    const [awayTeam, setAwayTeam] = useState(null);
    const [homeRecord, setHomeRecord] = useState(null);
    const [awayRecord, setAwayRecord] = useState(null);
    const [playerTeam, setPlayerTeam] = useState("");
    const [playerNum, setPlayerNum] = useState(0);
    const [homeScore, setHomeScore] = useState("");
    const [awayScore, setAwayScore] = useState("");
    const [playerData, setPlayerData] = useState({});
    const [playerRecord, setPlayerRecord] = useState("");
    const [opponentRecord, setOpponentRecord] = useState("");

    const handlePlayerClick = (player) => {
        let playerFileName = player.Player.replace(/ /g, "-");
        let playerFileName1 = player.Player.replace(/ /g, "_");
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
        setPlayerTeam(player.Team);
        setPlayerName(player.Player);

        // Assign stat types based on position
        if (activeTab == "stats" || player.Position === "QB") {
            statTypes = ["Passing", "Rushing"];
            position = "QB";
        } else if (activeTab == "rbStats" || player.Position === "RB") {
            statTypes = ["Rushing", "Receiving"];
            position = "RB";
        } else if (activeTab == "wrStats" || player.Position === "WR") {
            statTypes = ["Receiving", "Rushing"];
            position = "WR";
        }
        else if (player.Position === "TE" || activeTab == "teStats") {
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
            setPlayerNum(player.Number);
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
                            const playerName = columns[0].trim();
                            const playerExperience = columns[6].trim();
                            const playerNumber = columns[1].trim();

                            const normalizedPlayerName = playerName.replace(/ /g, '').toLowerCase();
                            const normalizedInputName = player.Player.replace(/ /g, '').toLowerCase();

                            console.log("CSV Player Name:", playerName, "CSV Experience:", playerExperience);
                            console.log("Normalized CSV Player Name:", normalizedPlayerName, "Normalized Input Name:", normalizedInputName);

                            if (normalizedPlayerName === normalizedInputName) {
                                setPlayerExperience(playerExperience);
                                setPlayerNum(playerNumber);  // ✅ only set when name matches
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
        else {
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
        /*console.log("selectedMatchNumber:", selectedMatchNumber);
        console.log("selectedConference:", selectedConference);
        console.log("selectedDivision:", selectedDivision);
        console.log("selectedTeam:", selectedTeam);*/

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
                    setIsSchedule(true);
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


    const applySearchFilter = (query) => {
        if (query) {
            const filteredData = data.filter((row) =>
                row.Player.toLowerCase().includes(query.toLowerCase())
            );
            setData(filteredData);
        } else {
            fetchStats(getFileNameForActiveTab());
        }
    };


    const handleSearchChange = (event) => {
        const query = event.target.value;
        setSearchQuery(query);
        applySearchFilter(query);
    };





    const fileMapping = {
        stats: "official_stats/official_qb_stats.csv",
        rbStats: "official_stats/official_rb_stats.csv",
        wrStats: "official_stats/official_wr_stats.csv",
        teStats: "official_stats/official_te_stats.csv",
        kickerStats: "official_stats/official_kicker_stats.csv",
        schedule: "schedule.csv",
        roster: "fullNFLSkillRoster.csv",
        ARIRoster: "rosters/arizona-cardinals.csv",
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
                        {/*Player Physical Details*/}
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

    const renderPlayerHeadshot = () => {


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
        setIsGameInfo(false);
        setIsSchedule(false);
        setHomeRecord("");
        setAwayRecord("");
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

    const handleGameBackClick = () => {
        setIsGameInfo(false);
        setIsWeeklyStats(true);
        setHomeRecord("");
        setAwayRecord("");
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
                {data.map((row, rowIndex) => {
                    let gradient = "none";

                    if (row.Position === "WR") {
                        gradient = "linear-gradient(to top right, rgb(182, 180, 180) 0%, rgba(12, 211, 78, 0.5) 100%)";
                    } else if (row.Position === "RB") {
                        gradient = "linear-gradient(to top right,  rgb(182, 180, 180) 0%, rgba(16, 51, 224, 0.5) 100%)";
                    } else if (row.Position === "TE") {
                        gradient = "linear-gradient(to top right,  rgb(182, 180, 180) 0%, rgba(217, 245, 9, 0.5) 100%)";
                    } else if (row.Position === "QB") {
                        gradient = "linear-gradient(to top right,  rgb(182, 180, 180) 0%, rgba(226, 9, 9, 0.5) 100%)";
                    } else if (row.Position === "K") {
                        gradient = "linear-gradient(to top right,  rgb(182, 180, 180) 0%, rgba(225, 21, 174, 0.5) 100%)";
                    } else if (row.OPP === "Panthers") {
                        gradient = "linear-gradient(to top right,  rgb(182, 180, 180) 0%, rgba(225, 21, 174, 0.5) 100%)";
                    }

                    return (
                        <tr key={rowIndex} onClick={() => handlePlayerClick(row)}>
                            {columns.map((col, colIndex) => (
                                <td key={colIndex} style={{ backgroundImage: gradient }}>
                                    {row[col]}
                                </td>
                            ))}
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );



    const renderPlayerProfile = () => {
        if (!playerName) return null;

        const formattedPlayerName = playerName.replace(/\s+/g, '_');
        const pngSrc = `/data/headshots/${formattedPlayerName}_headshot.png`;

        const formattedTeamName = weeklyPlayerTeamName.split('-').join('_');
        const teamLogoSrc = `/data/logos/${formattedTeamName}.png`;

        const formattedTeamName2 = weeklyPlayerTeamName
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');

        return (
            <div className="player-profile-container">
                <div className="headshot-wrapper">
                    <img
                        src={pngSrc}
                        alt={`${playerName}'s Headshot`}
                        className="headshot-img"
                    />
                </div>

                <div className="team-info-wrapper">
                    <img
                        src={teamLogoSrc}
                        alt={`${formattedTeamName2} Logo`}
                        className="team-logo-img"
                    />
                    <p className="team-name-text">Team: {formattedTeamName2}</p>
                    <p className="player-position-text">Position: {playerPos}</p>
                    <p className="player-position-text2">Years Player: {playerExperience}</p>
                </div>
            </div>
        );
    };



    const renderCareerStats = () => {
        if (careerStats.length === 0) return <p>No career stats available.</p>;

        const columns = Object.keys(careerStats[0]); // Ensure consistent columns

        // Remove empty rows (rows where all values are undefined, null, or empty)
        const filteredStats = careerStats.filter(row =>
            columns.some(col => row[col] !== undefined && row[col] !== null && row[col] !== "")
        );

        if (filteredStats.length === 0) return <p>No career stats available.</p>;

        // Example of position variables you could dynamically set
        return (
            <div>
                {/* Displaying the PNG with dynamic positioning */}
                <div className="weekly-tab-container">
                    <div className="back-button-container">
                        <button className="button2" onClick={handleBackClick}>
                            Back
                        </button>
                    </div>

                    <nav className="player-tabs-nav">
                        <button className="button2" onClick={() => {
                            setIsCareerStats(false);
                            setIsWeeklyStats(true);
                            setSearchQuery("");
                        }}>Weekly</button>

                        <button className="button2" onClick={() => {
                            setIsCareerStats(true);
                            setIsWeeklyStats(false);
                            setSearchQuery("");
                        }}>Career</button>
                    </nav>
                </div>
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
        if (weeklyStats.length === 0) return <p>No weekly stats available. "{newFilePath}"</p>;

        const customColumnMapping = {
            "YDS_1": ["QB", "WR", "TE"].includes(playerPos) ? "RSH_YDS" : "REC_YDS",
            "TD_1": ["QB", "WR", "TE"].includes(playerPos) ? "RSH_TD" : "REC_TD",
            "AVG_1": ["QB", "WR", "TE"].includes(playerPos) ? "RSH_AVG" : "REC_AVG",
            "LNG_1": ["QB", "WR", "TE"].includes(playerPos) ? "RSH_LNG" : "REC_LNG",
            "ATT_1": ["QB", "WR", "TE"].includes(playerPos) ? "RSH_ATT" : "REC_ATT",
            "Avg_1": "Ret_Avg"
        };

        const originalColumns = Object.keys(weeklyStats[0]);
        const renamedColumns = originalColumns.map(col => customColumnMapping[col] || col);

        const remappedStats = weeklyStats.map(row => {
            const newRow = {};
            originalColumns.forEach((col, i) => {
                const newColName = renamedColumns[i];
                newRow[newColName] = row[col];
            });
            return newRow;
        });

        const filteredStats = remappedStats.filter(row =>
            renamedColumns.some(col => row[col] !== undefined && row[col] !== null && row[col] !== "")
        );

        if (filteredStats.length === 0) return <p>No weekly stats available.</p>;

        // Assuming renamedColumns and filteredStats are defined and contain valid data
        const resultColumnIndex = renamedColumns.findIndex(col => col === "RESULT" || col === "Result");
        const regularSeasonStats = filteredStats.filter(row => row["Game Type"] === "Regular Season");

        // Calculate record (W-L-T)
        let wins = 0;
        let losses = 0;
        let ties = 0;

        // Calculate record based on RESULT column
        regularSeasonStats.forEach(game => {
            const result = game["RESULT"];
            if (typeof result === "string") {
                if (result.startsWith("W")) wins++;
                else if (result.startsWith("L")) losses++;
                else if (result.startsWith("T")) ties++;
            }
        });

        // Format the record
        const record = ties > 0 ? `${wins}-${losses}-${ties}` : `${wins}-${losses}`;

        // Update the playerRecord state with the calculated record
        if (playerRecord !== record) {
            setPlayerRecord(record);
        }

        const columnStats = {};
        renamedColumns.forEach((col) => {
            const numericValues = regularSeasonStats
                .map(row => parseFloat(row[col]))
                .filter(val => !isNaN(val));

            if (numericValues.length > 0) {
                columnStats[col] = {
                    min: Math.min(...numericValues),
                    max: Math.max(...numericValues),
                };
            }
        });

        return (
            <div>
                <div className="weekly-tab-container">
                    <div className="back-button-container">
                        <button className="button2" onClick={handleBackClick}>Back</button>
                    </div>

                    <nav className="player-tabs-nav">
                        <button className="button2" onClick={() => {
                            setIsCareerStats(false);
                            setIsWeeklyStats(true);
                            setSearchQuery("");
                        }}>Weekly</button>

                        <button className="button2" onClick={() => {
                            setIsCareerStats(true);
                            setIsWeeklyStats(false);
                            setSearchQuery("");
                        }}>Career</button>
                    </nav>

                    <div className="controls-container">
                        <select
                            onChange={(e) =>
                                fetchWeeklyStats({ playerName }, newFilePath + e.target.value + ".csv")
                            }
                            className="year-tab"
                        >
                            {Array.from({ length: playerExperience }, (_, i) => {
                                const year = 2025 - i;
                                return <option key={year} value={year}>{year}</option>;
                            })}
                        </select>
                    </div>
                </div>

                <h2 className="stats-header">{playerName}'s Weekly Stats</h2>

                {["Playoffs", "Regular Season", "Preseason"].map((gameType) => {
                    const statsForType = filteredStats.filter(row => row["Game Type"] === gameType);
                    if (statsForType.length === 0) return null;

                    const displayColumns = renamedColumns.filter(col => col !== "Game Type");

                    return (
                        <div key={gameType} style={{ marginBottom: "2rem" }}>
                            <h2 className="stats-header">{gameType}</h2>
                            <table>
                                <thead>
                                    <tr>
                                        {displayColumns.map((col, index) => (
                                            <th key={index} onClick={() => handleSort(col)}>
                                                {col}
                                                {sortConfig.key === col ? (sortConfig.direction === "ascending" ? " ↑" : " ↓") : ""}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {statsForType.map((row, rowIndex) => {
                                        const resultValue = resultColumnIndex !== -1 ? row[renamedColumns[resultColumnIndex]] : "";
                                        const firstLetter = resultValue?.[0];

                                        return (
                                            <tr key={rowIndex} onClick={() => handleGameClick(row)}>
                                                {displayColumns.map((col, colIndex) => {
                                                    let cellStyle = {};
                                                    const isRegularSeason = gameType === "Regular Season";

                                                    if (colIndex < 4) {
                                                        if (firstLetter === "W") {
                                                            cellStyle.backgroundImage = "linear-gradient(to top right, rgb(182, 180, 180) 0%, rgba(3, 185, 48, 0.5) 100%)";
                                                        } else if (firstLetter === "L") {
                                                            cellStyle.backgroundImage = "linear-gradient(to top right, rgb(182, 180, 180) 0%, rgba(255, 0, 0, 0.5) 100%)";
                                                        } else {
                                                            cellStyle.backgroundImage = "linear-gradient(to top right, rgb(182, 180, 180) 0%, rgba(91, 91, 91, 0.6) 100%)";
                                                        }
                                                    } else if (columnStats[col]) {
                                                        const value = parseFloat(row[col]);
                                                        const { min, max } = columnStats[col];

                                                        if (!isNaN(value) && max !== min) {
                                                            let normalized = (value - min) / (max - min);

                                                            if (["INT", "SCK", "SCKY", "FUM", "LOST", "BLK", "Ret"].includes(col)) {
                                                                normalized = 1 - normalized;
                                                            }

                                                            let red, green;
                                                            if (normalized < 0.5) {
                                                                red = 255;
                                                                green = Math.round(2 * normalized * 255);
                                                            } else {
                                                                red = Math.round(2 * (1 - normalized) * 255);
                                                                green = 255;
                                                            }

                                                            const finalColor = `rgba(${red}, ${green}, 0, 0.78) 100%`;
                                                            cellStyle.backgroundImage = isRegularSeason
                                                                ? `linear-gradient(to top right, rgb(182, 180, 180) 0%, ${finalColor})`
                                                                : "linear-gradient(to top right, rgb(182, 180, 180) 0%, rgba(91, 91, 91, 0.6) 100%)";
                                                        } else {
                                                            cellStyle.backgroundImage = "linear-gradient(to top right, rgb(182, 180, 180) 0%, rgba(91, 91, 91, 0.6) 100%)";
                                                        }
                                                    } else {
                                                        // Default fallback for all other cells
                                                        cellStyle.backgroundImage = "linear-gradient(to top right, rgb(182, 180, 180) 0%, rgba(91, 91, 91, 0.6) 100%)";
                                                    }

                                                    return (
                                                        <td key={colIndex} style={cellStyle}>
                                                            {row[col] !== undefined ? row[col] : ""}
                                                        </td>
                                                    );
                                                })}
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    );
                })}
            </div>
        );
    };



   const handleGameClick = (row) => {
    // Reset states
    setIsCareerStats(false);
    setIsCareerStats1(false);
    setIsWeeklyStats(false);
    setIsGameInfo(true);
    setSearchQuery("");
    setPlayerData(row);

    let opponent = row["OPP"];
    let score = row["RESULT"];
    let week = row["WK"];
    let thisStatType = playerPos === "K" ? "kicking" : "rushing";

    let gameDateStr = row["Game Date"];
    if (!gameDateStr) return;

    let [month, day, year] = gameDateStr.split("/").map(Number);
    let gameYear = (month === 1 || month === 2) ? year - 1 : year;

    let playerFileName = playerName.replace(/ /g, "_");
    let playerTeamFilePath = `data/skillPlayerCareerStats/${playerPos}/${thisStatType}/${playerFileName}_${thisStatType}.csv`;
    
    // Team abbreviation found - proceed to set team data
    const isHomeTeam = opponent.startsWith('@');
    const isWon = score.startsWith('W');
    opponent = opponent.replace('@', '');
    //fetch players correct team
    fetch(playerTeamFilePath)
        .then(response => response.text())
        .then(csvText => {
            Papa.parse(csvText, {
                header: true,
                complete: (results) => {
                    const yearTeamData = results.data;
                    const entry = yearTeamData.find(r => Number(r.YEAR) === gameYear);
                    if (entry) {
                        const team = entry.TEAM;
                        const matchedTeam = team_names.find(t => t.fullName === team);
                        if (matchedTeam) {
                            const teamAbbrev = matchedTeam.label;
                            if (isHomeTeam) {
                                setAwayTeam(teamAbbrev);
                            } else {
                                setHomeTeam(teamAbbrev);
                            }
                        } else {
                            console.warn(`No abbreviation found for fullName: ${team}`);
                        }
                    } else {
                        console.warn(`No team found for year ${gameYear}`);
                    }
                },
                error: (err) => console.error("PapaParse error:", err)
            });
        })
        .catch(error => {
            console.error("Fetch error:", error.message);
        });

    const opp = team_names.find(t => t.name === opponent);
    console.log("opp reccord: " + opp.records?.[gameYear]);
    if (isHomeTeam) {
        setHomeTeam(opponent);
        setHomeRecord(opp.records?.[gameYear]);
        setAwayRecord(playerRecord);
        if (isWon) {
            setAwayScore(score.replace('W', '').replace(/-.*$/, ''));
            setHomeScore(score.replace(/^.*-\s*/, ''));
        } else {
            setAwayScore(score.replace('L', '').replace(/-.*$/, ''));
            setHomeScore(score.replace(/^.*-\s*/, ''));
        }
    } else {
        setAwayTeam(opponent);
        setAwayRecord(opp.records?.[gameYear]);
        setHomeRecord(playerRecord);
        if (isWon) {
            setHomeScore(score.replace('W', '').replace(/ -.*$/, ''));
            setAwayScore(score.replace(/^.*-\s*/, ''));
        } else {
            setHomeScore(score.replace('L', '').replace(/-.*$/, ''));
            setAwayScore(score.replace(/^.*-\s*/, ''));
        }
    }
};

    

    const renderGameInfo = () => {
        if (!homeTeam || !awayTeam) return null;

        const gameHomeTeam = team_names.find(
            team => team.name === homeTeam || team.label === homeTeam
        );
        const gameAwayTeam = team_names.find(
            team => team.name === awayTeam || team.label === awayTeam
        );

        if (!gameHomeTeam || !gameAwayTeam) {
            return <div>Unknown team(s): {homeTeam} or {awayTeam}</div>;
        }
        return (
            <div>

                <div className="back-button-container">
                    <button
                        className="button2"
                        onClick={handleGameBackClick}
                        style={{ width: '6vw', marginLeft: '1.8vw', marginTop: '0.6vw' }} // Adjust the width as needed
                    >
                        Back
                    </button>
                    <div className="game-header">
                        <h3>{playerName} in {gameAwayTeam.fullName} vs. {gameHomeTeam.fullName} Game</h3>
                    </div>
                </div>
                <div className="teams-container">
                    <div className="team-block">
                        <img
                            src={`/data/logos/${gameAwayTeam.team}.png`}
                            alt={`${awayTeam} logo`}
                            className="team-logo"
                        />
                        <div className="team-record">({awayRecord})</div>
                        <div className="team-score">{awayScore}</div>

                    </div>

                    <div className="at-symbol">@</div>

                    <div className="team-block">
                        <img
                            src={`/data/logos/${gameHomeTeam.team}.png`}
                            alt={`${homeTeam} logo`}
                            className="team-logo"
                        />
                        <div className="team-record">({homeRecord})</div>
                        <div className="team-score">{homeScore}</div>
                    </div>
                </div><div className="headshot-container">
                    <div className="game-player-position">{playerPos} #{playerNum}</div>
                    <img
                        src={`/data/headshots/${playerName.replace(" ", "_").replace(" ", "_")}_headshot.png`}
                        alt={`No Headshot Found /data/headshots/${playerName.replace(" ", "_").replace(" ", "_")}_headshot.png`}
                        className="game-headshot"
                    />
                </div>
                <div className="game-stats">Week: {playerData.WK}</div>
                <div className="game-stats">Date: {playerData["Game Date"]}</div>
                <div className="game-stats">OPP: {playerData.OPP.replace('@','')}</div>
                <div className="game-stats">Result: {playerData.RESULT}</div>
                <div className="game-stats">Completions: {playerData.COMP}</div>
                <div className="game-stats">Attempts: {playerData.ATT}</div>
                <div className="game-stats">Yards: {playerData.YDS}</div>
                <div className="game-stats">Average: {playerRecord}</div>
                <div className="game-overview">



                </div>

            </div>
        );

    };







    const team_names = [
        {
            label: "All Teams",
            value: "roster",
            team: "fullNFLSkillRoster",
            name: "All Teams",
            fullName: "All Teams",
            stadium: null,
            elevation: null,
            logo: "nfl_logo",
            coordinates: { lat: 33.5275, lng: -112.2625 },
            outdoors: false,
            astroTurf: false,
            primary_color: "000000",
            secondary_color: "000000",
            tertiary_color: "000000",
            records: {2015: "0-0", 2016: "0-0", 2017: "0-0", 2018: "0-0", 2019: "0-0", 2020: "0-0", 2021: "0-0", 2022: "0-0", 2023: "0-0", 2024: "0-0", 2025: "0-0", }
        }, 
        {
            label: "ARI",
            value: "ARIRoster",
            team: "arizona-cardinals",
            name: "Cardinals",
            fullName: "Arizona Cardinals",
            stadium: "State Farm Stadium",
            elevation: 1070,
            logo: "arizona_cardinals",
            coordinates: { lat: 33.5275, lng: -112.2625 },
            outdoors: false,
            astroTurf: false,
            primary_color: "97233F",
            secondary_color: "000000",
            tertiary_color: "FFB612",
            records: {2015: "13-3", 2016: "7-8-1", 2017: "8-8", 2018: "3-13", 2019: "5-10-1", 2020: "8-8", 2021: "11-6", 2022: "4-13", 2023: "4-13", 2024: "8-9", 2025: "0-0", }
        },
        {
            label: "ATL",
            value: "ATLRoster",
            team: "atlanta-falcons",
            name: "Falcons",
            fullName: "Atlanta Falcons",
            stadium: "Mercedes-Benz Stadium",
            elevation: 997,
            logo: "atlanta_falcons",
            coordinates: { lat: 33.6367, lng: -84.4279 },
            outdoors: false,
            astroTurf: true,
            primary_color: "A71930",
            secondary_color: "000000",
            tertiary_color: "A5ACAF",
            records: {2015: "8-8", 2016: "11-5", 2017: "10-6", 2018: "7-9", 2019: "7-9", 2020: "4-12", 2021: "7-10", 2022: "7-10", 2023: "7-10", 2024: "8-9", 2025: "0-0", }
        },
        {
            label: "BAL",
            value: "BALRoster",
            team: "baltimore-ravens",
            name: "Ravens",
            fullName: "Baltimore Ravens",
            stadium: "M&T Bank Stadium",
            elevation: 33,
            logo: "baltimore_ravens",
            coordinates: { lat: 39.2777, lng: -76.6220 },
            outdoors: true,
            astroTurf: false,
            primary_color: "241773",
            secondary_color: "000000",
            tertiary_color: "9E7C0C",
            records: {2015: "5-11", 2016: "8-8", 2017: "9-7", 2018: "10-6", 2019: "14-2", 2020: "11-5", 2021: "8-9", 2022: "10-7", 2023: "13-4", 2024: "12-5", 2025: "0-0", }
        },
        {
            label: "BUF",
            value: "BUFRoster",
            team: "buffalo-bills",
            name: "Bills",
            fullName: "Buffalo Bills",
            stadium: "Highmark Stadium",
            elevation: 866,
            logo: "buffalo_bills",
            coordinates: { lat: 42.7734, lng: -78.7869 },
            outdoors: true,
            astroTurf: false,
            primary_color: "00338D",
            secondary_color: "C60C30",
            tertiary_color: "FFFFFF",
            records: {2015: "8-8", 2016: "7-9", 2017: "9-7", 2018: "6-10", 2019: "10-6", 2020: "13-3", 2021: "11-6", 2022: "13-3", 2023: "11-6", 2024: "13-4", 2025: "0-0", }
        },
        {
            label: "CAR",
            value: "CARRoster",
            team: "carolina-panthers",
            name: "Panthers",
            fullName: "Carolina Panthers",
            stadium: "Bank of America Stadium",
            elevation: 751,
            logo: "carolina_panthers",
            coordinates: { lat: 35.2258, lng: -80.8531 },
            outdoors: true,
            astroTurf: false,
            primary_color: "0085CA",
            secondary_color: "000000",
            tertiary_color: "FFFFFF",
            records: {2015: "15-1", 2016: "6-10", 2017: "11-5", 2018: "7-9", 2019: "5-11", 2020: "5-11", 2021: "5-12", 2022: "7-10", 2023: "2-15", 2024: "5-12", 2025: "0-0", }
        },
        {
            label: "CHI",
            value: "CHIRoster",
            team: "chicago-bears",
            name: "Bears",
            fullName: "Chicago Bears",
            stadium: "Soldier Field",
            elevation: 594,
            logo: "chicago_bears",
            coordinates: { lat: 41.8623, lng: -87.6169 },
            outdoors: true,
            astroTurf: false,
            primary_color: "0B162A",
            secondary_color: "C83803",
            tertiary_color: "FFFFFF",
            records: {2015: "6-10", 2016: "3-13", 2017: "5-11", 2018: "12-4", 2019: "8-8", 2020: "8-8", 2021: "6-11", 2022: "3-14", 2023: "7-10", 2024: "5-12", 2025: "0-0", }
        },
        {
            label: "CIN",
            value: "CINRoster",
            team: "cincinnati-bengals",
            name: "Bengals",
            fullName: "Cincinnati Bengals",
            stadium: "Paycor Stadium",
            elevation: 482,
            logo: "cincinnati_bengals",
            coordinates: { lat: 39.0958, lng: -84.5167 },
            outdoors: true,
            astroTurf: false,
            primary_color: "FB4F14",
            secondary_color: "000000",
            tertiary_color: "FFFFFF",
            records: {2015: "12-4", 2016: "6-9-1", 2017: "7-9", 2018: "6-10", 2019: "2-14", 2020: "4-11-1", 2021: "10-7", 2022: "12-4", 2023: "9-8", 2024: "9-8", 2025: "0-0", }
        },
        {
            label: "CLE",
            value: "CLERoster",
            team: "cleveland-browns",
            name: "Browns",
            fullName: "Cleveland Browns",
            stadium: "Cleveland Browns Stadium",
            elevation: 653,
            logo: "cleveland_browns",
            coordinates: { lat: 41.5064, lng: -81.6994 },
            outdoors: true,
            astroTurf: false,
            primary_color: "311D00",
            secondary_color: "FF3C00",
            tertiary_color: "FFFFFF",
            records: {2015: "3-13", 2016: "1-15", 2017: "0-16", 2018: "7-8-1", 2019: "6-10", 2020: "11-5", 2021: "8-9", 2022: "7-10", 2023: "11-6", 2024: "3-14", 2025: "0-0", }
        },
        {
            label: "DAL",
            value: "DALRoster",
            team: "dallas-cowboys",
            name: "Cowboys",
            fullName: "Dallas Cowboys",
            stadium: "AT&T Stadium",
            elevation: 640,
            logo: "dallas_cowboys",
            coordinates: { lat: 32.7477, lng: -97.0929 },
            outdoors: false,
            astroTurf: false,
            primary_color: "003594",
            secondary_color: "041E42",
            tertiary_color: "869397",
            records: {2015: "4-12", 2016: "13-3", 2017: "9-7", 2018: "10-6", 2019: "8-8", 2020: "6-10", 2021: "12-5", 2022: "12-5", 2023: "12-5", 2024: "7-10", 2025: "0-0", }
        },
        {
            label: "DEN",
            value: "DENRoster",
            team: "denver-broncos",
            name: "Broncos",
            fullName: "Denver Broncos",
            stadium: "Empower Field at Mile High",
            elevation: 5280,
            logo: "denver_broncos",
            coordinates: { lat: 39.7391, lng: -104.9903 },
            outdoors: true,
            astroTurf: false,
            primary_color: "FB4F14",
            secondary_color: "002244",
            tertiary_color: "FFFFFF",
            records: {2015: "12-4", 2016: "9-7", 2017: "5-11", 2018: "6-10", 2019: "7-9", 2020: "5-11", 2021: "7-10", 2022: "5-12", 2023: "8-9", 2024: "10-7", 2025: "0-0", }
        },
        {
            label: "DET",
            value: "DETRoster",
            team: "detroit-lions",
            name: "Lions",
            fullName: "Detroit Lions",
            stadium: "Ford Field",
            elevation: 600,
            logo: "detroit_lions",
            coordinates: { lat: 42.3402, lng: -83.0458 },
            outdoors: false,
            astroTurf: true,
            primary_color: "0076B6",
            secondary_color: "B0B7BC",
            tertiary_color: "000000",
            records: {2015: "7-9", 2016: "9-7", 2017: "9-7", 2018: "6-10", 2019: "3-12-1", 2020: "5-11", 2021: "3-13-1", 2022: "9-8", 2023: "12-5", 2024: "15-2", 2025: "0-0", }
        },
        {
            label: "GB",
            value: "GBRoster",
            team: "green-bay-packers",
            name: "Packers",
            fullName: "Green Bay Packers",
            stadium: "Lambeau Field",
            elevation: 640,
            logo: "green_bay_packers",
            coordinates: { lat: 44.5013, lng: -88.0620 },
            outdoors: true,
            astroTurf: false,
            primary_color: "203731",
            secondary_color: "FFB612",
            tertiary_color: "FFFFFF",
            records: {2015: "10-6", 2016: "10-6", 2017: "7-9", 2018: "6-9-1", 2019: "13-3", 2020: "13-3", 2021: "13-4", 2022: "8-9", 2023: "9-8", 2024: "11-6", 2025: "0-0", }
        },
        {
            label: "HOU",
            value: "HOURoster",
            team: "houston-texans",
            name: "Texans",
            fullName: "Houston Texans",
            stadium: "NRG Stadium",
            elevation: 80,
            logo: "houston_texans",
            coordinates: { lat: 29.6847, lng: -95.4115 },
            outdoors: false,
            astroTurf: false,
            primary_color: "03202F",
            secondary_color: "A71930",
            tertiary_color: "FFFFFF",
            records: {2015: "9-7", 2016: "9-7", 2017: "4-12", 2018: "11-5", 2019: "10-6", 2020: "4-12", 2021: "4-13", 2022: "3-13-1", 2023: "10-7", 2024: "10-7", 2025: "0-0", }
        },
        {
            label: "IND",
            value: "INDRoster",
            team: "indianapolis-colts",
            name: "Colts",
            fullName: "Indianapolis Colts",
            stadium: "Lucas Oil Stadium",
            elevation: 718,
            logo: "indianapolis_colts",
            coordinates: { lat: 39.7618, lng: -86.1635 },
            outdoors: false,
            astroTurf: false,
            primary_color: "002C5F",
            secondary_color: "A2AAAD",
            tertiary_color: "003087",
            records: {2015: "8-8", 2016: "8-8", 2017: "4-12", 2018: "10-6", 2019: "7-9", 2020: "11-5", 2021: "9-8", 2022: "4-12-1", 2023: "9-8", 2024: "8-9", 2025: "0-0", }
        },
        {
            label: "JAX",
            value: "JAXRoster",
            team: "jacksonville-jaguars",
            name: "Jaguars",
            fullName: "Jacksonville Jaguars",
            stadium: "EverBank Stadium",
            elevation: 16,
            logo: "jacksonville_jaguars",
            coordinates: { lat: 30.3238, lng: -81.6371 },
            outdoors: true,
            astroTurf: false,
            primary_color: "006778",
            secondary_color: "D7A22A",
            tertiary_color: "000000",
            records: {2015: "5-11", 2016: "3-13", 2017: "10-6", 2018: "5-11", 2019: "6-10", 2020: "1-15", 2021: "3-14", 2022: "9-8", 2023: "9-8", 2024: "4-13", 2025: "0-0", }
        },
        {
            label: "KC",
            value: "KCRoster",
            team: "kansas-city-chiefs",
            name: "Chiefs",
            fullName: "Kansas City Chiefs",
            stadium: "Arrowhead Stadium",
            elevation: 889,
            logo: "kansas_city_chiefs",
            coordinates: { lat: 39.0485, lng: -94.4846 },
            outdoors: true,
            astroTurf: false,
            primary_color: "E31837",
            secondary_color: "FFB81C",
            tertiary_color: "FFFFFF",
            records: {2015: "11-5", 2016: "12-4", 2017: "10-6", 2018: "12-4", 2019: "12-4", 2020: "14-2", 2021: "12-5", 2022: "14-3", 2023: "11-6", 2024: "15-2", 2025: "0-0", }
        },
        {
            label: "LV",
            value: "LVRoster",
            team: "las-vegas-raiders",
            name: "Raiders",
            fullName: "Las Vegas Raiders",
            stadium: "Allegiant Stadium",
            elevation: 2190,
            logo: "las_vegas_raiders",
            coordinates: { lat: 36.0908, lng: -115.1835 },
            outdoors: false,
            astroTurf: false,
            primary_color: "000000",
            secondary_color: "A5ACAF",
            tertiary_color: "FFFFFF",
            records: {2015: "7-9", 2016: "12-4", 2017: "6-10", 2018: "4-12", 2019: "7-9", 2020: "8-8", 2021: "10-7", 2022: "6-11", 2023: "8-9", 2024: "4-13", 2025: "0-0", }
        },
        {
            label: "LAC",
            value: "LACRoster",
            team: "los-angeles-chargers",
            name: "Chargers",
            fullName: "Los Angeles Chargers",
            stadium: "SoFi Stadium",
            elevation: 72,
            logo: "los_angeles_chargers",
            coordinates: { lat: 33.9531, lng: -118.3396 },
            outdoors: false,
            astroTurf: false,
            primary_color: "0080C6",
            secondary_color: "FFC20E",
            tertiary_color: "FFFFFF",
            records: {2015: "4-12", 2016: "5-11", 2017: "9-7", 2018: "12-4", 2019: "5-11", 2020: "7-9", 2021: "9-8", 2022: "10-7", 2023: "5-12", 2024: "11-6", 2025: "0-0", }
        },
        {
            label: "LAR",
            value: "LARRoster",
            team: "los-angeles-rams",
            name: "Rams",
            fullName: "Los Angeles Rams",
            stadium: "SoFi Stadium",
            elevation: 72,
            logo: "los_angeles_rams",
            coordinates: { lat: 33.9531, lng: -118.3396 },
            outdoors: false,
            astroTurf: false,
            primary_color: "003594",
            secondary_color: "FFA300",
            tertiary_color: "FFFFFF",
            records: {2015: "7-9", 2016: "4-12", 2017: "11-5", 2018: "13-3", 2019: "9-7", 2020: "10-6", 2021: "12-5", 2022: "5-12", 2023: "10-7", 2024: "10-7", 2025: "0-0", }
        },
        {
            label: "MIA",
            value: "MIARoster",
            team: "miami-dolphins",
            name: "Dolphins",
            fullName: "Miami Dolphins",
            stadium: "Hard Rock Stadium",
            elevation: 7,
            logo: "miami_dolphins",
            coordinates: { lat: 25.9587, lng: -80.2381 },
            outdoors: true,
            astroTurf: false,
            primary_color: "008E97",
            secondary_color: "FC4C02",
            tertiary_color: "FFFFFF",
            records: {2015: "6-10", 2016: "10-6", 2017: "6-10", 2018: "7-9", 2019: "5-11", 2020: "10-6", 2021: "9-8", 2022: "9-8", 2023: "11-6", 2024: "8-9", 2025: "0-0", }
        },
        {
            label: "MIN",
            value: "MINRoster",
            team: "minnesota-vikings",
            name: "Vikings",
            fullName: "Minnesota Vikings",
            stadium: "U.S. Bank Stadium",
            elevation: 840,
            logo: "minnesota_vikings",
            coordinates: { lat: 44.9747, lng: -93.2581 },
            outdoors: false,
            astroTurf: true,
            primary_color: "4F2683",
            secondary_color: "FFC62F",
            tertiary_color: "FFFFFF",
            records: {2015: "11-5", 2016: "8-8", 2017: "13-3", 2018: "8-7-1", 2019: "10-6", 2020: "7-9", 2021: "8-9", 2022: "13-4", 2023: "7-10", 2024: "14-3", 2025: "0-0", }
        },
        {
            label: "NE",
            value: "NERoster",
            team: "new-england-patriots",
            name: "Patriots",
            fullName: "New England Patriots",
            stadium: "Gillette Stadium",
            elevation: 289,
            logo: "new_england_patriots",
            coordinates: { lat: 42.0909, lng: -71.2643 },
            outdoors: true,
            astroTurf: false,
            primary_color: "002244",
            secondary_color: "C60C30",
            tertiary_color: "8A8D8F",
            records: {2015: "12-4", 2016: "14-2", 2017: "13-3", 2018: "11-5", 2019: "12-4", 2020: "7-9", 2021: "10-7", 2022: "8-9", 2023: "4-13", 2024: "4-13", 2025: "0-0", }
        },
        {
            label: "NO",
            value: "NORoster",
            team: "new-orleans-saints",
            name: "Saints",
            fullName: "New Orleans Saints",
            stadium: "Caesars Superdome",
            elevation: 3,
            logo: "new_orleans_saints",
            coordinates: { lat: 29.9511, lng: -90.0815 },
            outdoors: false,
            astroTurf: true,
            primary_color: "D3BC8D",
            secondary_color: "000000",
            tertiary_color: "FFFFFF",
            records: {2015: "7-9", 2016: "7-9", 2017: "11-5", 2018: "13-3", 2019: "13-3", 2020: "12-4", 2021: "9-8", 2022: "7-10", 2023: "9-8", 2024: "5-12", 2025: "0-0", }
        },
        {
            label: "NYG",
            value: "NYGRoster",
            team: "new-york-giants",
            name: "Giants",
            fullName: "New York Giants",
            stadium: "MetLife Stadium",
            elevation: 3,
            logo: "new_york_giants",
            coordinates: { lat: 40.8136, lng: -74.0746 },
            outdoors: true,
            astroTurf: false,
            primary_color: "0B2265",
            secondary_color: "A71930",
            tertiary_color: "A5ACAF",
            records: {2015: "10-6", 2016: "11-5", 2017: "13-3", 2018: "5-11", 2019: "4-12", 2020: "6-10", 2021: "4-13", 2022: "9-7-1", 2023: "6-11", 2024: "3-14", 2025: "0-0", }
        },
        {
            label: "NYJ",
            value: "NYJRoster",
            team: "new-york-jets",
            name: "Jets",
            fullName: "New York Jets",
            stadium: "MetLife Stadium",
            elevation: 3,
            logo: "new_york_jets",
            coordinates: { lat: 40.8136, lng: -74.0746 },
            outdoors: true,
            astroTurf: false,
            primary_color: "046A38",
            secondary_color: "27251F",
            tertiary_color: "FFFFFF",
            records: {2015: "10-6", 2016: "5-11", 2017: "5-11", 2018: "4-12", 2019: "7-9", 2020: "2-14", 2021: "4-13", 2022: "7-10", 2023: "7-10", 2024: "5-12", 2025: "0-0", }
        },
        {
            label: "PHI",
            value: "PHIRoster",
            team: "philadelphia-eagles",
            name: "Eagles",
            fullName: "Philadelphia Eagles",
            stadium: "Lincoln Financial Field",
            elevation: 39,
            logo: "philadelphia_eagles",
            coordinates: { lat: 39.9008, lng: -75.1678 },
            outdoors: true,
            astroTurf: false,
            primary_color: "004C54",
            secondary_color: "A5ACAF",
            tertiary_color: "AAC0C6",
            records: {2015: "7-9", 2016: "7-9", 2017: "13-3", 2018: "9-7", 2019: "9-7", 2020: "4-11-1", 2021: "9-8", 2022: "14-3", 2023: "11-6", 2024: "14-3", 2025: "0-0", }
        },
        {
            label: "PIT",
            value: "PITRoster",
            team: "pittsburgh-steelers",
            name: "Steelers",
            searchName: "steelers",
            fullName: "Pittsburgh Steelers",
            stadium: "Heinz Field",
            elevation: 733,
            logo: "pittsburgh_steelers",
            coordinates: { lat: 40.4469, lng: -80.0150 },
            outdoors: true,
            astroTurf: false,
            primary_color: "FFB612",
            secondary_color: "101820",
            tertiary_color: "A5ACAF",
            records: {2015: "10-6", 2016: "11-5", 2017: "13-3", 2018: "9-6-1", 2019: "8-8", 2020: "12-4", 2021: "9-7-1", 2022: "9-8", 2023: "10-7", 2024: "10-7", 2025: "0-0", }
        },
        {
            label: "SF",
            value: "SFRoster",
            team: "san-francisco-49ers",
            name: "49ers",
            fullName: "San Francisco 49ers",
            stadium: "Levi's Stadium",
            elevation: 29,
            logo: "san_francisco_49ers",
            coordinates: { lat: 37.4021, lng: -121.9695 },
            outdoors: true,
            astroTurf: false,
            primary_color: "AA0000",
            secondary_color: "B3995D",
            tertiary_color: "FFFFFF",
            records: {2015: "5-11", 2016: "2-14", 2017: "6-10", 2018: "4-12", 2019: "13-3", 2020: "6-10", 2021: "10-7", 2022: "13-4", 2023: "12-5", 2024: "6-11", 2025: "0-0", }
        },
        {
            label: "SEA",
            value: "SEARoster",
            team: "seattle-seahawks",
            name: "Seahawks",
            fullName: "Seattle Seahawks",
            stadium: "Lumen Field",
            elevation: 181,
            logo: "seattle_seahawks",
            coordinates: { lat: 47.5952, lng: -122.3324 },
            outdoors: true,
            astroTurf: false,
            primary_color: "002244",
            secondary_color: "69BE28",
            tertiary_color: "A5ACAF",
            records: {2015: "10-6", 2016: "10-5-1", 2017: "9-7", 2018: "10-6", 2019: "11-5", 2020: "12-4", 2021: "7-10", 2022: "9-8", 2023: "9-8", 2024: "10-7", 2025: "0-0", }
        },
        
        {
            label: "TB",
            value: "TBRoster",
            team: "tampa-bay-buccaneers",
            name: "Buccaneers",
            fullName: "Tampa Bay Buccaneers",
            stadium: "Raymond James Stadium",
            elevation: 10,
            logo: "tampa_bay_buccaneers",
            coordinates: { lat: 27.9759, lng: -82.5030 },
            outdoors: true,
            astroTurf: false,
            primary_color: "D50A0A",
            secondary_color: "FF7900",
            tertiary_color: "0A0A)8",
            records: {2015: "6-10", 2016: "9-7", 2017: "5-11", 2018: "5-11", 2019: "7-9", 2020: "11-5", 2021: "13-4", 2022: "8-9", 2023: "9-8", 2024: "10-7", 2025: "0-0", }
        },
        {
            label: "TEN",
            value: "TENRoster",
            team: "tennessee-titans",
            name: "Titans",
            fullName: "Tennessee Titans",
            stadium: "Nissan Stadium",
            elevation: 440,
            logo: "tennessee_titans",
            coordinates: { lat: 36.1660, lng: -86.7716 },
            outdoors: true,
            astroTurf: false,
            primary_color: "0C2340",
            secondary_color: "4B92DB",
            tertiary_color: "8A8D8F",
            records: {2015: "3-13", 2016: "9-7", 2017: "9-7", 2018: "9-7", 2019: "9-7", 2020: "11-5", 2021: "12-5", 2022: "7-10", 2023: "6-11", 2024: "3-14", 2025: "0-0", }
        },
        {
            label: "WAS",
            value: "WASRoster",
            team: "washington-commanders",
            name: "Commanders",
            fullName: "Washington Commanders",
            stadium: "FedExField",
            elevation: 53,
            logo: "washington_commanders",
            coordinates: { lat: 38.9070, lng: -76.8646 },
            outdoors: true,
            astroTurf: false,
            primary_color: "5A1414",
            secondary_color: "FFB612",
            tertiary_color: "773141",
            records: {2015: "9-7", 2016: "8-7-1", 2017: "7-9", 2018: "7-9", 2019: "3-13", 2020: "7-9", 2021: "7-10", 2022: "8-8-1", 2023: "4-13", 2024: "12-5", 2025: "0-0", }
        }
    ];




    const getRosterLabel = (activeTab) => {
        const team = team_names.find(team => team.value === activeTab);
        return team ? `${team.fullName}` : "All Teams Roster";
    };




    return (
        <div>
            <header>
                <h1 className="text-outline">NFL Statistics Analyzer</h1>

                <nav className="tabs-nav">
                    <button onClick={() => { setIsCareerStats(false); setIsCareerStats1(false); setIsWeeklyStats(false); setIsSchedule(false); setIsGameInfo(false); setActiveTab("stats"); setSearchQuery(""); applySearchFilter(""); }}>Player Data</button>
                    <button onClick={() => { setIsCareerStats(false); setIsCareerStats1(false); setIsWeeklyStats(false); setIsSchedule(false); setIsGameInfo(false); setActiveTab("stats"); setSearchQuery(""); applySearchFilter(""); }}>Draft Hub</button>
                    <button onClick={() => { setIsCareerStats(false); setIsCareerStats1(false); setIsWeeklyStats(false); setIsSchedule(false); setIsGameInfo(false); setActiveTab("schedule"); setSearchQuery(""); applySearchFilter(""); }}>Schedule</button>
                    <button onClick={() => { setIsCareerStats(false); setIsCareerStats1(false); setIsWeeklyStats(false); setIsSchedule(false); setIsGameInfo(false); setActiveTab("roster"); setSearchQuery(""); applySearchFilter(""); }}>NFL Roster</button>
                </nav>



            </header>

            <div>
                {isSchedule && (
                    <div>
                        <h3 className="schedule">
                            Schedule
                        </h3>
                    </div>

                )}
                {isWeeklyStats && (
                    <div>
                        {/*renderPlayerProfile()*/}
                        {renderWeeklyStats()}
                    </div>
                )}

                {isGameInfo && (
                    <div>
                        {renderGameInfo()}
                    </div>
                )}
                {isCareerStats && (
                    <div>
                        { /*renderPlayerProfile()*/}
                        {renderCareerStats()}
                    </div>
                )}
                {isCareerStats1 && !isWeeklyStats && (
                    <div>
                        {renderCareerStats1()}
                    </div>
                )}
                {!isCareerStats1 && !isCareerStats && !isWeeklyStats && !isGameInfo && (
                    <div>
                        {/* Team selection dropdown */}

                        {/* Container for search bar and dropdown */}
                        {["stats", "rbStats", "wrStats", "teStats", "kickerStats", "defenseStats", "offenseStats"].includes(activeTab) && (
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
                                    <option value="defenseStats">Team DEF Stats</option>
                                    <option value="offenseStats">Team OFF Stats</option>
                                </select>
                                <h3 className="position-name-stats">
                                    {activeTab === "stats" ? "Quarterback Stats" :
                                        activeTab === "rbStats" ? "Running Back Stats" :
                                            activeTab === "wrStats" ? "Wide Receiver Stats" :
                                                activeTab === "teStats" ? "Tight End Stats" :
                                                    activeTab === "kickerStats" ? "Kicker Stats" :
                                                        activeTab === "defenseStats" ? "Team Defensive Stats" :
                                                            activeTab === "offenseStats" ? "Team Offensive Stats" :    
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
                        {!["stats", "rbStats", "wrStats", "teStats", "kickerStats", "defenseStats", "offenseStats", "schedule"].includes(activeTab) && (
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
