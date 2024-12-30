import React, { useState, useEffect, Component } from "react";
import Papa from "papaparse";
import "./App.css";

// NFL Teams and Divisions Data
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

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error caught by ErrorBoundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong. Redirecting to home page...</h1>;
    }

    return this.props.children;
  }
}

const App = () => {
  const [activeTab, setActiveTab] = useState("stats");
  const [columns, setColumns] = useState([]);
  const [data, setData] = useState([]);
  const [careerStats, setCareerStats] = useState(null);
  const [selectedDivision, setSelectedDivision] = useState("");
  const [sortConfig, setSortConfig] = useState({ key: null, direction: "ascending" });
  const [searchQuery, setSearchQuery] = useState(""); 
  const [currentPlayer, setCurrentPlayer] = useState(""); 
  const [filePath, setFilePath] = useState(""); 

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
        setData([]);  
      });
  };

  const fetchNFLRoster = () => {
    fetch("data/nfl_roster.csv")
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
        console.error("Error loading NFL roster file:", error);
        setData([]);  
      });
  }


  const fetchTeamStats = () => {
    fetch("/data/nfl_official_team_stats.csv")
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
        console.error("Error loading team stats file:", error);
        setData([]);  
      });
  };

  useEffect(() => {
    setCareerStats(null);
    setData([]);

     if (activeTab === "standings") {
      fetchTeamStats(); // Load team stats when the standings tab is active
    } else {
      const fileMap = {
        "stats": "official_qb_stats.csv",
        "defenseStats": "official_defense_stats.csv",
        "roster": "data/nfl_roster.csv",
        "rbStats": "official_rb_stats.csv",
        "wrStats": "official_wr_stats.csv",
        "kickerStats": "official_kicker_stats.csv"
      };
      fetchStats(fileMap[activeTab] || "schedule.csv");
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
    if (activeTab === "standings") {
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
    }

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
                <button onClick={() => setActiveTab("standings")}>Standings</button> {/* New standings tab */}
                <button onClick={() => setActiveTab("roster")}>NFL Roster</button> {/* New standings tab */}
            </nav>
        </header>

        <div>
            <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for a player"
            />
            <button onClick={() => searchQuery && fetchCareerStats(searchQuery.replace(/\s+/g, '_'))}>Search</button>
        </div>

        <div>
            <h2>
                {activeTab === "stats"
                    ? "Quarterback Stats"
                    : activeTab === "rbStats"
                    ? "Running Back Stats"
                    : activeTab === "wrStats"
                    ? "Wide Receiver Stats"
                    : activeTab === "kickerStats"
                    ? "Kicker Stats"
                    : activeTab === "defenseStats"
                    ? "Defense Stats"
                    : activeTab === "schedule"
                    ? "Schedule"
                    : activeTab === "standings"
                    ? "Standings"
                    : activeTab === "roster"
                    ? "NFL Roster"
                    : ""}
            </h2>
            {data.length > 0 ? renderTable() : <p>Loading data...</p>}
        </div>
    </div>
);
};

export default App;
