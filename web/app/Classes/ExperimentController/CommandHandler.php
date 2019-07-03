<?php

namespace App\Classes\ExperimentController;

use App\Classes\SuccessResponse;


class CommandHandler {

    const PROVISIONER_MAIN = 'python /home/vagrant/openbenchmark/experiment_provisioner/main.py';
    const OV_GUARD_TIME    = 20; //A guard time in seconds for the nodes to start sending serial data before running OV


    function reserve_nodes($user_id, $scenario, $testbed, $async=true) {
        $action = "reserve";
        $cmd = self::PROVISIONER_MAIN . " --user-id=$user_id --action=$action --scenario=$scenario --testbed=$testbed > /dev/null";

        if ($async)
            $cmd .= " &";

        shell_exec($cmd);

        return SuccessResponse::response(200, $this->get_response_messages($action, $user_id));
    }

    function flash_firmware($user_id, $firmware, $async=true) {
        $action = "flash";
        $cmd = self::PROVISIONER_MAIN . " --user-id=$user_id --action=$action";
        
        if ($firmware != null)
            $cmd .= " --firmware=$firmware";

        $cmd .= " > /dev/null";

        if ($async)
            $cmd .= " &";

        shell_exec($cmd);

        return SuccessResponse::response(200, $this->get_response_messages($action, $user_id));
    }

    function start_ov($user_id, $scenario, $testbed, $simulator, $async=true) {
        $action = "ov-start";
        $cmd = self::PROVISIONER_MAIN . " --user-id=$user_id --action=ov-start --scenario=$scenario --testbed=$testbed";

        if ($simulator)
            $cmd .= " --simulator";

        $cmd .= " > /dev/null";

        if ($async)
            $cmd .= " &";

        shell_exec($cmd);

        return SuccessResponse::response(200, $this->get_response_messages($action, $user_id));
    }

    function exp_terminate($user_id) {
        $action = "terminate";
        $cmd = self::PROVISIONER_MAIN . " --user-id=$user_id --action=$action > /dev/null &";
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