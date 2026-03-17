<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%
    if (session.getAttribute("owner_id") == null) {
        response.sendRedirect("login.jsp");
        return;
    }
%>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dashboard - PetWellness</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>Welcome, <%= session.getAttribute("full_name") %>!</h1>
        <p>You are logged in to PetWellness.</p>
        <p>Email: <%= session.getAttribute("email") %></p>

        <div class="button-group">
            <a class="btn" href="logout.jsp">Logout</a>
        </div>
    </div>
</body>
</html>