import React from 'react';
import { Box, Paper, Typography, Grid, Card, CardContent } from '@mui/material';
import { TrendingUp, TrendingDown, AttachMoney } from '@mui/icons-material';
import { FmeaRow } from '../../types';

interface FinancialRiskPanelProps {
  fmeaRows: FmeaRow[];
}

const FinancialRiskPanel: React.FC<FinancialRiskPanelProps> = ({ fmeaRows }) => {
  const totalFinancialImpact = fmeaRows.reduce((sum, row) => {
    return sum + (row.financial_impact || 0);
  }, 0);

  const averageFinancialImpact =
    fmeaRows.length > 0 ? totalFinancialImpact / fmeaRows.length : 0;

  const highRiskRows = fmeaRows.filter(
    (row) => (row.financial_impact || 0) > averageFinancialImpact * 1.5
  );

  const mediumRiskRows = fmeaRows.filter(
    (row) =>
      (row.financial_impact || 0) <= averageFinancialImpact * 1.5 &&
      (row.financial_impact || 0) > averageFinancialImpact * 0.5
  );

  const lowRiskRows = fmeaRows.filter(
    (row) => (row.financial_impact || 0) <= averageFinancialImpact * 0.5
  );

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <Paper sx={{ p: 3, mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Financial Risk Analysis
      </Typography>

      <Grid container spacing={2} sx={{ mt: 1 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AttachMoney color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Impact</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {formatCurrency(totalFinancialImpact)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">High Risk</Typography>
              </Box>
              <Typography variant="h4" color="error">
                {highRiskRows.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatCurrency(
                  highRiskRows.reduce((sum, row) => sum + (row.financial_impact || 0), 0)
                )}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingDown color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Average Impact</Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                {formatCurrency(averageFinancialImpact)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Risk Distribution
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Box>
            <Typography variant="body2" color="error">
              High Risk: {highRiskRows.length} rows
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="warning.main">
              Medium Risk: {mediumRiskRows.length} rows
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="success.main">
              Low Risk: {lowRiskRows.length} rows
            </Typography>
          </Box>
        </Box>
      </Box>
    </Paper>
  );
};

export default FinancialRiskPanel;

