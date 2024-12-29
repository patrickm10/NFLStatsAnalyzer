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
  const [selectedDivision, setSelectedDivision] = useState("");

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

  return (
    <div>
      <header>
        <h1>NFL Viewer</h1>
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

      {activeTab === "stats" && (
        <div>
          <h2>Quarterback Stats</h2>
          {data.length > 0 ? (
            <table>
              <thead>
                <tr>
                  {columns.map((col, index) => (
                    <th key={index}>{col}</th>
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
          ) : (
            <p>Loading data...</p>
          )}
        </div>
      )}

      {activeTab === "rbStats" && (
        <div>
          <h2>Running Back Stats</h2>
          {data.length > 0 ? (
            <table>
              <thead>
                <tr>
                  {columns.map((col, index) => (
                    <th key={index}>{col}</th>
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
          ) : (
            <p>Loading data...</p>
          )}
        </div>
      )}

      {activeTab === "wrStats" && (
        <div>
          <h2>Wide Receiver Stats</h2>
          {data.length > 0 ? (
            <table>
              <thead>
                <tr>
                  {columns.map((col, index) => (
                    <th key={index}>{col}</th>
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
          ) : (
            <p>Loading data...</p>
          )}
        </div>
      )}

      {activeTab === "kickerStats" && (
        <div>
          <h2>Kicker Stats</h2>
          {data.length > 0 ? (
            <table>
              <thead>
                <tr>
                  {columns.map((col, index) => (
                    <th key={index}>{col}</th>
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
          ) : (
            <p>Loading data...</p>
          )}
        </div>
      )}

      {activeTab === "defenseStats" && (
        <div>
          <h2>Defense Stats</h2>
          {data.length > 0 ? (
            <table>
              <thead>
                <tr>
                  {columns.map((col, index) => (
                    <th key={index}>{col}</th>
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
          ) : (
            <p>Loading data...</p>
          )}
        </div>
      )}

      {activeTab === "schedule" && (
        <div>
          <h2>NFL Schedule</h2>
          {data.length > 0 ? (
            <table>
              <thead>
                <tr>
                  {columns.map((col, index) => (
                    <th key={index}>{col}</th>
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
          ) : (
            <p>Loading data...</p>
          )}
        </div>
      )}

      {activeTab === "teams" && (
        <div className="App">
          <header className="App-header">
            <h2>NFL Teams Viewer</h2>
            <p>Select a division to view teams:</p>
            <div className="buttons">
              {Object.keys(divisions).map((division) => (
                <button
                  key={division}
                  onClick={() => setSelectedDivision(division)}
                >
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
