import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "../pages/Login/Login";
import Dashboard from "../pages/Dashboard/Dashboard";
import Users from "../pages/Users/Users";
import Files from "../pages/Files/Files";
import Logs from "../pages/Logs/Logs";
import Settings from "../pages/Settings/Settings";
import MainLayout from "../layouts/MainLayout";
import { getCurrentUser } from "../services/authService";
function ProtectedRoute({children}){return getCurrentUser()?children:<Navigate to="/login" replace/>;}
function AppRouter(){return <BrowserRouter><Routes><Route path="/login" element={<Login/>}/><Route path="/" element={<ProtectedRoute><MainLayout/></ProtectedRoute>}><Route index element={<Dashboard/>}/><Route path="users" element={<Users/>}/><Route path="files" element={<Files/>}/><Route path="logs" element={<Logs/>}/><Route path="settings" element={<Settings/>}/></Route><Route path="*" element={<Navigate to="/" replace/>}/></Routes></BrowserRouter>}
export default AppRouter;
