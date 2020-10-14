const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const mongoose = require('mongoose');

const port = process.env.PORT || 2000;
const base = `${__dirname}/public`;

//connecting to mongoDB
mongoose.Promise = global.Promise;
mongoose.connect("mongodb+srv://MARCLDG:SIT31153HD@cluster0.f3acr.mongodb.net/changestream?retryWrites=true&w=majority")

//creating a dataschema
var dataSchema = new mongoose.Schema({
    _id: String,
    mac_address: String,
    status: Boolean,
    level: Number
  }, {collection: 'collection'});

var Data = mongoose.model("collection", dataSchema);

//Setting Cross-Origin Headers
app.use((req, res, next) => {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Methods", "POST, PUT, GET, OPTIONS, REQUEST");
    res.header("Access-Control-Allow-Headers", "Origin, X-RequestedWith, Content-Type, Accept");

    next();
});

//Setting express to use body parser
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
//app.use(cookieParser());

app.use(express.static('public'));

app.post('/update-lights', (req, res) => {
    const{bulbip, bulbstatus} = req.body;
    console.log(req.body)
    Data.findOne({_id: bulbip}, function(err, document){
        console.log(document)
        document.status = bulbstatus;
        document.save((err) => {
            if (err) { console.log(err); }
            });
    })
    return res.json({
        success: true
    });
});

app.get('/', async (req, res) => {
    var bulbs = await Data.find({})
    return res.send(bulbs)
});

//Web Listener\\
app.listen(port, () => {
    console.log(`Listening on port ${port}`);
});