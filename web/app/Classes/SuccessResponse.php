<?php

namespace App\Classes;

use Response;


class SuccessResponse {

	public static function response($http_code, $message) {
		return Response::json([
			"http_code"     => $http_code,
			"message"       => $message,
		], $http_code);
	}
	
}