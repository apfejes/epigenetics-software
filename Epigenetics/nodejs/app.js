/**
 * Module dependencies.
 */

var express = require('express');
var ArticleProvider = require('./articleprovider-mongodb').ArticleProvider;
var Tsvreader = require('./tsvreader.js').Tsvreader;
var ObjectID = require('mongodb').ObjectID;
var app = express();
var passport = require('passport'),
    LocalStrategy = require('passport-local').Strategy;
var port = 3000;

// Configuration

app.configure(function(){
  app.use(express.static(__dirname + '/public'));
  app.use(express.cookieParser());
  app.use(express.bodyParser());
  app.use(express.session({ secret: 'lims session' }));
  app.use(passport.initialize());
  app.use(passport.session());
  app.set('views', __dirname + '/views');
  app.set('view engine', 'jade');
  app.use(express.methodOverride());
  app.use(require('stylus').middleware({ src: __dirname + '/public' }));
  app.use(app.router);

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
//  PASSPORT authentication
//------------------------------------


passport.use(new LocalStrategy(
	function (username, password, callback) {
	  articleProvider.localstrategy(username, password, callback);
  }
));

passport.serializeUser(function(user, done) {
  done(null, user._id);
});

passport.deserializeUser(function(id, done) {
  articleProvider.deserialize(id, done);
});


app.post('/login', passport.authenticate('local', { successRedirect: '/',
                                                    failureRedirect: '/login',
                                                    failureFlash: 'Invalid user name or password.' }));
                                                    
app.get('/login', function(req, res){
  res.render('login.jade', {title: 'Kobor Lab Lims - login'});
});


//------------------------------------
//  HOME:
//------------------------------------

app.get('/', ensureAuthenticated, function(req, res){
    articleProvider.findAllProjects( function(error, docs1){
      res.render('index.jade', {title: 'Kobor Lab Lims', projects:docs1});
    })
});

//------------------------------------
//  PROJECT PAGES
//------------------------------------

app.get('/input/project_new', ensureAuthenticated, function(req, res) {
    articleProvider.project_status( function(error, docs) {
      if (error) console.log("app.get", error)
      else res.render('project_new.jade', {title: 'New Project', status:docs});
    })
});

app.post('/input/project_new', ensureAuthenticated, function(req, res){
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

app.get('/input/project_edit/:id', ensureAuthenticated, function(req, res){
  articleProvider.project_status( function(error, docs) {
    articleProvider.findById(req.params.id, function(error, project) {
      res.render('project_edit.jade',{title: 'Edit Project'+ project.proj_name, project:project, status:docs});
    });
  });
});

app.post('/input/project_edit/:id', ensureAuthenticated, function(req, res){
    //console.log('updating project id: ', req.params.id)
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

app.get('/view/:id', ensureAuthenticated, function(req, res) {
  articleProvider.getNanodrop(req.params.id, function(error, nanodrops) {
    articleProvider.getPlates(req.params.id, function(error, plates) {
      articleProvider.getBsPlates(req.params.id, function(error, bsplates) {
        articleProvider.getTransactions(req.params.id, function(error, transactions) {
          articleProvider.getSamples(req.params.id, function(error, samples) {
            if (error) console.log("view/:id error: ", error)
            else articleProvider.findById(req.params.id, function(error, project) {
                res.render('project_details.jade',{proj_name: project.proj_name, 
                    project:project, transactions:transactions, plates:plates,
                    samples:samples, nanodrops:nanodrops, bsplates:bsplates});
            });
          });
        });
      });
    });
  });
});

//------------------------------------
//  Bisulfite Sequencing
//------------------------------------


// This function requires the Plate ID.

app.get('/input/bs_spreadsheet/:id', ensureAuthenticated, function(req, res){
  articleProvider.bsplateById(req.params.id, function(error, bsplates) {
    articleProvider.sampleByBsPlateId(req.params.id, function(error, samples) {
      res.render('bs_spreadsheet.jade',{title: 'Edit Plate', samples:samples, bsplates:bsplates});
    });
  });
});



app.get('/input/bs_new/:id', ensureAuthenticated, function(req, res) {
  articleProvider.getSamples(req.params.id, function(error, samples) {
    if (error) console.log("sample_spreadsheet/:id (get) error: ", error)
    else
      res.render('bs_new.jade', {samples:samples, projectid:req.params.id});
  })
});

app.post('/input/bs_new/:id', ensureAuthenticated, function(req, res){
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
            //console.log("layout ", JSON.stringify(layout))
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

app.get('/input/payment_new/:id', ensureAuthenticated, function(req, res) {
    articleProvider.transaction_type( function(error, docs) {
      if (error) console.log("app.get.payment_new", error)
      else res.render('payment_new.jade', {title: 'Add a Payment Transaction', trtype:docs, projectid:req.params.id});
    })
});

app.post('/input/payment_new/:id', ensureAuthenticated, function(req, res){
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

app.get('/input/sample_new/:id', ensureAuthenticated, function(req, res) {
    res.render('sample_new.jade', {title: 'New Sample', projectid:req.params.id}
    );
});

app.post('/input/sample_new/:id', ensureAuthenticated, function(req, res){
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

app.get('/view/sample_edit/:id', ensureAuthenticated, function(req, res){
  var id = req.params.id
  var sam = id.substring(0, id.indexOf("-"))
  var num = id.substring(id.indexOf("-")+1)
  articleProvider.sampleById(sam, num, function(error, samples) {
    res.render('sample_edit.jade',{title: 'View Sample Details: '+ sam + '-' + num, samples:samples});
  });
});

app.get('/view/sample_spreadsheet/:id', ensureAuthenticated, function(req, res){
  articleProvider.getSamples(req.params.id, function(error, samples) {
    if (error) console.log("sample_spreadsheet/:id (get) error: ", error)
    else res.render('sample_spreadsheet.jade',{samples:samples});
  });
});

app.post('/view/sample_spreadsheet/:id', ensureAuthenticated, function(req, res){
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


app.get('/view/sample_spreadsheet_edit/:id', ensureAuthenticated, function(req, res){
  articleProvider.getSamples(req.params.id, function(error, samples) {
    if (error) console.log("sample_spreadsheet/:id error: ", error)
    else res.render('sample_spreadsheet_edit.jade',{samples:samples});
  });
});

app.post('/view/sample_spreadsheet_edit/:id', ensureAuthenticated, function(req, res){
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

app.get('/input/bsplate_edit/:id', ensureAuthenticated, function(req, res){
  articleProvider.bsplateById(req.params.id, function(error, bsplate) {
    //console.log("BSPLATE:", bsplate)
    res.render('bsplate_edit.jade',{title: 'Edit Plate', bsplate:bsplate});
  });
});

// This function requires the Plate ID.

app.get('/input/bsplate_spreadsheet/:id', ensureAuthenticated, function(req, res){
  articleProvider.bsplateById(req.params.id, function(error, bsplates) {
    articleProvider.sampleByBsPlateId(req.params.id, function(error, samples) {
      res.render('bs_spreadsheet.jade',{title: 'Edit Plate', samples:samples, bsplates:bsplates});
    });
  });
});



//------------------------------------
//  PLATE INFO:
//------------------------------------

// This function requires the Plate ID.

app.get('/input/plate_edit/:id', ensureAuthenticated, function(req, res){
  articleProvider.plateById(req.params.id, function(error, plate) {
    res.render('plate_edit.jade',{title: 'Edit Plate', plate:plate});
  });
});


// This function requires the Plate ID.

app.post('/input/plate_edit/:id', ensureAuthenticated, function(req, res){
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
        sec2_MA1_1_lot: req.param('sec2_MA1_1_lot'),
        sec2_MA1_2_lot: req.param('sec2_MA1_2_lot'),
        sec2_RMP_1_lot: req.param('sec2_RMP_1_lot'),
        sec2_RMP_2_lot: req.param('sec2_RMP_2_lot'),
        sec2_MSM_1_lot: req.param('sec2_MSM_1_lot'),
        sec2_MSM_2_lot: req.param('sec2_MSM_2_lot'),
        sec3_operator: req.param('sec3_operator'),
        sec3_date: req.param('sec3_date'),
        sec3_vortex: req.param('sec3_vortex'),
        sec3_hb_start: req.param('sec3_hb_start'),
        sec3_hb_stop: req.param('sec3_hb_stop'),
        sec3_FMS_1: req.param('sec3_FMS_1'),
        sec3_FMS_2: req.param('sec3_FMS_2'),
        sec3_FMS_1_lot: req.param('sec3_FMS_1_lot'),
        sec3_FMS_2_lot: req.param('sec3_FMS_2_lot'),
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
        sec4_PM1_1_lot: req.param('sec4_PM1_1_lot'),
        sec4_PM1_2_lot: req.param('sec4_PM1_2_lot'),
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
        sec6_PB2_lot: req.param('sec6_PB2_lot'),
        sec7_operator: req.param('sec7_operator'),
        sec7_date: req.param('sec7_date'),
        sec7_PB1: req.param('sec7_PB1'),
        sec7_PB1_lot: req.param('sec7_PB1_lot'),
        sec8_operator: req.param('sec8_operator'),
        sec8_date: req.param('sec8_date'),
        sec8_RA1: req.param('sec8_RA1'),
        sec8_XC3: req.param('sec8_XC3'),
        sec8_XC1: req.param('sec8_XC1'),
        sec8_XC2_1: req.param('sec8_XC2_1'),
        sec8_XC2_2: req.param('sec8_XC2_2'),
        sec8_STM_1: req.param('sec8_STM_1'),
        sec8_STM_2: req.param('sec8_STM_2'),
        sec8_TEM_1: req.param('sec8_TEM_1'),
        sec8_TEM_2: req.param('sec8_TEM_2'),
        sec8_ATM_1: req.param('sec8_ATM_1'),
        sec8_ATM_2: req.param('sec8_ATM_2'),
        sec8_XC4: req.param('sec8_XC4'),
        sec8_PB1: req.param('sec8_PB1'),
        sec8_RA1_lot: req.param('sec8_RA1_lot'),
        sec8_XC3_lot: req.param('sec8_XC3_lot'),
        sec8_XC1_lot: req.param('sec8_XC1_lot'),
        sec8_XC2_1_lot: req.param('sec8_XC2_1_lot'),
        sec8_XC2_2_lot: req.param('sec8_XC2_2_lot'),
        sec8_STM_1_lot: req.param('sec8_STM_1_lot'),
        sec8_STM_2_lot: req.param('sec8_STM_2_lot'),
        sec8_TEM_1_lot: req.param('sec8_TEM_1_lot'),
        sec8_TEM_2_lot: req.param('sec8_TEM_2_lot'),
        sec8_ATM_1_lot: req.param('sec8_ATM_1_lot'),
        sec8_ATM_2_lot: req.param('sec8_ATM_2_lot'),
        sec8_XC4_lot: req.param('sec8_XC4_lot'),
        sec8_PB1_lot: req.param('sec8_PB1_lot')}
    }, false, function( error, docs) {
      res.redirect('/view/' + req.param('projectid'));
    });
});

// This function requires the Plate ID.

app.get('/input/plate_spreadsheet/:id', ensureAuthenticated, function(req, res){
  articleProvider.plateById(req.params.id, function(error, plates) {
    articleProvider.sampleByPlateId(req.params.id, function(error, samples) {
      res.render('plate_spreadsheet.jade',{title: 'Edit Plate', samples:samples, plates:plates});
    });
  });
});

//------------------------------------
//  NANODROP INFO:
//------------------------------------

app.get('/input/nanodrop_new/:id', ensureAuthenticated, function(req, res) {
  articleProvider.nanodrop_types( function(error, docs) {
    res.render('nanodrop_new.jade', {title: 'Add a Nanodrop File to this project', projectid:req.params.id, status:docs}
    );
  })
});

app.post('/input/nanodrop_new/:id', ensureAuthenticated, function(req, res) {
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

// Simple route middleware to ensure user is authenticated.
//   Use this route middleware on any resource that needs to be protected.  If
//   the request is authenticated (typically via a persistent login session),
//   the request will proceed.  Otherwise, the user will be redirected to the
//   login page.
function ensureAuthenticated(req, res, next) {
  if (req.isAuthenticated()) { return next(); }
  res.redirect('/login')
}


//------------------------------------
//  Yeast Chip-Chip :
//------------------------------------

app.get('/input/cc_view_all', ensureAuthenticated, function(req, res) {
  articleProvider.yeast_samples(function(error, samples) {
    if (error) {
      console.log("app.get.nanodrop_new (post)", error)
    } else {
       res.render('cc_all.jade', {samples:samples});
    }
  })
});

app.get('/input/cc_new', ensureAuthenticated, function(req, res) {
  res.render('cc_new.jade', {title: 'ChIP-chip data'});
  
  // not needed at the moment, but this is where to find 
  // the source code for processing cel files:
  //
  // http://biopython.org/DIST/docs/api/Bio.Affy.CelFile-pysrc.html
  //
  //------------------------------
  
});

app.post('/input/cc_new', ensureAuthenticated, function(req, res){
    articleProvider.insertyeastDB ('samples', {
        researcher: req.param('researcher'),
        crosslinkingtime: req.param('crosslinkingtime'),
        protocol: req.param('protocol'),
        arraylotnumber: req.param('arraylotnumber'),
        antibody: req.param('antibody'),
        arraytype: req.param('arraytype'),
        type: req.param('type'),
        antibodyvolume: req.param('antibodyvolume'),
        pubmedid: req.param('pubmedid'),
        catalognumber: req.param('catalognumber'),
        cel_file: req.param('cel_file'),
        strainnumber: req.param('strainnumber'),
        strainbackground: req.param('strainbackground'),
        comments: req.param('comments'),
        date: req.param('date')
    }, function(error, docs) {
      if (error) console.log("app.get.cc_new", error)
      else res.redirect('/input/cc_details/' + req.params.id);
    })
});

  //requires the chip-chip-sample id.

app.get('/input/cc_details/:id', ensureAuthenticated, function(req, res){
  articleProvider.project_status( function(error, docs) {
    articleProvider.findchipById(req.params.id, function(error, chipchip) {
      res.render('cc_details.jade',{title: 'View chip-chip', chipchip:chipchip, status:docs});
    });
  });
});


  //requires the chip-chip-sample id.
  
app.get('/input/cc_edit/:id', ensureAuthenticated, function(req, res){
  articleProvider.project_status( function(error, docs) {
    articleProvider.findchipById(req.params.id, function(error, chipchip) {
      res.render('cc_edit.jade',{title: 'Edit chip-chip', chipchip:chipchip, status:docs});
    });
  });
});


  //requires the chip-chip-sample id.

app.post('/input/cc_edit/:id', ensureAuthenticated, function(req, res){
    articleProvider.updateyeastDB ('samples', {_id:ObjectID.createFromHexString(req.params.id)},
      {$set: {researcher: req.param('researcher'),
        crosslinkingtime: req.param('crosslinkingtime'),
        protocol: req.param('protocol'),
        arraylotnumber: req.param('arraylotnumber'),
        antibody: req.param('antibody'),
        arraytype: req.param('arraytype'),
        type: req.param('type'),
        antibodyvolume: req.param('antibodyvolume'),
        pubmedid: req.param('pubmedid'),
        catalognumber: req.param('catalognumber'),
//        cel_file: req.param('cel_file'),
        strainnumber: req.param('strainnumber'),
        strainbackground: req.param('strainbackground'),
        comments: req.param('comments'),
        date: req.param('date')}
      }, false,
      function(error, docs) {
        if (error) console.log("app.get.cc_edit", error)
        else res.redirect('/input/cc_details/' + req.params.id);
      })
});



app.listen(port, "0.0.0.0");
console.log("Express server listening on port %d in %s mode", port, app.settings.env);
