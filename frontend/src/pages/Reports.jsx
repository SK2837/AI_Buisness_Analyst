import React, { useEffect, useState } from 'react';
import { FileText, Eye, Loader2 } from 'lucide-react';
import axios from 'axios';

const Reports = () => {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get('/api/v1/reports/')
            .then(res => setReports(res.data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    const handleView = (reportId) => {
        window.open(`http://localhost:8000/api/v1/reports/${reportId}/render`, '_blank');
    };

    if (loading) return (
        <div className="card" style={{ display: 'grid', placeItems: 'center', minHeight: '220px' }}>
            <Loader2 className="w-8 h-8 animate-spin" />
        </div>
    );

    return (
        <div className="card">
            <div>
                <div className="card-title">Reports Library</div>
                <div style={{ fontSize: '20px', fontWeight: 600 }}>Live reports from Olist data</div>
            </div>

            <table className="table" style={{ marginTop: '18px' }}>
                <thead>
                    <tr>
                        <th>Report</th>
                        <th>Description</th>
                        <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {reports.map((report) => (
                        <tr key={report.id}>
                            <td>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <FileText className="w-4 h-4" />
                                    <span style={{ fontWeight: 600 }}>{report.title}</span>
                                </div>
                            </td>
                            <td className="muted">{report.description}</td>
                            <td style={{ textAlign: 'right' }}>
                                <button className="button-ghost" onClick={() => handleView(report.id)}>
                                    <Eye className="w-4 h-4" /> View
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Reports;
