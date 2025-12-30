<?php
include('../conn/conn.php');

$date = $_POST['date'];
$location = $_POST['location'];
$moments = $_POST['moments'];

$journalImageName = $_FILES['image']['name'];
$journalImageTmpName = $_FILES['image']['tmp_name'];

$target_dir = "../images/";
$target_file = $target_dir . basename($journalImageName);
$uploadOk = 1;
$imageFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));

// Check if image file is a valid image
$check = getimagesize($journalImageTmpName);
if($check === false) {
    $uploadOk = 0;
}

// Check if file already exists
if (file_exists($target_file)) {
    $uploadOk = 0;
}

// Check file size
if ($_FILES["image"]["size"] > 500000) {
    $uploadOk = 0;
}

// Allow only certain image formats
$allowedFormats = ["jpg", "jpeg", "png", "gif"];
if(!in_array($imageFileType, $allowedFormats)) {
    $uploadOk = 0;
}

// Check if $uploadOk is set to 0 by an error
if ($uploadOk == 0) {
    echo " 
    <script>
        alert('Sorry, your file was not uploaded.');
        window.location.href = http://localhost/travel-journal/write-journal.php;
    </script>
    ";
} else {
    if (move_uploaded_file($journalImageTmpName, $target_file)) {
        $journalImage = $journalImageName;

        $stmt = $conn->prepare("INSERT INTO `tbl_journal` (`tbl_journal_id`,`image`, `date`, `location`, `moments`) VALUES (NULL, :journalImage, :date, :location, :moments)");
        $stmt->bindParam(':journalImage', $journalImage);
        $stmt->bindParam(':date', $date);
        $stmt->bindParam(':location', $location);
        $stmt->bindParam(':moments', $moments);
        $stmt->execute();

        
        header("location: http://localhost/travel-journal/");

    } else {
        echo " 
        <script>
            alert('Sorry, there was an error uploading your file.');
            window.location.href = http://localhost/travel-journal/write-journal.php;
        </script>
        ";
    }
}
?>
