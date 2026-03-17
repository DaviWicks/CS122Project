<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Sign Up - PetWellness</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container form-box">
        <h2>Create Account</h2>

        <%
            String error = request.getParameter("error");
            String success = request.getParameter("success");
            if ("1".equals(error)) {
        %>
            <p class="error">All fields are required.</p>
        <%
            } else if ("2".equals(error)) {
        %>
            <p class="error">Email already exists.</p>
        <%
            } else if ("3".equals(error)) {
        %>
            <p class="error">Something went wrong. Please try again.</p>
        <%
            } else if ("1".equals(success)) {
        %>
            <p class="success">Account created successfully. Please log in.</p>
        <%
            }
        %>

        <form action="signup_process.jsp" method="post">
            <label>Full Name</label>
            <input type="text" name="full_name" required>

            <label>Email</label>
            <input type="email" name="email" required>

            <label>Password</label>
            <input type="password" name="password" required>

            <button type="submit" class="btn">Sign Up</button>
        </form>

        <p><a href="index.jsp">Back to Home</a></p>
    </div>
</body>
</html>