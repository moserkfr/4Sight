export interface AttendanceRecord {
  id: number;
  name: string;
  timestamp: string;
  status: "Present" | "Absent";
  confidence?: string;
}

export const fetchAttendance = async (): Promise<AttendanceRecord[]> => {
  const response = await fetch('http://localhost:5000/api/attendance');
  return await response.json();
};