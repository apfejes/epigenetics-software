/**
 * Module dependencies.
 */

var express = require('express');
var ArticleProvider = require('./articleprovider-mongodb').ArticleProvider;
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
    articleProvider.save('projects', {
        proj_name: req.param('proj_name'),
        lab_contact: req.param('lab_contact'),
        col_name: req.param('col_name'),
        col_email: req.param('col_email'),
        sample_count: req.param('sample_count'),
        arrival_date: req.param('arrival_date'),
        role: req.param('role'),
        chip_run_date: req.param('chip_run_date')
    }, function( error, docs) {
      articleProvider.getIDbyName(req.param('proj_name'), function(error, id) {
        if (error) console.log("app.post.project_new", error)
        else res.redirect('/view/' + id[0]._id)
      });
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
    articleProvider.update('projects', req.params.id, {
        proj_name: req.param('proj_name'),
        lab_contact: req.param('lab_contact'),
        col_name: req.param('col_name'),
        col_email: req.param('col_email'),
        sample_count: req.param('sample_count'),
        arrival_date: req.param('arrival_date'),
        role: req.param('role'),
        chip_run_date: req.param('chip_run_date')
    }, function( error, docs) {
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
  articleProvider.getPlates(req.params.id, function(error, plates) {
    articleProvider.getTransactions(req.params.id, function(error, transactions) {
      if (error) console.log("view/:id error: ", error)
      else articleProvider.findById(req.params.id, function(error, project) {
          res.render('project_details.jade',{proj_name: project.proj_name, project:project, transactions:transactions, plates:plates});
      });
     });
  });
});

//app.get('/view/:id', function(req, res) {
//  articleProvider.getTransactions(req.params.id, function(error, transactions) {
//    if (error) console.log("view/:id error: ", error)
//    else articleProvider.findById(req.params.id, function(error, project) {
//        res.render('project_details.jade',{proj_name: project.proj_name, project:project, transactions:transactions});
//    });
//  });
//});



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
    articleProvider.save('transactions', {
        type: req.param('transaction'),
        amt: req.param('trans_amt'),
        date: req.param('trans_date'),
        projectid:req.params.id
    }, res.redirect('/view/' + req.params.id));
});


//------------------------------------
//  SAMPLE INFO:
//------------------------------------

app.get('/input/sample_new/:id', function(req, res) {
    res.render('sample_new.jade', {title: 'New Sample', projectid:req.params.id}
    );
});

app.post('/input/sample_new', function(req, res){
    articleProvider.save('samples', {
        sample_name: req.param('sample_name'),
    }, function( error, docs) {
        res.redirect('/')
    });
});


//------------------------------------
//  PLATE INFO:
//------------------------------------

app.get('/input/plate_new/:id', function(req, res) {
    res.render('plate_new.jade', {title: 'Add a Plate', projectid:req.params.id}
    );
});

app.post('/input/plate_new/:id', function(req, res){
    articleProvider.save('plates', {
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
        sec7_PB1: req.param('sec7_PB1'),
        projectid:req.params.id
    }, function( error, docs) {
      res.redirect('/view/' + req.params.id);
    });
});

// This function requires the Plate ID.

app.get('/input/plate_edit/:id', function(req, res){
  articleProvider.plateById(req.params.id, function(error, plate) {
    res.render('plate_edit.jade',{title: 'Edit Plate '+ req.params.id, plate:plate});
  });
});


// This function requires the Plate ID.

app.post('/input/plate_edit/:id', function(req, res){
    articleProvider.update('plates', req.param('plateid'), {
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
        sec7_PB1: req.param('sec7_PB1')
    }, function( error, docs) {
      res.redirect('/view/' + req.param('projectid'));
    });
});




app.post('/input/plate_new', function(req, res){
    articleProvider.save('plates', {
        plate_name: req.param('plate_name'),
    }, function( error, docs) {
        res.redirect('/')
    });
});

//------------------------------------
//  NANODROP INFO:
//------------------------------------

app.get('/input/nanodrop_new/:id', function(req, res) {
    res.render('nanodrop_new.jade', {title: 'Nanodrop File', projectid:req.params.id}
    );
});

app.post('/input/nanodrop_new/:id', function(req, res){
    
    
    
    
    articleProvider.save('samples', {
        sample_name: req.param('sample_name'),
    }, function( error, docs) {
        res.redirect('/')
    });
});





app.listen(3000, "0.0.0.0");
console.log("Express server listening on port %d in %s mode", 27017, app.settings.env);
