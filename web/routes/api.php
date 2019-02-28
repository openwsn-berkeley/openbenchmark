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

Route::get('/start-exp', 'ExperimentController@start');
Route::get('/terminate-exp', 'ExperimentController@exp_terminate');
Route::post('/firmware-upload', 'ExperimentController@upload');

//Test routes
Route::get('/reserve-exp', 'ExperimentController@reserve_exp');
Route::get('/start-otbox', 'ExperimentController@start_otbox');
Route::get('/start-ov', 'ExperimentController@start_ov');
Route::get('/start-watcher', 'ExperimentController@start_watcher');

Route::get('/scenarios', 'ExperimentController@get_scenarios');
