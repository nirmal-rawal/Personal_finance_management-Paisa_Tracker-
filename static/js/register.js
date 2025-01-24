const usernameField = document.querySelector('#usernameField');
const feedBackArea = document.querySelector(".invalid-feedback");
const emailField = document.querySelector('#emailField');
const emailFeedBackArea = document.querySelector('.emailFeedBackArea');
const passwordField = document.querySelector('#passwordField');
const usernameSuccessOutput = document.querySelector('.usernameSuccessOutput');
const showPasswordToggle = document.querySelector('.showPasswordToggle');

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

    emailField.classList.remove("is-invalid");
    emailFeedBackArea.style.display = 'none';

    if (emailVal.length > 0) {
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
                    emailField.classList.add("is-invalid");
                    emailFeedBackArea.style.display = 'block';
                    emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
                }
            });
    }
});

// Username validation
usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;
    usernameSuccessOutput.style.display = 'block';
    usernameSuccessOutput.textContent = `Checking ${usernameVal}`;
    usernameField.classList.remove("is-invalid");
    feedBackArea.style.display = 'none';

    if (usernameVal.length > 0) {
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
                }
            });
    }
});
