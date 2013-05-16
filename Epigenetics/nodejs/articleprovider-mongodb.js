var Db = require('mongodb').Db;
var Connection = require('mongodb').Connection;
var Server = require('mongodb').Server;
var BSON = require('mongodb').BSON;
var ObjectID = require('mongodb').ObjectID;

ArticleProvider = function(host, port) {
  this.db= new Db('test', new Server(host, port, {auto_reconnect: true}, {}), {safe:true});
  this.db.open(function(){});
};

//__________________________________
//
//  Return all documents (find) in a collection
//__________________________________

ArticleProvider.prototype.getDBData= function(collection_name, callback) {
  this.db.collection(collection_name, function(error, project_collection) {
    if( error ) {
      console.log("getDBData error:", e)
      callback(error);
    }
    else callback(null, project_collection);
  });
};

//__________________________________
//
//  Perform a specific query (find) on a collection 
//__________________________________


ArticleProvider.prototype.getDBQuery= function(collection_name, query_string, fields, sort_field, callback) {
  if (sort_field != null && sort_field != {}) {
    this.db.collection(collection_name).find(query_string, fields).sort(sort_field).toArray(function(e, results) {
      if (e) {
        console.log("getDBQuery error:", e)
        callback(e)
      }
      else callback(null, results)
    })
  } else {
   this.db.collection(collection_name).find(query_string, fields).toArray(function(e, results) {
      if (e) {
        console.log("getDBQuery error:", e)
        callback(e)
      }
      else callback(null, results)
    })
  }
};

//__________________________________
//
// UPDATE API
//__________________________________

ArticleProvider.prototype.updateDBid= function(collection_name, id, query_string, upsert, callback) {
  var upsert_string
  if (upsert == true) upsert_string = '{upsert:true}'
  else upsert_string = '{}'
  this.db.collection(collection_name).update({_id:new ObjectID(id)}, query_string, upsert_string , function(e, results) {
    if (e) { 
      console.log("updateDBid error:", e)
      callback(e)
    }
    else callback(null, results)
  })
};

ArticleProvider.prototype.updateDB= function(collection_name, update_criteria, query_string, upsert, callback) {
  var upsert_string
  if (upsert == true) upsert_string = '{upsert:true}'
  else upsert_string = '{}'
  this.db.collection(collection_name).update(update_criteria, query_string, upsert_string , function(e, results) {
    if (e) { 
      console.log("updateDB error:", e)
      callback(e)
    } else callback(null, results)
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
          if( error ) {
            console.log("findAllProjects error:", e)
            callback(error)
          }
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
          if( error ) {
            console.log("findByID error:", e)
            callback(error)
          } else callback(null, result)
        });
      }
    });
};

ArticleProvider.prototype.plateById = function(id, callback) {
    this.getDBData('plates', function(error, plates_collection) {
      if( error ) callback(error)
      else {
        collection.findOne({_id: project_collection.db.bson_serializer.ObjectID.createFromHexString(id)}, function(error, result) {
          if( error ) {
            console.log("plateById error:", e)
            callback(error)
          } else callback(null, result)
        });
      }
    });
};

ArticleProvider.prototype.sampleById = function(id, num, callback) {
    this.getDBQuery('samples', {sampleid: id, sample_num:num}, {}, {sampleid:1}, function(error, result) {
      if( error ) {
        console.log("sampleById error:", e)
        callback(error)
      } else callback(null, result)
    });
};

  //---- 
  //Retrieve only the project status options
  //---- 

ArticleProvider.prototype.project_status = function(callback) {
    this.getDBQuery('xlat', {xlat: "status"}, {desc:1, _id:0}, {}, function(error, project_status) {
      if( error ) {
        console.log("project-status error: ", error);
        callback(error);
      } else callback(null, project_status)
    });
};


  //---- 
  //Retrieve only the transaction types options
  //---- 
  
ArticleProvider.prototype.transaction_type = function(callback) {
    this.getDBQuery('xlat', {xlat: "transaction_type"}, {desc:1, _id:0}, {}, function(error, transaction) {
      if( error ) {
        console.log("transaction-type error: ", error);
        callback(error);
      } else callback(null, transaction)
    });
};

  //---- 
  //Retrieve transaction for a project
  //---- 
  
ArticleProvider.prototype.getTransactions = function(id, callback) {
    this.getDBQuery('transactions', {projectid: id}, {}, {}, function(error, transactions) {
      if( error ) {
        console.log("transaction-type error: ", error);
        callback(error);
      } else callback(null, transactions)
    });
};

  //---- 
  //Retrieve plates for a project
  //---- 
  
ArticleProvider.prototype.getPlates = function(id, callback) {
    this.getDBQuery('plates', {projectid: id}, {}, {}, function(error, transactions) {
      if( error ) {
        console.log("transaction-type error: ", error);
        callback(error);
      } else callback(null, transactions)
    });
};

  //---- 
  //Retrieve samples for a project
  //---- 
  

ArticleProvider.prototype.getSamples = function(id, callback) {
    this.getDBQuery('samples', {projectid: id}, {}, {sampleid:1}, function(error, samples) {
      if( error ) {
        console.log("samples-type error: ", error);
        callback(error);
      } else callback(null, samples)
    });
};



  //---- 
  //Retrieve only the transaction types options
  //---- 
  
ArticleProvider.prototype.getIDbyName = function(name, callback) {
    this.getDBQuery('projects', {proj_name: name}, {_id:1}, {}, function(error, id) {
      if( error ) {
        console.log("id-lookup error: ", error);
        callback(error);
      } else callback(null, id)
    });
};

  //---- 
  //Retrieve only the nanodrop options
  //---- 
  
ArticleProvider.prototype.getNanodrop = function(id, callback) {
    this.getDBQuery('nanodrop', {projectid: id}, {}, {}, function(error, id) {
      if( error ) {
        console.log("nanodrop-lookup error: ", error);
        callback(error);
      } else callback(null, id)
    });
};


//__________________________________
//
// SAVE FUNCTION
//__________________________________

ArticleProvider.prototype.save = function(collection_name, data, callback) {
    if( typeof(data.length)=="undefined")
      data = [data];
    for( var i =0;i< data.length;i++ ) {
      data = data[i];
      data.created_at = new Date();
      this.db.collection(collection_name).insert(data, function() {
        callback(null, data);
      })
    };
};


//__________________________________
//
// UPSERT FUNCTION
//__________________________________

ArticleProvider.prototype.upsert = function(collection_name, keys, data, callback) {
    if( typeof(data.length)=="undefined")
      data = [data];
    for( var i =0;i< data.length;i++ ) {
      data = data[i];
      data.created_at = new Date();
      this.db.collection(collection_name).update(keys, {$set : data},
                                   {upsert:true},function(error, c) {
                                   callback(null, data);
      })
    };
};


//__________________________________
//
// UPDATE FUNCTION
//__________________________________


ArticleProvider.prototype.update = function(collection, id, project, callback) {
    project.last_updated = new Date();
    this.updateDBid(collection, id, {$set: project}, false, function(error, c) {
      if( error ) callback(error)
      else callback(null, c);
    });
};

//__________________________________
//
// COMPLEX FUNCTIONS 
//__________________________________
//
// SAVE SAMPLES
//__________________________________

ArticleProvider.prototype.saveSamples = function(sampleids, project_id, callback) {
  //console.log(project_id, "  ", sampleids);
  var date = new Date();
  for( var i =0;i< sampleids.length;i++ ) {
    //console.log(project_id, "  ", sampleids[i])
    var s_id = ""
    var s_num = 1
    if (sampleids[i].indexOf("-") !== -1) {
      s_id = sampleids[i].substring(0,sampleids[i].indexOf("-"));
      s_num = sampleids[i].substring(1 + sampleids[i].indexOf("-"));
    } else {
      s_id = sampleids[i];
      s_num = 1
    }
    
    //console.log("samples processed:", sampleids[i], " ", s_id, " ", s_num)
    this.upsert('samples', {projectid: project_id, sampleid: s_id, sample_num: s_num},
      {last_updated: date},  
      function(error) {
        if( error ) {
          console.log("saveSamples error: ", error);
          callback(error)
        } 
      }
    );
  }
  callback();
};

//__________________________________
//
// SAVE NANODROP
//__________________________________

ArticleProvider.prototype.saveNanodrop = function(sampleids, filename, project_id, callback) {
  var date = new Date();
  for( var i =0;i< sampleids.length;i++ ) {
    var selected= {}
	if (sampleids[i].sample_id.indexOf("-") != -1) {
	  selected.sampleid = sampleids[i].sample_id.substring(0,sampleids[i].sample_id.indexOf("-"))
	  selected.sample_num = sampleids[i].sample_id.substring(sampleids[i].sample_id.indexOf("-") + 1)
	} else {
	  selected.sampleid = sampleids[i].sample_id
	  selected.sample_num = 1
	}
	selected.projectid = project_id
	selected.date = sampleids[i].date
	selected.time = sampleids[i].time
	selected.conc = sampleids[i].conc
	selected.units = sampleids[i].units
	selected.a260 = sampleids[i].a260
	selected.a280 = sampleids[i].a280
	selected.a230 = sampleids[i]._2300
	selected.na_type = sampleids[i].na_type
	selected.mod = sampleids[i].mod
	selected.path = sampleids[i].path
	selected.nanodropver = sampleids[i].nanodropver
	selected.firmware = sampleids[i].firmware
	selected.last_updated = date
	this.updateDB('samples', {projectid: project_id, sampleid: selected.sampleid, sample_num: selected.sample_num}, {$push: {nanodrop: selected}}, false,
      function(error) {  //the callback function
        if( error ) callback(error)
      }
    );
  }
  callback();
};




//__________________________________
//
//  Required Exports.
//__________________________________
//

exports.ArticleProvider = ArticleProvider;
