import React from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";

const AppLayout: React.FC = () => {
  return (
    <div className="flex h-screen bg-gray-100 dark:bg-dark-bg"> {/* Changed bg-light-bg to bg-gray-100 for testing */}
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 dark:bg-dark-card p-6"> {/* Changed bg-light-bg to bg-gray-100 for testing */}
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;

