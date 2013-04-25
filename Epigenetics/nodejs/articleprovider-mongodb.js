var Db = require('mongodb').Db;
var Connection = require('mongodb').Connection;
var Server = require('mongodb').Server;
var BSON = require('mongodb').BSON;
var ObjectID = require('mongodb').ObjectID;

ArticleProvider = function(host, port) {
  this.db= new Db('human_epigenetics', new Server(host, port, {auto_reconnect: true}, {}));
  this.db.open(function(){});
};

//APF: altered function to return a complete list of projects
ArticleProvider.prototype.getDBData= function(table_name, callback) {
  this.db.collection(table_name, function(error, project_collection) {
    if( error ) callback(error);
    else callback(null, project_collection);
  });
};

//APF: altered function 


ArticleProvider.prototype.getDBQuery= function(table_name, query_string, fields, callback) {
  this.db.collection(table_name).find(query_string, fields).toArray(function(e, results) {
    if (e) console.log("getDBQuery error:", e)
    else callback(null, results)
  })
};

//APF: Function to return the names of all projects
ArticleProvider.prototype.findAllProjects = function(callback) {
    this.getDBData('projects', function(error, project_collection) {
      if( error ) callback(error)
      else {
        project_collection.find().toArray(function(error, results) {
          if( error ) callback(error)
          else callback(null, results)
        });
      }
    });
};


//this is the function that was provided in the demo code
ArticleProvider.prototype.findById = function(id, callback) {
    this.getDBData('projects', function(error, project_collection) {
      if( error ) callback(error)
      else {
        project_collection.findOne({_id: project_collection.db.bson_serializer.ObjectID.createFromHexString(id)}, function(error, result) {
          if( error ) callback(error)
          else callback(null, result)
        });
      }
    });
};

//Retrieve only the project status options
ArticleProvider.prototype.project_status = function(callback) {
    this.getDBQuery('xlat', {xlat: "status"}, {desc:1, _id:0}, function(error, project_status) {
      if( error ) console.log("project-status error: ", error);
      else callback(null, project_status)
    });
};

//Retrieve only the transaction types options
ArticleProvider.prototype.transaction_type = function(callback) {
    this.getDBQuery('xlat', {xlat: "transaction_type"}, {desc:1, _id:0}, function(error, transaction) {
      if( error ) console.log("transaction-type error: ", error);
      else callback(null, transaction)
    });
};

//Retrieve only the transaction types options
ArticleProvider.prototype.getTransactions = function(id, callback) {
    this.getDBQuery('transactions', {projectid: id}, {}, function(error, transactions) {
      if( error ) console.log("transaction-type error: ", error);
      else callback(null, transactions)
    });
};

//Retrieve only the transaction types options
ArticleProvider.prototype.getIDbyName = function(name, callback) {
    this.getDBQuery('projects', {proj_name: name}, {_id:1}, function(error, id) {
      if( error ) console.log("id-lookup error: ", error);
      else callback(null, id)
    });
};

//APF:  Modified to use the projects - saves to a project table.
ArticleProvider.prototype.save = function(collection, projects, callback) {
    this.getDBData(collection, function(error, project_collection) {
      if( error ) callback(error)
      else {
        if( typeof(projects.length)=="undefined")
          projects = [projects];

        for( var i =0;i< projects.length;i++ ) {
          project = projects[i];
          project.created_at = new Date();
          if( project.comments === undefined ) project.comments = [];
          for(var j =0;j< project.comments.length; j++) {
            project.comments[j].created_at = new Date();
          }
        }

        project_collection.insert(projects, function() {
          callback(null, projects);
        });
      }
    });
};

exports.ArticleProvider = ArticleProvider;
