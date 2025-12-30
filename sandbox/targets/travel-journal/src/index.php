<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travel Journal</title>

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

        .title-container {
            background-color: rgba(150, 150, 150, 0.7);
            width: 100%;
            text-align: center;
            padding: 30px;
        }

        .title-container > h1 {
            font-size: 100px;
            color: rgb(50, 50, 50);
            text-shadow: 4px 4px rgb(200, 200, 200);
        }

        .travel-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: rgba(150, 150, 150, 0.7);
            width: 70%;
            margin-top: 50px;
            padding: 30px;
            border-radius: 10px;
        }

        .option-header {
            font-size: 40px;
            color: rgb(50, 50, 50);
            text-shadow: 4px 4px rgb(200, 200, 200);
        }

        .option-container {
            display: flex;
            justify-content: space-between;
            width: 600px;
            margin-top: 20px;
        }

        .option-container div {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            padding: 30px;  
            background-color: rgba(100, 100, 100, 0.6);
        }

        .option-container div:hover {
            background-color: rgba(20, 20, 20, 0.6);
        }

        .option-container img {
            width: 200px;
        }

        .option-container h2 {
            font-size: 30px;
            color: rgb(50, 50, 50);
            text-shadow: 4px 4px rgb(200, 200, 200);
        }
        

    </style>

</head>
<body>

<div class="main">

    <div class="title-container">
        <h1>Travel Journal</h1>
    </div>

    <div class="travel-container">
        <h1 class="option-header">What would you like to do?</h1>

        <div class="option-container">
            <div class="write-journal-container" onclick="redirectTo('write-journal.php')">
                <img src="https://cdn-icons-png.flaticon.com/512/3131/3131607.png" alt="">
                <h2>Write Journal</h2>
            </div>

            <div class="read-journal-container" onclick="redirectTo('read-journal.php')">
                <img src="https://cdn-icons-png.flaticon.com/512/4072/4072307.png" alt="">
                <h2>Read Journal</h2>
            </div>
        </div>
    </div>

</div>

<script>
    function redirectTo(page) {
        window.location.href = page;
    }
</script>

</body>
</html>