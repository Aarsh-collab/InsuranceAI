import { Navigate } from "react-router-dom";
import { getAdminToken } from "../../services/adminApi";

function RequireAdminAuth({ children }) {
  if (!getAdminToken()) {
    return <Navigate to="/admin/login" replace />;
  }

  return children;
}

export default RequireAdminAuth;
