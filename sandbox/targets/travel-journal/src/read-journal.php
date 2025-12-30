<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travel Journal</title>

    <!-- Boostrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">

    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500&display=swap');

        * {
            margin: 0;
            padding: 0;
            font-family: 'Poppins', sans-serif;
        }

        body {
            background-image: url('https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            overflow: hidden;
        }

        .main {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .read-journal-container {
            background-color: rgba(250, 250, 250, 0.8);
            padding: 50px;
            border-radius: 20px;
            width: 1200px;
            height: 750px;
            position: relative;
        }
        
        .read-journal-container > h1 {
            font-size: 45px;
            color: rgb(50, 50, 50);
            text-shadow: 4px 4px rgb(200, 200, 200);
            text-align: center;
        }

        .journals {
            display: flex;
            flex-wrap: wrap;
            overflow: auto;
        }
        
        .card {
            margin: 10px;
            color: rgb(255, 255, 255);
            border: none;
        }

        .back-button {
            position: absolute;
            bottom: 30px;
            right: 30px ;
        }

        .modal-content {
            margin-top: 40%;
        }
    </style>

</head>
<body>

<div class="main">

    <div class="read-journal-container">
        <h1>Read your memorable travels.</h1>

        <div class="journals">
            <?php 
                            
                include('./conn/conn.php');
    
                $stmt = $conn->prepare("SELECT * FROM `tbl_journal`");
                $stmt->execute();
    
                $result = $stmt->fetchAll();
    
                foreach($result as $row) {
                    $journalID = $row['tbl_journal_id'];
                    $image = $row['image'];
                    $date = $row['date'];
                    $moments = $row['moments'];
                    $location = $row['location'];
                    ?>
    
    
                <div class="card" style="width: 15rem; background-color:rgba(50,50,50,0.6);" >
                    <img src="images/<?= $image ?>" class="card-img-top" alt="..." style="height:150px;">
                    <div class="card-body">
                        <h5 class="card-title" id="location-<?= $journalID ?>"><?= $location ?></h5>
                        <small id="date-<?= $journalID ?>"><?= $date ?></small>
                        <small hidden id="moments-<?= $journalID ?>"><?= $moments ?></small>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-dark float-right" onclick="viewMore(<?=  $journalID ?>)">View More</button>
                    </div>
                </div>
    
                    <?php
                }
            ?>     
        </div>

        <!-- Modal -->
        <div class="modal fade" id="viewMoreModal" tabindex="-1" aria-labelledby="journalTitle" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="journalTitle"></h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <p id="journalMoment"></p>
                    </div>
                    <div class="modal-footer">
                        <small class="mr-auto">Date: <span id="journalDate"></span></small>
                        <button type="button" class="btn btn-secondary float-right" data-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
                        
        <button type="button" class="btn btn-secondary back-button" onclick="redirectTo('index.php')">Back to Home</button>


    </div>

</div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" integrity="sha384-9/reFTGAW83EW2RDu2S0VKaIzap3H66lZH81PoYlFhbGU+6BZp6G7niu735Sk7lN" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.min.js" integrity="sha384-+sLIOodYLS7CIrQpBjl+C7nPvqq+FbNUBDunl/OZv93DB7Ln/533i8e/mZXLi/P+" crossorigin="anonymous"></script>

    <script>
        function redirectTo(page) {
            window.location.href = page;
        }

        function viewMore(id) {
            $("#viewMoreModal").modal("show");

            let journalTitle = $("#location-" + id).text();
            let journalMoment = $("#moments-" + id).text();
            let journalDate = $("#date-" + id).text();

            $("#journalTitle").text(journalTitle);
            $("#journalMoment").text(journalMoment);
            $("#journalDate").text(journalDate);
        }
    </script>

</body>
</html>