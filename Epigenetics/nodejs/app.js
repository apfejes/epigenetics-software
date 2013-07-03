/**
 * Module dependencies.
 */

var express = require('express');
var ArticleProvider = require('./articleprovider-mongodb').ArticleProvider;
var Tsvreader = require('./tsvreader.js').Tsvreader;
var ObjectID = require('mongodb').ObjectID;
var app = express();

// Configuration

app.configure(function(){
  app.set('views', __dirname + '/views');
  app.set('view engine', 'jade');
  app.use(express.bodyParser());
  app.use(express.methodOverride());
  app.use(require('stylus').middleware({ src: __dirname + '/public' }));
  app.use(app.router);
  app.use(express.static(__dirname + '/public'));
});

app.configure('development', function(){
  app.use(express.errorHandler({ dumpExceptions: true, showStack: true })); 
});

app.configure('production', function(){
  app.use(express.errorHandler()); 
});

var articleProvider = new ArticleProvider('localhost', 27017);
var tsvreader = new Tsvreader();

// Routes

//------------------------------------
//  HOME:
//------------------------------------

app.get('/', function(req, res){
    articleProvider.findAllProjects( function(error, docs1){
      res.render('index.jade', {title: 'Kobor Lab Lims', projects:docs1});
    })
});

//------------------------------------
//  PROJECT PAGES
//------------------------------------

app.get('/input/project_new', function(req, res) {
    articleProvider.project_status( function(error, docs) {
      if (error) console.log("app.get", error)
      else res.render('project_new.jade', {title: 'New Project', status:docs});
    })
});

app.post('/input/project_new', function(req, res){
    articleProvider.insertDB('projects', {
        proj_name: req.param('proj_name'),
        lab_contact: req.param('lab_contact'),
        col_name: req.param('col_name'),
        col_email: req.param('col_email'),
        sample_count: req.param('sample_count'),
        arrival_date: req.param('arrival_date'),
        role: req.param('role'),
        chip_run_date: req.param('chip_run_date')
    }, function( error, docs) {
      res.redirect('/view/' + docs[0]._id)
    });
});

app.get('/input/project_edit/:id', function(req, res){
  articleProvider.project_status( function(error, docs) {
    articleProvider.findById(req.params.id, function(error, project) {
      res.render('project_edit.jade',{title: 'Edit Project'+ project.proj_name, project:project, status:docs});
    });
  });
});

app.post('/input/project_edit/:id', function(req, res){
    console.log('updating project id: ', req.params.id)
    articleProvider.updateDB('projects', {_id:ObjectID.createFromHexString(req.params.id)}, 
       {$set: {proj_name: req.param('proj_name'),
        lab_contact: req.param('lab_contact'),
        col_name: req.param('col_name'),
        col_email: req.param('col_email'),
        sample_count: req.param('sample_count'),
        arrival_date: req.param('arrival_date'),
        role: req.param('role'),
        chip_run_date: req.param('chip_run_date') }
    }, false,
    function( error, docs) {
      articleProvider.getIDbyName(req.param('proj_name'), function(error, id) {
        if (error) console.log("app.post.project_new", error)
        else res.redirect('/view/' + req.params.id)
      });
    });
});


    //----
    // Function for viewing a project overview
    //----

app.get('/view/:id', function(req, res) {

  articleProvider.getNanodrop(req.params.id, function(error, nanodrops) {
    articleProvider.getPlates(req.params.id, function(error, plates) {
      articleProvider.getTransactions(req.params.id, function(error, transactions) {
        articleProvider.getSamples(req.params.id, function(error, samples) {
          if (error) console.log("view/:id error: ", error)
          else articleProvider.findById(req.params.id, function(error, project) {
              res.render('project_details.jade',{proj_name: project.proj_name, 
                  project:project, transactions:transactions, plates:plates,
                  samples:samples, nanodrops:nanodrops});
          });
        });
      });
    });
  });
});

//------------------------------------
//  Bisulfite Sequencing
//------------------------------------

app.get('/input/bs_new/:id', function(req, res) {
  articleProvider.getSamples(req.params.id, function(error, samples) {
    if (error) console.log("sample_spreadsheet/:id (get) error: ", error)
    else 
      res.render('bs_new.jade', {samples:samples, projectid:req.params.id});
  })
});

app.post('/input/bs_new/:id', function(req, res){
  switch(req.param('step')) {
    case '0':
      articleProvider.process_Array(req.body, function(error, unassigned) {
        res.render('bs_step1.jade', {unassigned:JSON.stringify(unassigned)});
        //console.log("stringified:", JSON.stringify(unassigned));
      });
      break;
    case '1':
      articleProvider.reserve_array(req.body, function(reserved) {
        articleProvider.count_samples(JSON.parse(req.param('unassigned')), function(count) { //number of samples
          articleProvider.assign_to_bs_plate(reserved, JSON.parse(req.param('unassigned')), function(layout) {
            console.log("layout ", JSON.stringify(layout))
            res.render('bs_step2.jade',{count:count, layout:layout, layout_store:JSON.stringify(layout)});
          });
        });
      });
      break;
    case '2':  //assign to database.
      articleProvider.saveBSPlacement(req.param('layout_store'), req.params.id, function(plateid) {
        res.redirect('/input/bsplate_edit/' + plateid);
      });
      break
    default:
      res.redirect('/');
  }
});

//------------------------------------
//  PAYMENT INFO:
//------------------------------------

app.get('/input/payment_new/:id', function(req, res) {
    articleProvider.transaction_type( function(error, docs) {
      if (error) console.log("app.get.payment_new", error)
      else res.render('payment_new.jade', {title: 'Add a Payment Transaction', trtype:docs, projectid:req.params.id});
    })
});

app.post('/input/payment_new/:id', function(req, res){
    articleProvider.insertDB ('transactions', {
        type: req.param('transaction'),
        amt: req.param('trans_amt'),
        date: req.param('trans_date'),
        projectid:req.params.id
    }, function(error, docs) {
      if (error) console.log("app.get.payment_new", error)
      else res.redirect('/view/' + req.params.id);
    })
});


//------------------------------------
//  SAMPLE INFO:
//------------------------------------

app.get('/input/sample_new/:id', function(req, res) {
    res.render('sample_new.jade', {title: 'New Sample', projectid:req.params.id}
    );
});

app.post('/input/sample_new/:id', function(req, res){
    tsvreader.parseSimple(req.files.sample_file.path, function(error, data) {
      if (error) console.log("app.get.sample_new (post)", error)
      else {
        articleProvider.saveSamples(data, req.param('projectid'),function(error, docs){
          if (error) console.log("app.get.sample_new (post_save)", error)
          else {
          res.redirect('/view/' + req.param('projectid'));
          }
        })
      }
    });
});

// This function requires the Sample ID.

app.get('/view/sample_edit/:id', function(req, res){
  var id = req.params.id
  var sam = id.substring(0, id.indexOf("-"))
  var num = id.substring(id.indexOf("-")+1)
  articleProvider.sampleById(sam, num, function(error, samples) {
    res.render('sample_edit.jade',{title: 'View Sample Details: '+ sam + '-' + num, samples:samples});
  });
});

app.get('/view/sample_spreadsheet/:id', function(req, res){
  articleProvider.getSamples(req.params.id, function(error, samples) {
    if (error) console.log("sample_spreadsheet/:id (get) error: ", error)
    else res.render('sample_spreadsheet.jade',{samples:samples});
  });
});

app.post('/view/sample_spreadsheet/:id', function(req, res){
  //console.log(req.param('step'))
  switch(req.param('step')) {
    case '0':
      articleProvider.process_Array(req.body, function(error, data) {
        res.render('array_step1.jade',{data:JSON.stringify(data)});
      });
      break;
    case '1':
      //console.log("dataset:", JSON.parse(req.param('data')))
      articleProvider.reserve_array(req.body, function(layout) {
        articleProvider.count_samples(JSON.parse(req.param('data')), function(count) { //number of samples
          articleProvider.parse_manual(JSON.parse(req.param('data')), function(list) {  //number of manual entries to process.
            res.render('array_step2.jade',{count:count, list:list, layout:layout, layout_store:JSON.stringify(layout), data:req.param('data')});
          });
        });
      });
      break;
    case '2':
      articleProvider.manual_array(req.body, function(layout) {
        var old_layout = JSON.parse(req.param('layout_store'));
        for (var attrname in old_layout) {  
          layout[attrname] = old_layout[attrname];
        }
        //console.log("layout: step 2", layout);
        articleProvider.parse_inter_chip(JSON.parse(req.param('data')), function(inter_chip_list) {
          articleProvider.parse_intra_chip(JSON.parse(req.param('data')), function(intra_chip_list) {
            articleProvider.parse_random(JSON.parse(req.param('data')), function(random_list) {
              articleProvider.assign_to_chips(req.param('chips'), layout, inter_chip_list, intra_chip_list, random_list, function(assigned) {
                res.render('array_step3.jade',{chips:req.param('chips'), layout:layout, assigned:assigned, assigned_store:JSON.stringify(assigned)});
              })
            })
          })
        })
      });
      break;
    case '3':
      //console.log("assigned_store:",req.param('assigned_store')) 
      articleProvider.savePlacement(req.param('assigned_store'), req.params.id, function(plateid) {
        res.redirect('/input/plate_edit/' + plateid);
      });
      break;
    default:
      res.redirect('/');
  }
});


app.get('/view/sample_spreadsheet_edit/:id', function(req, res){
  articleProvider.getSamples(req.params.id, function(error, samples) {
    if (error) console.log("sample_spreadsheet/:id error: ", error)
    else res.render('sample_spreadsheet_edit.jade',{samples:samples});
  });
});

app.post('/view/sample_spreadsheet_edit/:id', function(req, res){
  //console.log("request body", req.body);
  articleProvider.process_sample_spreadsheet('samples', req.params.id, req.body, function( error, docs) {
    articleProvider.getIDbyName(req.param('proj_name'), function(error, id) {
      if (error) console.log("app.post.sample_spreadsheet", error)
      else res.redirect('/view/' + req.params.id)
    });
  });
});
//------------------------------------
//  Bisulfite PLATE INFO:
//------------------------------------

// This function requires the BS Plate ID.

app.get('/input/bsplate_edit/:id', function(req, res){
  articleProvider.bsplateById(req.params.id, function(error, bsplate) {
    console.log("BSPLATE:", bsplate)
    res.render('bsplate_edit.jade',{title: 'Edit Plate', bsplate:bsplate});
  });
});


//------------------------------------
//  PLATE INFO:
//------------------------------------

// This function requires the Plate ID.

app.get('/input/plate_edit/:id', function(req, res){
  articleProvider.plateById(req.params.id, function(error, plate) {
    res.render('plate_edit.jade',{title: 'Edit Plate', plate:plate});
  });
});


// This function requires the Plate ID.

app.post('/input/plate_edit/:id', function(req, res){
    articleProvider.updateDB('plates', {_id:ObjectID.createFromHexString(req.param('plateid'))}, 
       {$set: {barcode: req.param('barcode'),
        sec1_operator: req.param('sec1_operator'),
        sec1_date: req.param('sec1_date'),
        sec2_operator: req.param('sec2_operator'),
        sec2_date: req.param('sec2_date'),
        sec2_oven_start: req.param('sec2_oven_start'),
        sec2_oven_stop: req.param('sec2_oven_stop'),
        sec2_plate_bc: req.param('sec2_plate_bc'),
        sec2_MA1_1: req.param('sec2_MA1_1'),
        sec2_MA1_2: req.param('sec2_MA1_2'),
        sec2_RMP_1: req.param('sec2_RMP_1'),
        sec2_RMP_2: req.param('sec2_RMP_2'),
        sec2_MSM_1: req.param('sec2_MSM_1'),
        sec2_MSM_2: req.param('sec2_MSM_2'),
        sec3_operator: req.param('sec3_operator'),
        sec3_date: req.param('sec3_date'),
        sec3_vortex: req.param('sec3_vortex'),
        sec3_hb_start: req.param('sec3_hb_start'),
        sec3_hb_stop: req.param('sec3_hb_stop'),
        sec3_FMS_1: req.param('sec3_FMS_1'),
        sec3_FMS_2: req.param('sec3_FMS_2'),
        sec4_operator: req.param('sec4_operator'),
        sec4_date: req.param('sec4_date'),
        sec4_vortex: req.param('sec4_vortex'),
        sec4_hb_start: req.param('sec4_hb_start'),
        sec4_hb_stop: req.param('sec4_hb_stop'),
        sec4_in_start: req.param('sec4_in_start'),
        sec4_in_stop: req.param('sec4_in_stop'),
        sec4_cen_start: req.param('sec4_cen_start'),
        sec4_cen_stop: req.param('sec4_cen_stop'),
        sec4_dry_start: req.param('sec4_dry_start'),
        sec4_dry_stop: req.param('sec4_dry_stop'),
        sec4_2pol_open: req.param('sec4_2pol_open'),
        sec4_PM1_1: req.param('sec4_PM1_1'),
        sec4_PM1_2: req.param('sec4_PM1_2'),
        sec5_operator: req.param('sec5_operator'),
        sec5_date: req.param('sec5_date'),
        sec5_ovn_start: req.param('sec5_ovn_start'),
        sec5_ovn_stop: req.param('sec5_ovn_stop'),
        sec5_RA1: req.param('sec5_RA1'),
        sec6_operator: req.param('sec6_operator'),
        sec6_date: req.param('sec6_date'),
        sec6_vortex: req.param('sec6_vortex'),
        sec6_hb_start: req.param('sec6_hb_start'),
        sec6_hb_stop: req.param('sec6_hb_stop'),
        sec6_ovn_start: req.param('sec6_ovn_start'),
        sec6_ovn_stop: req.param('sec6_ovn_stop'),
        sec6_PB2: req.param('sec6_PB2'),
        sec7_operator: req.param('sec7_operator'),
        sec7_date: req.param('sec7_date'),
        sec7_PB1: req.param('sec7_PB1')}
    }, false, function( error, docs) {
      res.redirect('/view/' + req.param('projectid'));
    });
});

// This function requires the Plate ID.

app.get('/input/plate_spreadsheet/:id', function(req, res){
  articleProvider.plateById(req.params.id, function(error, plates) {
    articleProvider.sampleByPlateId(req.params.id, function(error, samples) {
      res.render('plate_spreadsheet.jade',{title: 'Edit Plate', samples:samples, plates:plates});
    });
  });
});

//------------------------------------
//  NANODROP INFO:
//------------------------------------

app.get('/input/nanodrop_new/:id', function(req, res) {
  articleProvider.nanodrop_types( function(error, docs) {
    res.render('nanodrop_new.jade', {title: 'Add a Nanodrop File to this project', projectid:req.params.id, status:docs}
    );
  })
});

app.post('/input/nanodrop_new/:id', function(req, res) {
    tsvreader.parseNanodropFile(req.files.nanodrop_file.path, function(error, data) {
      if (error) {
        console.log("app.get.nanodrop_new (post)", error)
        res.render('nanodrop_error.jade',{error:error});
      } else {
        articleProvider.saveNanodrop(data,req.files.nanodrop_file.name, req.param('projectid'), req.param('nd_type'), function(error, docs){
          if (error) { 
            console.log("app.get.nanodrop_new (post_save)", error)
            res.render('nanodrop_error.jade',{error:error});
          } else {
            res.redirect('/view/' + req.param('projectid'));
          }
        })
      }
    });
});


app.listen(3000, "0.0.0.0");
console.log("Express server listening on port %d in %s mode", 27017, app.settings.env);
