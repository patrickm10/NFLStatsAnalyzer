import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "./App.css";

const App = () => {
  const [activeTab, setActiveTab] = useState("stats");
  const [columns, setColumns] = useState([]);
  const [data, setData] = useState([]);
  const [searchQuery, setSearchQuery] = useState(""); // State to store the search query
  const [sortConfig, setSortConfig] = useState({ key: null, direction: "ascending" }); // State for sorting

  // Fetch stats for the specific tab
  const fetchStats = (fileName) => {
    console.log(`Fetching data for: ${fileName}`); // Log the file name being fetched
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
    } else if (activeTab === "roster") {
      fetchStats("nfl_roster.csv");
    }
  }, [activeTab]);

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handleSearchSubmit = () => {
    if (searchQuery) {
      const filteredData = data.filter((row) =>
        row.Player.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setData(filteredData);
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

      // Convert to numbers if possible
      const aNumeric = isNaN(aValue) ? aValue : parseFloat(aValue);
      const bNumeric = isNaN(bValue) ? bValue : parseFloat(bValue);

      if (aNumeric < bNumeric) return direction === "ascending" ? -1 : 1;
      if (aNumeric > bNumeric) return direction === "ascending" ? 1 : -1;
      return 0;
    });

    setData(sortedData);
    setSortConfig({ key: column, direction });
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
        <h1>NFL Viewer</h1>
        <nav>
          <button onClick={() => setActiveTab("stats")}>QB Stats</button>
          <button onClick={() => setActiveTab("rbStats")}>RB Stats</button>
          <button onClick={() => setActiveTab("wrStats")}>WR Stats</button>
          <button onClick={() => setActiveTab("kickerStats")}>Kicker Stats</button>
          <button onClick={() => setActiveTab("defenseStats")}>Defense Stats</button>
          <button onClick={() => setActiveTab("schedule")}>Schedule</button>
          <button onClick={() => setActiveTab("roster")}>NFL Roster</button>
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

      {/* Content for active tab */}
      <div>
        <h2>
          {activeTab === "stats" ? "Quarterback Stats" :
           activeTab === "rbStats" ? "Running Back Stats" :
           activeTab === "wrStats" ? "Wide Receiver Stats" :
           activeTab === "kickerStats" ? "Kicker Stats" :
           activeTab === "defenseStats" ? "Defense Stats" :
           activeTab === "schedule" ? "NFL Schedule" :
           activeTab === "roster" ? "NFL Roster" :
           "Schedule"}
        </h2>
        {data.length > 0 ? renderTable() : <p>Loading data...</p>}
      </div>
    </div>
  );
};

export default App;
