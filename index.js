const express = require('express');
const app = express();

const port = process.env.PORT || 80;
const base = `${__dirname}/public`;

//Setting Cross-Origin Headers
app.use((req, res, next) => {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Methods", "POST, PUT, GET, OPTIONS, REQUEST");
    res.header("Access-Control-Allow-Headers", "Origin, X-RequestedWith, Content-Type, Accept");

    next();
});

app.use(express.static('public'));

app.get('/', (req, res) => {
    res.sendFile(`${base}/frontend.html`);
});

//Web Listener\\
app.listen(port, () => {
    console.log(`Listening on port ${port}`);
});