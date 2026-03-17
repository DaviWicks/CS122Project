<%@ page import="java.sql.*" %>
<%@ page import="java.security.MessageDigest" %>
<%@ page import="com.petwellness.util.DBConnection" %>

<%!
    public String hashPassword(String password) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] hash = md.digest(password.getBytes("UTF-8"));
        StringBuilder sb = new StringBuilder();
        for (byte b : hash) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
%>

<%
    String fullName = request.getParameter("full_name");
    String email = request.getParameter("email");
    String password = request.getParameter("password");

    if (fullName == null || email == null || password == null ||
        fullName.trim().isEmpty() || email.trim().isEmpty() || password.trim().isEmpty()) {
        response.sendRedirect("signup.jsp?error=1");
        return;
    }

    Connection conn = null;
    PreparedStatement checkStmt = null;
    PreparedStatement insertStmt = null;
    ResultSet rs = null;

    try {
        conn = DBConnection.getConnection();

        String checkSql = "SELECT owner_id FROM pet_owner WHERE email = ?";
        checkStmt = conn.prepareStatement(checkSql);
        checkStmt.setString(1, email);
        rs = checkStmt.executeQuery();

        if (rs.next()) {
            response.sendRedirect("signup.jsp?error=2");
            return;
        }

        String hashedPassword = hashPassword(password);

        String insertSql = "INSERT INTO pet_owner (full_name, email, password_hash) VALUES (?, ?, ?)";
        insertStmt = conn.prepareStatement(insertSql);
        insertStmt.setString(1, fullName);
        insertStmt.setString(2, email);
        insertStmt.setString(3, hashedPassword);

        int rows = insertStmt.executeUpdate();

        if (rows > 0) {
            response.sendRedirect("signup.jsp?success=1");
        } else {
            response.sendRedirect("signup.jsp?error=3");
        }

    } catch (Exception e) {
        e.printStackTrace();
        response.sendRedirect("signup.jsp?error=3");
    } finally {
        try { if (rs != null) rs.close(); } catch (Exception e) {}
        try { if (checkStmt != null) checkStmt.close(); } catch (Exception e) {}
        try { if (insertStmt != null) insertStmt.close(); } catch (Exception e) {}
        try { if (conn != null) conn.close(); } catch (Exception e) {}
    }
%>