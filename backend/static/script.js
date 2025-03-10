function loginUser() {
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value.trim();

    if (!username || !password) {
        alert("Username and password cannot be empty.");
        return;
    }

    fetch('/login', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.message); });
        }
        return response.json();
    })
    .then(data => {
        if (data.redirect) {
            window.location.href = data.redirect; // ✅ Redirects properly after login
        } else {
            alert("❌ Invalid username or password.");
        }
    })
    .catch(error => {
        console.error("Error during login:", error);
        alert(`❌ Login failed: ${error.message}`);
    });
}



function registerUser() {
    const username = document.getElementById("register-username").value.trim();
    const password = document.getElementById("register-password").value.trim();

    if (!username || !password) {
        alert("Username and password cannot be empty.");
        return;
    }

    fetch('/register', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.message); });
        }
        return response.json();
    })
    .then(data => {
        alert("✅ Registration successful! Redirecting to login...");
        window.location.href = data.redirect;
    })
    .catch(error => {
        console.error("Error during registration:", error);
        alert(`❌ Registration failed: ${error.message}`);
    });
}



function submitQuiz() {
    fetch('/api/submit_quiz', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quiz_id: selectedQuizId, answers: answers })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let resultMessage = `✅ Quiz submitted! Your score: ${data.score}/10`;

            if (data.correct_answers) {
                resultMessage += "\n\nCorrect Answers:\n";
                data.correct_answers.forEach((ans, index) => {
                    resultMessage += `${index + 1}. ${ans.question} - ✅ ${ans.correct}\n`;
                });
            }

            alert(resultMessage);
            location.reload();
        } else {
            alert("❌ Failed to submit quiz. Try again.");
        }
    })
    .catch(error => {
        console.error("Error submitting quiz:", error);
        alert("An error occurred. Check the console.");
    });
}


