import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, BarChart2, FileText, Settings, LogOut, CalendarDays, RefreshCw } from 'lucide-react';

const Layout = ({ children }) => {
    const location = useLocation();

    const navItems = [
        { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/analysis', icon: BarChart2, label: 'Analysis' },
        { path: '/reports', icon: FileText, label: 'Reports' },
    ];

    return (
        <div className="app-shell">
            <aside className="sidebar">
                <div className="brand">
                    <span className="brand-mark">BA</span>
                    Insight Atlas
                </div>

                <div>
                    <div className="nav-title">Overview</div>
                    <nav className="nav-list">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = location.pathname === item.path;
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className="nav-link"
                                    data-active={isActive}
                                >
                                    <Icon className="w-4 h-4" />
                                    {item.label}
                                </Link>
                            );
                        })}
                    </nav>
                </div>

                <div className="sidebar-footer">
                    <button className="button-ghost">
                        <Settings className="w-4 h-4" />
                        Workspace Settings
                    </button>
                    <button className="button-ghost">
                        <LogOut className="w-4 h-4" />
                        Sign Out
                    </button>
                </div>
            </aside>

            <div className="main-area">
                <header className="topbar">
                    <div className="page-title">
                        {navItems.find((item) => item.path === location.pathname)?.label || 'Dashboard'}
                    </div>
                    <div className="topbar-controls">
                        <span className="chip">
                            <CalendarDays className="w-4 h-4" />
                            Last 30 days
                        </span>
                        <button className="button-primary">
                            <RefreshCw className="w-4 h-4" />
                            Sync data
                        </button>
                    </div>
                </header>

                <main className="content">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default Layout;
