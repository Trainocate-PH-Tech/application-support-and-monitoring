package training;

import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.*;
import java.io.*;
import java.nio.file.*;
import java.sql.*;
import java.time.Instant;
import java.util.*;

@WebServlet("/*")
public class LoyaltyServlet extends HttpServlet {
    private Properties config() throws IOException {
        Properties p = new Properties();
        try (InputStream in = Files.newInputStream(Path.of(System.getenv().getOrDefault("LAB_CONFIG", "/etc/support-lab/app.properties")))) { p.load(in); }
        return p;
    }
    private Connection db(Properties p) throws SQLException {
        try { Class.forName("com.mysql.cj.jdbc.Driver"); } catch (ClassNotFoundException e) { throw new SQLException("Driver unavailable", e); }
        return DriverManager.getConnection(p.getProperty("db.url"), p.getProperty("db.user"), p.getProperty("db.password"));
    }
    @Override protected void doGet(HttpServletRequest req, HttpServletResponse res) throws IOException {
        long start = System.nanoTime();
        String requestId = UUID.randomUUID().toString();
        String path = Optional.ofNullable(req.getPathInfo()).orElse("/");
        int status = 200; String result = "", error = "none";
        res.setContentType("text/plain;charset=UTF-8"); res.setHeader("X-Request-ID", requestId);
        try {
            Properties p = config();
            if (path.equals("/live")) result = "alive\n";
            else if (path.equals("/payment")) {
                if (p.getProperty("payment.fail", "false").equals("true")) { status=502; error="dependency_unavailable"; result="payment simulator unavailable\n"; }
                else result="payment simulator ready; no real payments\n";
            } else try (Connection c = db(p)) {
                int delay=Math.max(0, Math.min(2000, Integer.parseInt(p.getProperty("delay.ms", "0"))));
                if (delay > 0) Thread.sleep(delay);
                if (path.equals("/health")) {
                    try (Statement s=c.createStatement()) { s.setQueryTimeout(3); s.executeQuery("SELECT 1").close(); }
                    result="ready database=ok\n";
                } else if (path.equals("/player")) {
                    int id=Integer.parseInt(Optional.ofNullable(req.getParameter("id")).orElse("1"));
                    try (PreparedStatement s=c.prepareStatement("SELECT id,name,points FROM players WHERE id=?")) {
                        s.setQueryTimeout(5); s.setInt(1,id);
                        try (ResultSet r=s.executeQuery()) { if(r.next()) result=r.getInt(1)+","+r.getString(2)+","+r.getInt(3)+"\n"; else {status=404;result="player not found\n";} }
                    }
                } else if (path.equals("/report")) {
                    try (Statement s=c.createStatement()) {
                        s.setQueryTimeout(8);
                        try (ResultSet r=s.executeQuery("SELECT COUNT(*),SUM(amount) FROM transactions WHERE player_id=42")) {r.next();result="transactions="+r.getLong(1)+" total="+r.getBigDecimal(2)+"\n";}
                    }
                } else {status=404;result="Use /live /health /player?id=1 /report /payment\n";}
            }
        } catch (NumberFormatException e) { status=400;error="invalid_number";result="invalid numeric input\n";
        } catch (InterruptedException e) { Thread.currentThread().interrupt(); status=503;error="interrupted";result="interrupted\n";
        } catch (Exception e) { status=503;error=e instanceof SQLException ? "db_"+((SQLException)e).getSQLState() : e.getClass().getSimpleName();result="unavailable request_id="+requestId+"\n"; }
        res.setStatus(status); res.getWriter().write(result);
        long ms=(System.nanoTime()-start)/1_000_000;
        String safePath=path.replaceAll("[^a-zA-Z0-9/_-]", "_");
        System.out.printf("%s level=%s request_id=%s path=%s status=%d latency_ms=%d error=%s%n", Instant.now(), status>=500?"ERROR":"INFO", requestId,safePath,status,ms,error);
    }
}
