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
    String email = request.getParameter("email");
    String password = request.getParameter("password");

    if (email == null || password == null || email.trim().isEmpty() || password.trim().isEmpty()) {
        response.sendRedirect("login.jsp?error=2");
        return;
    }

    Connection conn = null;
    PreparedStatement stmt = null;
    ResultSet rs = null;

    try {
        conn = DBConnection.getConnection();

        String sql = "SELECT owner_id, full_name, password_hash FROM pet_owner WHERE email = ?";
        stmt = conn.prepareStatement(sql);
        stmt.setString(1, email);
        rs = stmt.executeQuery();

        if (rs.next()) {
            String storedHash = rs.getString("password_hash");
            String enteredHash = hashPassword(password);

            if (storedHash.equals(enteredHash)) {
                session.setAttribute("owner_id", rs.getInt("owner_id"));
                session.setAttribute("full_name", rs.getString("full_name"));
                session.setAttribute("email", email);

                response.sendRedirect("dashboard.jsp");
                return;
            }
        }

        response.sendRedirect("login.jsp?error=1");

    } catch (Exception e) {
        e.printStackTrace();
        response.sendRedirect("login.jsp?error=1");
    } finally {
        try { if (rs != null) rs.close(); } catch (Exception e) {}
        try { if (stmt != null) stmt.close(); } catch (Exception e) {}
        try { if (conn != null) conn.close(); } catch (Exception e) {}
    }
%>