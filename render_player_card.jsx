const renderPlayerCard = () => {
    // Ensure playerRosterData and Name exist before splitting
    const fullName = playerRosterData?.Name?.trim() || "Unknown Player";
    const nameParts = fullName.split(/\s+/); // Split on any whitespace
    const firstName = nameParts.length > 0 ? nameParts[0] : "Unknown"; // Default fallback
    const lastName = nameParts.length > 1 ? nameParts.slice(1).join(" ") : ""; // Allow for multiple last names

    // Ensure playerName is properly sanitized before replacing characters
    const sanitizedPlayerName = fullName.replace(/\s+/g, "_").replace(/'/g, "-");

    return (
        <div className="player-card">
            {/* Headshot Image - Adjusted to not be centered horizontally */}
            <div 
                className="image-container" 
                style={{ top: `38.5%`, left: '54%' }}  // Adjust left as needed
            >
                <img 
                    src={`/data/headshots/${sanitizedPlayerName}_headshot.png`} 
                    alt="Headshot Not Found" 
                    className="player-headshot" 
                />
            </div>
    
            {/* Player Name - First Name Above Last Name */}
            <div className="card-name">
                <p><strong>{firstName}</strong></p> {/* First Name */}
                {lastName && <p><strong>{lastName}</strong></p>}  {/* Last Name (if available) */}
            </div>
    
            {/* Player Position */}
            <div className="position">
                <p><strong>{playerRosterData?.Position || "Unknown Position"}</strong></p>
            </div>
    
            {/* Team Logo */}
            <div className="team-logo-container">
                <img 
                    src={`/data/logos/${(playerRosterData?.Team || "unknown-team").replace(/\s+/g, "-").toLowerCase()}.png`} 
                    alt="Team Logo Not Found" 
                    className="team-logo" 
                />
            </div>
    
            {/* Conference Logo */}
            <div className="conference-logo-container">
                <img 
                    src={`/data/logos/${(playerRosterData?.Conference || "unknown-conference")}.png`} 
                    alt="Conference Logo Not Found" 
                    className="conference-logo" 
                />
            </div>
        </div>
    );
};
