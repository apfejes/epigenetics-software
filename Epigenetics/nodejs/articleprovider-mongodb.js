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
  this.db.collection(collection_name).update({_id:ObjectID.createFromHexString(id)}, query_string, upsert_string , function(e, results) {
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
// INSERT API
//__________________________________


ArticleProvider.prototype.insertDB= function(collection_name, insert_criteria, callback) {
  this.db.collection(collection_name).insert(insert_criteria, function(e, results) {
    if (e) { 
      console.log("insertDB error:", e)
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
        project_collection.findOne({_id: ObjectID.createFromHexString(id)}, function(error, result) {
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
        plates_collection.findOne({_id: ObjectID.createFromHexString(id)}, function(error, result) {
          if( error ) {
            console.log("plateById error:", error)
            callback(error)
          } else callback(null, result)
        });
      }
    });
};

ArticleProvider.prototype.bsplateById = function(id, callback) {
    this.getDBData('bsplates', function(error, plates_collection) {
      if( error ) callback(error)
      else {
        plates_collection.findOne({_id: ObjectID.createFromHexString(id)}, function(error, result) {
          if( error ) {
            console.log("plateById error:", error)
            callback(error)
          } else callback(null, result)
        });
      }
    });
};

ArticleProvider.prototype.sampleByBsPlateId = function(id, callback) {
    this.getDBQuery('samples', {bsplates: ObjectID.createFromHexString(id)}, {}, {sampleid:1}, function(error, result) {
      if( error ) {
        console.log("sampleById error:", error)
        callback(error)
      } else callback(null, result)
    });
};



ArticleProvider.prototype.sampleByPlateId = function(id, callback) {
    this.getDBQuery('samples', {plates: ObjectID.createFromHexString(id)}, {}, {sampleid:1}, function(error, result) {
      if( error ) {
        console.log("sampleById error:", error)
        callback(error)
      } else callback(null, result)
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


  //---- 
  //Retrieve only the nanodrop types options
  //---- 

ArticleProvider.prototype.nanodrop_types = function(callback) {
    this.getDBQuery('xlat', {xlat: "nanodrop_type"}, {desc:1, _id:0}, {}, function(error, nanodrop_types) {
      if( error ) {
        console.log("nanodrop_types error: ", error);
        callback(error);
      } else callback(null, nanodrop_types)
    });
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
  var date = new Date();
  for( var i =0;i< sampleids.length;i++ ) {
    var s_id = ""
    var s_num = 1
    if (sampleids[i].indexOf("-") !== -1) {
      s_id = sampleids[i].substring(0,sampleids[i].indexOf("-"));
      s_num = sampleids[i].substring(1 + sampleids[i].indexOf("-"));
    } else {
      s_id = sampleids[i];
      s_num = 1
    }
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
// SAVE Placement on Bisulfite treatment plate
//__________________________________

ArticleProvider.prototype.saveBSPlacement = function(layout, project_id, callback) {
  var date = new Date();
  var o = JSON.parse(layout)
  var plateid = 0 
  o['projectid']= project_id
  this.insertDB('bsplates', o, function(error, results) { 
    if( error ) {
      console.log("UpdateDB for Save BS plates error: ", error)
      callback(error)
    } else{
      plateid = results[0]._id
      //console.log("newPlate:", plateid)
      for (key in o) {
        var value = o[key]
        //console.log("key : ",key, " - ", value)
        if (key != "projectid" && key != "_id") {
          s_id = value.substring(0, value.indexOf("-"))
          s_num = value.substring(value.indexOf("-")+1)
          //console.log("running update on projectid : ", project_id, " sampleid: ", s_id, " sample number:", s_num) 
          this.updateDB('samples', {projectid: project_id, sampleid: s_id, sample_num: s_num}, {$set: {bs_flag: null}, $push: {bsplates:plateid}}, false,
            function(error, c) {
              if ( error ) { 
                console.log("Error in updating samples assigned to plate")
                callback(error)
              } 
            }
          );
          
        } else {
          //just ignore this.  we don't need to process the projectid line.
        }
      }
      this.updateDB('projects', {_id: ObjectID.createFromHexString(project_id)}, {$push: {bsplates:plateid}}, false,
            function(error, c) {
              if ( error ) { 
                console.log("Error in updating plates assigned to project")
                callback(error)
              } 
            }
          );
      callback(results[0]._id);
    }
  }.bind(this));
};


//__________________________________
//
// SAVE Placement on plate
//__________________________________

ArticleProvider.prototype.savePlacement = function(assignments, project_id, callback) {
  var date = new Date();
  var o = JSON.parse(assignments)
  var plateid = 0 
  //var that = this
  o['projectid']= project_id
  this.insertDB('plates', o, function(error, results) { 
    if( error ) {
      console.log("UpdateDB for SavePlacement error: ", error)
      callback(error)
    } else{
      plateid = results[0]._id
      //console.log("newPlate:", plateid)
      for (key in o) {
        var value = o[key]
        //console.log("key : ",key, " - ", value)
        if (key != "projectid" && key != "_id") {
          s_id = value.substring(0, value.indexOf("-"))
          s_num = value.substring(value.indexOf("-")+1)
          //console.log("running update on projectid : ", project_id, " sampleid: ", s_id, " sample number:", s_num) 
          this.updateDB('samples', {projectid: project_id, sampleid: s_id, sample_num: s_num}, {$set: {proceed_flag: null}, $push: {plates:plateid}}, false,
            function(error, c) {
              if ( error ) { 
                console.log("Error in updating samples assigned to plate")
                callback(error)
              } 
            }
          );
          
        } else {
          //just ignore this.  we don't need to process the projectid line.
        }
      }
      this.updateDB('projects', {_id: ObjectID.createFromHexString(project_id)}, {$push: {plates:plateid}}, false,
            function(error, c) {
              if ( error ) { 
                console.log("Error in updating plates assigned to project")
                callback(error)
              } 
            }
          );
      callback(results[0]._id);
    }
  }.bind(this));
};




//__________________________________
//
// SAVE NANODROP
//__________________________________

ArticleProvider.prototype.saveNanodrop = function(sampleids, filename, project_id, nd_type, callback) {
  var date = new Date();
  for( var i =0;i< sampleids.length;i++ ) {
    var s_id = '';
    var s_num = '';
    var key = sampleids[i].sample_id;
    var key_i = key.indexOf("-");
	if (key_i != -1) {
	  s_id = key.substring(0,key_i)
	  s_num = key.substring(key_i + 1)
	} else {
	  s_id = sampleids[i].sample_id
	  s_num = 1
	}
	var selected= {}
	selected.nd_type = nd_type
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
	this.updateDB('samples', {projectid: project_id, sampleid: s_id, sample_num: s_num}, {$push: {nanodrop: selected}}, false,
      function(error) {  //the callback function
        if( error ) {
          console.log("UpdateDB for Nanodrop error: ", error)
          callback(error)
        }
      }
    );
  }
  callback();
};

//__________________________________
//
// SAVE SPREADSHEET
//__________________________________

ArticleProvider.prototype.process_sample_spreadsheet = function(collection, project_id, body, callback) {
  var date = new Date();
  var selected= {};
  var last_key = ""
  var e = ""
  for (key in body) {
    var sample_key = key.substring(0, key.lastIndexOf("-"));
    if (last_key == "") { 
      last_key = sample_key;
      selected['sampleid'] = key.substring(0, key.indexOf("-"));
      selected['sample_num'] = key.substring(key.indexOf("-")+1, key.lastIndexOf("-"));
    }
    if (sample_key == last_key) {
      selected[key.substring(key.lastIndexOf("-")+1)] = body[key];
    } else {
      // save record - split into the find component and the save component.
      var find = {}
      find['sampleid'] = selected['sampleid']
      find['sample_num'] = selected['sample_num']
      find['nanodrop.date'] = selected['date']
      find['nanodrop.time'] = selected['time']
      var set = {}
      if (selected['proceed_flag'] == "on") { 
        selected['proceed_flag'] = "checked"
      }
      set['proceed_flag'] = selected['proceed_flag']
      set['nanodrop.0.vol'] = selected['vol']
      set['nanodrop.0.dna_extract_date'] = selected['dna_extract_date']
      set['notes'] = selected['notes']
      //create query:
      this.updateDB('samples', find, {$set: set}, false, function(error) {  //the callback function
        if( error ) {
          console.log(error);
          e = error;
        }
      });
      //reset variables  for next key id.
      selected = {};
      last_key = sample_key;
      var a = key.indexOf("-");
      var b = key.lastIndexOf("-");
      selected['sampleid'] = key.substring(0, a);
      selected['sample_num'] = key.substring(a+1, b);
      selected[key.substring(b+1)] = body[key]; 
    }
  }
  // save record
  var find = {}
  find['sampleid'] = selected['sampleid']
  find['sample_num'] = selected['sample_num']
  find['nanodrop.date'] = selected['date']
  find['nanodrop.time'] = selected['time']
  var set = {}
  if (selected['proceed_flag'])    {  set['proceed_flag'] = selected['proceed_flag']  }
  if (selected['vol'])             {  set['nanodrop.0.vol'] = selected['vol']  }
  if (selected['dna_extract_date']){  set['nanodrop.0.dna_extract_date'] = selected['dna_extract_date']  }
  if (selected['notes'])           {  set['notes'] = selected['notes']  }
  //create query:
  
  this.updateDB('samples', find, {$set: set}, false, function(error) {  //the callback function
    if( error ) {
      console.log(error);
      e = error;
    }
  }); 
  callback(e);
};


//__________________________________
//
// Assign to BS plate
//__________________________________

ArticleProvider.prototype.assign_to_bs_plate = function(reserved,unassigned, callback) {
  var selected = [];
  for (item in unassigned) {
    if (unassigned[item].bs_flag && unassigned[item].bs_flag == "on") {
      //console.log("unassigned[item] :", unassigned[item])
      selected.push(unassigned[item])
    }
  }
  //console.log("selected:", selected)
  var len = selected.length
  selected.sort(function() {return 0.5 - Math.random()})  //randomize order
  
  if (reserved.length + selected.length > 96) {
    console.log("too many samples selected - assign to bs.plates")
  }
  i = 1
  j = 1
  layout = {}
  for (s in selected) {
    assigned = false;
    while (!assigned) {
      if (i > 8) {
        i = 1;
        j += 1;
      }
      if (j > 12) { 
        j = 1;
      }
      cell = i + "-" + j
      if (!reserved[cell]) {
        assigned = true;
        layout[cell] = selected[s].sampleid + "-" +  selected[s].sample_num
      } else {
        layout[cell] = "reserved"
      }
      i += 1
    } 
  }
  callback(layout) //replace null with error messages as required
}



//__________________________________
//
// Process Array - also used to process BS data
//__________________________________

ArticleProvider.prototype.process_Array = function(body, callback) {
  var collection = []
  var selected = {};
  var last_key = ""
  var e = ""
  for (key in body) {
    var sample_key = key.substring(0, key.lastIndexOf("-"));
    if (last_key == "") { 
      last_key = sample_key;
      selected['sampleid'] = key.substring(0, key.indexOf("-"));
      selected['sample_num'] = key.substring(key.indexOf("-")+1, key.lastIndexOf("-"));
    }
    if (sample_key == last_key) {
      selected[key.substring(key.lastIndexOf("-")+1)] = body[key];
    } else {
      // move to collection
      collection.push(selected)
      //reset variables  for next key id.
      selected = {};
      last_key = sample_key;
      var a = key.indexOf("-");
      var b = key.lastIndexOf("-");
      selected['sampleid'] = key.substring(0, a);
      selected['sample_num'] = key.substring(a+1, b);
      selected[key.substring(b+1)] = body[key]; 
    }
  }
  // save record
  collection.push(selected)
  callback(e, collection);
};


//__________________________________
//
//  Count Proceed Flags
//__________________________________
//

ArticleProvider.prototype.count_proceed_flags = function(body, callback) {
  
  count = 0;
  for (key in body) {
    var type = key.substring(key.lastIndexOf("-")+1)
    if (type == "proceed_flag") {
      if (body[key] == "on" || body[key] =="checked") {
        count++
      }
    }
  }
  callback(count)
}

//__________________________________
//
//  reserve/manual_array
//__________________________________
//

ArticleProvider.prototype.reserve_array = function(body, callback) {
  var tiles = {}
  for (key in body) {
    if (key.indexOf("-cell", key.length-5) != -1) {  //ends with -cell
      
      tiles[key.substring(0,key.lastIndexOf("-"))] = "reserved"
    }
  }
  callback(tiles)
}

ArticleProvider.prototype.manual_array = function(body, callback) {
  var tiles = {}
  for (key in body) {
    if (key.indexOf("-assign", key.length-7) != -1) {  //ends with -assign
      var k = key.substring(0,key.lastIndexOf("-"))
      tiles[body[key]] = key.substring(0,key.lastIndexOf("-")) 
    }
  }
  callback(tiles)
}

//__________________________________
//
//  parse_manual/interchip
//__________________________________
//

ArticleProvider.prototype.count_samples = function(data, callback) {
  
  var count = 0
  for (rec in data) {
    if (data[rec].proceed_flag != null) {
      count +=parseInt(data[rec].rep);
    }
  }
  callback(count)
}

ArticleProvider.prototype.parse_manual = function(data, callback) {
  
  var list = {}
  for (rec in data) {
    if (data[rec].rep_type == 3 && data[rec].proceed_flag != null) {  // manually placed
      list[data[rec].sampleid + "-" + data[rec].sample_num] = data[rec].rep
    }
  }
  callback(list)
}

ArticleProvider.prototype.parse_inter_chip = function(data, callback) {
  var list = {}
  for (rec in data) {
    if (data[rec].rep_type == 1 && data[rec].proceed_flag != null) {  // inter chip
      list[data[rec].sampleid + "-" + data[rec].sample_num] = data[rec].rep
    }
  }
  callback(list)
}

ArticleProvider.prototype.parse_intra_chip = function(data, callback) {
  var list = {}
  for (rec in data) {
    if (data[rec].rep_type == 2 && data[rec].proceed_flag != null) {  // intra chip
      list[data[rec].sampleid + "-" + data[rec].sample_num] = data[rec].rep
    }
  }
  callback(list)
}

ArticleProvider.prototype.parse_random = function(data, callback) {
  var list = {}
  for (rec in data) {
    if (data[rec].rep_type == 0 && data[rec].proceed_flag != null) {  // random chip
      list[data[rec].sampleid + "-" + data[rec].sample_num] = data[rec].rep
    }
  }
  callback(list)
}

//__________________________________
//
//  ASSIGN SAMPLES TO CHIPS!
//__________________________________
//


ArticleProvider.prototype.assign_to_chips = function(chips, layout, inter, intra, random, callback) {
  var assigned = {}
  for (l in layout) {    //trim off unneeded extensions on the sample name
    var sample = layout[l]
    if (sample.lastIndexOf("-") != sample.indexOf("-")) {
      assigned[l] = sample.substring(0,sample.lastIndexOf("-"))
    } else {
      assigned[l] = layout[l]
    }
  }
  var unassigned = {}  //identify all of the free cells to put samples into.
  for (var i =1; i <= 8; i++) {
    for (var j =1; j <= 12; j++) {
      var k = i + "-" + j;  //limit number of chips to fill based on the number of samples
      if (!layout[k] && (chips >= ((Math.floor((j-1)/6)*4) + Math.ceil(i/2)))) {
        unassigned[k] = "free"
      }
    }
  }
  for (i in inter) {  //max of inter[i] is set at 8 in sheet
    var r = []
    for (x = 1; x  <= chips; x++) {
      r.push(x)  //generate list of chips for each iteration
    }
    r.sort(function() {return 0.5 - Math.random()})  //randomize order
 
    
    for (var q = 1; q<= inter[i]; q++) {  //how many are we spreading across chips
      var n = r.pop()
      var s = []
      for (u in unassigned) {  //get free cells.
        var t = u.substring(0, u.indexOf("-"))
        var v = u.substring(u.indexOf("-")+1)
        if (n > 4) {  //second half of the array, chips 5-8
          if ((t == (2*n)-8 || t == ((2*n)-9)) && v > 6) {
            s.push(u)
            
          }
        } else { //on first half of the array, chips 1-4
          if ((t == (2*n) || t == ((2*n)-1)) && v < 7) { 
            s.push(u)
          }
        }
      }
      
      s.sort(function() {return 0.5 - Math.random()})  //randomize order
      //if s.length == 0.....  TODO: must deal with this.
      var cell = s.pop()
      assigned[cell] = i;  //write it to the list of assigned cells
      unassigned[cell] == "not-free"
    }
  }
  
    //refresh free cells per chip
    
  var intra_counts = []
  var unassigned = []
  for (var i = 1; i <= chips; i++) {
    var count = 0
    if (i < 5) {  //chips 1-4
      for (var n = (2 * i)-1; n <= (2*i); n++) {
        for (var m = 1; m <= 6; m++) {
          var k = n + "-" + m;
          if (!assigned[k]) {
            unassigned[k] = "free"
            count++;
          }
        }
      }
    } else { //chips 5-8
      for (var n = (2 * i)-9; n <= (2*i)-8; n++) {  //get the row numbers (2i-8 gives you row numbers.. (2*(i-4)-1 and 2*(i-4)-0))
        for (var m = 7; m <= 12; m++) {
          var k = n + "-" + m;
          if (!assigned[k]) {
            unassigned[k] = "free"
            count++;
          }
        }
      }
    }
    intra_counts[i] = count
  }
  
  var r = []
  for (x = 1; x  <= chips; x++) {
    r.push(x)  //generate list of chips for each iteration
  }
  r.sort(function() {return 0.5 - Math.random()})  //randomize order
  
  for (i in intra) {
    var n = r.pop()  //get a chip number
    while (r.length > 0 && intra_counts[n] < intra[i]) {  //if there aren't enough open spaces, and there are other chips to try, try again
      n = r.pop()
    }
    if (r.length == 0) {
      console.log("FAILURE couldn't fit intra on plate.")
    } else {
      var s = []
      for (u in unassigned) {  //get free cells.
        var u_maj = u.substring(0, u.indexOf("-"))
        var u_min = u.substring(u.indexOf("-")+1)
        if (n < 5) {  //chips 1 to 4
          if ((u_maj == (2*n) || u_maj == (2*n)-1) && (u_min <7) && unassigned[u] == "free") {
            s.push(u)
          }
        } else { //chips 5 to 8
          if ((u_maj == (2*n)-8 || u_maj == (2*n)-9) && (u_min > 6) && unassigned[u] == "free") {
            s.push(u)
          }
        }
      }
      //if s.length == 0.....  must deal with this.
      s.sort(function() {return 0.5 - Math.random()})  //randomize order
      for (var t = 1; t <= intra[i]; t++) {
        var cell = s.pop()
        assigned[cell] = i;
      }
      intra_counts[n] = intra_counts[n] - intra[t]
    }
  }
  
  //update free list.
  
  var unassigned = []
  for (var i = 1; i <= chips; i++) {
    var count = 0
    if (i < 5) {  //chips 1-4
      for (var n = (2 * i)-1; n <= (2*i); n++) {
        for (var m = 1; m <= 6; m++) {
          var k = n + "-" + m;
          if (!assigned[k]) {
            unassigned.push(k)
          }
        }
      }
    } else { //chips 5-8
      for (var n = (2 * i)-9; n <= (2*i)-8; n++) {  //get the row numbers (2i-8 gives you row numbers.. (2*(i-4)-1 and 2*(i-4)-0))
        for (var m = 7; m <= 12; m++) {
          var k = n + "-" + m;
          if (!assigned[k]) {
            unassigned.push(k)
          }
        }
      }
    }
  }
  
  unassigned.sort(function() {return 0.5 - Math.random()})  //randomize order

  for (k in random) {
    var n = unassigned.pop()
    if (n == undefined) {
       break;
    }
    assigned[n] = k
  }
  callback(assigned)
}


//__________________________________
//
//  Required Exports.
//__________________________________
//

exports.ArticleProvider = ArticleProvider;
