// Frontend JavaScript functionality for Gamified E-learning System

// Function to display current date and time in UTC
function displayDateTime() {
    const currentDateTime = new Date().toISOString(); // Gets current date and time in ISO format
    const formattedDateTime = currentDateTime.replace('T', ' ').substring(0, 19); // Formats to YYYY-MM-DD HH:MM:SS
    console.log(`Current Date and Time (UTC): ${formattedDateTime}`);
}

displayDateTime();

// You can add more functionality here as needed.