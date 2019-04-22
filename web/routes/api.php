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

Route::get('/start-exp/{scenario}/{testbed}/{simulator?}/{firmware?}', 'ExperimentController@start');
Route::post('/firmware-upload', 'ExperimentController@upload');

//Individual routes for every action
Route::get('/reserve-nodes/{scenario}/{testbed}', 'ExperimentController@reserve_nodes');
Route::get('/flash-firmware/{firmware?}', 'ExperimentController@flash_firmware');
Route::get('/start-ov/{scenario}/{testbed}/{simulator?}', 'ExperimentController@start_ov');
Route::get('/exp-terminate', 'ExperimentController@exp_terminate');

//Scenario data retreival routes
Route::get('/general/{param}/{scenario?}/{testbed?}', 'ExperimentController@get_config_data');