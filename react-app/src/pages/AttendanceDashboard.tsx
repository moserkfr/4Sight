import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchAttendance, AttendanceRecord } from '../services/api';
import '../App.css'; // Reuse your existing styles

const AttendanceDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [attendanceData, setAttendanceData] = useState<AttendanceRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch data on component mount and refresh every 5 seconds
  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchAttendance();
        setAttendanceData(data);
      } catch (error) {
        console.error('Failed to fetch attendance:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 5000); // Auto-refresh
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Attendance Records</h2>
        <button 
          onClick={() => navigate('/')} 
          className="back-button"
        >
          ← Back to Home
        </button>
      </div>

      {isLoading ? (
        <p>Loading attendance data...</p>
      ) : attendanceData.length === 0 ? (
        <p>No attendance records found</p>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Timestamp</th>
                <th>Status</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {attendanceData.map((record) => (
                <tr key={record.id}>
                  <td>{record.id}</td>
                  <td>{record.name}</td>
                  <td>{new Date(record.timestamp).toLocaleString()}</td>
                  <td>
                    <span className={`status-badge ${record.status.toLowerCase()}`}>
                      {record.status}
                    </span>
                  </td>
                  <td>
                    {record.confidence !== undefined
                      ? `${(parseFloat(record.confidence) * 100).toFixed(2)}%`
                      : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Stats Summary */}
      <div className="stats-summary">
        <p>
          Total Present: {attendanceData.filter(x => x.status === 'Present').length}
        </p>
        <p>
          Last Updated: {new Date().toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
};

export default AttendanceDashboard;