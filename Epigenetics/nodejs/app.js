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
    articleProvider.findAllProjects( function(error,docs1, docs2){
      res.render('index.jade', {title: 'Kobor Lab Lims', projects:docs1, samples:docs2});
    })
});


app.get('/input/project_new', function(req, res) {
    res.render('project_new.jade', {title: 'New Project'}
    );
});

app.post('/input/project_new', function(req, res){
    articleProvider.save('projects', {
        proj_name: req.param('proj_name'),
        col_name: req.param('col_name'),
        col_email: req.param('col_email'),
        sample_count: req.param('sample_count'),
        arrival_date: req.param('arrival_date'),
        role: req.param('role'),
        chip_run_date: req.param('chip_run_date')
    }, function( error, docs) {
        res.redirect('/')
    });
});


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
    articleProvider.findById(req.params.id, function(error, project) {
        res.render('project_details.jade',{proj_name: project.proj_name, project:project});
    });
});

//This piece of code is from the tutorial - left here for now as a code example.

//app.post('/blog/addComment', function(req, res) {
//    articleProvider.addCommentToArticle(req.param('_id'), {
//        person: req.param('person'),
//        comment: req.param('comment'),
//        created_at: new Date()
//       } , function( error, docs) {
//           res.redirect('/blog/' + req.param('_id'))
//       });
//});

app.listen(3000);
console.log("Express server listening on port %d in %s mode", 27017, app.settings.env);
