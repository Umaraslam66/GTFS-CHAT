import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";

interface DataTableProps {
  headers: string[];
  rows: (string | number)[][];
  caption?: string;
}

const DataTable = ({ headers, rows, caption }: DataTableProps) => {
  return (
    <div className="mt-3 rounded-md border border-border overflow-hidden">
      {caption && (
        <div className="px-4 py-2 bg-card border-b border-border">
          <p className="text-sm font-medium text-foreground">{caption}</p>
        </div>
      )}
      <ScrollArea className="w-full">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/50 hover:bg-muted/50">
              {headers.map((header, index) => (
                <TableHead
                  key={index}
                  className="text-xs font-semibold text-muted-foreground uppercase tracking-wide whitespace-nowrap"
                >
                  {header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row, rowIndex) => (
              <TableRow
                key={rowIndex}
                className={rowIndex % 2 === 0 ? "bg-background" : "bg-card/50"}
              >
                {row.map((cell, cellIndex) => (
                  <TableCell
                    key={cellIndex}
                    className="text-sm text-foreground whitespace-nowrap"
                  >
                    {cell}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
    </div>
  );
};

export default DataTable;
