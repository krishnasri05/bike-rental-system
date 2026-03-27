<!DOCTYPE html>
<html>
<head>
    <title>Bike Rental System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
        body{
            margin:0;
            font-family: 'Segoe UI', sans-serif;
            background: url('images/bikes/bikes.jpeg') no-repeat right 20% center/cover;
            height:100vh;
            display:flex;
            justify-content:center;
            align-items:center;
            overflow:hidden;
        }

        /* 🔥 Cinematic overlay */
        body::before{
            content:'';
            position:absolute;
            width:100%;
            height:100%;
            background: rgba(0,0,0,0.35);
        }

        /* 💎 Glass Card */
        .card{
            position:relative;
            width:420px;
            padding:25px;
            border-radius:20px;

            background: rgba(255,255,255,0.75);
            backdrop-filter: blur(18px);

            box-shadow:
                0 10px 40px rgba(0,0,0,0.6),
                0 0 20px rgba(44,62,148,0.2);

            text-align:center;

            /* 🎬 Animation */
            transform: translateY(40px);
            opacity:0;
            animation: fadeUp 1s ease forwards;
        }

        /* 🔥 Logo */
        .top-logo{
            width:100%;
            max-height:80px;
            object-fit:contain;
            margin-bottom:10px;

            opacity:0;
            animation: fadeIn 1.2s ease forwards;
        }

        .title{
            color:#2c3e94;
            font-size:28px;
            font-weight:bold;
            margin:10px 0;
        }

        .subtitle{
            color:#555;
            font-size:14px;
            margin-bottom:10px;
        }

        .section-title{
            margin:15px 0;
            font-size:12px;
            color:#777;
            letter-spacing:2px;
        }

        /* 👤 Members */
        .member{
            display:flex;
            align-items:center;
            background: rgba(255,255,255,0.6);
            padding:12px;
            border-radius:15px;
            margin:10px 0;

            transform: translateY(20px);
            opacity:0;
            animation: fadeUp 0.8s ease forwards;
        }

        .member:nth-child(1){ animation-delay:0.3s; }
        .member:nth-child(2){ animation-delay:0.4s; }
        .member:nth-child(3){ animation-delay:0.5s; }
        .member:nth-child(4){ animation-delay:0.6s; }
        .member:nth-child(5){ animation-delay:0.7s; }

        .circle{
            width:40px;
            height:40px;
            background:#2c3e94;
            color:white;
            border-radius:50%;
            display:flex;
            align-items:center;
            justify-content:center;
            margin-right:12px;
            font-weight:bold;
        }

        /* 👨‍🏫 Guide */
        .guide{
            margin-top:15px;
            padding:15px;
            border:2px dashed #2c3e94;
            border-radius:15px;
            color:#2c3e94;
            font-weight:bold;

            opacity:0;
            animation: fadeUp 1s ease forwards;
            animation-delay:0.8s;
        }

        /* 🔘 Button */
        .btn{
            display:block;
            margin-top:20px;
            padding:15px;
            background:#2c3e94;
            color:white;
            border-radius:15px;
            text-decoration:none;
            font-weight:bold;

            transition:0.3s;

            opacity:0;
            animation: fadeUp 1s ease forwards;
            animation-delay:1s;
        }

        .btn:hover{
            background:#1a237e;
            transform: scale(1.05);
            box-shadow:0 0 15px rgba(44,62,148,0.5);
        }

        /* 🎬 Animations */
        @keyframes fadeUp{
            to{
                transform: translateY(0);
                opacity:1;
            }
        }

        @keyframes fadeIn{
            to{
                opacity:1;
            }
        }

    </style>
</head>

<body>

<div class="card">

    <!-- LOGO -->
    <img src="images/bikes/logo.jpeg" class="top-logo">

    <!-- TITLE -->
    <h2 class="title">BIKE RENTAL SYSTEM</h2>
    <p class="subtitle">Bike Booking & Management Platform</p>

    <!-- TEAM -->
    <div class="section-title">— PRESENTED BY —</div>

    <div class="member"><div class="circle">P</div> P. Yeswanthi</div>
    <div class="member"><div class="circle">S</div> S. Sri Varshitha</div>
    <div class="member"><div class="circle">P</div> P. Krishna Sri</div>
    <div class="member"><div class="circle">T</div> T. Satya Padma Priya</div>
    <div class="member"><div class="circle">S</div> S. Adilakshmi</div>

    <!-- GUIDE -->
    <div class="guide">
        GUIDED BY <br>
        MR. T. SRI KRISHNA
    </div>

    <!-- BUTTON -->
    <a href="main.php" class="btn">Proceed to App →</a>

</div>

</body>
</html>