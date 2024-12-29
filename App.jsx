import React, { useState } from 'react';
import './App.css';

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

function App() {
  const [selectedDivision, setSelectedDivision] = useState('');

  const divisions = {
    'AFC East': NFL_Teams.slice(0, 4),
    'AFC North': NFL_Teams.slice(4, 8),
    'AFC South': NFL_Teams.slice(8, 12),
    'AFC West': NFL_Teams.slice(12, 16),
    'NFC East': NFL_Teams.slice(16, 20),
    'NFC North': NFL_Teams.slice(20, 24),
    'NFC South': NFL_Teams.slice(24, 28),
    'NFC West': NFL_Teams.slice(28, 32),
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>NFL Teams Viewer</h1>
        <p>Select a division to view teams:</p>
        <div className="buttons">
          {Object.keys(divisions).map(division => (
            <button key={division} onClick={() => setSelectedDivision(division)}>
              {division}
            </button>
          ))}
        </div>
        {selectedDivision && (
          <div className="team-list">
            <h2>{selectedDivision}</h2>
            <ul>
              {divisions[selectedDivision].map(team => (
                <li key={team}>{team}</li>
              ))}
            </ul>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
