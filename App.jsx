import React, { useState, useEffect } from 'react';
import { CSVReader } from 'react-papaparse';
import { Tabs, Tab, Table, Button, Form } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

const NFLStatsApp = () => {
    const NFL_Teams = [
        "New England Patriots",
        "Buffalo Bills",
        "Miami Dolphins",
        "New York Jets",
        "Pittsburgh Steelers",
        "Baltimore Ravens",
        "Cincinnati Bengals",
        "Cleveland Browns",
        "Houston Texans",
        "Indianapolis Colts",
        "Jacksonville Jaguars",
        "Tennessee Titans",
        "Kansas City Chiefs",
        "Los Angeles Chargers",
        "Denver Broncos",
        "Las Vegas Raiders",
        "Philadelphia Eagles",
        "Washington Commanders",
        "Dallas Cowboys",
        "New York Giants",
        "Detroit Lions",
        "Minnesota Vikings",
        "Green Bay Packers",
        "Chicago Bears",
        "Tampa Bay Buccaneers",
        "Atlanta Falcons",
        "New Orleans Saints",
        "Carolina Panthers",
        "Los Angeles Rams",
        "Seattle Seahawks",
        "Arizona Cardinals",
        "San Francisco 49ers",
    ];

    const AFC_East = NFL_Teams.slice(0, 4);
    const AFC_North = NFL_Teams.slice(4, 8);
    const AFC_South = NFL_Teams.slice(8, 12);
    const AFC_West = NFL_Teams.slice(12, 16);
    const NFC_East = NFL_Teams.slice(16, 20);
    const NFC_North = NFL_Teams.slice(20, 24);
    const NFC_South = NFL_Teams.slice(24, 28);
    const NFC_West = NFL_Teams.slice(28, 32);

    const [activeTab, setActiveTab] = useState('Quarterbacks');
    const [data, setData] = useState([]);
    const [sortConfig, setSortConfig] = useState(null);
    const [colorScale, setColorScale] = useState(true);

    const handleFileLoad = (fileData) => {
        const formattedData = fileData.map(row => row.data);
        setData(formattedData);
    };

    const calculateColor = (value, min, max) => {
        if (value === null || max === min) return '#FFFFFF';
        const normalized = (value - min) / (max - min);
        const red = Math.round(255 * (1 - normalized));
        const green = Math.round(255 * normalized);
        return `rgb(${red},${green},0)`;
    };

    const sortData = (column) => {
        let direction = 'ascending';
        if (
            sortConfig &&
            sortConfig.key === column &&
            sortConfig.direction === 'ascending'
        ) {
            direction = 'descending';
        }

        const sortedData = [...data].sort((a, b) => {
            if (a[column] < b[column]) return direction === 'ascending' ? -1 : 1;
            if (a[column] > b[column]) return direction === 'ascending' ? 1 : -1;
            return 0;
        });

        setData(sortedData);
        setSortConfig({ key: column, direction });
    };

    useEffect(() => {
        if (colorScale) {
            const numericColumns = data[0]?.filter(col => !isNaN(parseFloat(col)));
            numericColumns?.forEach((col, colIndex) => {
                const colValues = data.map(row => parseFloat(row[colIndex])).filter(val => !isNaN(val));
                const min = Math.min(...colValues);
                const max = Math.max(...colValues);

                data.forEach((row, rowIndex) => {
                    const value = parseFloat(row[colIndex]);
                    if (!isNaN(value)) {
                        row[colIndex] = {
                            value,
                            color: calculateColor(value, min, max)
                        };
                    }
                });
            });
        }
    }, [colorScale, data]);

    return (
        <div className="container mt-4">
            <h1>NFL Player Stats</h1>
            <Form.Check 
                type="switch"
                id="color-scale-toggle"
                label="Toggle Color Scale"
                checked={colorScale}
                onChange={(e) => setColorScale(e.target.checked)}
            />
            <Tabs
                activeKey={activeTab}
                onSelect={(k) => setActiveTab(k)}
                className="mb-3"
            >
                {['Quarterbacks', 'Running Backs', 'Wide Receivers', 'Kickers', 'Defense', 'Schedule'].map(tab => (
                    <Tab eventKey={tab} title={tab} key={tab}>
                        <CSVReader onFileLoaded={handleFileLoad} />
                        <Table bordered hover>
                            <thead>
                                <tr>
                                    {data[0]?.map((col, index) => (
                                        <th
                                            key={index}
                                            onClick={() => sortData(index)}
                                            style={{ cursor: 'pointer' }}
                                        >
                                            {col}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {data.slice(1)?.map((row, rowIndex) => (
                                    <tr key={rowIndex}>
                                        {row.map((cell, cellIndex) => (
                                            <td
                                                key={cellIndex}
                                                style={{
                                                    backgroundColor: colorScale ? cell.color : '#FFFFFF',
                                                }}
                                            >
                                                {cell.value || cell}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    </Tab>
                ))}
            </Tabs>
        </div>
    );
};

export default NFLStatsApp;
