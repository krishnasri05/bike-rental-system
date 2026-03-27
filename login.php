<?php
include 'includes/config.php';
include 'includes/auth.php';
preventLoggedInAccess();

$error = '';
$login_type = $_GET['type'] ?? 'client'; // Default to client login

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $email = sanitize($_POST['email']);
    $password = $_POST['password'];
    $login_type = $_POST['login_type'];
    
    try {
        if ($login_type == 'admin') {
            // Admin login
            $stmt = $pdo->prepare("SELECT * FROM admins WHERE email = ? AND status = 'active'");
            $stmt->execute([$email]);
            $user = $stmt->fetch();
            
            if ($user && password_verify($password, $user['password'])) {
                $_SESSION['user_id'] = $user['admin_id'];
                $_SESSION['user_type'] = 'admin';
                $_SESSION['username'] = $user['username'];
                $_SESSION['full_name'] = $user['full_name'];
                $_SESSION['email'] = $user['email'];
                
                // Update last login
                $pdo->prepare("UPDATE admins SET last_login = NOW() WHERE admin_id = ?")->execute([$user['admin_id']]);
                
                $_SESSION['success'] = "Welcome back, " . $user['full_name'] . "!";
                header("Location: admin/dashboard.php");
                exit;
            } else {
                $error = "Invalid admin credentials or account inactive!";
            }
            
        } else {
            // Client login
            $stmt = $pdo->prepare("SELECT * FROM clients WHERE email = ? AND status = 'active'");
            $stmt->execute([$email]);
            $user = $stmt->fetch();
            
            if ($user && password_verify($password, $user['password'])) {
                $_SESSION['user_id'] = $user['client_id'];
                $_SESSION['user_type'] = 'client';
                $_SESSION['username'] = $user['username'];
                $_SESSION['full_name'] = $user['full_name'];
                $_SESSION['email'] = $user['email'];
                
                $_SESSION['success'] = "Welcome back, " . $user['full_name'] . "!";
                header("Location: client/dashboard.php");
                exit;
            } else {
                $error = "Invalid credentials or account not activated!";
            }
        }
    } catch(PDOException $e) {
        $error = "Login failed: " . $e->getMessage();
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Bike Rental System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link href="assets/css/style.css" rel="stylesheet">
</head>
<body>
    <div class="login-container">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-5">
                    <div class="card login-card">
                        <div class="card-header text-center py-4">
                            <h2 class="mb-0">
                                <i class="fas fa-bicycle me-2"></i>BikeRental
                            </h2>
                            <p class="mb-0 mt-2">Sign in to your account</p>
                        </div>
                        <div class="card-body p-4">
                            <!-- Login Type Tabs -->
                            <ul class="nav nav-pills nav-justified mb-4" id="loginTabs">
                                <li class="nav-item">
                                    <a class="nav-link <?php echo $login_type == 'client' ? 'active' : ''; ?>" 
                                       href="?type=client">
                                        <i class="fas fa-user me-2"></i>Client Login
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link <?php echo $login_type == 'admin' ? 'active' : ''; ?>" 
                                       href="?type=admin">
                                        <i class="fas fa-cog me-2"></i>Admin Login
                                    </a>
                                </li>
                            </ul>

                            <!-- Success Message from Registration -->
                            <?php if(isset($_SESSION['success'])): ?>
                                <div class="alert alert-success alert-dismissible fade show" role="alert">
                                    <i class="fas fa-check-circle me-2"></i><?php echo $_SESSION['success']; ?>
                                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                </div>
                                <?php unset($_SESSION['success']); ?>
                            <?php endif; ?>

                            <!-- Error Message -->
                            <?php if(!empty($error)): ?>
                                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                                    <i class="fas fa-exclamation-triangle me-2"></i><?php echo $error; ?>
                                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                </div>
                            <?php endif; ?>

                            <form method="POST" action="">
                                <input type="hidden" name="login_type" value="<?php echo $login_type; ?>">
                                
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email Address</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                        <input type="email" class="form-control form-control-lg" id="email" name="email" 
                                               placeholder="Enter your email" required 
                                               value="<?php echo isset($_POST['email']) ? htmlspecialchars($_POST['email']) : ''; ?>">
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                        <input type="password" class="form-control form-control-lg" id="password" name="password" 
                                               placeholder="Enter your password" required>
                                        <button type="button" class="input-group-text toggle-password">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                    </div>
                                </div>

                                <div class="d-grid mb-3">
                                    <button type="submit" class="btn btn-gradient btn-lg">
                                        <i class="fas fa-sign-in-alt me-2"></i>Sign In
                                    </button>
                                </div>
                            </form>

                            <div class="text-center">
                                <?php if($login_type == 'client'): ?>
                                    <p class="mb-0">Don't have an account? 
                                        <a href="register.php" class="text-decoration-none">Create one here</a>
                                    </p>
                                <?php endif; ?>
                                <p class="mt-2">
                                    <a href="index.php" class="text-decoration-none">
                                        <i class="fas fa-arrow-left me-1"></i>Back to Homepage
                                    </a>
                                </p>
                            </div>

                            <!-- Demo Accounts Info -->
                            <div class="mt-4 p-3 bg-light rounded">
                                <!--<h6 class="mb-2"><i class="fas fa-info-circle me-2"></i>Demo Accounts:</h6>
                                 <small class="text-muted">
                                    <strong>Admin:</strong> admin@bikerental.com / password<br>
                                    <strong>Client:</strong> Register new account
                                </small> -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Toggle password visibility
        document.querySelector('.toggle-password').addEventListener('click', function() {
            const passwordInput = document.getElementById('password');
            const icon = this.querySelector('i');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        });
        
        // Simple form validation
        document.querySelector('form').addEventListener('submit', function(e) {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                e.preventDefault();
                alert('Please fill in all fields');
                return false;
            }
            
            if (!isValidEmail(email)) {
                e.preventDefault();
                alert('Please enter a valid email address');
                return false;
            }
        });
        
        function isValidEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        }
    </script>
</body>
</html>