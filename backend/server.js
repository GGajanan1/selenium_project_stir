const express = require('express');
const bodyParser = require('body-parser');
const { exec } = require('child_process');
require('dotenv').config();

const app = express();
const port = 3000;

app.use(bodyParser.json());

app.post('/run-script', (req, res) => {
    exec('python3 selenium_twitter_trending.py', { cwd: __dirname }, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing script: ${error}`);
            return res.status(500).json({ error: 'Script execution failed' });
        }
        try {
            const result = JSON.parse(stdout.trim());
            res.json(result);
        } catch (err) {
            console.error('Error parsing script output:', err);
            res.status(500).json({ error: 'Invalid script output' });
        }
    });
});

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
