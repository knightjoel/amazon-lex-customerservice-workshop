const fs = require('fs');
const AWS = require('aws-sdk');
const util = require('util');
const response = require('cfn-response');

const operatorDdbTable = process.env.OPERATOR_DDB_TABLE;
const wellsiteLocationDdbTable = process.env.WELL_SITE_LOCATION_DDB_TABLE;
const wellsiteVisitDdbTable = process.env.WELL_SITE_VISIT_DDB_TABLE;

const docClient = new AWS.DynamoDB.DocumentClient({
    region: process.env.AWS_REGION
});
const batchSize = 25;

exports.handler = function (event, context, callback) {

    console.log("Reading input from event:\n", util.inspect(event, {depth: 5}));
    const input = event.ResourceProperties;

    if (event.RequestType === 'Delete') {
        response.send(event, context, response.SUCCESS, {});
    }

    loadData('operatorData.json',operatorDdbTable);
    loadData('wellsiteLocationData.json',wellsiteLocationDdbTable);
    loadData('wellsiteVisitData.json',wellsiteVisitDdbTable);

    response.send(event, context, response.SUCCESS, {});

};

function loadData(dataFile, ddbTable) {
    var obj = JSON.parse(fs.readFileSync(dataFile, 'utf8'));

    var batchPutPromises = [];
    var itemArray = [];
    for (var i = 0; i < obj.length; i++) {
        if (i % batchSize === 0 && i !== 0) {
            var param = {RequestItems: {}};
            param['RequestItems'][ddbTable] = itemArray;
            batchPutPromises.push(docClient.batchWrite(param).promise());
            itemArray = [];
        }
        itemArray.push({PutRequest: {Item: obj[i]}});
    }
    var promParam = {RequestItems: {}};
    promParam['RequestItems'][ddbTable] = itemArray;
    batchPutPromises.push(docClient.batchWrite(promParam).promise());

    Promise.all(batchPutPromises).then(data => {
        console.log("done loading " + obj.length + " rows.");
        //response.send(evt, ctx, response.SUCCESS, {});
    }).catch(err => {
        console.error(err);
        //response.send(evt, ctx, response.FAILED, err);
    });
}