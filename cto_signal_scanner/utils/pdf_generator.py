from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime, timedelta
from pathlib import Path
import shutil

class ReportGenerator:
    def __init__(self, output_path=None, max_reports=30):
        """
        Initialize the report generator.
        
        Args:
            output_path: Optional custom path for the PDF
            max_reports: Maximum number of reports to keep (default 30)
        """
        # Create reports directory structure
        self.reports_dir = Path('reports')
        self.reports_dir.mkdir(exist_ok=True)
        
        # Create dated subdirectory
        today = datetime.now().strftime("%Y-%m")
        self.current_month_dir = self.reports_dir / today
        self.current_month_dir.mkdir(exist_ok=True)
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.current_month_dir / f"tech_report_{timestamp}.pdf"
        
        self.doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='Link',
            parent=self.styles['Normal'],
            textColor=colors.blue,
            underline=True
        ))
        
        self.styles.add(ParagraphStyle(
            name='Rating',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.darkgreen
        ))
        
        # Clean up old reports
        self.cleanup_old_reports(max_reports)

    def cleanup_old_reports(self, max_reports):
        """Remove old reports keeping only the specified number of most recent ones."""
        # Get all PDF files from all subdirectories
        all_reports = []
        for month_dir in self.reports_dir.glob("*"):
            if month_dir.is_dir():
                all_reports.extend(month_dir.glob("*.pdf"))
        
        # Sort by creation time (newest first)
        all_reports.sort(key=lambda x: x.stat().st_ctime, reverse=True)
        
        # Remove excess reports
        if len(all_reports) > max_reports:
            for old_report in all_reports[max_reports:]:
                old_report.unlink()
            
            # Clean up empty directories
            for month_dir in self.reports_dir.glob("*"):
                if month_dir.is_dir() and not any(month_dir.iterdir()):
                    month_dir.rmdir()

    def add_header(self, days_back):
        """Add header to the report."""
        title = f"CTO Signal Scanner Report"
        date_range = f"Articles from the last {days_back} days"
        generated = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.story.append(Paragraph(title, self.styles['Heading1']))
        self.story.append(Paragraph(date_range, self.styles['Heading2']))
        self.story.append(Paragraph(generated, self.styles['Normal']))
        self.story.append(Spacer(1, 20))

    def add_article(self, title, link, summary, rating, rationale):
        """Add an article to the report."""
        # Add title with link
        self.story.append(Paragraph(f"<a href='{link}'>{title}</a>", self.styles['Link']))
        self.story.append(Spacer(1, 10))
        
        # Add summary
        self.story.append(Paragraph(f"Summary: {summary}", self.styles['Normal']))
        self.story.append(Spacer(1, 10))
        
        # Add rating and rationale
        self.story.append(Paragraph(f"Rating: {rating}/10", self.styles['Rating']))
        self.story.append(Paragraph(f"Rationale: {rationale}", self.styles['Normal']))
        self.story.append(Spacer(1, 20))

    def generate(self):
        """Generate the PDF report."""
        self.doc.build(self.story)
        print(f"\nReport generated: {self.doc.filename}")
        print(f"Reports directory: {self.reports_dir.absolute()}") 