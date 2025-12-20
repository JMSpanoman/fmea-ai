import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader, Card, CardContent, CardHeader, CardTitle, Badge, Button } from '../components/ui';
import { getProjects, Project } from '../services/apiService';
import authService from '../services/authService';

const DashboardPageNew: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      if (!authService.isAuthenticated()) {
        await authService.authenticate();
      }
      const data = await getProjects();
      setProjects(data);
    } catch (err) {
      console.error('Error fetching projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const metrics = [
    { label: 'Total Open Risks', value: '12', change: '+3', variant: 'danger' as const, icon: '🛡️' },
    { label: 'High RPN Count', value: '8', change: '+2', variant: 'danger' as const, icon: '⚠️' },
    { label: 'Open CAPAs', value: '8', change: '4 due soon', variant: 'info' as const, icon: '🔧' },
    { label: 'Open Changes', value: '7', change: '3 today', variant: 'success' as const, icon: '🔄' },
  ];

  const aiInsights = [
    'Top 5 high-risk items need immediate attention',
    'Open CAPAs with high risk require review',
    '3 change controls pending approval',
  ];

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Overview of your quality management activities"
      />

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {metrics.map((metric) => (
          <Card key={metric.label} hover>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-2xl">{metric.icon}</span>
                <Badge variant={metric.variant} size="sm">
                  {metric.change}
                </Badge>
              </div>
              <div className="mb-2">
                <p className="text-3xl font-bold text-text-primary">{metric.value}</p>
                <p className="text-sm text-text-secondary mt-1">{metric.label}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Risk Trends */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Risk Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-surface-secondary rounded-lg">
                <span className="text-sm text-text-secondary">Power Management IC</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-surface-primary rounded-full overflow-hidden">
                    <div className="h-full bg-danger rounded-full" style={{ width: '85%' }} />
                  </div>
                  <Badge variant="danger">85</Badge>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-surface-secondary rounded-lg">
                <span className="text-sm text-text-secondary">Battery Life Sensor</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-surface-primary rounded-full overflow-hidden">
                    <div className="h-full bg-warning rounded-full" style={{ width: '72%' }} />
                  </div>
                  <Badge variant="warning">72</Badge>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-surface-secondary rounded-lg">
                <span className="text-sm text-text-secondary">Signal Processing Unit</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-surface-primary rounded-full overflow-hidden">
                    <div className="h-full bg-primary rounded-full" style={{ width: '64%' }} />
                  </div>
                  <Badge variant="info">64</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI Insights */}
        <Card>
          <CardHeader>
            <CardTitle>✨ AI Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {aiInsights.map((insight, index) => (
                <div
                  key={index}
                  className="p-3 bg-surface-secondary rounded-lg border border-border"
                >
                  <p className="text-sm text-text-primary">{insight}</p>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <Button variant="primary" size="sm" className="w-full">
                View All Insights
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Projects Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Recent Projects</CardTitle>
            <Button variant="secondary" size="sm" onClick={() => navigate('/projects')}>
              View All
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-text-secondary">Loading projects...</div>
          ) : projects.length === 0 ? (
            <div className="text-center py-8 text-text-secondary">No projects found</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.slice(0, 6).map((project) => (
                <Card
                  key={project.id}
                  hover
                  onClick={() => navigate(`/dfmea?project=${project.id}`)}
                  className="p-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-h3 font-semibold text-text-primary">{project.name}</h3>
                    <Badge variant="info">Active</Badge>
                  </div>
                  {project.description && (
                    <p className="text-sm text-text-secondary mb-3 line-clamp-2">
                      {project.description}
                    </p>
                  )}
                  <div className="flex items-center justify-between text-xs text-text-secondary">
                    <span>Created: {new Date(project.created_at).toLocaleDateString()}</span>
                    <Button variant="ghost" size="sm">
                      View →
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardPageNew;

