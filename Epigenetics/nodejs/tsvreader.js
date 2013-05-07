var fs = require('fs')
var sys = require('sys')
 
 
//_____________________________________________________
//
// This file is based on a script provided at 
// https://gist.github.com/jamescarr/467954#file-gistfile1-js
//
// You will need to call the function something like: 
//    parseCsvFile('tremors.txt', function(rec){
//      sys.puts("An tremor of magnitude " + rec.magnitude + " in " + rec.region)
//    });
//
//_____________________________________________________

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



Tsvreader.prototype.parseTsvFile = function(files, callback){
  //console.log("files:", files)
  //console.log("files.nanodrop_file:", files.nanodrop_file)
  var c = new Array()
  var stream = fs.createReadStream(files.nanodrop_file.path)
  var iteration = 0, header = [], buffer = ""
  stream.addListener('data', function(data){
    buffer+=data.toString()
    var parts = buffer.split('\r\n')
    parts.forEach(function(d, i){
      if(i == parts.length-1) return
      if(iteration++ == 0 && i == 0){
        header = d.split("\t")
        c[0] = header
      }else{
         c[iteration-1] = clean(d.split("\t"), '')
      }
    })
    for (var i = 0; i < c.length; i++) {
      console.log("c[%i]: %s", i, c[i])
    }
    buffer = parts[parts.length-1]
  })
  callback(null, c)
};

exports.Tsvreader = Tsvreader;
