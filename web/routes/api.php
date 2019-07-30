<?php

use Illuminate\Http\Request;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/

Route::middleware('auth:api')->get('/user', function (Request $request) {
    return $request->user();
});

Route::get('/start/{scenario}/{testbed}/{simulator?}/{firmware?}', 'ExperimentController@start');
Route::post('/firmware-upload', 'ExperimentController@upload');

//Storing and getting the information for an experiment
Route::post('/store', 'ExperimentController@store_experiment');
Route::get('/experiment/{id}', 'ExperimentController@get_experiment');

//Individual routes for every action
Route::get('/reserve/{scenario}/{testbed}', 'ExperimentController@reserve');
Route::get('/flash/{testbed}/{firmware?}/{branch?}', 'ExperimentController@flash');
Route::get('/sut-start/{scenario}/{testbed}/{simulator?}', 'ExperimentController@sut_start');
Route::get('/terminate', 'ExperimentController@terminate');

//Scenario data retreival routes
Route::get('/general/{param}/{scenario?}/{testbed?}', 'ExperimentController@get_config_data');

//Routes for accessing scenario logs
Route::get('/logs/{action}/{experiment_id?}', 'LogsController@get');
Route::get('/download/{experiment_id}/{log_type}', 'LogsController@download');