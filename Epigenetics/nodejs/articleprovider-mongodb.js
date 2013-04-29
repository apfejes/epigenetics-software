var Db = require('mongodb').Db;
var Connection = require('mongodb').Connection;
var Server = require('mongodb').Server;
var BSON = require('mongodb').BSON;
var ObjectID = require('mongodb').ObjectID;

ArticleProvider = function(host, port) {
  this.db= new Db('human_epigenetics', new Server(host, port, {auto_reconnect: true}, {}));
  this.db.open(function(){});
};

//__________________________________
//
//  Return all documents (find) in a collection
//__________________________________

ArticleProvider.prototype.getDBData= function(collection_name, callback) {
  this.db.collection(collection_name, function(error, project_collection) {
    if( error ) callback(error);
    else callback(null, project_collection);
  });
};

//__________________________________
//
//  Perform a specific query (find) on a collection 
//__________________________________


ArticleProvider.prototype.getDBQuery= function(collection_name, query_string, fields, callback) {
  this.db.collection(collection_name).find(query_string, fields).toArray(function(e, results) {
    if (e) console.log("getDBQuery error:", e)
    else callback(null, results)
  })
};

//__________________________________
//
// UPDATE API
//__________________________________

ArticleProvider.prototype.updateDB= function(collection_name, id, query_string,  callback) {
  this.db.collection(collection_name).update({_id:new ObjectID(id)}, query_string, {} , function(e, results) {
    if (e) console.log("updateDB error:", e)
    else callback(null, results)
  })
};

//__________________________________
//
// Functions for retrieval of specific information
//__________________________________


  //------
  //APF: Function to return the names of all projects, used by index to list projects
  //----- 
  
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

  //---- 
  //Function provided by demo tutorial code, used to return one record
  //----
  
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

  //---- 
  //Retrieve only the project status options
  //---- 

ArticleProvider.prototype.project_status = function(callback) {
    this.getDBQuery('xlat', {xlat: "status"}, {desc:1, _id:0}, function(error, project_status) {
      if( error ) console.log("project-status error: ", error);
      else callback(null, project_status)
    });
};


  //---- 
  //Retrieve only the transaction types options
  //---- 
  
ArticleProvider.prototype.transaction_type = function(callback) {
    this.getDBQuery('xlat', {xlat: "transaction_type"}, {desc:1, _id:0}, function(error, transaction) {
      if( error ) console.log("transaction-type error: ", error);
      else callback(null, transaction)
    });
};

  //---- 
  //Retrieve only the transaction types options
  //---- 
  
ArticleProvider.prototype.getTransactions = function(id, callback) {
    this.getDBQuery('transactions', {projectid: id}, {}, function(error, transactions) {
      if( error ) console.log("transaction-type error: ", error);
      else callback(null, transactions)
    });
};


  //---- 
  //Retrieve only the transaction types options
  //---- 
  
ArticleProvider.prototype.getIDbyName = function(name, callback) {
    this.getDBQuery('projects', {proj_name: name}, {_id:1}, function(error, id) {
      if( error ) console.log("id-lookup error: ", error);
      else callback(null, id)
    });
};

//__________________________________
//
// SAVE FUNCTION
//__________________________________

ArticleProvider.prototype.save = function(collection_name, projects, callback) {
    if( typeof(projects.length)=="undefined")
      projects = [projects];
    for( var i =0;i< projects.length;i++ ) {
      project = projects[i];
      project.created_at = new Date();
      this.db.collection(collection_name).insert(projects, function() {
        callback(null, projects);
      })
    };
};

//__________________________________
//
// UPDATE FUNCTION
//__________________________________


ArticleProvider.prototype.update = function(collection, id, project, callback) {
    project.last_updated = new Date();
    this.updateDB(collection, id, {$set: project}, function(error, c) {
      if( error ) callback(error)
      else callback(null, c);
    });
};

//__________________________________
//
//  Required Exports.
//__________________________________
//

exports.ArticleProvider = ArticleProvider;
