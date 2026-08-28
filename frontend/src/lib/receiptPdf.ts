import { jsPDF } from "jspdf";
import type { Field, Receipt } from "./types";
import { fieldLabel } from "./fieldLabels";

export type ReceiptPdfInput = {
  receipt: Receipt;
  serviceName?: string | null;
  fields?: Field[];
};

function formatFieldValue(field: Field): string {
  if (field.value == null || field.value === "") return "Not provided";
  if (field.id === "photo") return "Attached";
  return String(field.value).replace(/\s+/g, " ").trim();
}

function safeFilename(reference: string): string {
  return reference.replace(/[^\w-]+/g, "-").replace(/-+/g, "-") || "civic-ticket";
}

export function downloadReceiptPdf({ receipt, serviceName, fields = [] }: ReceiptPdfInput): void {
  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const margin = 16;
  const pageWidth = doc.internal.pageSize.getWidth();
  const contentWidth = pageWidth - margin * 2;
  let y = 18;

  const addLine = (text: string, size = 11, style: "normal" | "bold" = "normal") => {
    doc.setFont("helvetica", style);
    doc.setFontSize(size);
    const lines = doc.splitTextToSize(text, contentWidth) as string[];
    for (const line of lines) {
      if (y > 280) {
        doc.addPage();
        y = 18;
      }
      doc.text(line, margin, y);
      y += size * 0.45 + 2;
    }
  };

  const addGap = (gap = 4) => {
    y += gap;
  };

  doc.setDrawColor(11, 58, 110);
  doc.setFillColor(11, 58, 110);
  doc.rect(0, 0, pageWidth, 12, "F");
  doc.setTextColor(255, 255, 255);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  doc.text("Municipal Civic Cell — CivicAgent Prototype", margin, 8);
  doc.setTextColor(0, 0, 0);

  y = 22;
  addLine("Grievance acknowledgement", 18, "bold");
  addGap(2);
  addLine("Demo receipt only. Not sent to a live government department.", 9);
  addGap(6);

  addLine(`Service request ID: ${receipt.reference}`, 12, "bold");
  if (receipt.access_key) {
    addLine(`Access key: ${receipt.access_key}`, 12, "bold");
    addLine("Save this key to track your request.", 10);
  }
  addGap(4);

  addLine(`Status: ${receipt.status}`);
  addLine(`Department: ${receipt.department || "Civic services"}`);
  addLine(`Submitted: ${new Date(receipt.timestamp).toLocaleString("en-IN")}`);
  if (serviceName) {
    addLine(`Service: ${serviceName}`);
  }

  const detailFields = fields.filter(
    (field) => field.value != null && field.value !== "" && field.status !== "missing",
  );
  if (detailFields.length) {
    addGap(6);
    addLine("Issue details", 13, "bold");
    addGap(2);
    for (const field of detailFields) {
      addLine(`${fieldLabel(field.id)}: ${formatFieldValue(field)}`, 10);
    }
  }

  addGap(8);
  doc.setDrawColor(200, 200, 200);
  doc.line(margin, y, pageWidth - margin, y);
  addGap(4);
  addLine(
    "Track your request at /track using the service request ID and access key above.",
    9,
  );

  doc.save(`${safeFilename(receipt.reference)}.pdf`);
}
