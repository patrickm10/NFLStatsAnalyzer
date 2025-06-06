import React, { useEffect, useState } from "react";
import Papa from "papaparse";

const positions = [
  {
    label: "QB",
    file: "/data/official_stats/official_qb_stats.csv",
    weeklyFolder: "/data/qb_stats/qb_weekly_stats/",
    careerFolder: "/data/qb_stats/qb_career_stats/",
    careerSuffix: "_career_passing_stats.csv", // suffix for career stats filename
  },
  {
    label: "RB",
    file: "/data/official_stats/official_rb_stats.csv",
    weeklyFolder: "/data/rb_weekly_stats/",
    careerFolder: "/data/rb_career_stats/",
    careerSuffix: "_career_stats.csv",
  },
  {
    label: "WR",
    file: "/data/official_stats/official_wr_stats.csv",
    weeklyFolder: "/data/wr_weekly_stats/",
    careerFolder: "/data/wr_career_stats/",
    careerSuffix: "_career_stats.csv",
  },
  {
    label: "TE",
    file: "/data/official_stats/official_te_stats.csv",
    weeklyFolder: "/data/te_weekly_stats/",
    careerFolder: "/data/te_career_stats/",
    careerSuffix: "_career_stats.csv",
  },
  {
    label: "K",
    file: "/data/official_stats/official_k_stats.csv",
    weeklyFolder: "/data/k_weekly_stats/",
    careerFolder: "/data/k_career_stats/",
    careerSuffix: "_career_stats.csv",
  },
  {
    label: "D/ST",
    file: "/data/official_stats/official_defense_stats.csv",
    weeklyFolder: "/data/defense_weekly_stats/",
    careerFolder: "/data/defense_career_stats/",
    careerSuffix: "_career_stats.csv",
  },
];

export default function App() {
  const [selectedPosition, setSelectedPosition] = useState(positions[0]);
  const [mainData, setMainData] = useState([]);
  const [weeklyData, setWeeklyData] = useState(null);
  const [careerData, setCareerData] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [activeTab, setActiveTab] = useState("position"); // 'position', 'weekly', 'career'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load main position stats on position change
  useEffect(() => {
    setLoading(true);
    setError(null);
    setMainData([]);
    setWeeklyData(null);
    setCareerData(null);
    setSelectedPlayer(null);
    setActiveTab("position");

    fetch(selectedPosition.file)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load position stats");
        return res.text();
      })
      .then((csvText) => {
        const parsed = Papa.parse(csvText, { header: true, skipEmptyLines: true });
        setMainData(parsed.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [selectedPosition]);

  // Load weekly stats
  function loadWeeklyStats(playerName) {
    const filename = playerName.replace(/\s+/g, "_") + "_weekly_stats.csv";
    const url = selectedPosition.weeklyFolder + filename;

    return fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error("Weekly stats not found");
        return res.text();
      })
      .then((csvText) => Papa.parse(csvText, { header: true, skipEmptyLines: true }).data);
  }

  // Load career stats
  function loadCareerStats(playerName) {
    const filename = playerName.replace(/\s+/g, "_") + selectedPosition.careerSuffix;
    const url = selectedPosition.careerFolder + filename;

    return fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error("Career stats not found");
        return res.text();
      })
      .then((csvText) => Papa.parse(csvText, { header: true, skipEmptyLines: true }).data);
  }

  // On player click, load both weekly and career stats
  async function handlePlayerClick(playerName) {
    setLoading(true);
    setError(null);
    setWeeklyData(null);
    setCareerData(null);
    setSelectedPlayer(playerName);

    try {
      const [weekly, career] = await Promise.all([
        loadWeeklyStats(playerName),
        loadCareerStats(playerName),
      ]);
      setWeeklyData(weekly);
      setCareerData(career);
      setActiveTab("weekly"); // default tab when player clicked
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }

  const mainHeaders = mainData.length > 0 ? Object.keys(mainData[0]) : [];
  const weeklyHeaders = weeklyData && weeklyData.length > 0 ? Object.keys(weeklyData[0]) : [];
  const careerHeaders = careerData && careerData.length > 0 ? Object.keys(careerData[0]) : [];

  return (
    <div style={{ maxWidth: 900, margin: "auto", fontFamily: "Arial, sans-serif" }}>
      <h1>{selectedPosition.label} Rankings</h1>

      {/* Position Selector */}
      <select
        value={selectedPosition.label}
        onChange={(e) => {
          const pos = positions.find((p) => p.label === e.target.value);
          setSelectedPosition(pos);
        }}
        style={{
          marginBottom: 20,
          padding: "10px",
          fontSize: "1em",
          borderRadius: 6,
          border: "1px solid #ccc",
          cursor: "pointer",
          width: 200,
          background: "linear-gradient(135deg, #ce3e3e, #61597b)",
          color: "white",
        }}
      >
        {positions.map((pos) => (
          <option key={pos.label} value={pos.label}>
            {pos.label}
          </option>
        ))}
      </select>

      {/* Tabs */}
      <div style={{ display: "flex", justifyContent: "center", marginBottom: 20, gap: 10 }}>
        <button
          onClick={() => setActiveTab("position")}
          style={{
            padding: "10px 20px",
            cursor: "pointer",
            backgroundColor: activeTab === "position" ? "#007bff" : "#eee",
            color: activeTab === "position" ? "white" : "black",
            border: "none",
            borderBottom: activeTab === "position" ? "3px solid #0056b3" : "3px solid transparent",
            fontWeight: "bold",
            borderRadius: "4px 4px 0 0",
          }}
        >
          Position Stats
        </button>

        {weeklyData && (
          <button
            onClick={() => setActiveTab("weekly")}
            style={{
              padding: "10px 20px",
              cursor: "pointer",
              backgroundColor: activeTab === "weekly" ? "#007bff" : "#eee",
              color: activeTab === "weekly" ? "white" : "black",
              border: "none",
              borderBottom: activeTab === "weekly" ? "3px solid #0056b3" : "3px solid transparent",
              fontWeight: "bold",
              borderRadius: "4px 4px 0 0",
            }}
          >
            Weekly Stats {selectedPlayer ? `(${selectedPlayer})` : ""}
          </button>
        )}

        {careerData && (
          <button
            onClick={() => setActiveTab("career")}
            style={{
              padding: "10px 20px",
              cursor: "pointer",
              backgroundColor: activeTab === "career" ? "#007bff" : "#eee",
              color: activeTab === "career" ? "white" : "black",
              border: "none",
              borderBottom: activeTab === "career" ? "3px solid #0056b3" : "3px solid transparent",
              fontWeight: "bold",
              borderRadius: "4px 4px 0 0",
            }}
          >
            Career Stats {selectedPlayer ? `(${selectedPlayer})` : ""}
          </button>
        )}
      </div>

      {error && <div style={{ color: "red", marginBottom: 10 }}>Error: {error}</div>}
      {loading && <div style={{ marginBottom: 10 }}>Loading {activeTab} stats...</div>}

      {/* Position Stats Table */}
      {activeTab === "position" && !loading && !error && mainData.length > 0 && (
        <table border="1" cellPadding="5" style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead>
            <tr>{mainHeaders.map((h) => (<th key={h}>{h}</th>))}</tr>
          </thead>
          <tbody>
            {mainData.map((row, i) => {
              const playerName = row["Player"] || row[mainHeaders[0]];
              return (
                <tr
                  key={i}
                  style={{ cursor: "pointer" }}
                  onClick={() => playerName && handlePlayerClick(playerName)}
                  title="Click to view weekly & career stats"
                >
                  {mainHeaders.map((h) => (<td key={h}>{row[h]}</td>))}
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {/* Weekly Stats Table */}
      {activeTab === "weekly" && !loading && !error && weeklyData && weeklyData.length > 0 && (
        <table border="1" cellPadding="5" style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead>
            <tr>{weeklyHeaders.map((h) => (<th key={h}>{h}</th>))}</tr>
          </thead>
          <tbody>
            {weeklyData.map((row, i) => (
              <tr key={i}>
                {weeklyHeaders.map((h) => (<td key={h}>{row[h]}</td>))}
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Career Stats Table */}
      {activeTab === "career" && !loading && !error && careerData && careerData.length > 0 && (
        <table border="1" cellPadding="5" style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead>
            <tr>{careerHeaders.map((h) => (<th key={h}>{h}</th>))}</tr>
          </thead>
          <tbody>
            {careerData.map((row, i) => (
              <tr key={i}>
                {careerHeaders.map((h) => (<td key={h}>{row[h]}</td>))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
