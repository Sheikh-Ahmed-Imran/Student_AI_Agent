"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { Users, TrendingUp, UserCheck, Activity } from "lucide-react";

interface DepartmentData {
  department: string;
  count: number;
}

interface Student {
  id: number;
  name: string;
  department: string;
  email: string;
  created_at: string;
  last_active: string;
}

interface AnalyticsResponse {
  total_students: number;
  by_department: DepartmentData[];
  recent_students: Student[];
  active_last_7_days: Student[];
}

interface Stat {
  title: string;
  value: string;
  icon: any;
  trend?: "up" | "down";
}

export default function Analytics() {
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/analytics");
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error("Failed to fetch analytics:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading || !data) {
    return (
      <p className="text-muted-foreground text-center mt-8">
        Loading analytics...
      </p>
    );
  }

  // Stats cards
  const stats: Stat[] = [
    {
      title: "Total Students",
      value: data.total_students.toString(),
      icon: Users,
      trend: "up",
    },
    {
      title: "Recently Onboarded",
      value: data.recent_students.length.toString(),
      icon: UserCheck,
      trend: "up",
    },
    {
      title: "Active Last 7 Days",
      value: data.active_last_7_days.length.toString(),
      icon: Activity,
      trend: "up",
    },
    {
      title: "Growth Rate",
      value: "N/A",
      icon: TrendingUp,
      trend: "up",
    },
  ];

  // Pie chart data for departments
  const colors = ["#8B5CF6", "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#FBBF24"];
  const studentsByDepartment = data.by_department.map((dept, idx) => ({
    name: dept.department,
    value: dept.count,
    color: colors[idx % colors.length],
  }));

  // Bar chart data for active students
  const activeStudentsData = data.active_last_7_days.map((student) => ({
    name: student.name,
    logins: 1, // simple count per student
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Analytics Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Overview of student registration and activity metrics
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Students by Department */}
        <Card>
          <CardHeader>
            <CardTitle>Students by Department</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={studentsByDepartment}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={120}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {studentsByDepartment.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-2">
              {studentsByDepartment.map((dept) => (
                <div key={dept.name} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: dept.color }}
                  />
                  <span className="text-sm text-foreground">{dept.name}</span>
                  <span className="text-sm text-muted-foreground">({dept.value})</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Active Students Last 7 Days */}
        <Card>
          <CardHeader>
            <CardTitle>Active Students Last 7 Days</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height={320}>
                <BarChart
                  data={activeStudentsData}
                  margin={{ top: 20, right: 20, left: 0, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="logins" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recently Onboarded Students */}
      <Card>
        <CardHeader>
          <CardTitle>Recently Onboarded Students</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.recent_students.map((student) => (
              <div
                key={student.id}
                className="flex items-center justify-between p-3 border border-border rounded-lg"
              >
                <div>
                  <p className="font-medium text-foreground">{student.name}</p>
                  <p className="text-sm text-muted-foreground">{student.email}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">ID: {student.id}</p>
                  <p className="text-sm font-medium text-primary">{student.department}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
