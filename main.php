<?php include 'includes/config.php'; ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bike Rental System</title>

   
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">

    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

    
    <link href="assets/css/style.css" rel="stylesheet">
</head>

<body>

<div style="width:100%; background:white;">
    <img src="images/bikes/logo.jpeg" alt="GVP Header"
         style="width:100%; height:auto; display:block;">
</div>


<nav class="navbar navbar-expand-lg navbar-dark gradient-bg sticky-top">
    <div class="container">

       
        <a class="navbar-brand fw-bold" href="index.php">
            Bike Rental System
        </a>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item"><a class="nav-link" href="index.php">Home</a></li>
                <li class="nav-item"><a class="nav-link" href="#features">Features</a></li>
                <li class="nav-item"><a class="nav-link" href="#bikes">Bikes</a></li>
                <li class="nav-item"><a class="nav-link" href="login.php">Login</a></li>
                <li class="nav-item">
                    <a class="btn btn-light btn-sm ms-2" href="register.php">Get Started</a>
                </li>
            </ul>
        </div>
    </div>
</nav>


<section class="hero-section text-white d-flex align-items-center text-center">
    <div class="container">
        <div class="row justify-content-center">

            <div class="col-lg-8">
                <h1 class="display-4 fw-bold mb-4">
                    Rent Quality Bikes For Your Next Adventure
                </h1>
                <p class="lead mb-4">
                    Discover the perfect bike for your journey.
                </p>

                <div class="d-flex justify-content-center gap-3">
                    <a href="register.php" class="btn btn-light btn-lg">Start Riding</a>
                    <a href="#bikes" class="btn btn-outline-light btn-lg">View Bikes</a>
                </div>
            </div>

        </div>
    </div>
</section>


<section id="features" class="py-5">
    <div class="container text-center">
        <h2 class="fw-bold mb-4">Why Choose Us?</h2>

        <div class="row">
            <div class="col-md-4">
                <i class="fas fa-bicycle fa-2x mb-3"></i>
                <h5>Quality Bikes</h5>
                <p>Top brands with perfect maintenance.</p>
            </div>

            <div class="col-md-4">
                <i class="fas fa-dollar-sign fa-2x mb-3"></i>
                <h5>Affordable</h5>
                <p>No hidden charges.</p>
            </div>

            <div class="col-md-4">
                <i class="fas fa-shield-alt fa-2x mb-3"></i>
                <h5>Safe</h5>
                <p>Regular safety checks.</p>
            </div>
        </div>
    </div>
</section>


<section id="bikes" class="py-5 bg-light">
    <div class="container">
        <h2 class="text-center fw-bold mb-4">Our Bikes</h2>

        <div class="row">
        <?php
        $stmt = $pdo->query("SELECT * FROM bikes WHERE status='available' LIMIT 6");
        $bikes = $stmt->fetchAll();

        foreach($bikes as $bike):
        ?>
            <div class="col-md-4 mb-4">
                <div class="card h-100 shadow-sm">

                    <img src="<?php echo $bike['image_path']; ?>" class="card-img-top">

                    <div class="card-body">
                        <h5><?php echo $bike['name']; ?></h5>
                        <p><?php echo $bike['brand']; ?></p>
                        <p><strong>₹<?php echo $bike['price_per_hour']; ?>/hr</strong></p>

                        <a href="login.php" class="btn btn-primary w-100">
                            Rent Now
                        </a>
                    </div>

                </div>
            </div>
        <?php endforeach; ?>
        </div>
    </div>
</section>


<footer class="bg-dark text-white text-center py-3">
    <p>&copy; 2024 Bike Rental System</p>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>

</body>
</html>