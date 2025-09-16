import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
} from "@mui/material";
import { FmeaRow } from "../../types";

interface FmeaTableProps {
  fmeaRows: FmeaRow[];
}

const FmeaTable: React.FC<FmeaTableProps> = ({ fmeaRows }) => {
  return (
    <TableContainer component={Paper} sx={{ mt: 4, boxShadow: 3 }}>
      <Typography variant="h6" sx={{ p: 2 }}>
        FMEA Table
      </Typography>
      <Table sx={{ minWidth: 1200 }} aria-label="FMEA Table">
        <TableHead>
          <TableRow sx={{ backgroundColor: "#f5f5f5" }}>
            <TableCell>ID</TableCell>
            <TableCell>Location</TableCell>
            <TableCell>Component</TableCell>
            <TableCell>Failure Mode</TableCell>
            <TableCell>Effect</TableCell>
            <TableCell>Cause</TableCell>
            <TableCell>Severity</TableCell>
            <TableCell>Probability</TableCell>
            <TableCell>Detection</TableCell>
            <TableCell>RPN</TableCell>
            <TableCell>Mitigation</TableCell>
            <TableCell>Action Taken</TableCell>
            <TableCell>Post-Mitigation Severity</TableCell>
            <TableCell>Post-Mitigation Probability</TableCell>
            <TableCell>Post-Mitigation Detection</TableCell>
            <TableCell>Post-Mitigation RPN</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {fmeaRows.map((row) => (
            <TableRow key={row.id} hover>
              <TableCell>{row.id}</TableCell>
              <TableCell>{row.location}</TableCell>
              <TableCell>{row.component}</TableCell>
              <TableCell>{row.failure_mode}</TableCell>
              <TableCell>{row.effect}</TableCell>
              <TableCell>{row.cause}</TableCell>
              <TableCell>{row.severity}</TableCell>
              <TableCell>{row.probability}</TableCell>
              <TableCell>{row.detection}</TableCell>
              <TableCell>{row.rpn}</TableCell>
              <TableCell>{row.mitigation}</TableCell>
              <TableCell>{row.action_taken}</TableCell>
              <TableCell>{row.revised_severity}</TableCell>
              <TableCell>{row.revised_probability}</TableCell>
              <TableCell>{row.revised_detection}</TableCell>
              <TableCell>{row.revised_rpn}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default FmeaTable;
