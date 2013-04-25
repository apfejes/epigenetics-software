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

app.get('/', function(req, res){
    articleProvider.findAllProjects( function(error, docs1){
      res.render('index.jade', {title: 'Kobor Lab Lims', projects:docs1});
    })
});


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

app.get('/input/sample_new', function(req, res) {
    res.render('sample_new.jade', {title: 'New Sample'}
    );
});

app.post('/input/sample_new', function(req, res){
    articleProvider.save('samples', {
        sample_name: req.param('sample_name'),
    }, function( error, docs) {
        res.redirect('/')
    });
});


app.get('/view/:id', function(req, res) {
  articleProvider.getTransactions(req.params.id, function(error, transactions) {
    if (error) console.log("view/:id error: ", error)
    else articleProvider.findById(req.params.id, function(error, project) {
        res.render('project_details.jade',{proj_name: project.proj_name, project:project, transactions:transactions});
    });
   });
});

app.listen(3000);
console.log("Express server listening on port %d in %s mode", 27017, app.settings.env);
