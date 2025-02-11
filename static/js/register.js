const usernameField = document.querySelector('#usernameField');
const feedBackArea = document.querySelector(".invalid-feedback");
const emailField = document.querySelector('#emailField');
const emailFeedBackArea = document.querySelector('.emailFeedBackArea');
const passwordField = document.querySelector('#passwordField');
const usernameSuccessOutput = document.querySelector('.usernameSuccessOutput');
const showPasswordToggle = document.querySelector('.showPasswordToggle');
const submitBtn = document.querySelector(".submit-btn");

// Function to toggle password visibility
const handleToggleInput = () => {
    if (passwordField.getAttribute("type") === "password") {
        passwordField.setAttribute("type", "text");
        showPasswordToggle.textContent = "HIDE";
    } else {
        passwordField.setAttribute("type", "password");
        showPasswordToggle.textContent = "SHOW";
    }
};

// Event listener for toggling password visibility
showPasswordToggle.addEventListener('click', handleToggleInput);

// Function to get CSRF token from cookies
const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

const csrfToken = getCookie('csrftoken');

// Email validation
emailField.addEventListener('keyup', (e) => {
    const emailVal = e.target.value;

    // Clear error messages if the field is empty
    if (emailVal.length === 0) {
        emailField.classList.remove("is-invalid");
        emailFeedBackArea.style.display = 'none';
        submitBtn.removeAttribute("disabled");
        return; // Exit the function early
    }

    // Clear previous error messages
    emailField.classList.remove("is-invalid");
    emailFeedBackArea.style.display = 'none';

    // Validate email if the field is not empty
    fetch("/authentication/validate-email/", {
        method: "POST",
        body: JSON.stringify({ email: emailVal }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,  // Include CSRF token
        },
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.email_error) {
                submitBtn.setAttribute('disabled', "disabled");
                submitBtn.disabled = true;
                emailField.classList.add("is-invalid");
                emailFeedBackArea.style.display = 'block';
                emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
            } else {
                submitBtn.removeAttribute("disabled");
            }
        });
});

// Username validation
usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;

    // Clear error messages if the field is empty
    if (usernameVal.length === 0) {
        usernameField.classList.remove("is-invalid");
        feedBackArea.style.display = 'none';
        usernameSuccessOutput.style.display = 'none';
        submitBtn.removeAttribute("disabled");
        return; // Exit the function early
    }

    // Show "Checking..." message
    usernameSuccessOutput.style.display = 'block';
    usernameSuccessOutput.textContent = `Checking ${usernameVal}`;

    // Clear previous error messages
    usernameField.classList.remove("is-invalid");
    feedBackArea.style.display = 'none';

    // Validate username if the field is not empty
    fetch("/authentication/validate-username/", {
        method: "POST",
        body: JSON.stringify({ username: usernameVal }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,  // Include CSRF token
        },
    })
        .then((res) => res.json())
        .then((data) => {
            usernameSuccessOutput.style.display = 'none';
            if (data.username_error) {
                usernameField.classList.add("is-invalid");
                feedBackArea.style.display = 'block';
                feedBackArea.innerHTML = `<p>${data.username_error}</p>`;
                submitBtn.disabled = true;
            } else {
                // Check if email is different from username
                if (emailField.value && emailField.value === usernameVal) {
                    emailFeedBackArea.style.display = 'block';
                    emailFeedBackArea.innerHTML = `<p>Email and username should not be the same.</p>`;
                    submitBtn.disabled = true;
                } else {
                    submitBtn.removeAttribute("disabled");
                }
            }
        });
});