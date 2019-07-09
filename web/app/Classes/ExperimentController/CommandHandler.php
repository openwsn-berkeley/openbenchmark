<?php

namespace App\Classes\ExperimentController;

use App\Classes\SuccessResponse;


class CommandHandler {

    const WORKING_DIR      = '/home/vagrant/openbenchmark';
    const PROVISIONER_MAIN = 'python openbenchmark.py';


    function reserve($user_id, $scenario, $testbed, $async=true) {
        $action = "reserve";
        $cmd = self::PROVISIONER_MAIN . " --user-id=$user_id --action=$action --scenario=$scenario --testbed=$testbed > /dev/null";

        if ($async)
            $cmd .= " &";

        return $this->_exec_action($action, $cmd, $user_id);
    }

    function flash($user_id, $firmware, $async=true) {
        $action = "flash";
        $cmd = self::PROVISIONER_MAIN . " --user-id=$user_id --action=$action";
        
        if ($firmware != null)
            $cmd .= " --firmware=$firmware";

        $cmd .= " > /dev/null";

        if ($async)
            $cmd .= " &";

        return $this->_exec_action($action, $cmd, $user_id);
    }

    function sut_start($user_id, $scenario, $testbed, $simulator, $async=true) {
        $action = "sut-start";
        $cmd = self::PROVISIONER_MAIN . " --user-id=$user_id --action=$action --scenario=$scenario --testbed=$testbed";

        if ($simulator)
            $cmd .= " --simulator";

        $cmd .= " > /dev/null";

        if ($async)
            $cmd .= " &";

        return $this->_exec_action($action, $cmd, $user_id);
    }

    function terminate($user_id) {
        $action = "terminate";
        $cmd = self::PROVISIONER_MAIN . " --user-id=$user_id --action=$action > /dev/null &";

        return $this->_exec_action($action, $cmd, $user_id);
    }

    private function _exec_action($action, $cmd, $user_id) {
        chdir(self::WORKING_DIR);
        shell_exec($cmd);
        return SuccessResponse::response(200, $this->get_response_messages($action, $user_id));
    }

    private function get_response_messages($action, $user_id) {
        return [
            "action" => $action,
            "broker" => "broker.mqttdashboard.com",
            "monitoring-topics" => [
                "step-notifications"  => "openbenchmark/$user_id/notifications",
                "debug-notifications" => "openbenchmark/$user_id/debug",
                "kpi-data"            => "openbenchmark/$user_id/kpi",
                "raw-data"            => "openbenchmark/$user_id/raw",
            ]
        ];
    } 

}