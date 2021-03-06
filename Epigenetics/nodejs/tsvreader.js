var fs = require('fs')
var sys = require('sys')
 
 
//_____________________________________________________
//
// This file was derived from a script provided at 
// https://gist.github.com/jamescarr/467954#file-gistfile1-js
//
//_________________________________________________

//function parseCsvFile(fileName, callback){
//  var stream = fs.createReadStream(fileName)
//  var iteration = 0, header = [], buffer = ""
//  var pattern = /(?:^|,)("(?:[^"]+)*"|[^,]*)/g
//  stream.addListener('data', function(data){
//    buffer+=data.toString()
//    var parts = buffer.split('\r\n')
//    parts.forEach(function(d, i){
//      if(i == parts.length-1) return
//      if(iteration++ == 0 && i == 0){
//        header = d.split(pattern)
//      }else{
//        callback(buildRecord(d))
//      }
//    })
//    buffer = parts[parts.length-1]
//  })
 
//  function buildRecord(str){
//    var record = {}
//    str.split(pattern).forEach(function(value, index){
//      if(header[index] != '')
//        record[header[index].toLowerCase()] = value.replace(/"/g, '')
//    })
//    return record
//  }
//}


//------------------------------------------------
//
//  Tab Separated Values reader
//
//------------------------------------------------

Tsvreader = function() {
  this.t= 'string'
};

function clean(a, value) {
  var z = new Array()
  for(var i = 0; i<a.length; i++){
    if (a[i] != value) {
      z.push(a[i])
    }
  }
  return z
}



Tsvreader.prototype.parseTsvFile = function(path, callback){
  var stream = fs.createReadStream(path)
  var c = new Array(), header = [], buffer = "", refresh_header = true
  var iteration = 0
  stream.addListener('data', function(data){
    buffer+=data.toString()
    var parts = buffer.split('\r\n')
    parts.forEach(function(d, i){
      if(parts.length-1 == 0) {
        return
      }
      if(refresh_header) {         //header line
        header = d.split("\t")
        header.forEach(function(x,j) {
          header[j] = x.trim().replace(/[()/.]/g,"").replace(/ /g,"_")
          if (/^\d/.test(header[j])) {
            header[j] = "_" + header[j]
          }
        refresh_header = false
        })
      }else if (d === "") {        //blank lines - next line will be a header.
        refresh_header = true
      }else{                       //data line
         c[iteration]= buildRecord(d)
         iteration++

      }
    })
    
    buffer = parts[parts.length-1]
    callback(null, c) 
  })

  function buildRecord(str){
    var record = {}
    str.split("\t").forEach(function(value, index){
      if(index <= header.length-1 && header[index] != '' && value != '')
        record[header[index].toLowerCase()] = value.trim().replace(/"/g, '')
    })
    return record
  }
};


Tsvreader.prototype.parseSimple = function(path, callback){
  var stream = fs.createReadStream(path)
  var c = new Array(), buffer = "", iteration = 0
  stream.addListener('data', function(data){
    buffer+=data.toString()
    var parts = buffer.split('\n')
    parts.forEach(function(d, i){
      if(parts.length-1 == 0) {
        return
      }
      if (d != "") {        //blank lines should be ignored.
         c[iteration]= d
         iteration++
      }
    })
    buffer = parts[parts.length-1]

  })
  stream.addListener('end', function (error, data) {
    callback(null, c) 
  })
};

Tsvreader.prototype.parseNanodropFile = function(path, callback){
  var stream = fs.createReadStream(path, {'bufferSize': 12 * 1024})
  var c = new Array(), header = [], buffer = "", refresh_header = true
  var iteration = 0
  var Mod = "", Path = "", Sw = "", Fw = ""
  var hash = {}; list =[];
  
  stream.addListener('data', function(data){
    buffer+=data.toString()
    var parts = buffer.split('\r\n')
    parts.forEach(function(d, i) {
      if(parts.length-1 == 0) {
        return
      }
      text = d.split("\t")
      if (text[0] === "Module:") {
        Mod = text[1].trim(); 
      } else if (text[0] === "Path:") {
        Path = text[1].trim();
      } else if (text[0] === "Software:") {
        Sw = text[1].trim();
      } else if (text[0] === "Firmware:") {
        Fw = text[1].trim();
      } else if (text[0] === "Plate ID") {
        header = text;
        header.forEach(function(x,j) {
          header[j] = x.trim().replace(/[()/.]/g,"").replace(/ /g,"_")
          if (/^\d/.test(header[j])) header[j] = "_" + header[j]
         })
      } else {                       //data line
         var rec = buildRecord(d);
         if (rec.sample_id != '' && rec.sample_id != undefined) {
           //rec.mod = Mod;  //don't really care about which nanodrop module was used.
           rec.path = Path;
           rec.nanodropver = Sw;
           rec.firmware = Fw;
           if (rec.units == 'ng/ul') {
             rec.units = 'ng/µl';
           }
           if (rec._3500 == undefined) { // if this field is missing, the buffer broke on this record.  It will return in the next.
             console.log(i, " Could not finish reading ", rec.sample_id, " and so dropping it")
           } else if (rec.a260 >0 && rec.conc > 0 && rec.a280 >0) {
             if (rec.sample_id in hash) {
                list.push(rec.sample_id)
                //console.log(rec)
               //throw new Error('Duplicate records in Nanodrop file: ' + rec.sample_id)
             } else {
               hash[rec.sample_id] = true
               c[iteration] = rec;
               iteration++
             }
           }
           rec = {}
         }
      }
    })
    buffer = parts[parts.length-1]
  })
  stream.addListener('end', function (error, data) {
    if (list.length >0) {
      callback(list)
    } else {
      callback(null, c)
    } 
  })
  

  function buildRecord(str){
    var record = {}
    str.split("\t").forEach(function(value, index){
      if(index <= header.length-1 && header[index] != '' && value != '')
        record[header[index].toLowerCase()] = value.trim().replace(/"/g, '')
    })
    return record
  }
};



exports.Tsvreader = Tsvreader;
