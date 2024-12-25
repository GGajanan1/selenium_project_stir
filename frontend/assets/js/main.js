document.getElementById('fetch-button').addEventListener('click', async () => {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = 'Fetching...';

    try {
        const response = await fetch('http://localhost:3000/run-script', { method: 'POST' });
        if (!response.ok) throw new Error('Failed to fetch data');

        const data = await response.json();
        resultsDiv.innerHTML = `
            <h2>Trending Topics</h2>
            <ul>
                <li>${data.trend1 || 'N/A'}</li>
                <li>${data.trend2 || 'N/A'}</li>
                <li>${data.trend3 || 'N/A'}</li>
                <li>${data.trend4 || 'N/A'}</li>
                <li>${data.trend5 || 'N/A'}</li>
            </ul>
            <p>IP Address: ${data.ip_address}</p>
            <p>Timestamp: ${data.date_time}</p>
        `;
    } catch (error) {
        resultsDiv.innerHTML = 'Error fetching data!';
        console.error('Error:', error);
    }
});
