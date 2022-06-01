<?php
// $servername = "139.162.39.94";
// $dbname = "smartfarm";
// $username = "root";
// $password = "root";

$servername = "139.162.39.94:3306";
$dbname = "smartfarm";
$username = "root";
$password = "root";

$iot_farmname = $voltage = $iot_temp = $iot_humid = $iot_ph = $iot_light = $heatindex = "";

if ($_SERVER["REQUEST_METHOD"] == "GET") { // GET request method for insert into sql

    $iot_farmname = test_input($_GET["iot_farmname"]);
    $iot_humid = test_input($_GET["iot_humid"]);
    $voltage = test_input($_GET["voltage"]);
    $iot_temp = test_input($_GET["iot_temp"]);
    $iot_ph = test_input($_GET["iot_ph"]);
    $iot_light = test_input($_GET["iot_light"]);
    $heatindex = test_input($_GET["heatindex"]);
    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    $sql = "INSERT INTO farm_iot (iot_farmname, iot_humid, voltage, iot_temp, iot_ph, iot_light, heatindex)
        VALUES ('" . $iot_farmname . "', '" . $iot_humid . "', '" . $voltage . "', '" . $iot_temp . "', '" . $iot_ph . "', '" . $iot_light . "', '" . $heatindex . "')";

    if ($conn->query($sql) === TRUE) {
        echo "New record created successfully";
    } else {
        echo "Error: " . $sql . "<br>" . $conn->error;
    }

    $conn->close();
} else if ($_SERVER["REQUEST_METHOD"] == "POST") {// GET request controller from server

    if (empty($_POST["iot_farmname"])){
        echo "No data At all, Sadge.";
        exit;
    }

    $iot_farmname = test_input($_POST["iot_farmname"]);
    $search=urldecode($iot_farmname);
    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    $sql = "SELECT * FROM farm_controller WHERE iot_farmname = '" . $iot_farmname . "'";

    $result = $conn->query($sql);
    $data = $result->fetch_assoc();

    echo $data['light'] . ' ';
    echo $data['fan'] . ' ';
    echo $data['heatlight'] . ' ';
    echo $data['fog'] . ' ';
    echo $data['phlow'] . ' ';
    echo $data['phhigh'];

    $conn->close();
} else {
    echo "No data At all, Sadge.";
}

function test_input($data)
{
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}
