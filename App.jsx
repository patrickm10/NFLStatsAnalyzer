import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "./App.css";

const NFL_Teams = [
  "New England Patriots", "Buffalo Bills", "Miami Dolphins", "New York Jets",
  "Pittsburgh Steelers", "Baltimore Ravens", "Cincinnati Bengals", "Cleveland Browns",
  "Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars", "Tennessee Titans",
  "Kansas City Chiefs", "Los Angeles Chargers", "Denver Broncos", "Las Vegas Raiders",
  "Philadelphia Eagles", "Washington Commanders", "Dallas Cowboys", "New York Giants",
  "Detroit Lions", "Minnesota Vikings", "Green Bay Packers", "Chicago Bears",
  "Tampa Bay Buccaneers", "Atlanta Falcons", "New Orleans Saints", "Carolina Panthers",
  "Los Angeles Rams", "Seattle Seahawks", "Arizona Cardinals", "San Francisco 49ers"
];

const App = () => {
  const [activeTab, setActiveTab] = useState("stats");
  const [columns, setColumns] = useState([]);
  const [data, setData] = useState([]);
  const [careerStats, setCareerStats] = useState(null);
  const [selectedDivision, setSelectedDivision] = useState("");
  const [sortConfig, setSortConfig] = useState({ key: null, direction: "ascending" });
  const [searchQuery, setSearchQuery] = useState(""); // State to store the search query
  const [currentPlayer, setCurrentPlayer] = useState(""); // Track current player for career stats

  const divisions = {
    "AFC East": NFL_Teams.slice(0, 4),
    "AFC North": NFL_Teams.slice(4, 8),
    "AFC South": NFL_Teams.slice(8, 12),
    "AFC West": NFL_Teams.slice(12, 16),
    "NFC East": NFL_Teams.slice(16, 20),
    "NFC North": NFL_Teams.slice(20, 24),
    "NFC South": NFL_Teams.slice(24, 28),
    "NFC West": NFL_Teams.slice(28, 32),
  };

  const fetchStats = (fileName) => {
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
        setData(parsedData.data || []);
      })
      .catch((error) => {
        console.error("Error loading CSV file:", error);
      });
  };

  const fetchCareerStats = (playerName) => {
    const formattedName = playerName.replace(/\s+/g, '_');
    const filePath = `/wr_stats/career_stats/${formattedName}_career_receiving_stats.csv`;
    console.log(filePath);

    setCurrentPlayer(playerName); // Update the current player name

    fetch(filePath)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
      })
      .then((csvText) => {
        const parsedData = Papa.parse(csvText, { header: true });
        if (parsedData.data && parsedData.data.length > 0) {
          setCareerStats(parsedData.data || []);
        } else {
          console.log("Fail: No data fetched for player:", playerName);
          setCareerStats([]); // Set empty array if no career stats found
        }
      })
      .catch((error) => {
        console.error("Error loading career stats file:", error);
      });
  };

  useEffect(() => {
    if (activeTab === "stats") {
      fetchStats("official_qb_stats.csv");
    } else if (activeTab === "rbStats") {
      fetchStats("official_rb_stats.csv");
    } else if (activeTab === "wrStats") {
      fetchStats("official_wr_stats.csv");
    } else if (activeTab === "kickerStats") {
      fetchStats("official_kicker_stats.csv");
    } else if (activeTab === "defenseStats") {
      fetchStats("official_defense_stats.csv");
    } else if (activeTab === "schedule") {
      fetchStats("schedule.csv");
    }
  }, [activeTab]);

  const handleSort = (column) => {
    let direction = "ascending";
    if (sortConfig.key === column && sortConfig.direction === "ascending") {
      direction = "descending";
    }

    const sortedData = [...data].sort((a, b) => {
      const aValue = isNaN(a[column]) ? a[column] : parseFloat(a[column]);
      const bValue = isNaN(b[column]) ? b[column] : parseFloat(b[column]);

      if (aValue < bValue) return direction === "ascending" ? -1 : 1;
      if (aValue > bValue) return direction === "ascending" ? 1 : -1;
      return 0;
    });

    setData(sortedData);
    setSortConfig({ key: column, direction });
  };

  const renderTable = () => {
    // Filter data based on searchQuery (searching for player name)
    const filteredData = data.filter((row) =>
      row.Player.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
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
          {filteredData.map((row, rowIndex) => {
            const playerName = row.Player;
            return (
              <tr key={rowIndex} onClick={() => fetchCareerStats(playerName)}>
                {columns.map((col, colIndex) => (
                  <td key={colIndex}>{row[col]}</td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    );
  };

  const renderCareerStats = () => (
    <div>
      <h3>Career Stats</h3>
      {careerStats && careerStats.length > 0 ? (
        <table>
          <thead>
            <tr>
              {Object.keys(careerStats[0]).map((key, index) => (
                <th key={index}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {careerStats.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {Object.keys(row).map((key, colIndex) => (
                  <td key={colIndex}>{row[key]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No career stats available for {currentPlayer} or loading...</p> 
      )}
    </div>
  );

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handleSearchSubmit = () => {
    if (searchQuery) {
      const formattedSearchQuery = searchQuery.replace(/\s+/g, '_');
      fetchCareerStats(formattedSearchQuery);
    }
  };

  return (
    <div>
      <header>
        <h1>NFL Analyzer</h1>
        <nav>
          <button onClick={() => setActiveTab("stats")}>QB Stats</button>
          <button onClick={() => setActiveTab("rbStats")}>RB Stats</button>
          <button onClick={() => setActiveTab("wrStats")}>WR Stats</button>
          <button onClick={() => setActiveTab("kickerStats")}>Kicker Stats</button>
          <button onClick={() => setActiveTab("defenseStats")}>Defense Stats</button>
          <button onClick={() => setActiveTab("schedule")}>Schedule</button>
          <button onClick={() => setActiveTab("teams")}>Teams</button>
        </nav>
      </header>

      {/* Search Bar for player */}
      <div>
        <input
          type="text"
          value={searchQuery}
          onChange={handleSearchChange}
          placeholder="Search for a player"
        />
        <button onClick={handleSearchSubmit}>Search</button>
      </div>

      {activeTab !== "teams" && (
        <div>
          <h2>{activeTab === "stats" ? "Quarterback Stats" : activeTab === "rbStats" ? "Running Back Stats" : activeTab === "wrStats" ? "Wide Receiver Stats" : "Kicker Stats"}</h2>
          {data.length > 0 ? renderTable() : <p>Loading data...</p>}
          {renderCareerStats()}
        </div>
      )}

      {activeTab === "teams" && (
        <div className="App">
          <header className="App-header">
            <h2>NFL Teams Viewer</h2>
            <p>Select a division to view teams:</p>
            <div className="buttons">
              {Object.keys(divisions).map((division) => (
                <button key={division} onClick={() => setSelectedDivision(division)}>
                  {division}
                </button>
              ))}
            </div>
            {selectedDivision && (
              <div className="team-list">
                <h3>{selectedDivision}</h3>
                <ul>
                  {divisions[selectedDivision].map((team) => (
                    <li key={team}>{team}</li>
                  ))}
                </ul>
              </div>
            )}
          </header>
        </div>
      )}
    </div>
  );
};

export default App;
