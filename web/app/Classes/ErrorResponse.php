<?php

namespace App\Classes;

use Response;

class ErrorResponse {

	public static function response($http_code, $error_message) {
		return Response::json([
			"http_code"     => $http_code,
			"error_message" => $error_message,
		], $http_code);
	}
	
}