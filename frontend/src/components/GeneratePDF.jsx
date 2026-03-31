import jsPDF from "jspdf";
import html2canvas from "html2canvas";

const GeneratePDF = ({ data }) => {

  const generatePDF = async () => {
    const input = document.getElementById("pdf-content");

    const canvas = await html2canvas(input, { scale: 2 });
    const imgData = canvas.toDataURL("image/png");

    const pdf = new jsPDF("p", "mm", "a4");

    const imgWidth = 210;
    const pageHeight = 295;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    let heightLeft = imgHeight;
    let position = 0;

    pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    // Multiple pages support
    while (heightLeft > 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    pdf.save("inventory-report.pdf");
  };

  return (
    <div>
      {/* Button */}
      <button
        onClick={generatePDF}
        style={{
          backgroundColor: "blue",
          color: "white",
          padding: "10px",
          marginBottom: "10px",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer"
        }}
      >
        Download PDF
      </button>

      {/* PDF Content */}
      <div id="pdf-content" style={{ padding: "20px", background: "white" }}>
        <h2>Inventory Report</h2>

        <table border="1" width="100%" style={{ borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th>Component</th>
              <th>Material</th>
              <th>Quantity</th>
              <th>Category</th>
            </tr>
          </thead>

          <tbody>
            {data && data.map((item, index) => (
              <tr key={index}>
                <td>{item.name || "-"}</td>
                <td>{item.material || "-"}</td>
                <td>{item.quantity || "-"}</td>
                <td>{item.category || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <p style={{ marginTop: "20px" }}>
          Date: {new Date().toLocaleDateString()}
        </p>
      </div>
    </div>
  );
};

export default GeneratePDF;