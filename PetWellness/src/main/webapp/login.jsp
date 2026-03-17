<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Login - PetWellness</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container form-box">
        <h2>Login</h2>

        <%
            String error = request.getParameter("error");
            if ("1".equals(error)) {
        %>
            <p class="error">Invalid email or password.</p>
        <%
            } else if ("2".equals(error)) {
        %>
            <p class="error">Please enter both email and password.</p>
        <%
            }
        %>

        <form action="login_process.jsp" method="post">
            <label>Email</label>
            <input type="email" name="email" required>

            <label>Password</label>
            <input type="password" name="password" required>

            <button type="submit" class="btn">Login</button>
        </form>

        <p><a href="index.jsp">Back to Home</a></p>
    </div>
</body>
</html>