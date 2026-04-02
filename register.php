<?php
include 'includes/config.php';
include 'includes/auth.php';
preventLoggedInAccess();

$error = '';
$success = '';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = sanitize($_POST['username']);
    $email = sanitize($_POST['email']);
    $password = $_POST['password'];
    $confirm_password = $_POST['confirm_password'];
    $full_name = sanitize($_POST['full_name']);
    $phone = sanitize($_POST['phone']);
    $address = sanitize($_POST['address']);
    $license_number = normalizeLicenseNumber(sanitize($_POST['license_number']));
    
    // Validation
    if (empty($username) || empty($email) || empty($password) || empty($full_name)) {
        $error = "Please fill in all required fields!";
    } elseif ($password !== $confirm_password) {
        $error = "Passwords do not match!";
    } elseif (strlen($password) < 6) {
        $error = "Password must be at least 6 characters long!";
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $error = "Please enter a valid email address!";
    } elseif (!empty($license_number) && !isValidLicenseNumber($license_number)) {
        $error = "Invalid Indian license format. Use format like MH1420110012345.";
    } else {
        try {
            // Check if username or email already exists
            $stmt = $pdo->prepare("SELECT client_id FROM clients WHERE username = ? OR email = ?");
            $stmt->execute([$username, $email]);
            
            if ($stmt->fetch()) {
                $error = "Username or email already exists!";
            } else {
                // Insert new client
                $hashed_password = password_hash($password, PASSWORD_DEFAULT);
                $stmt = $pdo->prepare("INSERT INTO clients (username, email, password, full_name, phone, address, license_number, status) 
                                      VALUES (?, ?, ?, ?, ?, ?, ?, 'active')");
                
                if ($stmt->execute([$username, $email, $hashed_password, $full_name, $phone, $address, $license_number])) {
                    // Registration successful - set success message and redirect
                    $_SESSION['success'] = "Registration successful! You can now login to your account.";
                    header("Location: login.php");
                    exit();
                } else {
                    $error = "Registration failed. Please try again.";
                }
            }
        } catch(PDOException $e) {
            $error = "Registration failed: " . $e->getMessage();
        }
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register - Bike Rental System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link href="assets/css/style.css" rel="stylesheet">
    <style>
        .registration-container {
            min-height: 100vh;
            display: flex;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px 0;
        }
        .registration-card {
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .form-check-input:checked {
            background-color: #667eea;
            border-color: #667eea;
        }
        .password-strength {
            height: 5px;
            border-radius: 5px;
            margin-top: 5px;
            transition: all 0.3s ease;
        }
        .strength-weak { background-color: #dc3545; width: 25%; }
        .strength-fair { background-color: #ffc107; width: 50%; }
        .strength-good { background-color: #28a745; width: 75%; }
        .strength-strong { background-color: #20c997; width: 100%; }
    </style>
</head>
<body>
    <div class="registration-container">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card registration-card">
                        <div class="card-header text-center py-4 text-white" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                            <h2 class="mb-2">
                                <i class="fas fa-bicycle me-2"></i>Join BikeRental
                            </h2>
                            <p class="mb-0">Create your account and start your biking adventure</p>
                        </div>
                        <div class="card-body p-4 p-md-5">
                            <?php if(!empty($error)): ?>
                                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                                    <i class="fas fa-exclamation-triangle me-2"></i><?php echo $error; ?>
                                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                </div>
                            <?php endif; ?>

                            <form method="POST" action="" id="registrationForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="full_name" class="form-label">Full Name <span class="text-danger">*</span></label>
                                            <div class="input-group">
                                                <span class="input-group-text"><i class="fas fa-user"></i></span>
                                                <input type="text" class="form-control" id="full_name" name="full_name" 
                                                       value="<?php echo $_POST['full_name'] ?? ''; ?>" required
                                                       placeholder="Enter your full name">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="username" class="form-label">Username <span class="text-danger">*</span></label>
                                            <div class="input-group">
                                                <span class="input-group-text"><i class="fas fa-at"></i></span>
                                                <input type="text" class="form-control" id="username" name="username" 
                                                       value="<?php echo $_POST['username'] ?? ''; ?>" required
                                                       placeholder="Choose a username">
                                            </div>
                                            <div class="form-text">This will be your unique identifier</div>
                                        </div>
                                    </div>
                                </div>

                                <div class="mb-3">
                                    <label for="email" class="form-label">Email Address <span class="text-danger">*</span></label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                        <input type="email" class="form-control" id="email" name="email" 
                                               value="<?php echo $_POST['email'] ?? ''; ?>" required
                                               placeholder="Enter your email address">
                                    </div>
                                </div>

                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="password" class="form-label">Password <span class="text-danger">*</span></label>
                                            <div class="input-group">
                                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                                <input type="password" class="form-control" id="password" name="password" required
                                                       placeholder="Create a password">
                                                <button type="button" class="input-group-text toggle-password">
                                                    <i class="fas fa-eye"></i>
                                                </button>
                                            </div>
                                            <div class="password-strength" id="passwordStrength"></div>
                                            <div class="form-text">Password must be at least 6 characters long</div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="confirm_password" class="form-label">Confirm Password <span class="text-danger">*</span></label>
                                            <div class="input-group">
                                                <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                                <input type="password" class="form-control" id="confirm_password" name="confirm_password" required
                                                       placeholder="Confirm your password">
                                                <button type="button" class="input-group-text toggle-password">
                                                    <i class="fas fa-eye"></i>
                                                </button>
                                            </div>
                                            <div class="form-text" id="passwordMatch"></div>
                                        </div>
                                    </div>
                                </div>

                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="phone" class="form-label">Phone Number</label>
                                            <div class="input-group">
                                                <span class="input-group-text"><i class="fas fa-phone"></i></span>
                                                <input type="tel" class="form-control" id="phone" name="phone" 
                                                       value="<?php echo $_POST['phone'] ?? ''; ?>"
                                                       placeholder="Your phone number">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="license_number" class="form-label">License Number</label>
                                            <div class="input-group">
                                                <span class="input-group-text"><i class="fas fa-id-card"></i></span>
                                                <input type="text" class="form-control" id="license_number" name="license_number" 
                                                       value="<?php echo $_POST['license_number'] ?? ''; ?>"
                                                       placeholder="Indian license number (e.g. MH1420110012345)">
                                            </div>
                                            <small class="text-muted">Format: SSRRYYYYNNNNNNN (optional at registration).</small>
                                            <div id="licenseFormatFeedback" class="form-text"></div>
                                        </div>
                                    </div>
                                </div>

                                <div class="mb-4">
                                    <label for="address" class="form-label">Address</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-home"></i></span>
                                        <textarea class="form-control" id="address" name="address" rows="2" 
                                                  placeholder="Your complete address"><?php echo $_POST['address'] ?? ''; ?></textarea>
                                    </div>
                                </div>

                                <div class="mb-4">
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" id="terms" required>
                                        <label class="form-check-label" for="terms">
                                            I agree to the <a href="#" class="text-decoration-none">Terms of Service</a> and <a href="#" class="text-decoration-none">Privacy Policy</a>
                                        </label>
                                    </div>
                                </div>

                                <div class="d-grid mb-4">
                                    <button type="submit" class="btn btn-gradient btn-lg py-3">
                                        <i class="fas fa-user-plus me-2"></i>Create Account
                                    </button>
                                </div>
                            </form>

                            <div class="text-center">
                                <p class="mb-0">Already have an account? 
                                    <a href="login.php" class="text-decoration-none fw-bold">Sign in here</a>
                                </p>
                                <p class="mt-2">
                                    <a href="index.php" class="text-decoration-none">
                                        <i class="fas fa-arrow-left me-1"></i>Back to Homepage
                                    </a>
                                </p>
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
        document.querySelectorAll('.toggle-password').forEach(button => {
            button.addEventListener('click', function() {
                const input = this.closest('.input-group').querySelector('input');
                const icon = this.querySelector('i');
                
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.replace('fa-eye', 'fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.replace('fa-eye-slash', 'fa-eye');
                }
            });
        });

        // Password strength indicator
        document.getElementById('password').addEventListener('input', function() {
            const password = this.value;
            const strengthBar = document.getElementById('passwordStrength');
            let strength = 0;
            
            if (password.length >= 6) strength += 25;
            if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength += 25;
            if (password.match(/\d/)) strength += 25;
            if (password.match(/[^a-zA-Z\d]/)) strength += 25;
            
            strengthBar.className = 'password-strength';
            if (strength <= 25) {
                strengthBar.classList.add('strength-weak');
            } else if (strength <= 50) {
                strengthBar.classList.add('strength-fair');
            } else if (strength <= 75) {
                strengthBar.classList.add('strength-good');
            } else {
                strengthBar.classList.add('strength-strong');
            }
        });

        // Password match validation
        document.getElementById('confirm_password').addEventListener('input', function() {
            const password = document.getElementById('password').value;
            const confirmPassword = this.value;
            const matchText = document.getElementById('passwordMatch');
            
            if (confirmPassword === '') {
                matchText.textContent = '';
                matchText.className = 'form-text';
            } else if (password === confirmPassword) {
                matchText.textContent = 'Passwords match!';
                matchText.className = 'form-text text-success';
            } else {
                matchText.textContent = 'Passwords do not match!';
                matchText.className = 'form-text text-danger';
            }
        });

        // Form validation
        document.getElementById('registrationForm').addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            const terms = document.getElementById('terms').checked;
            const licenseInput = document.getElementById('license_number');
            const licenseValue = licenseInput.value.trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
            const indianLicensePattern = /^[A-Z]{2}[0-9]{2}[0-9]{4}[0-9]{7}$/;

            if (licenseValue !== '' && !indianLicensePattern.test(licenseValue)) {
                e.preventDefault();
                alert('Invalid Indian license format. Use format like MH1420110012345.');
                licenseInput.focus();
                return false;
            }
            
            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Please make sure passwords match!');
                return false;
            }
            
            if (!terms) {
                e.preventDefault();
                alert('Please agree to the Terms of Service and Privacy Policy!');
                return false;
            }
        });

        // Real-time username availability check (optional enhancement)
        document.getElementById('username').addEventListener('blur', function() {
            const username = this.value;
            if (username.length < 3) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });

        // Live Indian license format validation
        const licenseInput = document.getElementById('license_number');
        const licenseFeedback = document.getElementById('licenseFormatFeedback');
        const indianLicensePattern = /^[A-Z]{2}[0-9]{2}[0-9]{4}[0-9]{7}$/;

        licenseInput.addEventListener('input', function() {
            const normalized = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            this.value = normalized;

            if (normalized === '') {
                this.classList.remove('is-invalid');
                this.classList.remove('is-valid');
                licenseFeedback.textContent = '';
                licenseFeedback.className = 'form-text';
                return;
            }

            if (indianLicensePattern.test(normalized)) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                licenseFeedback.textContent = 'Valid Indian license format.';
                licenseFeedback.className = 'form-text text-success';
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
                licenseFeedback.textContent = 'Invalid format. Example: MH1420110012345';
                licenseFeedback.className = 'form-text text-danger';
            }
        });
    </script>
</body>
</html>